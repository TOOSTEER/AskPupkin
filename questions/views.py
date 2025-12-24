from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import Question, Answer, Tag, Profile
from .forms import QuestionForm, AnswerForm, UserRegistrationForm, ProfileForm

def paginate(objects_list, request, per_page=10):
    paginator = Paginator(objects_list, per_page)
    page_number = request.GET.get('page', 1)
    
    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)
    
    return page

def index(request):
    questions = Question.objects.with_details().new()
    page = paginate(questions, request, 20)
    return render(request, 'index.html', {
        'questions': page,
        'sort': 'new'
    })

def hot(request):
    questions = Question.objects.with_details().hot()
    page = paginate(questions, request, 20)
    return render(request, 'hot.html', {
        'questions': page,
        'sort': 'hot'
    })

def tag(request, tag_name):
    tag_obj = get_object_or_404(Tag, name=tag_name)
    questions = Question.objects.with_details().by_tag(tag_name)
    page = paginate(questions, request, 20)
    return render(request, 'tag.html', {
        'questions': page,
        'tag': tag_obj,
        'sort': 'tag'
    })

def question(request, question_id):
    question_obj = get_object_or_404(
        Question.objects.with_details()
        .prefetch_related('answers__author__profile'),
        id=question_id
    )
    
    answers = question_obj.answers.all()
    page = paginate(answers, request, 30)
    
    if request.method == 'POST' and request.user.is_authenticated:
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.author = request.user
            answer.question = question_obj
            answer.save()
            return redirect('question', question_id=question_id)
    else:
        form = AnswerForm()
    
    return render(request, 'question.html', {
        'question': question_obj,
        'answers': page,
        'form': form
    })

@login_required
def ask(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.author = request.user
            question.save()
            form.save_m2m()
            return redirect('question', question_id=question.id)
    else:
        form = QuestionForm()
    
    return render(request, 'ask.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect(request.GET.get('next', 'index'))
    else:
        form = AuthenticationForm()
    
    return render(request, 'login.html', {'form': form})

def signup(request):
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        profile_form = ProfileForm(request.POST, request.FILES)
        
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            
            login(request, user)
            return redirect('index')
    else:
        user_form = UserRegistrationForm()
        profile_form = ProfileForm()
    
    return render(request, 'signup.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST, instance=request.user)
        profile_form = ProfileForm(
            request.POST, 
            request.FILES, 
            instance=request.user.profile
        )
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('profile')
    else:
        user_form = UserRegistrationForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
    
    return render(request, 'profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

def logout_view(request):
    logout(request)
    return redirect('index')