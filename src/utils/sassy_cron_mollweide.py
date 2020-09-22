#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# +
# import(s)
# -
from sqlalchemy import create_engine
from src import *
from src.common import *
from src.models.sassy_cron import *
from src.utils.Alerce import Alerce
from src.utils.utils import UtilsLogger

import io
import itertools
import math
import matplotlib.pyplot as plt
import os
import unicodedata


# +
# constant(s)
# -
CLASSIFIERS = Alerce().alerce_early_classifier
PROPORTIONAL = unicodedata.lookup('PROPORTIONAL TO')
SASSY_DB_HOST = os.getenv('SASSY_DB_HOST', None)
SASSY_DB_USER = os.getenv('SASSY_DB_USER', None)
SASSY_DB_PASS = os.getenv('SASSY_DB_PASS', None)
SASSY_DB_NAME = os.getenv('SASSY_DB_NAME', None)
SASSY_DB_PORT = os.getenv('SASSY_DB_PORT', None)


# +
# function: db_connect()
# -
# noinspection PyBroadException
def db_connect():
    try:
        engine = create_engine(
            f'postgresql+psycopg2://{SASSY_DB_USER}:{SASSY_DB_PASS}@{SASSY_DB_HOST}:{SASSY_DB_PORT}/{SASSY_DB_NAME}')
        get_session = sessionmaker(bind=engine)
        return get_session()
    except Exception as e:
        print(f'Failed to connect to database, error={e}')
        return None


# +
# function: db_disconnect()
# -
# noinspection PyBroadException
def db_disconnect(_session=None):
    try:
        _session.close()
        _session.close_all_sessions()
    except Exception:
        pass


