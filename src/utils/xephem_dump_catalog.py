#!/usr/bin/env python3


# +
# import(s)
# -
import argparse
import copy
import os
import sys


# +
# constant(s)
# -
XEPHEM_FIELD_2A = {
    'A': f'Cluster of galaxies',
    'B': f'Star, binary (deprecated)',
    'C': f'Cluster, globular',
    'D': f'Star, visual double',
    'F': f'Nebula, diffuse',
    'G': f'Galaxy, spiral',
    'H': f'Galaxy, spherical',
    'J': f'Radio',
    'K': f'Nebula, dark',
    'L': f'Pulsar',
    'M': f'Star, multiple',
    'N': f'Nebula, bright',
    'O': f'Cluster, open',
    'P': f'Nebula, planetary',
    'Q': f'Quasar',
    'R': f'Supernova remnant',
    'S': f'Star',
    'T': f'Stellar object',
    'U': f'Cluster, with nebulosity',
    'Y': f'Supernova',
    'V': f'Star, variable'
}

XEPHEM_FIELD_2B = ['T', 'B', 'D', 'S', 'V']


# +
# class: XephemCatalogParser()
# -
class XephemCatalogParser(object):

    # +
    # method: __init__()
    # -
    def __init__(self, catalog=''):
        """ initialize the class """

        # get input(s)
        self.catalog = catalog

        # (private) variable(s)
        self.__catalog_exists = self.catalog_exists()
        self.__catalog_rows = self.rows_in_catalog()
        self.__catalog_data = None
        self.__catalog_fields = None
        self.__catalog_objects = {}

        # (protected) variables
        self._ret = None

        # constant(s)
        self.XEPHEM_FIELD_2_METHODS = {
            'f': self._parse_fixed,
            'e': self._parse_elliptic,
            'h': self._parse_hyperbolic,
            'p': self._parse_parabolic,
            'E': self._parse_geocentric,
            'P': self._parse_planet,
            'B': self._parse_binary
        }

    # +
    # decorator(s)
    # -
    @property
    def catalog(self):
        return self.__catalog

    @catalog.setter
    def catalog(self, catalog):
        self.__catalog = catalog if (isinstance(catalog, str) and catalog.strip() != f'') else f''

    # +
    # (hidden) method: _parse_fixed()
    # -
    def _parse_fixed(self, _in_name='', _in_type=None, _in_fields=None):
        _ptr = self.__catalog_objects[f'{_in_name}']
        if len(_in_type) >= 1:
            _ptr['type'] = _in_type[0]
            _ptr['type_description'] = XEPHEM_FIELD_2A.get(_in_type[0], '')
        if len(_in_type) >= 2:
            _ptr['type_subtype'] = copy.deepcopy(_in_type[1:])
        _ptr[f'RA'] = _in_fields[0] if len(_in_fields) >= 1 else ''
        _ptr[f'Dec'] = _in_fields[1] if len(_in_fields) >= 2 else ''
        _ptr[f'magnitude'] = _in_fields[2] if len(_in_fields) >= 3 else ''
        _ptr[f'epoch'] = _in_fields[3] if len(_in_fields) >= 4 else '2000'
        _ptr[f'RA'] = _in_fields[0] if len(_in_fields) >= 1 else ''
        _ptr[f'RA'] = _in_fields[0] if len(_in_fields) >= 1 else ''

    # +
    # (hidden) method: _parse_elliptical()
    # -
    def _parse_elliptic(self, _in_name='', _in_type=None, _in_fields=None):
        """ parses fields for heliocentric elliptical orbits """
        if not isinstance(_in_name, str) or _in_name.strip() == '':
            raise Exception(f'Invalid input _in_name={_in_name}')
        if _in_type is None or not isinstance(_in_type, list) or _in_type == []:
            raise Exception(f'Invalid input _in_type={_in_type}')
        self.__ret = None
        return self.__ret

    # +
    # (hidden) method: _parse_hyperbolic()
    # -
    def _parse_hyperbolic(self, _in_name='', _in_type=None, _in_fields=None):
        """ parses fields for heliocentric hyperbolic orbits """
        if not isinstance(_in_name, str) or _in_name.strip() == '':
            raise Exception(f'Invalid input _in_name={_in_name}')
        if _in_type is None or not isinstance(_in_type, list) or _in_type == []:
            raise Exception(f'Invalid input _in_type={_in_type}')
        self.__ret = None
        return self.__ret

    # +
    # (hidden) method: _parse_parabolic()
    # -
    def _parse_parabolic(self, _in_name='', _in_type=None, _in_fields=None):
        """ parses fields for heliocentric parabolic orbits """
        if not isinstance(_in_name, str) or _in_name.strip() == '':
            raise Exception(f'Invalid input _in_name={_in_name}')
        if _in_type is None or not isinstance(_in_type, list) or _in_type == []:
            raise Exception(f'Invalid input _in_type={_in_type}')
        self.__ret = None
        return self.__ret

    # +
    # (hidden) method: _parse_geocentric()
    # -
    def _parse_geocentric(self, _in_name='', _in_type=None, _in_fields=None):
        """ parses fields for geocentric elliptical orbits """
        if not isinstance(_in_name, str) or _in_name.strip() == '':
            raise Exception(f'Invalid input _in_name={_in_name}')
        if _in_type is None or not isinstance(_in_type, list) or _in_type == []:
            raise Exception(f'Invalid input _in_type={_in_type}')
        self.__ret = None
        return self.__ret

    # +
    # (hidden) method: _parse_planet()
    # -
    def _parse_planet(self, _in_name='', _in_type=None, _in_fields=None):
        """ parses fields for planet or natural satellite orbits """
        if not isinstance(_in_name, str) or _in_name.strip() == '':
            raise Exception(f'Invalid input _in_name={_in_name}')
        if _in_type is None or not isinstance(_in_type, list) or _in_type == []:
            raise Exception(f'Invalid input _in_type={_in_type}')
        self.__ret = None
        return self.__ret

    # +
    # (hidden) method: _parse_binary()
    # -
    def _parse_binary(self, _in_name='', _in_type=None, _in_fields=None):
        """ parses fields for (true) binary pair orbits """
        if not isinstance(_in_name, str) or _in_name.strip() == '':
            raise Exception(f'Invalid input _in_name={_in_name}')
        if _in_type is None or not isinstance(_in_type, list) or _in_type == []:
            raise Exception(f'Invalid input _in_type={_in_type}')
        self.__ret = None
        return self.__ret

    # +
    # method: catalog_exists()
    # -
    def catalog_exists(self):
        """ true if catalog file exists else false """
        return os.path.isfile(os.path.abspath(os.path.expanduser(self.__catalog)))

    # +
    # method: rows_in_catalog()
    # -
    def rows_in_catalog(self):
        """ returns number of non-comment, non-blank rows in catalog """
        _rows = 0
        if self.__catalog_exists:
            with open(self.__catalog, 'r') as fd:
                _rows = sum(1 for _l in fd if (_l.strip() != '' and _l.strip()[0].isalnum()))
        return _rows

    # +
    # method: dump_catalog()
    # -
    def dump_catalog(self):
        """ returns string representation of data """
        if self.__catalog_objects is None:
            _res = f''
        elif isinstance(self.__catalog_objects, tuple) and not ():
            _res = f''.join(f'{_v}\n' for _v in self.__catalog_objects)[:-1]
        elif isinstance(self.__catalog_objects, list) and not []:
            _res = f''.join(f'{_v}\n' for _v in self.__catalog_objects)[:-1]
        elif isinstance(self.__catalog_objects, set) and not {}:
            _res = f''.join(f'{_v}\n' for _v in self.__catalog_objects)[:-1]
        elif isinstance(self.__catalog_objects, dict) and not {}:
            _res = f''.join(f'{_k}={_v}\n' for _k, _v in self.__catalog_objects.items())[:-1]
        else:
            _tmp = self.__catalog_objects
            _res = f'{_tmp}'
        return _res

    # +
    # method: read_catalog()
    # -
    def read_catalog(self):
        """ returns (internal) set containing catalog data """
        if self.__catalog_exists and self.__catalog_rows > 0:
            with open(self.__catalog, 'r') as _fd:
                self.__catalog_data = set(
                    _l for _l in _fd if (_l.strip() != '' and _l.strip()[0].isalnum()))

    # +
    # method: parse_catalog()
    # -
    def parse_catalog(self):
        """ returns (internal) set containing catalog data """
        if self.__catalog_exists and self.__catalog_rows > 0:
            for _line in self.__catalog_data:

                # split line into (up to) 14 fields
                _fields = _line.strip('\n').split(',')
                if len(_fields) == 0:
                    raise Exception('No fields in catalog')

                # initialize dictionary for this element
                _names = [_n.strip()[:20] for _n in _fields[0].split('|')]
                if len(_names) == 0:
                    raise Exception('No names in catalog')
                if _names[0] not in self.__catalog_objects:
                    self.__catalog_objects[f'{_names[0]}'] = {
                        f'field_1': f'{_names}',
                        f'field_2': _fields[1].strip() if len(_fields) >= 2 else '',
                        f'field_3': _fields[2].strip() if len(_fields) >= 3 else '',
                        f'field_4': _fields[3].strip() if len(_fields) >= 4 else '',
                        f'field_5': _fields[4].strip() if len(_fields) >= 5 else '',
                        f'field_6': _fields[5].strip() if len(_fields) >= 6 else '',
                        f'field_7': _fields[6].strip() if len(_fields) >= 7 else '',
                        f'field_8': _fields[7].strip() if len(_fields) >= 8 else '',
                        f'field_9': _fields[8].strip() if len(_fields) >= 9 else '',
                        f'field_10': _fields[9].strip() if len(_fields) >= 10 else '',
                        f'field_11': _fields[10].strip() if len(_fields) >= 11 else '',
                        f'field_12': _fields[11].strip() if len(_fields) >= 12 else '',
                        f'field_13': _fields[12].strip() if len(_fields) >= 13 else '',
                        f'field_14': _fields[13].strip() if len(_fields) >= 14 else ''
                    }

                # field 2 is type (and must exist)
                _types = [_t.strip() for _t in _fields[1].split('|')]
                if len(_types) == 0:
                    raise Exception('No types in catalog')
                _func = self.XEPHEM_FIELD_2_METHODS.get(_types[0], None)
                if _func is not None:
                    # noinspection PyArgumentList
                    return _func(_in_name=_names[0], _in_type=_types[1:], _in_fields=_fields[2:])


