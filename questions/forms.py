from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from .models import Question, Answer, Profile, Tag
import os

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Имя пользователя',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Пароль'
        })
    )
    
    error_messages = {
        'invalid_login': "Неверное имя пользователя или пароль.",
        'inactive': "Этот аккаунт неактивен.",
    }

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'example@mail.com'
        })
    )
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Имя пользователя'
        }),
        help_text="Не более 150 символов. Только буквы, цифры и @/./+/-/_"
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Пароль'
        }),
        label='Пароль',
        help_text="Пароль должен содержать не менее 8 символов"
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Подтвердите пароль'
        }),
        label='Подтверждение пароля'
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Пользователь с таким email уже существует")
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("Пользователь с таким именем уже существует")
        return username

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar']
        widgets = {
            'avatar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'id': 'avatar-upload'
            }),
        }
        labels = {
            'avatar': 'Аватар',
        }
    
    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            if avatar.size > 2 * 1024 * 1024:
                raise ValidationError('Размер изображения не должен превышать 2MB')
            ext = os.path.splitext(avatar.name)[1].lower()
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
            if ext not in valid_extensions:
                raise ValidationError('Поддерживаемые форматы: JPG, JPEG, PNG, GIF')
        return avatar

class UserEditForm(forms.ModelForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Имя пользователя'
            }),
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        user_id = self.instance.id
        if User.objects.filter(email=email).exclude(id=user_id).exists():
            raise ValidationError("Пользователь с таким email уже существует")
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        user_id = self.instance.id
        if User.objects.filter(username=username).exclude(id=user_id).exists():
            raise ValidationError("Пользователь с таким именем уже существует")
        return username

class QuestionForm(forms.ModelForm):
    tags_input = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Введите до 3 тегов через запятую',
            'class': 'form-control',
            'id': 'tags-input'
        }),
        label='Теги',
        help_text="Можно указать не более 3 тегов"
    )
    
    class Meta:
        model = Question
        fields = ['title', 'content', 'image']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите заголовок вопроса',
                'maxlength': '255'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Опишите свой вопрос подробно',
                'rows': 10,
                'maxlength': '5000'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'id': 'question-image-upload'
            }),
        }
        labels = {
            'title': 'Заголовок',
            'content': 'Содержание',
            'image': 'Изображение (опционально)',
        }
        help_texts = {
            'content': 'Максимальная длина: 5000 символов',
        }
    
    def clean_tags_input(self):
        tags_str = self.cleaned_data.get('tags_input', '')
        tags = [tag.strip().lower() for tag in tags_str.split(',') if tag.strip()]
        
        if len(tags) > 3:
            raise ValidationError('Можно указать не более 3 тегов')
        
        if len(tags) == 0:
            raise ValidationError('Укажите хотя бы один тег')
        
        for tag in tags:
            if len(tag) > 50:
                raise ValidationError(f'Тег "{tag}" слишком длинный (максимум 50 символов)')
        
        return tags
    
    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            if image.size > 5 * 1024 * 1024:
                raise ValidationError('Размер изображения не должен превышать 5MB')
            ext = os.path.splitext(image.name)[1].lower()
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
            if ext not in valid_extensions:
                raise ValidationError('Поддерживаемые форматы: JPG, JPEG, PNG, GIF')
        return image
    
    def save(self, commit=True, author=None):
        question = super().save(commit=False)
        if author:
            question.author = author
        
        if commit:
            question.save()
        
        tags = self.cleaned_data.get('tags_input', [])
        tag_objects = []
        
        for tag_name in tags:
            tag, created = Tag.objects.get_or_create(name=tag_name[:50])
            tag_objects.append(tag)
        
        question.tags.set(tag_objects)
        
        return question

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['content', 'image']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Введите ваш ответ',
                'rows': 6,
                'maxlength': '3000',
                'id': 'answer-content'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'id': 'answer-image-upload'
            }),
        }
        labels = {
            'content': 'Ответ',
            'image': 'Изображение (опционально)',
        }
        help_texts = {
            'content': 'Максимальная длина: 3000 символов',
        }
    
    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            if image.size > 5 * 1024 * 1024:
                raise ValidationError('Размер изображения не должен превышать 5MB')
            ext = os.path.splitext(image.name)[1].lower()
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
            if ext not in valid_extensions:
                raise ValidationError('Поддерживаемые форматы: JPG, JPEG, PNG, GIF')
        return image