from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Q, Sum
from .models import Tag, Question

def site_info(request):
    popular_tags = Tag.objects.annotate(
        question_count=Count('questions')
    ).order_by('-question_count')[:20]
    
    week_ago = timezone.now() - timedelta(days=7)
    
    from django.contrib.auth.models import User
    best_users = User.objects.annotate(
        total_rating=Sum(
            'questions__rating',
            filter=Q(questions__created_date__gte=week_ago)
        ) + Sum(
            'answers__rating',
            filter=Q(answers__created_date__gte=week_ago)
        )
    ).filter(total_rating__isnull=False).order_by('-total_rating')[:10]
    
    return {
        'popular_tags': popular_tags,
        'best_users': best_users,
    }