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

    # Note that all of this are relative to the base path, /manager. 
    connect('root', '/', controller='services', action='index')
    connect('home', '/home', controller='home', action='index')
    
    connect('services', '/services', controller='services', action='listServices')
    connect('services', '/services/removeService/{id}', controller='services', action='removeService')
    
    connect('servicevms', '/servicevms', controller='servicevms', action='index')
    connect('servicevms_startSVM', '/servicevms/startSVM/{id}', controller='servicevms', action='startSVM')
    connect('servicevms_stopSVM', '/servicevms/stopSVM/{id}', controller='servicevms', action='stopSVM')
    connect('servicevms_vnc', '/servicevms/openvnc/{id}', controller='servicevms', action='openvnc')
    connect('/{controller}/{action}/{id}')

    connect('modify', '/modify', controller='modify', action='index')
    connect('modifysvm', '/modify/openSVM/{id}', controller='modify', action='openSVM')
    connect('createsvm', '/modify/createSVM', controller='modify', action='createSVM')

    #Example
    # connect('/', coontroller='cloudlet', action='home')

    return mapper
