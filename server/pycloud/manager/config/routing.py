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
    
    connect('/instances', controller='instances', action='index')
    connect('/instances/startInstance/{id}', controller='instances', action='startInstance')
    connect('/instances/stopInstance/{id}', controller='instances', action='stopInstance')
    connect('/instances/openvnc/{id}', controller='instances', action='openVNC')
    connect('/instances/lastchange', controller='instances', action='getLastChangestamp')

    connect('/service/add', controller='modify', action='index')
    connect('/service/createSVM', controller='modify', action='createSVM')
    connect('/service/openSVM/{id}', controller='modify', action='openSVM')
    connect('/service/edit/{id}', controller='modify', action='index')    

    return mapper
