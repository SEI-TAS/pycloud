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
    
    # Note that all of this are relative to the base path, /api.
    
    # ServiceVM Controller actions. 
    connect('list', '/servicevm/listServices', controller='services', action='list')    
    connect('find', '/servicevm/find', controller='services', action='find')
    connect('startvm', '/servicevm/start', controller='servicevm', action='start')
    connect('stopvm', '/servicevm/stop', controller='servicevm', action='stop')
    
    # App Push Controller actions.
    connect('getAppList', '/app/getList', controller='apppush', action='getList')
    connect('getApp', '/app/getApp', controller='apppush', action='getApp')

    connect('metadata', '/cloudlet_info', controller='cloudlet', action='metadata')

    #Example
    # connect('/', coontroller='cloudlet', action='home')

    return mapper