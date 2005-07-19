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
import datetime, time

from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens as Manage
from OFS.Folder import Folder

from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.zasync.manager import AsynchronousCallManager
from Products.zasync.permissions import MakeAsynchronousSessionCalls,\
                                        MakeAsynchronousApplicationCalls

def _custom_delta(time1, time2):
        time1 = time1.hour * 3600 + time1.minute * 60 + time1.second
        time2 = time2.hour * 3600 + time2.minute * 60 + time2.second
        return abs(time1-time2)

class ZAsyncDispatcher(Folder):
    id = 'asynchronous_call_dispatcher'
    title = meta_type = 'Asynchronous Call Dispatcher'
    icon = "misc_/zasync/tool.gif"
    max_idle_time = 60

    security = ClassSecurityInfo()

    security.declarePrivate('_get_alive_managers')
    def _get_alive_managers(self):
        """ filters out 'dead' zasync clients """
        right_now = datetime.datetime.now()
        managers = [item for id, item in self.objectItems()]
        alive_managers = []
        for manager in managers:
            need_ping = False
            last_ping = manager.getLastPing()
            if last_ping is None:
                # has never been pinged
                # zope rebooted ?
                # make a ping call and wait a bit
                manager.ping()
                time.sleep(0.5)
                last_ping = manager .getLastPing()
            last_pong = manager.getLastPong()
            if last_pong is None:
                need_ping = True
            else:
                delta = _custom_delta(right_now, last_ping)
                if delta > self.max_idle_time:
                    need_ping = True
            if need_ping:
                # make a ping call, for next calls
                manager.ping()
            else:
                alive_managers.append(manager)

        return alive_managers

    security.declarePrivate('_getZasyncManagers')
    def _getZasyncManagers(self):
        return self._get_alive_managers()

    security.declarePrivate('_retrieveBestAsyncManager')
    def _retrieveBestAsyncManager(self):
        best_choice = None
        best_choice_load = 999
        for manager in self._getZasyncManagers():
            load = manager.lenNewCalls() + manager.lenAcceptedCalls()
            if load < best_choice_load:
                best_choice_load = load
                best_choice = manager
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