# +
# function: xephem_dump_catalog()
# -
def xephem_dump_catalog(_catalog=''):

    # check input(s)
    if not os.path.isfile(os.path.abspath(os.path.expanduser(args.catalog))):
        raise Exception(f'ERROR: invalid input, _catalog={_catalog}')

    # noinspection PyBroadException
    try:
        xcp = XephemCatalogParser(_catalog)
    except Exception as e:
        raise Exception(f'Failed to instantiate XephemCatalogParser() class, error={e}')

    # read the catalog
    xcp.read_catalog()

    # parse the catalog
    xcp.parse_catalog()
    print(f'{_catalog} has:\n {xcp.dump_catalog()}')

    # output result(s)
    print(f'{_catalog} has {xcp.rows_in_catalog()} entries')


# +
# main()
# -
if __name__ == '__main__':

    # get command line argument(s)
    # noinspection PyTypeChecker
    _parser = argparse.ArgumentParser(description='Dump Catalog',
                                      formatter_class=argparse.RawTextHelpFormatter)
    _parser.add_argument('-c', '--catalog', default='', help="""Input EDB catalog""")
    args = _parser.parse_args()

    # execute
    if os.path.isfile(os.path.abspath(os.path.expanduser(args.catalog))):
        xephem_dump_catalog(os.path.abspath(os.path.expanduser(args.catalog)))
    else:
        print(f'<<ERROR>> Insufficient command line arguments specified\nUse: python3 {sys.argv[0]} --help')
