#!/usr/bin/python
# -*- encoding: iso-8859-15 -*-
# (C) Copyright 2005 Nuxeo SARL <http://nuxeo.com>
# Author: Tarek Ziadé <tz@nuxeo.com>
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
import unittest
import os
import time, datetime
from zope.testing import doctest
from Testing.ZopeTestCase import installProduct
from Testing.ZopeTestCase import ZopeTestCase

from Products.zasyncdispatcher.zasyncdispatcher import ZAsyncDispatcher,\
                                                       _custom_delta
from Products.zasync.manager import AsynchronousCallManager
from Products.zasyncdispatcher import asyncedCall, canAsync

installProduct('zasync')

class AsynchronousFakePing(AsynchronousCallManager):
    def ping(self):
        """make a ping request to the zasync client to see if it replies
        in the heartbeat method."""
        self._last_ping = datetime.datetime.now()
        self._last_pong = self._last_ping + \
                    datetime.timedelta(seconds=self.rotation_period)

def constructAsynchronousCallManager(dispatcher,
                                     id="asynchronous_call_manager"):
    """Construct an AsynchronousCallManager"""
    acm = AsynchronousFakePing(id)
    container = dispatcher.this()
    container._setObject(id, acm)

class FakeBIM:
    def getBrowserId(self):
        return 'ok'

class ZAsyncDispatcherTestCase(ZopeTestCase):

    def test_asyncedCall(self):
        asyncedCall(self, 'python:1')

    def test_asyncedCall(self):
        self.assertEquals(canAsync(self), False)

    def test_instance(self):
        dispatcher = ZAsyncDispatcher()
        self.assertNotEquals(dispatcher, None)

    def test_collection(self):
        dispatcher = ZAsyncDispatcher()
        self.assertNotEquals(dispatcher, None)
        for i in range(3):
            constructAsynchronousCallManager(dispatcher, 'async_%d' % i)

        self.assertEquals(len(dispatcher.objectIds()), 3)

    def test_putCall(self):
        dispatcher = ZAsyncDispatcher()
        self.assertNotEquals(dispatcher, None)
        for i in range(3):
            constructAsynchronousCallManager(dispatcher, 'async_%d' % i)

        # just checking that a call is made (ValueError is raised because
        # there's no plugins)
        self.assertRaises(ValueError, dispatcher.putCall, 'ok')

    def test_putSessionCall(self):
        from Products.Sessions.BrowserIdManager import BROWSERID_MANAGER_NAME
        dispatcher = ZAsyncDispatcher()
        self.assertNotEquals(dispatcher, None)
        for i in range(3):
            id = 'async_%d' % i
            constructAsynchronousCallManager(dispatcher, id)
            setattr(dispatcher[id], BROWSERID_MANAGER_NAME, FakeBIM())
        # just checking that a call is made (ValueError is raised because
        # there's no plugins)

        self.assertRaises(ValueError, dispatcher.putSessionCall, 'ok')

    def test__custom_delta(self):
        now = datetime.datetime.now()
        time.sleep(1)
        now2 = datetime.datetime.now()
        delta = _custom_delta(now2, now)
        self.assertEquals(delta, 1)

        delta = _custom_delta(now, now2)
        self.assertEquals(delta, 1)

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(ZAsyncDispatcherTestCase),
        doctest.DocTestSuite('Products.zasyncdispatcher.zasyncdispatcher'),
        ))
