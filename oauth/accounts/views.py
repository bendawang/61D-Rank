# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import Http404
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib import auth
from django.views.decorators.http import require_http_methods

app_server="http://172.17.0.3:8001"


@require_http_methods(["GET","POST"])
@csrf_exempt
def login(request):
    if ('next' in request.GET) or ('next' in request.POST):
        if request.user.is_authenticated:
            if 'next' in request.GET:
                return redirect(request.GET['next'])
            else:
                return redirect(request.POST['next'])
        if request.method != 'POST':
            return render(request, 'login.html', {'next': request.GET.get('next', '/')})#accounts/profile
        else:
            username = request.POST.get('username', '').strip()
            password = request.POST.get('password', '').strip()
            user = auth.authenticate(username=username, password=password)
            if user is not None and user.is_active:
                # Correct password, and the user is marked "active"
                auth.login(request, user)
                # Redirect to a success page.
                return redirect(request.POST['next'])
            else:
                # Show an error page
                return render(request, 'login.html', {'msg': 'Invalid username or password', 'next': request.POST['next']})
    raise Http404()

@require_http_methods(["GET"])
def logout(request):
    auth.logout(request)
    referer_url = request.META.get('HTTP_REFERER', '/')
    if referer_url.startswith(app_server):
        return HttpResponseRedirect(app_server)
    raise Http404()
