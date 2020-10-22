#!/usr/bin/env python3


# +
# import(s)
# -
import argparse
import pprint
import psycopg2
import os
import sys


# +
# dunder string(s)
# -
__author__ = 'Philip N. Daly'
__date__ = '7 December, 2018'
__doc__ = """

    usage: psql.test.py [-h] [-a AUTHORIZATION] [-c COMMAND] [-d DATABASE] [-p PORT] [-s SERVER] [-v]

"""
__email__ = 'pndaly@email.arizona.edu'
__institution__ = 'Steward Observatory, 933 N. Cherry Avenue, Tucson AZ 85719'


# +
# constant(s)
# -
SASSY_DB_AUTHORIZATION = f"{os.getenv('SASSY_DB_USER', None)}:{os.getenv('SASSY_DB_PASS', None)}"
SASSY_DB_HOST = os.getenv('SASSY_DB_HOST', None)
SASSY_DB_NAME = os.getenv('SASSY_DB_NAME', None)
SASSY_DB_PORT = int(os.getenv('SASSY_DB_PORT', None))

FETCH_METHOD = ['raw', 'fetchall', 'fetchone', 'fetchmany']
FETCH_MANY = 5


# +
# class: PsqlConnectionTester()
# -
class PsqlConnectionTester(object):

    # +
    # method: __init__()
    # -
    def __init__(self, database=SASSY_DB_NAME, authorization=SASSY_DB_AUTHORIZATION,
                 server=SASSY_DB_HOST, port=SASSY_DB_PORT, verbose=False):
        """ initialize the class """

        # get input(s)
        self.database = database
        self.authorization = authorization
        self.server = server
        self.port = port
        self.verbose = verbose

        # private variable(s)
        self.__connection = None
        self.__cursor = None
        self.__connection_string = None
        self.__result = None
        self.__results = None

    # +
    # decorator(s)
    # -
    @property
    def database(self):
        return self.__database

    @database.setter
    def database(self, database):
        self.__database = database if (isinstance(database, str) and database.strip() != f'') else SASSY_DB_NAME

    @property
    def authorization(self):
        return self.__authorization

    @authorization.setter
    def authorization(self, authorization):
        self.__authorization = authorization if (
                isinstance(authorization, str) and authorization.strip() != f'' and
                f':' in authorization) else SASSY_DB_AUTHORIZATION
        self.__username, self.__password = self.__authorization.split(f':')

    @property
    def server(self):
        return self.__server

    @server.setter
    def server(self, server):
        self.__server = server if (isinstance(server, str) and server.strip() != f'') else SASSY_DB_HOST

    @property
    def port(self):
        return self.__port

    @port.setter
    def port(self, port):
        self.__port = port if (isinstance(port, int) and port > 0) else int(SASSY_DB_PORT)

    @property
    def verbose(self):
        return self.__verbose

    @verbose.setter
    def verbose(self, verbose):
        self.__verbose = True if (isinstance(verbose, bool) and verbose) else False

    # +
    # method: connect()
    # -
    def connect(self):
        """ connect to database """

        # set variable(s)
        self.__connection = None
        self.__cursor = None
        self.__connection_string = f"host='{self.server}' dbname='{self.database}' " \
            f"user='{self.__username}' password='{self.__password}'"
        if self.verbose:
            print(f'Connection string is "{self.__connection_string}"')

        # get connection
        if self.verbose:
            print(f'Connecting to {self.database} on {self.server}:{self.port} with {self.authorization}')

        try:
            self.__connection = psycopg2.connect(self.__connection_string)
        except Exception as e:
            raise Exception(f'Failed to connect to {self.database} on '
                            f'{self.server}:{self.port} with {self.authorization}, error={e}')
        else:
            if self.verbose:
                print(f'Connected to {self.database} on {self.server}:{self.port} with {self.authorization}')

        # get cursor
        if self.verbose:
            print(f'Getting cursor for {self.database} on {self.server}:{self.port} with {self.authorization}')
        try:
            self.__cursor = self.__connection.cursor()
        except Exception as e:
            raise Exception(f'Failed to get cursor for {self.database} on '
                            f'{self.server}:{self.port} with {self.authorization}. error={e}')
        else:
            if self.verbose:
                print(f'Got cursor for {self.database} on {self.server}:{self.port} with {self.authorization}')

    # +
    # method: disconnect()
    # -
    def disconnect(self):
        """ disconnect from database """

        # disconnect cursor
        if self.__cursor is not None:
            if self.verbose:
                print(f'Disconnecting cursor')
            self.__cursor.close()

        # disconnect connection
        if self.__connection is not None:
            if self.verbose:
                print(f'Disconnecting connection')
            self.__connection.close()

        # reset variable(s)
        self.__connection = None
        self.__cursor = None

    # +
    # method: fetchall()
    # -
    def fetchall(self, command=''):
        """ execute fetchall() command """

        # check input(s)
        if not isinstance(command, str) or command.strip() == '':
            raise Exception(f'invalid input, command={command}')

        # return if nothing to do
        if self.__cursor is None:
            return f''

        # execute query
        if self.verbose:
            print(f'Executing "{command}"')
        self.__cursor.execute(command)
        if self.verbose:
            print(f'Executed "{command}"')

        # fetch all result(s)
        self.__results = self.__cursor.fetchall()
        return self.__results

    # +
    # method: fetchmany()
    # -
    def fetchmany(self, command='', number=0):
        """ execute fetchmany() command """

        # check input(s)
        if not isinstance(command, str) or command.strip() == '':
            raise Exception(f'invalid input, command={command}')
        if not isinstance(number, int) or number <= 0:
            raise Exception(f'invalid input, number={number}')

        # return if nothing to do
        if self.__cursor is None:
            return f''

        # execute query
        if self.verbose:
            print(f'Executing "{command}"')
        self.__cursor.execute(command)
        if self.verbose:
            print(f'Executed "{command}"')

        # fetch many result(s)
        self.__results = self.__cursor.fetchall()
        return self.__results

    # +
    # method: fetchone()
    # -
    def fetchone(self, command=''):
        """ execute fetchone() command """

        # check input(s)
        if not isinstance(command, str) or command.strip() == '':
            raise Exception(f'invalid input, command={command}')

        # return if nothing to do
        if self.__cursor is None:
            return f''

        # execute query
        if self.verbose:
            print(f'Executing {command}')
        self.__cursor.execute(command)
        if self.verbose:
            print(f'Executed {command}')

        # fetch one result
        self.__result = self.__cursor.fetchall()
        return self.__result

    # +
    # method: raw()
    # -
    def raw(self, command=''):
        """ execute fetchone() command """

        # check input(s)
        if not isinstance(command, str) or command.strip() == '':
            raise Exception(f'invalid input, command={command}')

        # return if nothing to do
        if self.__cursor is None:
            return f''

        # execute query
        if self.verbose:
            print(f'Executing {command}')
        self.__cursor.execute(command)
        if self.verbose:
            print(f'Executed {command}')

        # fetch one result
        self.__result = self.__cursor.fetchall()
        return self.__result


