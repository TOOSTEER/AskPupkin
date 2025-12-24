from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponseForbidden, JsonResponse
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import json
from .models import Question, Answer, Tag, Profile, QuestionLike, AnswerLike
from .forms import (
    QuestionForm, AnswerForm, UserRegistrationForm, 
    ProfileForm, UserEditForm, CustomAuthenticationForm
)
from .mixins import LoginRequiredRedirectMixin

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
    
    page_num = request.GET.get('page', 1)
    
    if request.method == 'POST' and request.user.is_authenticated:
        form = AnswerForm(request.POST, request.FILES)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.author = request.user
            answer.question = question_obj
            answer.save()
            
            answers_count = question_obj.answers.count()
            per_page = 30
            answer_page = (answers_count - 1) // per_page + 1
            
            redirect_url = reverse('question', args=[question_id])
            if answer_page > 1:
                redirect_url += f'?page={answer_page}'
            redirect_url += f'#answer-{answer.id}'
            
            return redirect(redirect_url)
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = AnswerForm()
    
    return render(request, 'question.html', {
        'question': question_obj,
        'answers': page,
        'form': form,
        'page_num': page_num
    })

@login_required
def ask(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST, request.FILES)
        if form.is_valid():
            question = form.save(author=request.user)
            messages.success(request, 'Вопрос успешно добавлен!')
            return redirect('question', question_id=question.id)
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = QuestionForm()
    
    return render(request, 'ask.html', {'form': form})

@csrf_protect
def login_view(request):
    if request.user.is_authenticated:
        return redirect(request.GET.get('next', 'index'))
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            next_url = request.POST.get('next', 'index')
            if not next_url or next_url == reverse('logout'):
                next_url = 'index'
            
            messages.success(request, f'Добро пожаловать, {user.username}!')
            return redirect(next_url)
        else:
            messages.error(request, 'Неверное имя пользователя или пароль.')
    else:
        form = CustomAuthenticationForm()
    
    next_url = request.GET.get('next', 'index')
    return render(request, 'login.html', {
        'form': form,
        'next': next_url
    })

@csrf_protect
def signup(request):
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        profile_form = ProfileForm(request.POST, request.FILES)
        
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password1'])
            user.save()
            
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('index')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        user_form = UserRegistrationForm()
        profile_form = ProfileForm()
    
    return render(request, 'signup.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

@login_required
def profile_edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=request.user)
        profile_form = ProfileForm(
            request.POST, 
            request.FILES, 
            instance=request.user.profile
        )
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('profile')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
    
    return render(request, 'profile_edit.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

def profile(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    user_questions = Question.objects.filter(author=request.user).order_by('-created_date')[:10]
    user_answers = Answer.objects.filter(author=request.user).order_by('-created_date')[:10]
    
    return render(request, 'profile.html', {
        'user_questions': user_questions,
        'user_answers': user_answers
    })

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'Вы успешно вышли из системы.')
    return redirect(request.GET.get('next', 'index'))

@login_required
@require_POST
@csrf_exempt
def question_like_ajax(request, question_id):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Требуется авторизация', 'redirect': reverse('login')})
    
    try:
        question = Question.objects.get(id=question_id)
    except Question.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Вопрос не найден'})
    
    try:
        data = json.loads(request.body)
        value = int(data.get('value', 0))
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'success': False, 'error': 'Неверный формат данных'})
    
    if value not in [1, -1]:
        return JsonResponse({'success': False, 'error': 'Неверное значение лайка'})
    
    like, created = QuestionLike.objects.get_or_create(
        user=request.user,
        question=question,
        defaults={'value': value}
    )
    
    if not created:
        if like.value == value:
            like.delete()
            question.rating -= value
        else:
            question.rating -= like.value
            like.value = value
            like.save()
            question.rating += value
    else:
        question.rating += value
    
    question.save()
    
    user_like = QuestionLike.objects.filter(user=request.user, question=question).first()
    user_value = user_like.value if user_like else 0
    
    return JsonResponse({
        'success': True,
        'new_rating': question.rating,
        'user_value': user_value
    })

@login_required
@require_POST
@csrf_exempt
def answer_like_ajax(request, answer_id):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Требуется авторизация', 'redirect': reverse('login')})
    
    try:
        answer = Answer.objects.get(id=answer_id)
    except Answer.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Ответ не найден'})
    
    try:
        data = json.loads(request.body)
        value = int(data.get('value', 0))
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'success': False, 'error': 'Неверный формат данных'})
    
    if value not in [1, -1]:
        return JsonResponse({'success': False, 'error': 'Неверное значение лайка'})
    
    like, created = AnswerLike.objects.get_or_create(
        user=request.user,
        answer=answer,
        defaults={'value': value}
    )
    
    if not created:
        if like.value == value:
            like.delete()
            answer.rating -= value
        else:
            answer.rating -= like.value
            like.value = value
            like.save()
            answer.rating += value
    else:
        answer.rating += value
    
    answer.save()
    
    user_like = AnswerLike.objects.filter(user=request.user, answer=answer).first()
    user_value = user_like.value if user_like else 0
    
    return JsonResponse({
        'success': True,
        'new_rating': answer.rating,
        'user_value': user_value
    })

@login_required
@require_POST
def mark_answer_correct(request, answer_id):
    answer = get_object_or_404(Answer, id=answer_id)
    question = answer.question
    
    if question.author != request.user:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Вы не автор этого вопроса'}, status=403)
        return HttpResponseForbidden("Вы не автор этого вопроса")
    
    question.answers.filter(is_correct=True).update(is_correct=False)
    
    answer.is_correct = True
    answer.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'answer_id': answer_id})
    
    return redirect('question', question_id=question.id)

@login_required
@require_POST
@csrf_exempt
def mark_answer_correct_ajax(request, answer_id):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Требуется авторизация', 'redirect': reverse('login')})
    
    try:
        answer = Answer.objects.get(id=answer_id)
    except Answer.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Ответ не найден'})
    
    question = answer.question
    
    if question.author != request.user:
        return JsonResponse({'success': False, 'error': 'Вы не автор этого вопроса'}, status=403)
    
    question.answers.filter(is_correct=True).update(is_correct=False)
    
    answer.is_correct = True
    answer.save()
    
    return JsonResponse({
        'success': True,
        'answer_id': answer_id,
        'question_id': question.id
    })

@login_required
@require_GET
def check_user_like_status(request):
    if not request.user.is_authenticated:
        return JsonResponse({'authenticated': False})
    
    question_id = request.GET.get('question_id')
    answer_id = request.GET.get('answer_id')
    
    result = {'authenticated': True}
    
    if question_id:
        try:
            question = Question.objects.get(id=question_id)
            like = QuestionLike.objects.filter(user=request.user, question=question).first()
            result['question_like'] = like.value if like else 0
        except Question.DoesNotExist:
            result['question_like'] = 0
    
    if answer_id:
        try:
            answer = Answer.objects.get(id=answer_id)
            like = AnswerLike.objects.filter(user=request.user, answer=answer).first()
            result['answer_like'] = like.value if like else 0
        except Answer.DoesNotExist:
            result['answer_like'] = 0
    
    return JsonResponse(result)

def handler404(request, exception):
    return render(request, '404.html', status=404)