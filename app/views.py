from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Count
from .models import Question, Tag, Answer

def paginate(objects_list, request, per_page=20):
    paginator = Paginator(objects_list, per_page)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    return page_obj

def index(request):
    questions = Question.objects.new_questions().select_related('author').prefetch_related('tags').annotate(answers_count=Count('answers'))
    page_obj = paginate(questions, request)
    return render(request, 'index.html', {'page_obj': page_obj, 'title': 'New Questions'})

def hot_questions(request):
    questions = Question.objects.best_questions().select_related('author').prefetch_related('tags').annotate(answers_count=Count('answers'))
    page_obj = paginate(questions, request)
    return render(request, 'hot.html', {'page_obj': page_obj, 'title': 'Popular Questions'})

def questions_by_tag(request, tag_name):
    tag = get_object_or_404(Tag, name=tag_name)
    questions = Question.objects.questions_by_tag(tag_name).select_related('author').prefetch_related('tags').annotate(answers_count=Count('answers'))
    page_obj = paginate(questions, request)
    return render(request, 'tag.html', {
        'page_obj': page_obj,
        'tag': tag,
        'title': f'Questions with tag "{tag_name}"'
    })

def question_detail(request, question_id):
    question = get_object_or_404(
        Question.objects.select_related('author').prefetch_related('tags'), 
        id=question_id
    )
    answers = question.answers.all().select_related('author').order_by('-rating', '-created_date')
    page_obj = paginate(answers, request, per_page=10)
    return render(request, 'question.html', {
        'question': question,
        'page_obj': page_obj
    })

def login(request):
    return render(request, 'login.html')

def signup(request):
    return render(request, 'signup.html')

def ask(request):
    return render(request, 'ask.html')