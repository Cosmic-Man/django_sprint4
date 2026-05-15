from django.views.generic import CreateView, DetailView
from django.contrib.auth import get_user_model, login
from django.urls import reverse_lazy
from .forms import RegistrationForm
from blog.models import Post

User = get_user_model()


class RegistrationView(CreateView):
    """Представление для регистрации нового пользователя"""

    model = User
    form_class = RegistrationForm
    template_name = "registration/registration_form.html"
    success_url = reverse_lazy("blog:index")

    def form_valid(self, form):
        """Автоматический вход после регистрации"""
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


class ProfileView(DetailView):
    """Представление для просмотра профиля пользователя"""

    model = User
    template_name = "blog/profile.html"
    context_object_name = "profile_user"
    slug_field = "username"
    slug_url_kwarg = "username"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["posts"] = Post.objects.filter(
            author=self.object).order_by("-pub_date")
        return context
