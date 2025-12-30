from django import template
from django.template.defaultfilters import stringfilter
from django.utils.html import escape
import markdown

register = template.Library()

@register.filter(name='markdown')
@stringfilter
def markdown_filter(value):
    value = escape(value)
    
    extensions = [
        'markdown.extensions.fenced_code',
        'markdown.extensions.codehilite',
        'markdown.extensions.tables',
        'markdown.extensions.toc',
        'markdown.extensions.nl2br',
    ]
    
    try:
        return markdown.markdown(value, extensions=extensions)
    except:
        return value

@register.filter(name='truncate_words')
@stringfilter
def truncate_words(value, arg):
    try:
        words = int(arg)
    except ValueError:
        return value
    
    word_list = value.split()
    if len(word_list) > words:
        return ' '.join(word_list[:words]) + '...'
    return value

@register.filter(name='split')
def split_filter(value, delimiter=','):
    if not value:
        return []
    return [item.strip() for item in str(value).split(delimiter)]

@register.filter(name='get_item')
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter(name='add_class')
def add_class(field, css_class):
    return field.as_widget(attrs={"class": css_class})

@register.filter(name='pluralize_en')
def pluralize_en(number, forms):
    try:
        number = int(number)
    except (ValueError, TypeError):
        return ''
    
    forms_list = forms.split(',')
    if len(forms_list) != 3:
        return forms_list[0] if forms_list else ''
    
    if number == 1:
        return forms_list[0]
    elif 2 <= number <= 4:
        return forms_list[1]
    else:
        return forms_list[2]

@register.simple_tag
def url_replace(request, field, value):
    dict_ = request.GET.copy()
    dict_[field] = value
    return dict_.urlencode()

@register.filter(name='time_since_short')
def time_since_short(value):
    if not value:
        return ""
    
    from django.utils import timezone
    from datetime import timedelta
    
    now = timezone.now()
    diff = now - value
    
    if diff < timedelta(minutes=1):
        return "just now"
    elif diff < timedelta(hours=1):
        minutes = int(diff.total_seconds() / 60)
        return f"{minutes}m ago"
    elif diff < timedelta(days=1):
        hours = int(diff.total_seconds() / 3600)
        return f"{hours}h ago"
    elif diff < timedelta(days=30):
        days = diff.days
        return f"{days}d ago"
    elif diff < timedelta(days=365):
        months = int(diff.days / 30)
        return f"{months}mo ago"
    else:
        years = int(diff.days / 365)
        return f"{years}y ago"