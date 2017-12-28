from django.shortcuts import redirect, reverse, get_object_or_404, render_to_response, render
from django.urls import reverse_lazy
from django.http.response import HttpResponseRedirect
from django.contrib.auth import get_user_model
from django.views.generic import TemplateView, ListView, UpdateView, CreateView, DetailView, DeleteView, View
from django.views.generic.edit import SingleObjectMixin
from django.views.generic.dates import DayArchiveView
from pure_pagination.mixins import PaginationMixin
from django.contrib.auth.mixins import PermissionRequiredMixin, AccessMixin
from django.utils.crypto import get_random_string
from django.db import transaction
from django.utils.timezone import now
from django.db.models.functions import TruncDay
from django.db.models import Sum, Count
from django.db.models import Q, F
from accounts.models import Invitecode
from urllib.parse import urlparse
from datetime import timedelta
from . import models
from django.contrib.sessions.models import Session
from accounts.models import USER_LEVEL
from oauth.settings import LEVEL_STATUS_CHOICES

User = get_user_model()

# Create your views here.


class AdminPermissionMixin(PermissionRequiredMixin):
    error_403_template = 'management/403.html'

    def _response_403_template(self, template_name=None, *args, **kwargs):
        template_name = template_name if template_name else self.error_403_template
        response = render(self.request, template_name, kwargs)
        response.status_code = 403
        return response

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_staff and not request.user.is_auditor:
            return self._response_403_template(errors="你没有后台权限", template_name='403.html')
        if not self.has_permission():
            return self._response_403_template(errors="你需要 %s 权限" % (self.permission_required, ))
        return super(AdminPermissionMixin, self).dispatch(request, *args, **kwargs)


class HideDeleteView(SingleObjectMixin, View):
    jump_url = None

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.show = False
        self.object.save()

        return HttpResponseRedirect(request.META.get('HTTP_REFERER') or self.jump_url)


class IndexView(AdminPermissionMixin, TemplateView):
    """
        referer http://stackoverflow.com/questions/8746014/django-group-by-date-day-month-year
    """

    date_field = "created_time"
    template_name = 'management/index.html'
    permission_required = 'archives.change_post'

    def _get_user_chart(self):
        query = User.objects\
            .values('level') \
            .annotate(cnt=Count('id')) \
            .values('level', 'cnt') \
            .order_by()

        ret = []
        user_level = dict(USER_LEVEL)
        for user in query:
            ret.append({
                'level': user_level.get(user['level']),
                'count': user['cnt']
            })

        return ret


    def get_context_data(self, **kwargs):
        kwargs['user_count'] = User.objects.count()

        kwargs['user_chart'] = self._get_user_chart()

        return super(IndexView, self).get_context_data(**kwargs)


class UserView(AdminPermissionMixin, PaginationMixin, ListView):
    template_name = 'management/user.html'
    queryset = User.objects.all()
    paginate_by = 15
    permission_required = 'accounts.change_member'


class UserDetailView(AdminPermissionMixin, DetailView):
    model = User
    template_name = 'management/user_detail.html'
    permission_required = 'accounts.change_member'


class BanUserView(AdminPermissionMixin, SingleObjectMixin, View):
    permission_required = 'accounts.change_member'

    def get_queryset(self):
        if self.request.user.is_superuser:
            return User.objects.filter(is_superuser=False)
        elif self.request.user.is_staff:
            return User.objects.filter(is_superuser=False, is_staff=False)
        else:
            return User.objects.filter(is_superuser=False, is_staff=False, is_auditor=False)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        pk = self.kwargs.get(self.pk_url_kwarg)
        queryset = self.get_queryset().filter(pk=pk)

        try:
            object = queryset.get()
        except queryset.model.DoesNotExist:
            return redirect(request.META.get('HTTP_REFERER', reverse('management-user-list')))

        object.is_active = not object.is_active
        object.save()

        for s in Session.objects.all():
            data = s.get_decoded()
            if data.get('_auth_user_id', None) == str(object.id):
                s.delete()

        return redirect(request.META.get('HTTP_REFERER', reverse('management-user-list')))

class InviteCodeListView(AdminPermissionMixin, PaginationMixin, ListView):
    template_name = 'management/invitecode_list.html'
    paginate_by = 10
    model = Invitecode
    permission_required = 'accounts.change_invitecode'


class GenerateInvitecodeView(AdminPermissionMixin, View):
    template_name = 'management/invitecode_list.html'
    paginate_by = 10
    model = Invitecode
    permission_required = 'accounts.add_invitecode'

    def post(self, request):
        code = Invitecode(createdby=request.user, code=get_random_string(32, '0123456789abcdef'))
        code.save()
        return redirect('management-invitecode')


class DeleteInviteCodeView(AdminPermissionMixin, DeleteView):
    success_url = reverse_lazy('management-invitecode')
    queryset = Invitecode.objects.filter(used=False)
    permission_required = 'accounts.delete_invitecode'

    get = DeleteView.http_method_not_allowed

class JavascriptView(TemplateView):
    template_name = 'js/management.js'
    raise_exception = True
    content_type = 'text/javascript'