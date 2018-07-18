# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import reverse


class Project(models.Model):
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=25)
    description = models.TextField(max_length=500)
    total_rating = models.IntegerField(default=0, null=True)

    title = models.CharField(max_length=20)
    rating = models.IntegerField(default=0, null=True, blank=True)
    address = models.CharField(max_length=25)
    pub_date = models.DateField(auto_now_add=True)

    longitude = models.FloatField()
    latitude = models.FloatField()
    rated_users = models.IntegerField(default=0, null=True)
    image = models.ImageField(upload_to="project_images", null=False, blank=False)

    def __str__(self):
        return self.user.username + '-' + self.name + '-' + str(self.pk)

    def get_absolute_url(self):
        return reverse("main:view-project", kwargs={'pk': self.pk})


class Suggestion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username + ' --> ' + self.project.name


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    account_type = models.CharField(blank=False, max_length=10)

    suggestions = models.ManyToManyField(Suggestion, blank=True)
    rated_projects = models.ManyToManyField(Project, blank=True)
    image = models.ImageField(default='/user_images/default_image.png', upload_to='user_images', blank=True, null=True)

    def __str__(self):
        return self.user.username


class Friends(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    array = models.ManyToManyField(Profile, blank=True)

    def __str__(self):
        return self.user.username


class PendingFriendRequests(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    array = models.ManyToManyField(Profile, blank=True)

    def __str__(self):
        return self.user.username


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    text = models.CharField(max_length=300)
    pub_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.project.user.username + '-' + self.project.name
