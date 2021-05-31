from django.views.generic.edit import FormView, DeleteView, CreateView
from django.views.generic.base import TemplateView, RedirectView
from django.views.generic import ListView
from .register_form import RegisterForm
from django.shortcuts import get_object_or_404
from django.contrib.auth import login, authenticate, views as auth_views
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.db.models import F
from rest_framework.decorators import action
from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework import permissions
from .serializers import UserSerializer, GroupSerializer, LinkSerializer
from .models import Link
from rest_framework import mixins
from util.tasks import mailGroup
from rest_framework.response import Response

class UserSetApi(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


class GroupSetApi(viewsets.ModelViewSet):
    queryset = Group.objects.all().order_by('-id')
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAdminUser]
    
    @action(methods=['POST'], detail=True,
    url_name='mail_send', url_path='mail-send')
    def mailSend(self, request, pk=None):
        if 'subject' not in request.data:
            return Response({"Missing subject"}, status=status.HTTP_400_BAD_REQUEST)
        if 'text' not in request.data:
            return Response({"Missing text"}, status=status.HTTP_400_BAD_REQUEST)
        if Group.objects.filter(id=pk).count() == 0:
            return Response({"Invalid group"}, status=status.HTTP_404_NOT_FOUND)
        mail_text = request.data['text']
        subject = request.data['subject']
        mailGroup.delay(pk,subject, mail_text)
        return Response({'In executing %s:%s' % (pk, mail_text)})

class LinkSetApi(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.DestroyModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    queryset = Link.objects.all().order_by('-created_at')
    serializer_class = LinkSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)


class LinkCreateView(LoginRequiredMixin, CreateView):
    login_url = reverse_lazy('login')
    template_name = 'zip_link/create_link.html'
    model = Link
    fields = ['origin_link']
    title = 'create_link'

    def form_valid(self, form):
        form.instance.user = self.request.user
        link = form.save()
        link.save()
        context = self.get_context_data(form=form)
        context['new_link'] = link.link_from
        return self.render_to_response(context)


class LinksView(LoginRequiredMixin, ListView):
    login_url = reverse_lazy('login')
    success_url = reverse_lazy('link-list')
    template_name = 'zip_link/links.html'
    title = 'links'
    paginate_by = 10

    def get_queryset(self):
        queryset = Link.objects.order_by('-created_at')
        return queryset


class DeleteRedirectView(LoginRequiredMixin, DeleteView):
    login_url = reverse_lazy('login')
    model = Link
    success_url = reverse_lazy('links')

    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(self.success_url)

    def delete(self, request, *args, **kwargs):
        self.object = get_object_or_404(Link, link_from=kwargs['link'])
        if request.user != self.object.user:
            raise PermissionDenied
        self.object.delete()
        return HttpResponseRedirect(self.success_url)


class RedirectToView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        link = get_object_or_404(Link, link_from=kwargs['link'])
        link.counter = F("counter") + 1
        link.save(update_fields=["counter"])
        return link.link_to


class HomeView(TemplateView):
    template_name = 'zip_link/home.html'
    title = 'home'


class AccountView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('login')
    template_name = 'zip_link/cabinet.html'
    title = 'cabinet'


class RegisterView(FormView):
    template_name = 'zip_link/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('links')
    title = 'register'

    def form_valid(self, form):
        user = form.save()
        user.refresh_from_db()
        user.profile.birth_date = form.cleaned_data.get('birth_date')
        user.profile.gender = form.cleaned_data.get('gender')
        user.save()
        login(self.request, user)
        return super().form_valid(form)


class LoginView(auth_views.LoginView):
    template_name = 'zip_link/login.html'
    success_url = reverse_lazy('account')
    title = 'login'

    def get_success_url(self):
        url = self.get_redirect_url()
        return url or self.success_url


class LogoutView(auth_views.LogoutView):
    next_page = '/'
