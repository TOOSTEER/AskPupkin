from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Profile, Question, Answer, Tag, QuestionLike, AnswerLike

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Профиль'

class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 1
    fields = ['content', 'author', 'rating', 'is_correct']

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'created_date', 'rating']
    list_filter = ['created_date', 'tags']
    search_fields = ['title', 'content']
    inlines = [AnswerInline]

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['content', 'author', 'question', 'created_date', 'rating', 'is_correct']
    list_filter = ['created_date', 'is_correct']
    search_fields = ['content']

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'avatar']
    search_fields = ['user__username']

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)