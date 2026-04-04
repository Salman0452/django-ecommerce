from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.generic import FormView, TemplateView

from .forms import LoginForm, ProfileForm, RegistrationForm
from .services import register_user, update_profile


class RegisterView(FormView):
    template_name = 'users/register.html'
    form_class = RegistrationForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('products:list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        user = register_user(email, password)
        login(self.request, user)
        return redirect('products:list')


class UserLoginView(FormView):
    template_name = 'users/login.html'
    form_class = LoginForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('products:list')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['next'] = self.request.GET.get('next', '')
        return context

    def form_valid(self, form):
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        user = authenticate(self.request, username=email, password=password)
        if user is not None:
            login(self.request, user)
            next_url = self.request.POST.get('next') or self.request.GET.get('next')
            if next_url and url_has_allowed_host_and_scheme(
                next_url, allowed_hosts={self.request.get_host()}
            ):
                return redirect(next_url)
            return redirect('products:list')
        form.add_error(None, 'Invalid email or password.')
        return self.form_invalid(form)


class UserLogoutView(LoginRequiredMixin, TemplateView):
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        logout(request)
        return redirect('products:list')


class ProfileView(LoginRequiredMixin, FormView):
    template_name = 'users/profile.html'
    form_class = ProfileForm

    def get_initial(self):
        return {
            'first_name': self.request.user.first_name,
            'last_name': self.request.user.last_name,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile_user'] = self.request.user
        return context

    def form_valid(self, form):
        update_profile(
            self.request.user,
            form.cleaned_data['first_name'],
            form.cleaned_data['last_name'],
        )
        return redirect('users:profile')
