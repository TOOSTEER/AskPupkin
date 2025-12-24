from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('hot/', views.hot, name='hot'),
    path('tag/<str:tag_name>/', views.tag, name='tag'),
    path('question/<int:question_id>/', views.question, name='question'),
    
    # Авторизация
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    
    # Профиль
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    
    # Формы
    path('ask/', views.ask, name='ask'),
    
    # API для лайков
    path('question/<int:question_id>/like/', views.question_like, name='question_like'),
    path('answer/<int:answer_id>/like/', views.answer_like, name='answer_like'),
    path('answer/<int:answer_id>/correct/', views.mark_answer_correct, name='mark_answer_correct'),
]