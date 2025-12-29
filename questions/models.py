from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    
    def __str__(self):
        return f"Profile: {self.user.username}"

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
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

class Question(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions')
    tags = models.ManyToManyField(Tag, related_name='questions')
    created_date = models.DateTimeField(default=timezone.now)
    rating = models.IntegerField(default=0)
    
    objects = QuestionManager()
    
    def __str__(self):
        return self.title[:50]
    
    def get_absolute_url(self):
        return reverse('question', args=[self.id])
    
    def get_answers_count(self):
        return self.answers.count()

class Answer(models.Model):
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    created_date = models.DateTimeField(default=timezone.now)
    rating = models.IntegerField(default=0)
    is_correct = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Answer to: {self.question.title[:30]}"

class QuestionLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='likes')
    value = models.SmallIntegerField(choices=[(1, 'Like'), (-1, 'Dislike')])
    
    class Meta:
        unique_together = ['user', 'question']

class AnswerLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='likes')
    value = models.SmallIntegerField(choices=[(1, 'Like'), (-1, 'Dislike')])
    
    class Meta:
        unique_together = ['user', 'answer']