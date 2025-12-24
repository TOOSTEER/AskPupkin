from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('hot/', views.hot, name='hot'),
    path('tag/<str:tag_name>/', views.tag, name='tag'),
    path('question/<int:question_id>/', views.question, name='question'),
    
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    
    path('ask/', views.ask, name='ask'),
    
    path('question/<int:question_id>/like/', views.question_like_ajax, name='question_like_ajax'),
    path('answer/<int:answer_id>/like/', views.answer_like_ajax, name='answer_like_ajax'),
    path('answer/<int:answer_id>/correct/', views.mark_answer_correct, name='mark_answer_correct'),
    path('answer/<int:answer_id>/correct/ajax/', views.mark_answer_correct_ajax, name='mark_answer_correct_ajax'),
    path('check_like_status/', views.check_user_like_status, name='check_user_like_status'),
]