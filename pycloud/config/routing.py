"""Routes configuration

The more specific and detailed routes should be defined first so they
may take precedent over the more generic routes. For more information
refer to the routes manual at http://routes.groovie.org/docs/
"""
from routes import Mapper

def make_map():
    """Create, configure and return the routes Mapper"""
    map = Mapper()
    connect = map.connect


    connect('/', controller='api', action='home')

    #Example
    # connect('/', coontroller='cloudlet', action='home')

    return map
