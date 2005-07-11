# -*- coding: ISO-8859-15 -*-
# Copyright (c) 2005 Nuxeo SARL <http://nuxeo.com>
# Authors: Tarek Ziad� <tz@nuxeo.com>
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
from AccessControl.Permissions import view_management_screens
import zasyncdispatcher

def initialize(context):
    """Zope product setup"""
    context.registerClass(
        zasyncdispatcher.ZAsyncDispatcher,
        icon="www/daliclock.gif",
        permission=view_management_screens,
        constructors=(zasyncdispatcher.constructZAsyncDispatcherForm,
                      zasyncdispatcher.constructZAsyncDispatcher)
        )
