# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render, reverse, redirect
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib.auth import login, authenticate


def index(request):
    if request.user.is_anonymous:
        return render(request, 'static_pages/index.html', {'custom_bootstrap': True})
    return redirect(reverse('main:home'))


def check_user_exist(request):
    user_exist = User.objects.filter(username=request.GET.get("name", "")).exists()
    data = {"exists": user_exist}
    return JsonResponse(data)


def signin(request):
    user = authenticate(username=request.POST['username'], password=request.POST['password'])
    if user:
        login(request, user)
        return redirect(reverse('main:home'))
    return render(request, 'static_pages/index.html', {'error_message': 'wrong username or password',
                                                       'custom_bootstrap': True,
                                                       'login_model_active': True
                                                       })
