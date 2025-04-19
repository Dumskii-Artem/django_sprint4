## Linux

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



## В Windows
```
git clone git@github.com:Dumskii-Artem/django_sprint4.git  
  
в VSCode  
cd *****.....django_sprint4  
py -3.9 -m venv venv  
.\venv\Scripts\activate  
python -m pip install --upgrade pip  
pip install -r requirements.txt  
cd .\blogicum\  
python manage.py migrate  
python manage.py loaddata db.json  
if you want: python manage.py createsuperuser  
запускаем сервер  
python manage.py runserver  
в барузере вбиваем адрес http://127.0.0.1:8000/  
отсановить сервер ctrl+C в терминале VSCode  
django_sprint4\blogicum> pytest - работает  
```