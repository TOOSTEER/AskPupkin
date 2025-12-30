from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile, Question, Answer, Tag, QuestionLike, AnswerLike

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profiles'
    verbose_name = 'Profile'
    fields = ('avatar',)

class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active')

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'rating', 'created_date', 'get_answers_count']
    list_filter = ['created_date', 'tags']
    search_fields = ['title', 'content']
    filter_horizontal = ['tags']
    readonly_fields = ['rating']
    
    def get_answers_count(self, obj):
        return obj.answers.count()
    get_answers_count.short_description = 'Answers Count'

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['content_preview', 'author', 'question', 'rating', 'created_date', 'is_correct']
    list_filter = ['created_date', 'is_correct']
    search_fields = ['content']
    
    def content_preview(self, obj):
        return obj.content[:100] + "..." if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Answer'

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_questions_count']
    search_fields = ['name']
    
    def get_questions_count(self, obj):
        return obj.questions.count()
    get_questions_count.short_description = 'Questions Count'

@admin.register(QuestionLike)
class QuestionLikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'question', 'value']
    list_filter = ['value']

@admin.register(AnswerLike)
class AnswerLikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'answer', 'value']
    list_filter = ['value']