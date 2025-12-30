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
            'placeholder': 'Username',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )
    
    error_messages = {
        'invalid_login': "Invalid username or password.",
        'inactive': "This account is inactive.",
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
            'placeholder': 'Username'
        }),
        help_text="Maximum 150 characters. Letters, digits and @/./+/-/_ only."
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        }),
        label='Password',
        help_text="Password must be at least 8 characters"
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        }),
        label='Password Confirmation'
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("User with this email already exists")
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("User with this username already exists")
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
            'avatar': 'Avatar',
        }
    
    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            if avatar.size > 2 * 1024 * 1024:
                raise ValidationError('Image size should not exceed 2MB')
            ext = os.path.splitext(avatar.name)[1].lower()
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
            if ext not in valid_extensions:
                raise ValidationError('Supported formats: JPG, JPEG, PNG, GIF')
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
                'placeholder': 'Username'
            }),
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        user_id = self.instance.id
        if User.objects.filter(email=email).exclude(id=user_id).exists():
            raise ValidationError("User with this email already exists")
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        user_id = self.instance.id
        if User.objects.filter(username=username).exclude(id=user_id).exists():
            raise ValidationError("User with this username already exists")
        return username

class QuestionForm(forms.ModelForm):
    tags_input = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter up to 3 tags separated by commas',
            'class': 'form-control',
            'id': 'tags-input'
        }),
        label='Tags',
        help_text="You can specify up to 3 tags"
    )
    
    class Meta:
        model = Question
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter question title',
                'maxlength': '255'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe your question in detail',
                'rows': 10,
                'maxlength': '5000'
            }),
        }
        labels = {
            'title': 'Title',
            'content': 'Content',
        }
        help_texts = {
            'content': 'Maximum length: 5000 characters',
        }
    
    def clean_tags_input(self):
        tags_str = self.cleaned_data.get('tags_input', '')
        tags = [tag.strip().lower() for tag in tags_str.split(',') if tag.strip()]
        
        if len(tags) > 3:
            raise ValidationError('You can specify up to 3 tags')
        
        if len(tags) == 0:
            raise ValidationError('Specify at least one tag')
        
        for tag in tags:
            if len(tag) > 50:
                raise ValidationError(f'Tag "{tag}" is too long (maximum 50 characters)')
        
        return tags
    
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
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your answer',
                'rows': 6,
                'maxlength': '3000',
                'id': 'answer-content'
            }),
        }
        labels = {
            'content': 'Answer',
        }
        help_texts = {
            'content': 'Maximum length: 3000 characters',
        }