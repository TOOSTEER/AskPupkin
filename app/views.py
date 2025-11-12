from django.shortcuts import render
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

def paginate(objects_list, request, per_page=10):
    paginator = Paginator(objects_list, per_page)
    page_number = request.GET.get('page', 1)
    
    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)
    
    return page

def index(request):
    questions = []
    for i in range(1, 30):
        questions.append({
            'title': f'Question title {i}',
            'id': i,
            'text': f'This is text for question {i}. It contains some details about the problem.',
            'tags': ['python', 'django', 'web'] if i % 3 == 0 else ['javascript', 'html'] if i % 3 == 1 else ['css', 'design'],
            'answers_count': i % 10,
            'votes': i % 20,
        })
    
    page = paginate(questions, request, 5)
    return render(request, 'index.html', {
        'page': page,
        'title': 'New Questions'
    })

def hot_questions(request):
    questions = []
    for i in range(1, 30):
        questions.append({
            'title': f'Hot Question {i}',
            'id': i,
            'text': f'This is a popular question {i} with many votes.',
            'tags': ['popular', 'hot', 'trending'],
            'answers_count': i % 15,
            'votes': 50 + i,
        })
    
    page = paginate(questions, request, 5)
    return render(request, 'index.html', {
        'page': page,
        'title': 'Hot Questions'
    })

def by_tag(request, tag_name):
    questions = []
    for i in range(1, 20):
        questions.append({
            'title': f'Question about {tag_name} {i}',
            'id': i,
            'text': f'This question is specifically about {tag_name}.',
            'tags': [tag_name, 'related'],
            'answers_count': i % 8,
            'votes': i % 25,
        })
    
    page = paginate(questions, request, 5)
    return render(request, 'index.html', {
        'page': page,
        'title': f'Tag: {tag_name}'
    })

def question(request, question_id):
    question_data = {
        'title': f'Question {question_id}',
        'id': question_id,
        'text': f'This is the full text of question {question_id}. It contains all the details that the user provided when asking the question.',
        'tags': ['python', 'django', 'web'],
    }
    
    answers = []
    for i in range(1, 15):
        answers.append({
            'text': f'This is answer {i} to question {question_id}. It provides a solution or suggestion.',
            'id': i,
        })
    
    page = paginate(answers, request, 5)
    return render(request, 'question.html', {
        'question': question_data,
        'page': page
    })

def login(request):
    return render(request, 'login.html')

def signup(request):
    return render(request, 'signup.html')

def ask(request):
    return render(request, 'ask.html')