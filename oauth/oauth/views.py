# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import JsonResponse
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib import auth
from django.contrib.auth.models import User
from oauth2_provider.models import AccessToken
from oauth2_provider.decorators import protected_resource
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView

@csrf_exempt
@protected_resource()
@require_http_methods(["POST"])
def get_username(request):
    #print(AccessToken.objects.get(token=request.POST['token']).user.nickname)
    #print(AccessToken.objects.get(token=request.POST['token']).user.is_superuser)
    #print(AccessToken.objects.get(token=request.POST['token']).user.email)
    #print(JsonResponse({ 'username':AccessToken.objects.get(token=request.POST['token']).user.__str__() }))
    if 'token' in request.POST:
        try:
            data={
                    'nickname':AccessToken.objects.get(token=request.POST['token']).user.nickname,
                    'email':AccessToken.objects.get(token=request.POST['token']).user.email,
                    'is_superuser':AccessToken.objects.get(token=request.POST['token']).user.is_superuser
                }
            return JsonResponse(data)
        except:
            pass
    raise Http404()

class IndexView(TemplateView):
    template_name = 'index.html'