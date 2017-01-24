__author__ = 'niyoufa'

import pdb
import logging
import os
from tornado.options import parse_command_line, options, define

def parse_config_file(path):
    """Rewrite tornado default parse_config_file.

    Parses and loads the Python config file at the given path.

    This version allow customize new options which are not defined before
    from a configuration file.
    """
    config = {}
    try:#py3
        with open(path,'r',encoding='utf-8') as f:
            code = compile(f.read(), path, 'exec')
            exec(code, config, config)
    except:#py2
        execfile(path, config, config)

    for name in config:
        if name in options:
            options[name].set(config[name])
        else:
            define(name, config[name])

def parse_options():
    _root = os.path.join(os.path.dirname(os.path.dirname(__file__)),"")
    _settings = os.path.join(_root, "settings.py")

    try:
        parse_config_file(_settings)
        logging.info("Using settings.py as default settings.")
        print("Using settings.py as default settings.")
    except Exception as e:
        import traceback
        print (traceback.format_exc())
        logging.error("No any default settings, are you sure? Exception: %s" % e)

    parse_command_line()
