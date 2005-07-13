# -*- coding: ISO-8859-15 -*-
# Copyright (c) 2005 Nuxeo SARL <http://nuxeo.com>
# Authors: Tarek Ziadé <tz@nuxeo.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#
# $Id$
""" asynchronous load balancer over zasync
"""
from Acquisition import aq_get
from AccessControl.Permissions import view_management_screens

import zasyncdispatcher

# extracted from cmf
_marker = object()
def _getToolByName(obj, name, default=_marker):
    try:
        tool = aq_get(obj, name, default, 1)
    except AttributeError:
        if default is _marker:
            raise
        return default
    else:
        if tool is _marker:
            raise AttributeError, name
        return tool

def asyncedCall(context, call):
    """ send an asynced call within a CMF portal

    returns None,None in case of failure, ie asynced not installed
    """
    dispatcher = _getToolByName(context, 'asynchronous_call_dispatcher', None)
    if dispatcher is not None:
        return dispatcher.putCall('zope_exec', '/', {}, call, {})
    else:
        return None, None

def canAsync(context):
    """ tells if async works """
    dispatcher = _getToolByName(context, 'asynchronous_call_dispatcher', None)
    return dispatcher is not None

def initialize(context):
    """Zope product setup"""
    context.registerClass(
        zasyncdispatcher.ZAsyncDispatcher,
        icon="www/daliclock.gif",
        permission=view_management_screens,
        constructors=(zasyncdispatcher.constructZAsyncDispatcherForm,
                      zasyncdispatcher.constructZAsyncDispatcher)
        )
