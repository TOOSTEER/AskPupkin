#!/usr/bin/env python
import sys
import os

def check_environment():
    print(" Проверка окружения проекта...")
    
    checks = []
    
    python_version = sys.version_info
    checks.append((
        "Python version",
        python_version >= (3, 9),
        f"Current: {python_version.major}.{python_version.minor}.{python_version.micro}, Required: >=3.9"
    ))
    
    try:
        import django
        django_version = django.get_version()
        checks.append((
            "Django",
            True,
            f"Version: {django_version}"
        ))
    except ImportError:
        checks.append((
            "Django",
            False,
            "Not installed"
        ))
    
    try:
        import crispy_forms
        checks.append((
            "django-crispy-forms",
            True,
            "Installed"
        ))
    except ImportError:
        checks.append((
            "django-crispy-forms",
            False,
            "Not installed - run: pip install django-crispy-forms"
        ))
    
    in_venv = sys.prefix != sys.base_prefix
    checks.append((
        "Virtual environment",
        in_venv,
        f"Active: {in_venv}"
    ))
    
    req_exists = os.path.exists('requirements.txt')
    checks.append((
        "requirements.txt",
        req_exists,
        f"Exists: {req_exists}"
    ))
    
    print("\n Результаты проверки:")
    print("-" * 60)
    
    all_passed = True
    for name, passed, message in checks:
        status = "ok" if passed else "?"
        if not passed:
            all_passed = False
        print(f"{status} {name}: {message}")
    
    print("-" * 60)
    
    if all_passed:
        print("\n Все проверки пройдены! Проект готов к запуску.")
        print("\nЗапуск проекта:")
        print("1. Активировать виртуальное окружение")
        print("2. python manage.py migrate")
        print("3. python manage.py createsuperuser")
        print("4. python manage.py runserver")
        return 0
    else:
        print("\n  Есть проблемы с окружением!")
        print("\nРешение:")
        print("1. Создать виртуальное окружение: python -m venv venv")
        print("2. Активировать: source venv/bin/activate (Linux/Mac) или venv\\Scripts\\activate (Windows)")
        print("3. Установить зависимости: pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(check_environment())