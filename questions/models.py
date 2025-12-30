from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from django.template.defaultfilters import timesince

class Profile(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        verbose_name="User"
    )
    avatar = models.ImageField(
        upload_to='avatars/', 
        null=True, 
        blank=True,
        verbose_name="Avatar"
    )
    
    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"
    
    def __str__(self):
        return f"Profile: {self.user.username}"

class Tag(models.Model):
    name = models.CharField(
        max_length=50, 
        unique=True,
        verbose_name="Tag Name"
    )
    
    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('tag', args=[self.name])

class QuestionManager(models.Manager):
    def with_details(self):
        return self.get_queryset().prefetch_related('tags', 'author__profile')
    
    def new(self):
        return self.with_details().order_by('-created_date')
    
    def hot(self):
        return self.with_details().order_by('-rating', '-created_date')
    
    def by_tag(self, tag_name):
        return self.with_details().filter(tags__name=tag_name).order_by('-rating', '-created_date')

class Question(models.Model):
    title = models.CharField(
        max_length=255,
        verbose_name="Question Title"
    )
    content = models.TextField(verbose_name="Question Content")
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='questions',
        verbose_name="Author"
    )
    tags = models.ManyToManyField(
        Tag, 
        related_name='questions',
        verbose_name="Tags"
    )
    created_date = models.DateTimeField(
        default=timezone.now,
        verbose_name="Created Date"
    )
    rating = models.IntegerField(
        default=0,
        verbose_name="Rating"
    )
    
    objects = QuestionManager()
    
    class Meta:
        verbose_name = "Question"
        verbose_name_plural = "Questions"
        ordering = ['-created_date']
    
    def __str__(self):
        return self.title[:50]
    
    def get_absolute_url(self):
        return reverse('question', args=[self.id])
    
    def get_answers_count(self):
        return self.answers.count()
    
    @property
    def time_since_created(self):
        return timesince(self.created_date)

class Answer(models.Model):
    content = models.TextField(verbose_name="Answer Content")
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='answers',
        verbose_name="Author"
    )
    question = models.ForeignKey(
        Question, 
        on_delete=models.CASCADE, 
        related_name='answers',
        verbose_name="Question"
    )
    created_date = models.DateTimeField(
        default=timezone.now,
        verbose_name="Created Date"
    )
    rating = models.IntegerField(
        default=0,
        verbose_name="Rating"
    )
    is_correct = models.BooleanField(
        default=False,
        verbose_name="Correct Answer"
    )
    
    class Meta:
        verbose_name = "Answer"
        verbose_name_plural = "Answers"
        ordering = ['-created_date']
    
    def __str__(self):
        return f"Answer to: {self.question.title[:30]}"
    
    @property
    def time_since_created(self):
        return timesince(self.created_date)

class QuestionLike(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        verbose_name="User"
    )
    question = models.ForeignKey(
        Question, 
        on_delete=models.CASCADE, 
        related_name='likes',
        verbose_name="Question"
    )
    value = models.SmallIntegerField(
        choices=[(1, 'Like'), (-1, 'Dislike')],
        verbose_name="Value"
    )
    
    class Meta:
        unique_together = ['user', 'question']
        verbose_name = "Question Like"
        verbose_name_plural = "Question Likes"

class AnswerLike(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        verbose_name="User"
    )
    answer = models.ForeignKey(
        Answer, 
        on_delete=models.CASCADE, 
        related_name='likes',
        verbose_name="Answer"
    )
    value = models.SmallIntegerField(
        choices=[(1, 'Like'), (-1, 'Dislike')],
        verbose_name="Value"
    )
    
    class Meta:
        unique_together = ['user', 'answer']
        verbose_name = "Answer Like"
        verbose_name_plural = "Answer Likes"