from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import Http404
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import auth
from django.contrib.auth import get_user_model

import requests
import json

oauth_server="http://172.17.0.2:8000"
app_server="http://172.17.0.3:8001"
client_id="8AEMpOR3vJHL9NhcCEqQwM70Gc7VkiWiI9NKTPDe"
client_secret="vkiCSnubjTle5ak77HYiNNljD3vLdf91CzZHW1oIrTvfz5twyVtTAaqlpEbr0zraPrwNog6nqoqsb4Di5eE3VEHhZcI6Q4nTXAxBuZACjPuvuUZKsCJcKZnQkkN3stxi"
User = get_user_model()

# Create your views here.
@require_http_methods(["GET"])
def index(request):
    return render(request, 'index.html')

@require_http_methods(["GET"])
def about(request):
    return render(request, 'about.html')

@require_http_methods(["GET"])
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(oauth_server+"/accounts/logout/")

def _authenticate(request, email):
    try:
        user = User._default_manager.get_by_natural_key(email)
    except :
        pass
    else:
        #if _user_can_authenticate(email):
        #    return user

        return user
    return None

def _user_can_authenticate(email):
    """
    Reject users with is_active=False. Custom user models that don't have
    that attribute are allowed.
    """
    is_active = getattr(email, 'is_active', None)
    return is_active or is_active is None



@require_http_methods(["GET"])
@csrf_exempt
def receive_authcode(request):

    if 'start_oauth' in request.session and request.session['start_oauth'] == True:
        request.session['start_oauth'] = 0
    else:
        raise Http404()
    try:
        if 'code' in request.GET:
            code = request.GET.get('code', '').strip()
            if code=='':
                raise Http404()
            url = oauth_server+'/o/token/'
            s = requests.Session()
            var = {'grant_type':'authorization_code',
                   'code':code,
                   'redirect_uri':app_server+'/o/receive_authcode',
                   'client_id':client_id,
                   'client_secret':client_secret,
            }
            r = s.post(url=url,data=var)
           # print(r.content)
            res=json.loads(r.text)
            if 'access_token' in res:
                access_token=res['access_token']
                url = oauth_server+'/o/get-username/'
                s = requests.Session()
                var = {'token':access_token,}
                headers = {'Authorization': 'Bearer '+access_token}
                r = s.post(url=url,data=var,headers=headers)
                #print(r.content)
                res=json.loads(r.text)
                #print(res)
                nickname=res['nickname']
                email=res['email']
                is_superuser = res['is_superuser']
                user = _authenticate(request, email)
                if user!=None:
                    auth.login(request, user)
                    return redirect('/')
                else:
                    if is_superuser==True:
                        new_user = User.objects.create_superuser(email=email, nickname=nickname,
                                                            password="e6gqxLHvFR74LNBLvJpFDw20IrQH6nef")
                        new_user.save()
                        user = _authenticate(request, email)
                        print(user)
                    else:
                        new_user = User.objects.create_user(email=email,nickname=nickname, password="e6gqxLHvFR74LNBLvJpFDw20IrQH6nef")
                        new_user.save()
                        user = _authenticate(request, email)
                    if user!=None:
                        auth.login(request, user)
                        return redirect('/')
                    else:
                        raise Http404()
    except:
        pass
    raise Http404()

@require_http_methods(["GET"])
def login(request):
    if request.user.is_authenticated:
        return redirect('/')
    auth_url = oauth_server+"/o/authorize/?client_id="+client_id+"&state=preauth&response_type=code"
    request.session['start_oauth'] = True
    #print(request.session.__dict__)
    return HttpResponseRedirect(auth_url)
