#!/usr/bin/env python3


# +
# import(s)
# -
import base64
import boto3
import fastavro
import io
import os

from astropy.coordinates import SkyCoord
from astropy.time import Time

from kafka import KafkaConsumer
from botocore.exceptions import ClientError
from sqlalchemy import exc

from src.models.ztf import ZtfAlert
from src.models.ztf import db
from src.app import app
from src.app import logger


# +
# constant(s)
# -
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID", None)
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", None)
AWS_USE_S3 = False if AWS_ACCESS_KEY is None else True
BUCKET_NAME = os.getenv("S3_BUCKET", None)

GROUP_ID = 'LCOGT'
PRODUCER_HOST = 'public.alerts.ztf.uw.edu'
PRODUCER_PORT = '9092'
TOPIC = "^(ztf_\d{8}_programid1)"


# +
# create AWS session
# -
if AWS_USE_S3:
    session = boto3.Session(aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    s3 = session.resource('s3')
else:
    s3 = None


# +
# (hidden) function: _packet_path()
# -
def _packet_path(packet=None):

    # check input(s) and return string
    if packet is not None and 'candidate' in packet and 'jd' in packet['candidate']:
        jd_time = Time(packet['candidate']['jd'], format='jd')
        return '{}/{}/{}/'.format(
            jd_time.datetime.year, str(jd_time.datetime.month).zfill(2), str(jd_time.datetime.day).zfill(2)
        )
    else:
        return ''


# +
# function: do_ingest()
# -
# noinspection PyBroadException
def do_ingest(encoded_packet=None):

    # check input(s)
    if encoded_packet is None:
        raise Exception('do_ingest() entry: encoded packet is empty')
    else:
        logger.info('encoded_packet contains data')

    # decode the packet
    try:
        f_data = base64.b64decode(encoded_packet)
    except Exception as e:
        raise Exception(f'Unable to decode packet, error={e}')
    else:
        logger.info('encoded_packet decoded OK')

    # get data
    try:
        freader = fastavro.reader(io.BytesIO(f_data))
        for packet in freader:
            logger.info('Calling ingest_avro()')
            ingest_avro(packet)
    except Exception as e:
        raise Exception(f'Packet read error, unable to ingest data, error={e}')

    # if using AWS, upload the file to the S3 bucket
    if AWS_USE_S3:
        try:
            freader = fastavro.reader(io.BytesIO(f_data))
            for packet in freader:
                fname = '{}.avro'.format(packet['candid'])
                logger.info('Calling upload_avro()')
                upload_avro(io.BytesIO(f_data), fname, packet)
        except Exception as e:
            raise Exception(f'Packet upload error, unable to upload data, error={e}')


# +
# function: ingest_avro
# -
def ingest_avro(packet=None):

    # check input(s)
    if packet is None or 'candidate' not in packet or 'prv_candidates' not in packet:
        raise Exception('ingest_avro() entry: packet is empty!')

    # ingest data
    with app.app_context():

        ra = packet['candidate'].pop('ra')
        dec = packet['candidate'].pop('dec')
        location = f'srid=4035;POINT({ra} {dec})'
        c = SkyCoord(ra, dec, unit='deg')
        galactic = c.galactic

        deltamaglatest = None
        if packet['prv_candidates']:
            prv_candidates = sorted(packet['prv_candidates'], key=lambda x: x['jd'], reverse=True)
            for candidate in prv_candidates:
                if packet['candidate']['fid'] == candidate['fid'] and candidate['magpsf']:
                    deltamaglatest = packet['candidate']['magpsf'] - candidate['magpsf']
                    break

        deltamagref = None
        if packet['candidate']['distnr'] < 2:
            deltamagref = packet['candidate']['magnr'] - packet['candidate']['magpsf']

        alert = ZtfAlert(
            objectId=packet['objectId'],
            publisher=packet.get('publisher', ''),
            alert_candid=packet['candid'],
            location=location,
            deltamaglatest=deltamaglatest,
            deltamagref=deltamagref,
            gal_l=galactic.l.value,
            gal_b=galactic.b.value,
            **packet['candidate']
            )
        try:
            logger.info('Updating object database', extra={'tags': {'candid': alert.alert_candid}})
            # db.session.update(alert)
            db.session.add(alert)
            db.session.commit()
            logger.info('Updated object into database', extra={'tags': {'candid': alert.alert_candid}})
        except exc.SQLAlchemyError:
            db.session.rollback()
            logger.warn('Failed to update object into database', extra={'tags': {'candid': alert.alert_candid}})


# +
# function: upload_avro()
# -
def upload_avro(f=None, fname='', packet=None):

    # check input(s)
    if f is None:
        raise Exception('upload_avro() entry: data is not present')

    if not isinstance(fname, str) or fname.strip() == '':
        raise Exception('upload_avro() entry: fname is empty')

    if packet is None:
        raise Exception('upload_avro() entry: packet is empty')

    date_key = _packet_path(packet)
    filename = '{}{}'.format(date_key, fname)
    logger.info('filename={}'.format(filename))

    if AWS_USE_S3:
        try:
            s3.Object(BUCKET_NAME, filename).put(
                Body=f,
                ContentDisposition=f'attachment; filename={filename}',
                ContentType='avro/binary'
            )
            logger.info('Successfully uploaded file to s3', extra={'tags': {'filename': filename}})
        except ClientError as e:
            logger.warn('Failed to upload file to s3 (e={})'.format(e), extra={'tags': {'filename': filename}})
    else:
        pass


# +
# function: start_consumer()
# -
def start_consumer():

    # noinspection PyBroadException
    try:
        # get consumer
        consumer = KafkaConsumer(bootstrap_servers=f'{PRODUCER_HOST}:{PRODUCER_PORT}', group_id=GROUP_ID)
        consumer.subscribe(pattern=TOPIC)
        logger.info('Successfully subscribed to Kafka topic',
                    extra={'tags': {'subscribed_topics': list(consumer.subscription())}})
    except Exception as e:
        logger.error(f'Failed to subscribe to Kafka {PRODUCER_HOST}:{PRODUCER_PORT} for group {GROUP_ID}, error={e}')
    else:

        # process message(s)
        for msg in consumer:
            if hasattr(msg, 'value'):
                alert = msg.value
                logger.debug('Received alert from stream, ingesting ...')
                do_ingest(base64.b64encode(alert).decode('UTF-8'))
                logger.debug('Ingested alert, committing index to Kafka producer')
                consumer.commit()
                logger.debug('Committed index to Kafka producer')
            else:
                logger.error('Alert has now value!')


# +
# main()
# -
if __name__ == '__main__':
    db.create_all()
    start_consumer()
