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
""" ZAsyncDispatcher

works a bit like a load balancer:

    o centralizes async calls
    o handles a list of zasync call managers
    o dispatch calls to the less busy one

this is helpfull when several zasync process can be run
"""
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens as Manage
from OFS.Folder import Folder

from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.zasync.manager import AsynchronousCallManager
from Products.zasync.permissions import MakeAsynchronousSessionCalls,\
                                        MakeAsynchronousApplicationCalls

class ZAsyncDispatcher(Folder):
    id = 'asynchronous_call_dispatcher'
    title = meta_type = 'Asynchronous Call Dispatcher'
    icon = "misc_/zasync/tool.gif"

    security = ClassSecurityInfo()

    security.declarePrivate('_retrieveBestAsyncManager')
    def _retrieveBestAsyncManager(self):
        best_choice = None
        best_choice_load = 999
        for id, item in self.objectItems():
            load = item.lenNewCalls() + item.lenAcceptedCalls()
            if load < best_choice_load:
                best_choice_load = load
                best_choice = item
        return best_choice

    #
    # load-balanced APIs
    #
    security.declareProtected(MakeAsynchronousApplicationCalls, 'putCall')
    def putCall(self, _plugin, *args, **kwargs):
        ob = self._retrieveBestAsyncManager()
        result = ob._putCall(None, _plugin, *args, **kwargs)
        return ob.id, result

    security.declareProtected(MakeAsynchronousSessionCalls, 'putSessionCall')
    def putSessionCall(self, _plugin, *args, **kwargs):
        ob = self._retrieveBestAsyncManager()
        result = ob._putCall((ob._getBrowserId(),), _plugin, *args, **kwargs)
        return ob.id, result

constructZAsyncDispatcherForm = PageTemplateFile(
    'www/constructZAsyncDispatcherForm.zpt', globals(),
    __name__='manage_addDispatcherForm')

def constructZAsyncDispatcher(context, id="asynchronous_call_dispatcher",
                              RESPONSE=None):
    """Construct a ZAsyncDispatcher"""
    dispatcher = ZAsyncDispatcher(id)
    container = context.this()
    container._setObject(id, dispatcher)

    if RESPONSE is not None:
        RESPONSE.redirect(container.absolute_url() + '/manage_main')
