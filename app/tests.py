from django.test import TestCase
from django.contrib.auth.models import User
from .models import Question, Answer, Tag

class QuestionModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
    
    def test_question_creation(self):
        question = Question.objects.create(
            title='Test Question',
            content='Test content',
            author=self.user
        )
        self.assertEqual(question.title, 'Test Question')
        self.assertEqual(question.author.username, 'testuser')