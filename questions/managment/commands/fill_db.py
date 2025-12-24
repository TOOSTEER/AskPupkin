from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from questions.models import Profile, Question, Answer, Tag, QuestionLike, AnswerLike
from faker import Faker
import random
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Fill database with sample data'
    
    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int, help='Multiplication ratio')
    
    def handle(self, *args, **options):
        ratio = options['ratio']
        fake = Faker()
        
        num_users = ratio
        num_questions = ratio * 10
        num_answers = ratio * 100
        num_tags = ratio
        num_likes = ratio * 200
        
        self.stdout.write(f'Creating {num_users} users...')
        
        users = []
        profiles = []
        for i in range(num_users):
            user = User(
                username=fake.user_name() + str(i),
                email=fake.email(),
                password='testpass123'
            )
            users.append(user)
        
        User.objects.bulk_create(users)
        
        for user in User.objects.all():
            profile = Profile(user=user)
            profiles.append(profile)
        
        Profile.objects.bulk_create(profiles)
        
        self.stdout.write(f'Creating {num_tags} tags...')
        tags = []
        for i in range(num_tags):
            tag = Tag(name=fake.word() + str(i))
            tags.append(tag)
        
        Tag.objects.bulk_create(tags)
        
        self.stdout.write(f'Creating {num_questions} questions...')
        questions = []
        all_users = list(User.objects.all())
        all_tags = list(Tag.objects.all())
        
        for i in range(num_questions):
            question = Question(
                title=fake.sentence()[:255],
                content=fake.text(max_nb_chars=1000),
                author=random.choice(all_users),
                created_date=fake.date_time_between(
                    start_date='-30d', 
                    end_date='now',
                    tzinfo=timezone.get_current_timezone()
                ),
                rating=random.randint(-10, 50)
            )
            questions.append(question)
        
        Question.objects.bulk_create(questions)
        
        for question in Question.objects.all():
            question_tags = random.sample(all_tags, min(3, len(all_tags)))
            question.tags.set(question_tags)
        
        self.stdout.write(f'Creating {num_answers} answers...')
        answers = []
        all_questions = list(Question.objects.all())
        
        for i in range(num_answers):
            answer = Answer(
                content=fake.text(max_nb_chars=500),
                author=random.choice(all_users),
                question=random.choice(all_questions),
                created_date=fake.date_time_between(
                    start_date='-30d', 
                    end_date='now',
                    tzinfo=timezone.get_current_timezone()
                ),
                rating=random.randint(-5, 25),
                is_correct=random.choice([True, False])
            )
            answers.append(answer)
        
        Answer.objects.bulk_create(answers)
        
        self.stdout.write(f'Creating {num_likes} likes...')
        question_likes = []
        answer_likes = []
        
        for i in range(num_likes // 2):
            user = random.choice(all_users)
            question = random.choice(all_questions)
            question_likes.append(QuestionLike(
                user=user,
                question=question,
                value=random.choice([1, -1])
            ))
        
        all_answers = list(Answer.objects.all())
        for i in range(num_likes // 2):
            user = random.choice(all_users)
            answer = random.choice(all_answers)
            answer_likes.append(AnswerLike(
                user=user,
                answer=answer,
                value=random.choice([1, -1])
            ))
        
        QuestionLike.objects.bulk_create(question_likes)
        AnswerLike.objects.bulk_create(answer_likes)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created: {num_users} users, {num_questions} questions, '
                f'{num_answers} answers, {num_tags} tags, {num_likes} likes'
            )
        )