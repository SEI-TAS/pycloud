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


from routes import Mapper

if __name__ == "__main__":
    from pycloud import make_app
    from pycloud.config import environment

    # Load the enviroment first
    environment.load_enviroment()

    # Run the server
    run_server(make_app())
