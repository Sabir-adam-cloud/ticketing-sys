from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.http import Http404
from django.shortcuts import redirect, render

from .forms import ProfileForm, RegisterForm
from .models import CustomUser


LOGIN_ROLES = {
    'client': {
        'title': 'Connexion client',
        'description': 'Connectez-vous avec votre nom utilisateur et mot de passe client.',
        'username': '',
    },
    'agent': {
        'title': 'Connexion agent',
        'description': 'Connectez-vous avec votre compte agent.',
        'username': 'walid',
    },
    'admin': {
        'title': 'Connexion administrateur',
        'description': 'Connectez-vous avec votre compte administrateur.',
        'username': 'amine',
    },
}


def login_choice(request):
    return render(request, 'users/login_choice.html')


class SupportLoginView(LoginView):
    template_name = 'users/login.html'

    def dispatch(self, request, *args, **kwargs):
        self.login_role = kwargs.get('role')
        if self.login_role not in LOGIN_ROLES:
            raise Http404('Type de connexion introuvable.')
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        username = LOGIN_ROLES[self.login_role]['username']
        if username:
            initial['username'] = username
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['login_role'] = self.login_role
        context['login_data'] = LOGIN_ROLES[self.login_role]
        return context

    def form_valid(self, form):
        user = form.get_user()
        if self.login_role == 'client' and user.role != CustomUser.Role.CLIENT:
            form.add_error(None, 'Utilisez la connexion agent ou administrateur.')
            return self.form_invalid(form)
        if self.login_role == 'agent' and user.role != CustomUser.Role.AGENT:
            form.add_error(None, 'Ce compte n est pas un compte agent.')
            return self.form_invalid(form)
        if self.login_role == 'admin' and not user.is_support_admin:
            form.add_error(None, 'Ce compte n est pas un compte administrateur.')
            return self.form_invalid(form)
        return super().form_valid(form)

    def get_success_url(self):
        user = self.request.user
        if user.is_support_admin:
            return '/tickets/admin-dashboard/'
        return super().get_success_url()


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Votre compte a ete cree.')
            return redirect('tickets:dashboard')
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})


@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil mis a jour.')
            return redirect('users:profile')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'users/profile.html', {'form': form})
