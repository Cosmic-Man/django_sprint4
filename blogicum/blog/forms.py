from django import forms
from .models import Post, Comment
from django.contrib.auth.models import User


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ["author"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "text": forms.Textarea(attrs={"class": "form-control",
                                          "rows": 10}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "pub_date": forms.DateTimeInput(
                attrs={"class": "form-control",
                       "type": "datetime-local"}
            ),
            "is_published": forms.CheckboxInput(
                attrs={"class": "form-check-input"}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["text"]
        widgets = {
            "text": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Напишите ваш комментарий...",
                }
            ),
        }


class ProfileForm(forms.ModelForm):
    """Форма для редактирования профиля пользователя"""

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email"]
        widgets = {
            "username": forms.TextInput(
                attrs={"class": "form-control",
                       "placeholder": "Введите логин"}
            ),
            "first_name": forms.TextInput(
                attrs={"class": "form-control",
                       "placeholder": "Введите имя"}
            ),
            "last_name": forms.TextInput(
                attrs={"class": "form-control",
                       "placeholder": "Введите фамилию"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control",
                       "placeholder": "example@mail.com"}
            ),
        }
        labels = {
            "username": "Логин",
            "first_name": "Имя",
            "last_name": "Фамилия",
            "email": "Электронная почта",
        }
        help_texts = {
            "username": "Обязательное поле. "
            "Только буквы, цифры и символы @/./+/-/_.",
        }
