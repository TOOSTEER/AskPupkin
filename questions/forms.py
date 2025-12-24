from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Question, Answer, Profile, Tag

class QuestionForm(forms.ModelForm):
    tags_input = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Введите теги через запятую',
            'class': 'form-control'
        }),
        label='Теги'
    )
    
    class Meta:
        model = Question
        fields = ['title', 'content']
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
        }
        labels = {
            'title': 'Заголовок',
            'content': 'Содержание',
        }
    
    def clean_tags_input(self):
        tags_str = self.cleaned_data.get('tags_input', '')
        tags = [tag.strip().lower() for tag in tags_str.split(',') if tag.strip()]
        
        if len(tags) > 3:
            raise forms.ValidationError('Можно указать не более 3 тегов')
        
        return tags
    
    def save(self, commit=True):
        question = super().save(commit=commit)
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
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Введите ваш ответ',
                'rows': 6,
                'maxlength': '3000'
            }),
        }
        labels = {
            'content': 'Ответ',
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
            'placeholder': 'Введите имя пользователя'
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Пароль'
        }),
        label='Пароль'
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

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar']
        widgets = {
            'avatar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }
        labels = {
            'avatar': 'Аватар',
        }