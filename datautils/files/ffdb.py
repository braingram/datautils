#!/usr/bin/env python
"""
Flat file database utilities and structures

example config
    'frames': {
        'regex': '(?P<row>[0-9]{4})_(?P<col>[0-9]{4})\.tif',
        'groups': {
            'row': 'int',
            'col': 'int',
            'camera': 'int',
            'grab': 'int',
            'timestamp': 'int',
        },
        'xeger': '{row:04d}_{col:04d}\.tif',
        'return': {
            'type': 'dict',
        },
    },
    'processed': {
        'return': {
            'type': 'FFDB'
            'args': ()
        },
    }
"""


import datetime
import json
import logging
import os
import re

from ..qfilter.query import qfilter


config_filename = '.ffdb'


return_types = {
    'int': lambda fn, *args, **kwargs: int(fn),
    'str': lambda fn, *args, **kwargs: str(fn),
    'float': lambda fn, *args, **kwargs: float(fn),
    'dict': lambda fn, *args, **kwargs: dict(kwargs, fn=fn),
}


def time_dict(s, f):
    t = datetime.datetime.strptime(s, f)
    return {
        k: getattr(t, k) for k in (
            'year', 'month', 'day', 'hour', 'minute', 'second', 'microsecond')}


group_types = {
    'int': int,
    'str': str,
    'float': float,
    'datetime': datetime.datetime.strptime,
    'time_dict': time_dict,
}


logger = logging.getLogger(__name__)


class FFDBError(Exception):
    pass


class FFDB(object):
    """Access data arranged as flat files in a directory"""
    def __init__(self, directory, config=None):
        if not os.path.isdir(directory):
            raise FFDBError("FFDB: %s not a directory" % directory)
        self.directory = os.path.realpath(os.path.expanduser(directory))
        if config is None:
            config = {}
        cfg_fn = os.path.join(self.directory, config_filename)
        # look for a .ffdb file inside the directory
        if os.path.exists(cfg_fn):
            logger.info("Loading FFDB config from file %s" % cfg_fn)
            with open(cfg_fn, 'r') as f:
                file_config = json.load(f)
            file_config.update(config)
            self.config = file_config
        else:
            self.config = config

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, cfg):
        """
        Reconfigure the database with a new configuration with:
        keys = dataset names
        values = dataset configurations

        TODO document dataset configurations
        """
        # resolve all options
        # first clear the existing config
        self._config = {}
        for k in cfg:
            if k in self._config:
                raise FFDBError("Duplicate key: %s" % k)
            self._config[k] = {}

            # copy over regex and xeger, default to dataset name
            for attr in ('regex', 'xeger'):
                if attr not in cfg[k]:
                    self._config[k][attr] = k
                else:
                    self._config[k][attr] = cfg[k][attr]

            # parse configuration detailing how the data should be returned
            self._config[k]['return'] = {
                'args': (), 'kwargs': {}}
            # by default, return the filename as a string
            if 'return' not in cfg[k]:
                self._config[k]['return']['type'] = return_types['str']
            else:
                if isinstance(cfg[k]['return'], dict):
                    rcfg = cfg[k]['return']
                    if 'type' not in rcfg:
                        raise FFDBError(
                            "Invalid return config, missing type %s" % (
                                cfg[k]['return'], ))
                    if rcfg['type'] not in return_types:
                        raise FFDBError(
                            "Unknown return type %s" % (rcfg['type'], ))
                    self._config[k]['return']['type'] = \
                        return_types[rcfg['type']]
                    self._config[k]['return']['args'] = \
                        rcfg.get('args', ())
                    self._config[k]['return']['kwargs'] = \
                        rcfg.get('kwargs', {})
                else:
                    if cfg[k]['return'] not in return_types:
                        raise FFDBError(
                            "Unknown return type %s" % (cfg['return'], ))
                    self._config[k]['return']['type'] = \
                        return_types[cfg[k]['return']]
            self._config[k]['groups'] = {}
            gcfg = cfg[k].get('groups', {})
            for gk in gcfg:
                if isinstance(gcfg[gk], dict):
                    if 'type' not in gcfg[gk]:
                        raise FFDBError(
                            "Invalid group type %s missing type" % (gk, ))
                    if gcfg[gk]['type'] not in group_types:
                        raise FFDBError(
                            "Unknown group type %s" % (gcfg[gk], ))
                    self._config[k]['groups'][gk] = {
                        'type': group_types[gcfg[gk]['type']],
                        'args': gcfg[gk].get('args', ()),
                        'kwargs': gcfg[gk].get('kwargs', {}),
                    }
                else:
                    if gcfg[gk] not in group_types:
                        raise FFDBError(
                            "Unknown group type %s" % (gcfg[gk], ))
                    self._config[k]['groups'][gk] = group_types[gcfg[gk]]
        # pull out all regexes
        self._regexes = {}
        for k in self._config:
            r = self._config[k]['regex']
            if r in self._regexes:
                raise FFDBError("duplicate regex: %r" % r)
            self._regexes[r] = k
        # update index
        self.update()

    def update(self):
        self.data = {k: [] for k in self._config}
        self.orphans = []
        for fn in os.listdir(self.directory):
            ffn = os.path.join(self.directory, fn)
            for r in self._regexes:
                m = re.match(r, fn)
                if m is not None:
                    name = self._regexes[r]
                    # parse result
                    rcfg = self._config[name]['return']
                    args = rcfg['args']
                    kwargs = rcfg['kwargs'].copy()
                    gd = m.groupdict()
                    groups = self._config[name]['groups']
                    for k in gd:
                        if k in groups:
                            if isinstance(groups[k], dict):
                                kwargs[k] = groups[k]['type'](
                                    gd[k], *groups[k].get('args', ()),
                                    **groups[k].get('kwargs', {}))
                            else:
                                kwargs[k] = groups[k](gd[k])
                        else:
                            kwargs[k] = gd[k]
                    self.data[name].append(rcfg['type'](ffn, *args, **kwargs))
                    break
            # didn't match any
            # if it's a directory, load it as a FFDB
            if os.path.isdir(ffn):
                self.data[fn] = FFDB(ffn)
            else:  # else, list it as an orphan
                self.orphans.append(ffn)

    def query(self, key, query=None):
        """Query the database (using a qfilter type filter)
        """
        if key not in self._config:
            raise FFDBError("Unknown key %s" % key)
        if query is None:
            return self.data[key]
        return qfilter(self.data[key], query)

    def generate_filename(self, key, **kwargs):
        if key not in self._config:
            raise FFDBError("Unknown key %s" % key)
        return os.path.join(
            self.directory, self._config[key]['xeger'].format(**kwargs))

    def __getitem__(self, key):
        return self.data.__getitem__(key)


return_types['FFDB'] = \
    lambda fn, *args, **kwargs: dict(kwargs, db=FFDB(fn, *args))
