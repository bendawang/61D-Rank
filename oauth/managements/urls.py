from django.conf.urls import url, include
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    url(r'^js/$', view=views.JavascriptView.as_view(content_type='text/javascript'), name='js'),
    url(r'^$', views.IndexView.as_view(), name='management-index'),
    url(r'^user/$', views.UserView.as_view(), name='management-user-list'),
    url(r'^user/(?P<pk>\d+)/$', views.UserDetailView.as_view(), name='management-user-detail'),
    url(r'^user/(?P<pk>\d+)/ban/$', views.BanUserView.as_view(), name='management-user-ban'),

    url(r'^invitecode/$', views.InviteCodeListView.as_view(), name='management-invitecode'),
    url(r'^invitecode/generate/$', views.GenerateInvitecodeView.as_view(), name='management-generate-invitecode'),
    url(r'^invitecode/delete/(?P<pk>\d+)/$', views.DeleteInviteCodeView.as_view(), name='management-delete-invitecode'),
]