# +
# function: action()
# -
def action(iargs=None):

    # check input(s)
    if iargs is None:
        raise Exception(f'invalid input(s), iargs={iargs}')
    else:
        if iargs.verbose:
            print(f'iargs={iargs}')

    # get a command (edit default command as you see fit)
    if iargs.command.strip() == '':
        iargs.command = f"SELECT * FROM alert WHERE (rb > 0.85 AND fwhm < 5.0) LIMIT 50;"

    # instantiate class
    try:
        _t = PsqlConnectionTester(iargs.database, iargs.authorization, iargs.server, int(iargs.port), iargs.verbose)
    except Exception as e:
        raise Exception(f'failed to create class, error={e}')
    else:
        print(f'PsqlConnectionTester(database={_t.database}, authorization={_t.authorization}, '
              f'server={_t.server}, port={_t.port}, verbose={_t.verbose}) created OK')

    # do something
    if _t:

        # connect
        _t.connect()

        # select
        if iargs.method.lower() == 'fetchall':
            _all = _t.fetchall(iargs.command)
            if _all:
                print(f'_t.fetchall(\"{iargs.command}\"), returns:')
                pprint.pprint(f'{_all}')

        elif iargs.method.lower() == 'fetchone':
            _one = _t.fetchone(iargs.command)
            if _one:
                print(f'_t.fetchone(\"{iargs.command}\"), returns:')
                pprint.pprint(f'{_one}')

        elif iargs.method.lower() == 'fetchmany':
            _many = _t.fetchmany(iargs.command, int(iargs.nelms))
            if _many:
                print(f'_t.fetchmany(\"{iargs.command}\", {iargs.nelms}), returns:')
                pprint.pprint(f'{_many}')

        elif iargs.method.lower() == 'raw':
            _many = _t.raw(iargs.command)
            if _many:
                print(f'_t.fetchmany(\"{iargs.command}\", {iargs.nelms}), returns:')
                pprint.pprint(f'{_many}')

        # disconnect
        _t.disconnect()


# +
# main()
# -
if __name__ == '__main__':

    # get command line argument(s)
    # noinspection PyTypeChecker
    _parser = argparse.ArgumentParser(description=f'Test PostGresQL Database Connection',
                                      formatter_class=argparse.RawTextHelpFormatter)
    _parser.add_argument(f'-a', f'--authorization', default=f'{SASSY_DB_AUTHORIZATION}',
                         help=f"""database authorization=<str>:<str>, defaults to '%(default)s'""")
    _parser.add_argument(f'-c', f'--command', default='',
                         help=f"""database command=<str>, defaults to '%(default)s'""")
    _parser.add_argument(f'-d', f'--database', default=f'{SASSY_DB_NAME}',
                         help=f"""database name=<str>, defaults to '%(default)s'""")
    _parser.add_argument(f'-m', f'--method', default=f'{FETCH_METHOD[0]}',
                         help=f"""database method=<str>, in {FETCH_METHOD} defaults to %(default)s""")
    _parser.add_argument(f'-n', f'--nelms', default=FETCH_MANY,
                         help=f"""database nelms=<int> (for fetchmany) defaults to %(default)s""")
    _parser.add_argument(f'-p', f'--port', default=int(SASSY_DB_PORT),
                         help=f"""database port=<int>, defaults to %(default)s""")
    _parser.add_argument(f'-s', f'--server', default=f'{SASSY_DB_HOST}',
                         help=f"""database server=<address>,  defaults to '%(default)s'""")
    _parser.add_argument(f'-v', f'--verbose', default=False, action='store_true', 
                         help=f'if present, produce more verbose output')
    args = _parser.parse_args()

    # execute
    if args:
        action(args)
    else:
        raise Exception(f'Insufficient command line arguments specified\nUse: python3 {sys.argv[0]} --help')
