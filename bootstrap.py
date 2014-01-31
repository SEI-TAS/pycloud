__author__ = 'jdroot'

import cherrypy

def run_server(app):

    cherrypy.tree.graft(app, "/")

    # Set the configuration of the web server
    cherrypy.config.update({
        'log.screen': True,
        'engine.autoreload_on': True,
        'server.socket_port': 5000,
        'server.socket_host': '0.0.0.0',
        'tools.staticdir.on': False,
        'tools.staticdir.root': 'static',
        'tools.staticdir.dir': '.'
    })

    # Start the CherryPy WSGI web server
    cherrypy.engine.start()
    cherrypy.engine.block()

def load_conf(conf='config.conf'):
    from ConfigParser import ConfigParser
    config = ConfigParser()
    config.read(conf)
    ret = {}
    for section in config._sections.keys():
        for key in config._sections[section].keys():
            if not key.startswith("__"): # ignore __nane__
                value = config._sections[section][key]
                key = "pycloud.%s.%s" % (section, key)
                ret[key] = value
    return ret

if __name__ == "__main__":
    from pycloud import make_app
    from pycloud.config import environment

    # Load the enviroment first
    environment.load_enviroment(app_conf=load_conf())

    # Run the server
    run_server(make_app())
