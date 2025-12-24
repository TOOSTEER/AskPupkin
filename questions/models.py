from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
import datetime

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    avatar = models.ImageField(upload_to='avatars/%Y/%m/%d/', null=True, blank=True, verbose_name="Аватар")
    
    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"
    
    def __str__(self):
        return f"Профиль {self.user.username}"
    
    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return '/static/img/default-avatar.png'

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Название")
    
    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('tag', args=[self.name])

class QuestionManager(models.Manager):
    def new(self):
        return self.order_by('-created_date')
    
    def hot(self):
        return self.order_by('-rating', '-created_date')
    
    def by_tag(self, tag_name):
        return self.filter(tags__name=tag_name).order_by('-rating', '-created_date')
    
    def with_details(self):
        return self.select_related('author__profile').prefetch_related('tags')

class Question(models.Model):
    title = models.CharField(max_length=255, verbose_name="Заголовок")
    content = models.TextField(max_length=5000, verbose_name="Содержание")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions', verbose_name="Автор")
    tags = models.ManyToManyField(Tag, related_name='questions', verbose_name="Теги")
    created_date = models.DateTimeField(default=timezone.now, verbose_name="Дата создания")
    rating = models.IntegerField(default=0, verbose_name="Рейтинг")
    
    objects = QuestionManager()
    
    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"
        ordering = ['-created_date']
    
    def __str__(self):
        return self.title[:50]
    
    def get_absolute_url(self):
        return reverse('question', args=[self.id])
    
    def time_since_created(self):
        now = timezone.now()
        diff = now - self.created_date
        
        if diff.days > 365:
            years = diff.days // 365
            return f'{years} год назад' if years == 1 else f'{years} года назад'
        elif diff.days > 30:
            months = diff.days // 30
            return f'{months} месяц назад' if months == 1 else f'{months} месяца назад'
        elif diff.days > 0:
            return f'{diff.days} дней назад' if diff.days > 1 else 'вчера'
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f'{hours} часов назад' if hours > 1 else 'час назад'
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f'{minutes} минут назад' if minutes > 1 else 'минуту назад'
        else:
            return 'только что'
    
    def get_answers_count(self):
        return self.answers.count()

class Answer(models.Model):
    content = models.TextField(max_length=3000, verbose_name="Содержание")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answers', verbose_name="Автор")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers', verbose_name="Вопрос")
    created_date = models.DateTimeField(default=timezone.now, verbose_name="Дата создания")
    rating = models.IntegerField(default=0, verbose_name="Рейтинг")
    is_correct = models.BooleanField(default=False, verbose_name="Правильный ответ")
    
    class Meta:
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"
        ordering = ['-is_correct', '-rating', 'created_date']
    
    def __str__(self):
        return f"Ответ от {self.author.username} на вопрос #{self.question.id}"
    
    def time_since_created(self):
        now = timezone.now()
        diff = now - self.created_date
        
        if diff.days > 0:
            return f'{diff.days} дней назад' if diff.days > 1 else 'вчера'
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f'{hours} часов назад' if hours > 1 else 'час назад'
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f'{minutes} минут назад' if minutes > 1 else 'минуту назад'
        else:
            return 'только что'

class QuestionLike(models.Model):
    LIKE = 1
    DISLIKE = -1
    
    CHOICES = [
        (LIKE, 'Нравится'),
        (DISLIKE, 'Не нравится'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='likes', verbose_name="Вопрос")
    value = models.SmallIntegerField(choices=CHOICES, verbose_name="Оценка")
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата оценки")
    
    class Meta:
        verbose_name = "Оценка вопроса"
        verbose_name_plural = "Оценки вопросов"
        unique_together = ['user', 'question']
    
    def __str__(self):
        return f"{self.user.username} оценил вопрос #{self.question.id}"

class AnswerLike(models.Model):
    LIKE = 1
    DISLIKE = -1
    
    CHOICES = [
        (LIKE, 'Нравится'),
        (DISLIKE, 'Не нравится'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='likes', verbose_name="Ответ")
    value = models.SmallIntegerField(choices=CHOICES, verbose_name="Оценка")
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата оценки")
    
    class Meta:
        verbose_name = "Оценка ответа"
        verbose_name_plural = "Оценки ответов"
        unique_together = ['user', 'answer']
    
    def __str__(self):
        return f"{self.user.username} оценил ответ #{self.answer.id}"