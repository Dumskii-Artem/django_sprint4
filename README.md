
git@github.com:Dumskii-Artem/django_sprint4.git

django + sqlite.

to run on Linux:

cd django_sprint4
python3 -m venv venv
source venv/bin/activate
python3 -m pip install --upgrade pip
pip install -r requirements.txt
cd blogicum/
python3 manage.py migrate
python3 manage.py loaddata db.json 

if you want:
python3 manage.py createsuperuser

python3 manage.py runserver
or
python3 manage.py runserver 8002