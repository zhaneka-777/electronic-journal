# electronic-journal
Студенттердің үлгерімін және сабаққа қатысуын бақылауға арналған электрондық журнал жүйесі
## Installation (Орнату және іске қосу)
# electronic-journal
Студенттердің үлгерімін және сабаққа қатысуын бақылауға арналған электрондық журнал жүйесі.

## Description (Сипаттама)
Бұл веб-қосымша оқу орындарындағы бағалау процесін автоматтандыруға және студенттердің үлгерімін онлайн режимде бақылауға арналған.

## Features (Мүмкіндіктер)
- Пайдаланушыларды тіркеу және авторизациялау (Мұғалім/Студент).
- Пәндер мен топтар бойынша баға қою.
- Студенттердің үлгерім статистикасын көру.

## Tech Stack (Технологиялар)
- **Backend:** Python (Django)
- **Frontend:** HTML, CSS, JavaScript
- **Database:** SQLite

## Installation (Орнату және іске қосу)
Жобаны іске қосу үшін мына командаларды орындаңыз:

```bash
# Виртуалды ортаны құру және іске қосу
python3 -m venv venv
source venv/bin/activate

# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

# Django-ны орнату
pip install django

pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate

# Серверді іске қосу
python manage.py runserver
 ⁠
## Негізгі беттер
•⁠  ⁠⁠ / ⁠ — login
•⁠  ⁠⁠ /register/ ⁠ — тіркелу
•⁠  ⁠⁠ /dashboard/ ⁠ — рөлге сай басты бет
•⁠  ⁠⁠ /grades/ ⁠ — бағалар
•⁠  ⁠⁠ /teacher-journal/ ⁠ — мұғалім журналы
•⁠  ⁠⁠ /audit-log/ ⁠ — аудит журналы
•⁠  ⁠⁠ /profile/ ⁠ — профиль
•⁠  ⁠⁠ /export/excel/ ⁠ — Excel экспорт
•⁠  ⁠⁠ /export/pdf/ ⁠ — PDF экспорт
