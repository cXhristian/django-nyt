from __future__ import absolute_import
from __future__ import unicode_literals
# -*- coding: utf-8 -*-
import json
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

import django_nyt


def disable_notify(func):
    """Disable notifications. Example:

    @disable_notify
    def your_function():
        notify("no one will be notified", ...)
    """
    def wrap(request, *args, **kwargs):
        django_nyt._disable_notifications = True
        response = func(request, *args, **kwargs)
        django_nyt._disable_notifications = False
        return response
    return wrap


def login_required_ajax(func):
    """Similar to login_required. But if the request is an ajax request, then
    it returns an error in json with a 403 status code."""

    def wrap(request, *args, **kwargs):
        if request.is_ajax():
            if not request.user or not request.user.is_authenticated():
                return json_view(lambda *a,
                                 **kw: {'error': 'not logged in'})(request,
                                                                   status=403)
            return func(request, *args, **kwargs)
        else:
            return login_required(func)(request, *args, **kwargs)
    return wrap


def json_view(func):
    def wrap(request, *args, **kwargs):
        obj = func(request, *args, **kwargs)
        data = json.dumps(obj, ensure_ascii=False)
        status = kwargs.get('status', 200)
        response = HttpResponse(content_type='application/json', status=status)
        response.write(data)
        return response
    return wrap
