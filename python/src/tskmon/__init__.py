#!/usr/bin/python
# -*- coding: utf-8 -*-
##
# __init__: Client for the tskmon API.
##
# © 2013 Christopher E. Granade (cgranade@gmail.com)
#
# This file is a part of the tskmon project.
# Licensed under the AGPL version 3.
##
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
##

## FEATURES ###################################################################

from __future__ import division

## IMPORTS ####################################################################

import urlparse
import httplib
import json
import webbrowser
import time

import os

## CONSTANTS ##################################################################

SERVER = (
    "tskmon.herokuapp.com"
    if os.getenv('TSKMON_SERVER') is None
    else
    os.getenv('TSKMON_SERVER')
)

## FUNCTIONS ##################################################################

def api_path(endpoint):
    return "/api/{endpoint}.json".format(
        endpoint=endpoint
    )

def server_connection():
    return httplib.HTTPSConnection(SERVER)

## CLASSES ####################################################################

class Task(object):
    def __init__(self, client, json_body):
        self._client = client
        self._body = json.loads(json_body)
        
    @property
    def task_id(self):
        return self._body['id']

    @property
    def current_progress(self):
        return float(self._body['current_progress'])

    @property
    def max_progress(self):
        return float(self._body['max_progress'])

    @property
    def description(self):
        return self._body['description']

    @property
    def status(self):
        return self._body['status']

    @property
    def creator(self):
        return self._body['creator']

    @property
    def status(self):
        return self._body['status']

    def delete(self):
        self._client._delete(self.task_id)

    def update(self, progress=None, max_progress=None, description=None, status=None):
        kwargs = {}
        if progress is not None:
            kwargs['current_progress'] = progress
        if max_progress is not None:
            kwargs['max_progress'] = max_progress
        if description is not None:
            kwargs['description'] = description
        if status is not None:
            kwargs['status'] = status
        self._body = json.loads(self._client._update(self.task_id, **kwargs))


class TskmonClient(object):

    def __init__(self, token, app_name="tskmon-client/Python"):
        
        self._token = token
        self._creator = app_name

    def __headers(self):
        return {
            'Authorization': 'Token {}'.format(self._token),
            'Content-Type': 'application/json'
        }

        
    def new_task(self, description, status="", progress=0, max_progress=None):
        # TODO: make this return a Task object that can be updated,
        #       instead of just returning the JSON.
        params = {
            'description': description,
            'status': status,
            'current_progress': progress,
            'creator': self._creator
        }

        if max_progress is not None:
            params['max_progress'] = max_progress

        body = json.dumps(params)
        print body

        conn = server_connection()
        conn.request('POST', api_path('tasks/'),
            body=body,
            headers=self.__headers()
        )
        response = conn.getresponse()
        if response.status != 201:
            raise IOError("{} {}".format(response.status, response.reason))

        return Task(self, response.read())
        
    def _delete(self, task_id):
        conn = server_connection()
        conn.request('DELETE', api_path('tasks/{}'.format(task_id)),
            headers=self.__headers()
        )
        response = conn.getresponse()
        if response.status // 100 != 2:
            raise IOError("{} {}".format(response.status, response.reason))
        
    def _update(self, task_id, **params):
        body = json.dumps(params)
        
        conn = server_connection()
        conn.request('PUT', api_path('tasks/{}'.format(task_id)),
            body=body,
            headers=self.__headers()
        )
        response = conn.getresponse()
        if response.status != 200:
            raise IOError("{} {}".format(response.status, response.reason))
        
        return response.read()
