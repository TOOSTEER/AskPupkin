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
from .models import Question, Answer, Tag, Profile, QuestionLike, AnswerLike
from .forms import (
    QuestionForm, AnswerForm, UserRegistrationForm, 
    ProfileForm, UserEditForm, CustomAuthenticationForm
)
from .mixins import LoginRequiredRedirectMixin
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect

def paginate(objects_list, request, per_page=10):
    """Функция пагинации"""
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
    """Главная страница - новые вопросы"""
    questions = Question.objects.with_details().new()
    page = paginate(questions, request, 20)
    return render(request, 'index.html', {
        'questions': page,
        'sort': 'new'
    })

def hot(request):
    """Популярные вопросы"""
    questions = Question.objects.with_details().hot()
    page = paginate(questions, request, 20)
    return render(request, 'hot.html', {
        'questions': page,
        'sort': 'hot'
    })

def tag(request, tag_name):
    """Вопросы по тегу"""
    tag_obj = get_object_or_404(Tag, name=tag_name)
    questions = Question.objects.with_details().by_tag(tag_name)
    page = paginate(questions, request, 20)
    return render(request, 'tag.html', {
        'questions': page,
        'tag': tag_obj,
        'sort': 'tag'
    })

def question(request, question_id):
    """Страница вопроса с ответами"""
    question_obj = get_object_or_404(
        Question.objects.with_details()
        .prefetch_related('answers__author__profile'),
        id=question_id
    )
    
    answers = question_obj.answers.all()
    page = paginate(answers, request, 30)
    
    # Проверяем, был ли передан номер страницы для ответов
    page_num = request.GET.get('page', 1)
    
    if request.method == 'POST' and request.user.is_authenticated:
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.author = request.user
            answer.question = question_obj
            answer.save()
            
            # Получаем страницу, на которой будет отображаться ответ
            answers_count = question_obj.answers.count()
            per_page = 30
            answer_page = (answers_count - 1) // per_page + 1
            
            # Редирект на страницу с ответом
            redirect_url = reverse('question', args=[question_id])
            if answer_page > 1:
                redirect_url += f'?page={answer_page}'
            redirect_url += f'#answer-{answer.id}'
            
            return redirect(redirect_url)
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
    """Форма добавления вопроса"""
    if request.method == 'POST':
        form = QuestionForm(request.POST)
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
    """Форма входа с обработкой параметра next"""
    if request.user.is_authenticated:
        return redirect(request.GET.get('next', 'index'))
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # Получаем URL для редиректа
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
    """Форма регистрации"""
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        profile_form = ProfileForm(request.POST, request.FILES)
        
        if user_form.is_valid() and profile_form.is_valid():
            # Сохраняем пользователя
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password1'])
            user.save()
            
            # Сохраняем профиль
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            
            # Авторизуем пользователя
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
    """Форма редактирования профиля"""
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
    """Страница профиля пользователя"""
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
    """Выход из системы"""
    logout(request)
    messages.info(request, 'Вы успешно вышли из системы.')
    return redirect(request.GET.get('next', 'index'))

@login_required
@require_POST
def question_like(request, question_id):
    """Обработка лайков вопросов"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'redirect': reverse('login')})
    
    question = get_object_or_404(Question, id=question_id)
    value = int(request.POST.get('value', 0))
    
    if value not in [1, -1]:
        return JsonResponse({'success': False, 'error': 'Неверное значение'})
    
    # Проверяем, есть ли уже оценка от пользователя
    like, created = QuestionLike.objects.get_or_create(
        user=request.user,
        question=question,
        defaults={'value': value}
    )
    
    if not created:
        if like.value == value:
            # Удаляем оценку, если пользователь кликнул на ту же кнопку
            like.delete()
            question.rating -= value
        else:
            # Меняем оценку
            question.rating -= like.value
            like.value = value
            like.save()
            question.rating += value
    else:
        question.rating += value
    
    question.save()
    
    return JsonResponse({
        'success': True,
        'new_rating': question.rating
    })

@login_required
@require_POST
def answer_like(request, answer_id):
    """Обработка лайков ответов"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'redirect': reverse('login')})
    
    answer = get_object_or_404(Answer, id=answer_id)
    value = int(request.POST.get('value', 0))
    
    if value not in [1, -1]:
        return JsonResponse({'success': False, 'error': 'Неверное значение'})
    
    # Проверяем, есть ли уже оценка от пользователя
    like, created = AnswerLike.objects.get_or_create(
        user=request.user,
        answer=answer,
        defaults={'value': value}
    )
    
    if not created:
        if like.value == value:
            # Удаляем оценку, если пользователь кликнул на ту же кнопку
            like.delete()
            answer.rating -= value
        else:
            # Меняем оценку
            answer.rating -= like.value
            like.value = value
            like.save()
            answer.rating += value
    else:
        answer.rating += value
    
    answer.save()
    
    return JsonResponse({
        'success': True,
        'new_rating': answer.rating
    })

@login_required
@require_POST
def mark_answer_correct(request, answer_id):
    """Отметка ответа как правильного"""
    answer = get_object_or_404(Answer, id=answer_id)
    question = answer.question
    
    # Проверяем, что пользователь - автор вопроса
    if question.author != request.user:
        return HttpResponseForbidden("Вы не автор этого вопроса")
    
    # Снимаем отметку с других ответов
    question.answers.filter(is_correct=True).update(is_correct=False)
    
    # Отмечаем выбранный ответ как правильный
    answer.is_correct = True
    answer.save()
    
    return redirect('question', question_id=question.id)

def handler404(request, exception):
    """Обработчик 404 ошибки"""
    return render(request, '404.html', status=404)