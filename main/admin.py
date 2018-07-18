# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import *

admin.site.register(Profile)
admin.site.register(Friends)
admin.site.register(PendingFriendRequests)

admin.site.register(Project)
admin.site.register(Comment)
admin.site.register(Suggestion)