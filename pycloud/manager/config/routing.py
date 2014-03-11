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

    connect('services', '/services', controller='services', action='index')
    
    # ServiceVM Controller actions.
    connect('find', '/api/servicevm/find', controller='servicevm', action='find')
    connect('startvm', '/api/servicevm/start', controller='servicevm', action='start')
    connect('stopvm', '/api/servicevm/stop', controller='servicevm', action='stop')
    
    # App Push Controller actions.
    connect('getAppList', '/api/app/getList', controller='apppush', action='getList')
    connect('getApp', '/api/app/getApp', controller='apppush', action='getApp')

    #Example
    # connect('/', coontroller='cloudlet', action='home')

    return mapper