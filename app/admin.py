from django.contrib import admin
from .models import Profile, Question, Answer, Tag, QuestionLike, AnswerLike

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'avatar']
    search_fields = ['user__username']

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'rating', 'created_date']
    list_filter = ['created_date', 'tags']
    search_fields = ['title', 'content']
    filter_horizontal = ['tags']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author')

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['question', 'author', 'rating', 'is_correct', 'created_date']
    list_filter = ['is_correct', 'created_date']
    search_fields = ['content']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('question', 'author')

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(QuestionLike)
class QuestionLikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'question', 'value', 'created_date']
    list_filter = ['value', 'created_date']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'question')

@admin.register(AnswerLike)
class AnswerLikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'answer', 'value', 'created_date']
    list_filter = ['value', 'created_date']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'answer')