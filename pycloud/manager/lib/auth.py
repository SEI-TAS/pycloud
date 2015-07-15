# KVM-based Discoverable Cloudlet (KD-Cloudlet)
# Copyright (c) 2015 Carnegie Mellon University.
# All Rights Reserved.
#
# THIS SOFTWARE IS PROVIDED "AS IS," WITH NO WARRANTIES WHATSOEVER. CARNEGIE MELLON UNIVERSITY EXPRESSLY DISCLAIMS TO THE FULLEST EXTENT PERMITTEDBY LAW ALL EXPRESS, IMPLIED, AND STATUTORY WARRANTIES, INCLUDING, WITHOUT LIMITATION, THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT OF PROPRIETARY RIGHTS.
#
# Released under a modified BSD license, please see license.txt for full terms.
# DM-0002138
#
# KD-Cloudlet includes and/or makes use of the following Third-Party Software subject to their own licenses:
# MiniMongo
# Copyright (c) 2010-2014, Steve Lacy
# All rights reserved. Released under BSD license.
# https://github.com/MiniMongo/minimongo/blob/master/LICENSE
#
# Bootstrap
# Copyright (c) 2011-2015 Twitter, Inc.
# Released under the MIT License
# https://github.com/twbs/bootstrap/blob/master/LICENSE
#
# jQuery JavaScript Library v1.11.0
# http://jquery.com/
# Includes Sizzle.js
# http://sizzlejs.com/
# Copyright 2005, 2014 jQuery Foundation, Inc. and other contributors
# Released under the MIT license
# http://jquery.org/license
__author__ = 'Sebastian'

from pylons import request, response, session, tmpl_context as c
from pycloud.pycloud.pylons.lib import helpers as h

#####################################################################################################################
# Checks if we have been authenticated. If not, redirects to login page.
#####################################################################################################################
def ensure_authenticated():
    user = session.get('user')
    if not user:
        return h.redirect_to(controller='auth', action='signin_form')

#####################################################################################################################
# Authenticates a user. If it doesn't work, returns to login page.
#####################################################################################################################
def authenticate():
    # TODO: change this to check user from DB.
    if len(request.params) > 1 and request.params['password'] == request.params['username']:
        session['user'] = request.params['username']
        session.save()
        return h.redirect_to(controller='home', action='index')
    else:
        h.flash('Invalid credentials.')
        return h.redirect_to(controller='auth', action='signin_form')

#####################################################################################################################
# Clears out the logged in user.
#####################################################################################################################
def signout():
    session.clear()
    session.save()
