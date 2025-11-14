import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ask_pupkin.settings')
django.setup()

from django.contrib.auth.models import User
from app.models import Profile, Question, Answer, Tag

def reset_and_fill():
    print("=== RESETTING AND FILLING DATABASE ===")
    
    # Clear data
    User.objects.all().delete()
    Tag.objects.all().delete()
    
    # Create users
    for i in range(10):
        user = User.objects.create_user(
            username=f'user{i}',
            password='password123'
        )
        Profile.objects.create(user=user)
        print(f'Created user: user{i}')
    
    # Create tags
    for i in range(10):
        Tag.objects.create(name=f'tag{i}')
        print(f'Created tag: tag{i}')
    
    # Create questions
    users = list(User.objects.all())
    tags = list(Tag.objects.all())
    
    for i in range(100):
        question = Question.objects.create(
            title=f'Question {i}',
            content=f'This is content for question {i}',
            author=random.choice(users),
            rating=random.randint(0, 50)
        )
        question.tags.add(random.choice(tags))
    
    # Create answers
    questions = list(Question.objects.all())
    for i in range(1000):
        Answer.objects.create(
            content=f'Answer {i}',
            author=random.choice(users),
            question=random.choice(questions),
            rating=random.randint(0, 30)
        )
    
    print("=== DATABASE READY ===")
    print(f"Users: {User.objects.count()}")
    print(f"Questions: {Question.objects.count()}")
    print(f"Answers: {Answer.objects.count()}")
    print(f"Tags: {Tag.objects.count()}")

if __name__ == '__main__':
    reset_and_fill()