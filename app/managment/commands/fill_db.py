from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from app.models import Profile, Question, Answer, Tag
import random

class Command(BaseCommand):
    help = 'Fill database with sample data'
    
    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int, help='Multiplication ratio')
    
    def handle(self, *args, **options):
        ratio = options['ratio']
        
        self.stdout.write(f'Starting database fill with ratio {ratio}...')
        
        # Create users
        for i in range(ratio):
            user = User.objects.create_user(
                username=f'user{i}',
                password='password123'
            )
            Profile.objects.create(user=user)
        
        # Create tags
        for i in range(ratio):
            Tag.objects.create(name=f'tag{i}')
        
        # Create questions
        users = list(User.objects.all())
        tags = list(Tag.objects.all())
        
        for i in range(ratio * 10):
            question = Question.objects.create(
                title=f'Question {i}',
                content=f'Content for question {i}',
                author=random.choice(users),
                rating=random.randint(0, 50)
            )
            if tags:
                question.tags.add(random.choice(tags))
        
        # Create answers
        questions = list(Question.objects.all())
        for i in range(ratio * 100):
            Answer.objects.create(
                content=f'Answer {i}',
                author=random.choice(users),
                question=random.choice(questions),
                rating=random.randint(0, 30)
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully filled database:\n'
                f'- Users: {User.objects.count()}\n'
                f'- Questions: {Question.objects.count()}\n'
                f'- Answers: {Answer.objects.count()}\n'
                f'- Tags: {Tag.objects.count()}'
            )
        )