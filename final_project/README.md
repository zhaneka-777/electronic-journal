# Электрондық журнал және үлгерім жүйесі

Бұл нұсқа іске қосуға ыңғайлы етіп жаңартылды: login, register, forgot password, dashboard, grades, teacher journal, audit log, profile, export Excel/PDF батырмалары жұмыс істейді.

## Іске қосу
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

## Demo аккаунттар
- admin / Admin12345
- teacher1 / Teacher12345
- student1 / Student12345

## Негізгі беттер
- `/` — login
- `/register/` — тіркелу
- `/dashboard/` — рөлге сай басты бет
- `/grades/` — бағалар
- `/teacher-journal/` — мұғалім журналы
- `/audit-log/` — аудит журналы
- `/profile/` — профиль
- `/export/excel/` — Excel экспорт
- `/export/pdf/` — PDF экспорт
