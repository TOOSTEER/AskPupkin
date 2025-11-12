from django.urls import path
from . import views

app_name = 'app'

urlpatterns = [
    path('', views.index, name='index'),
    path('hot/', views.hot_questions, name='hot'),
    path('tag/<str:tag_name>/', views.by_tag, name='by_tag'),
    path('question/<int:question_id>/', views.question, name='question'),
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('ask/', views.ask, name='ask'),
]