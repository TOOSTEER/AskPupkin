from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    
    def __str__(self):
        return self.user.username

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name

class QuestionManager(models.Manager):
    def new_questions(self):
        return self.get_queryset().order_by('-created_date')
    
    def best_questions(self):
        return self.get_queryset().order_by('-rating')
    
    def questions_by_tag(self, tag_name):
        return self.get_queryset().filter(tags__name=tag_name).order_by('-created_date')

class Question(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag)
    created_date = models.DateTimeField(default=timezone.now)
    rating = models.IntegerField(default=0)
    
    objects = QuestionManager()
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('question', kwargs={'question_id': self.id})
    
    def update_rating(self):
        self.rating = QuestionLike.objects.filter(question=self).aggregate(
            models.Sum('value')
        )['value__sum'] or 0
        self.save()

class Answer(models.Model):
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    created_date = models.DateTimeField(default=timezone.now)
    is_correct = models.BooleanField(default=False)
    rating = models.IntegerField(default=0)
    
    def __str__(self):
        return f"Answer to {self.question.title}"
    
    def update_rating(self):
        self.rating = AnswerLike.objects.filter(answer=self).aggregate(
            models.Sum('value')
        )['value__sum'] or 0
        self.save()

class QuestionLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    value = models.SmallIntegerField(choices=[(1, 'Like'), (-1, 'Dislike')])
    created_date = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ['user', 'question']
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.question.update_rating()

class AnswerLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    value = models.SmallIntegerField(choices=[(1, 'Like'), (-1, 'Dislike')])
    created_date = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ['user', 'answer']
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.answer.update_rating()