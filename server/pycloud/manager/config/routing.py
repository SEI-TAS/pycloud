"""Routes configuration

The more specific and detailed routes should be defined first so they
may take precedent over the more generic routes. For more information
refer to the routes manual at http://routes.groovie.org/docs/
"""
from routes import Mapper

def make_map():
    """Create, configure and return the routes Mapper"""
    mapper = Mapper()
    connect = mapper.connect

    # Note that all of these paths are relative to the base path, /manager. 
    connect('/', controller='services', action='index')
    connect('/home', controller='home', action='index')
    
    connect('/services', controller='services', action='listServices')
    connect('/services/removeService/{id}', controller='services', action='removeService')
    
    connect('/servicevms', controller='servicevms', action='index')
    connect('/servicevms/startSVM/{id}', controller='servicevms', action='startSVM')
    connect('/servicevms/stopSVM/{id}', controller='servicevms', action='stopSVM')
    connect('/servicevms/openvnc/{id}', controller='servicevms', action='openvnc')

    connect('/modify', controller='modify', action='index')
    connect('/modify/{id}', controller='modify', action='index')    
    connect('/modify/createSVM', controller='modify', action='createSVM')
    connect('/modify/openSVM/{id}', controller='modify', action='openSVM')

    return mapper