# +
# function: sassy_cron_mollweide()
# -
# noinspection PyBroadException,PyUnresolvedReferences
def sassy_cron_mollweide(_log=None, _output='sassy_cron_mollweide.png'):

    # set default(s)
    list_g_0, list_g_1, list_g_2, list_g_3, list_g_4, list_g_5 = [], [], [], [], [], []
    list_r_0, list_r_1, list_r_2, list_r_3, list_r_4, list_r_5 = [], [], [], [], [], []
    list_i_0, list_i_1, list_i_2, list_i_3, list_i_4, list_i_5 = [], [], [], [], [], []
    list_glade = []
    _buf = io.BytesIO()

    # connect to database
    _s = db_connect()

    # get data
    _query = _s.query(SassyCron)
    for _q in _query.all():

        # add glade candidate
        list_glade.append([math.radians(_q.gra-180.0), math.radians(_q.gdec), 100.0/_q.gdist])

        # g filter
        if _q.zfid == 1:
            if _q.aetype.strip() == CLASSIFIERS[0]:
                list_g_0.append([math.radians(_q.zra-180.0), math.radians(_q.zdec), 50.0*_q.aeprob])
            elif _q.aetype.strip() == CLASSIFIERS[1]:
                list_g_1.append([math.radians(_q.zra-180.0), math.radians(_q.zdec), 50.0*_q.aeprob]) 
            elif _q.aetype.strip() == CLASSIFIERS[2]:
                list_g_2.append([math.radians(_q.zra-180.0), math.radians(_q.zdec), 50.0*_q.aeprob]) 
            elif _q.aetype.strip() == CLASSIFIERS[3]:
                list_g_3.append([math.radians(_q.zra-180.0), math.radians(_q.zdec), 50.0*_q.aeprob]) 
            elif _q.aetype.strip() == CLASSIFIERS[4]:
                list_g_4.append([math.radians(_q.zra-180.0), math.radians(_q.zdec), 50.0*_q.aeprob]) 
            else:
                list_g_5.append([math.radians(_q.zra-180.0), math.radians(_q.zdec), 25.0]) 

        # r filter
        elif _q.zfid == 2:
            if _q.aetype.strip() == CLASSIFIERS[0]:
                list_r_0.append([math.radians(_q.zra-180.0), math.radians(_q.zdec), 50.0*_q.aeprob]) 
            elif _q.aetype.strip() == CLASSIFIERS[1]:
                list_r_1.append([math.radians(_q.zra-180.0), math.radians(_q.zdec), 50.0*_q.aeprob]) 
            elif _q.aetype.strip() == CLASSIFIERS[2]:
                list_r_2.append([math.radians(_q.zra-180.0), math.radians(_q.zdec), 50.0*_q.aeprob]) 
            elif _q.aetype.strip() == CLASSIFIERS[3]:
                list_r_3.append([math.radians(_q.zra-180.0), math.radians(_q.zdec), 50.0*_q.aeprob]) 
            elif _q.aetype.strip() == CLASSIFIERS[4]:
                list_r_4.append([math.radians(_q.zra-180.0), math.radians(_q.zdec), 50.0*_q.aeprob]) 
            else:
                list_r_5.append([math.radians(_q.zra-180.0), math.radians(_q.zdec), 25.0]) 

        # i filter
        elif _q.zfid == 3:
            if _q.aetype.strip() == CLASSIFIERS[0]:
                list_r_0.append([math.radians(_q.zra-180.0), math.radians(_q.zdec), 50.0*_q.aeprob]) 
            elif _q.aetype.strip() == CLASSIFIERS[1]:
                list_r_1.append([math.radians(_q.zra-180.0), math.radians(_q.zdec), 50.0*_q.aeprob]) 
            elif _q.aetype.strip() == CLASSIFIERS[2]:
                list_r_2.append([math.radians(_q.zra-180.0), math.radians(_q.zdec), 50.0*_q.aeprob]) 
            elif _q.aetype.strip() == CLASSIFIERS[3]:
                list_r_3.append([math.radians(_q.zra-180.0), math.radians(_q.zdec), 50.0*_q.aeprob]) 
            elif _q.aetype.strip() == CLASSIFIERS[4]:
                list_r_4.append([math.radians(_q.zra-180.0), math.radians(_q.zdec), 50.0*_q.aeprob]) 
            else:
                list_r_5.append([math.radians(_q.zra-180.0), math.radians(_q.zdec), 25.0]) 
        else:
            if _log:
                _log.error(f"{_q} has unknown filter")

    # disconnect from database
    db_disconnect(_s)

    # plot it
    fig = plt.figure(figsize=(8,6))
    fig.set_tight_layout(True)
    ax = fig.add_subplot(111, projection="mollweide")

    try:
        x, y, z = zip(*list_glade)
        ax.scatter(x, y, color='black', s=z, alpha=0.25, marker='.', label="Glade")
    except:
        pass

    try:
        x, y, z = zip(*list_g_0)
        ax.scatter(x, y, color='green', s=z, alpha=0.25, marker='o', label="AGN")
        x, y, z = zip(*list_g_1)
        ax.scatter(x, y, color='green', s=z, alpha=0.25, marker='d', label="Supernova")
        x, y, z = zip(*list_g_2)
        ax.scatter(x, y, color='green', s=z, alpha=0.25, marker='^', label="Variable Star")
        x, y, z = zip(*list_g_3)
        ax.scatter(x, y, color='green', s=z, alpha=0.25, marker='s', label="Asteroid")
        x, y, z = zip(*list_g_4)
        ax.scatter(x, y, color='green', s=z, alpha=0.25, marker='+', label="Bogus")
        x, y, z = zip(*list_g_5)
        ax.scatter(x, y, color='green', s=z, alpha=0.25, marker='x', label="None")
    except:
        pass

    try:
        x, y, z = zip(*list_r_0)
        ax.scatter(x, y, color='red', s=z, alpha=0.25, marker='o')
        x, y, z = zip(*list_r_1)
        ax.scatter(x, y, color='red', s=z, alpha=0.25, marker='d')
        x, y, z = zip(*list_r_2)
        ax.scatter(x, y, color='red', s=z, alpha=0.25, marker='^')
        x, y, z = zip(*list_r_3)
        ax.scatter(x, y, color='red', s=z, alpha=0.25, marker='s')
        x, y, z = zip(*list_r_4)
        ax.scatter(x, y, color='red', s=z, alpha=0.25, marker='+')
        x, y, z = zip(*list_r_5)
        ax.scatter(x, y, color='red', s=z, alpha=0.25, marker='x')
    except:
        pass

    try:
        x, y, z = zip(*list_i_0)
        ax.scatter(x, y, color='orange', s=z, alpha=0.25, marker='o')
        x, y, z = zip(*list_i_1)
        ax.scatter(x, y, color='orange', s=z, alpha=0.25, marker='d')
        x, y, z = zip(*list_i_2)
        ax.scatter(x, y, color='orange', s=z, alpha=0.25, marker='^')
        x, y, z = zip(*list_i_3)
        ax.scatter(x, y, color='orange', s=z, alpha=0.25, marker='s')
        x, y, z = zip(*list_i_4)
        ax.scatter(x, y, color='orange', s=z, alpha=0.25, marker='+')
        x, y, z = zip(*list_i_5)
        ax.scatter(x, y, color='orange', s=z, alpha=0.25, marker='x')
    except:
        pass

    _l = list(itertools.chain(list_g_0, list_g_1, list_g_2, list_g_3, list_g_4, list_g_5,
              list_r_0, list_r_1, list_r_2, list_r_3, list_r_4, list_r_5,
              list_i_0, list_i_1, list_i_2, list_i_3, list_i_4, list_i_5))

    ax.set_xticklabels(['14h','16h','18h','20h','22h','0h','2h','4h','6h','8h','10h'])
    ax.grid(True)
    plt.legend(loc='lower center')
    plt.title(f"{len(_l)} SassyCron Target(s), {len(list_glade)} Glade Galaxies\n(Marker Area {PROPORTIONAL} Classifier Probability, except for None)")
    if _output.strip() != '':
        plt.savefig(_output)
        plt.savefig(_buf, format='png', dpi=100, bbox_inches='tight')
        plt.close()
    else:
        plt.show()



# +
# main()
# -
if __name__ == '__main__':
    sassy_cron_mollweide(_log=UtilsLogger('SassyCronMollweide').logger, _output='')
