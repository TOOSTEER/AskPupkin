from django.contrib import admin
from django.db.models import Count
from .models import Profile, Question, Answer, Tag, QuestionLike, AnswerLike

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'avatar']
    search_fields = ['user__username']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'rating', 'created_date', 'answers_count']
    list_filter = ['created_date', 'tags']
    search_fields = ['title', 'content']
    filter_horizontal = ['tags']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author').prefetch_related('tags').annotate(answers_count=Count('answers'))
    
    def answers_count(self, obj):
        return obj.answers_count
    answers_count.short_description = 'Answers'

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['question', 'author', 'rating', 'is_correct', 'created_date']
    list_filter = ['is_correct', 'created_date']
    search_fields = ['content']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author', 'question')

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'questions_count']
    search_fields = ['name']
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(questions_count=Count('question'))
    
    def questions_count(self, obj):
        return obj.questions_count
    questions_count.short_description = 'Questions'

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