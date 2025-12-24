from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse

class LoginRequiredRedirectMixin(LoginRequiredMixin):
    """Миксин для редиректа неавторизованных пользователей"""
    login_url = '/login/'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            next_url = request.get_full_path()
            login_url = f"{reverse('login')}?next={next_url}"
            return redirect(login_url)
        return super().dispatch(request, *args, **kwargs)

class OwnerRequiredMixin:
    """Миксин для проверки владельца объекта"""
    
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != request.user:
            raise PermissionDenied("У вас нет прав для редактирования этого объекта")
        return super().dispatch(request, *args, **kwargs)