1. Set Up the Project
[] python3 -m venv venv 
[] source venv/bin/activate
[] pip install flask
[] pip3 freeze > requirements.txt

[] Development Mode : FLASK_ENV=development flask run
[] Set development Mode: export FLASK_ENV=development


dropdb restaurant_inventory_db
createdb restaurant_inventory_db

ipython3
%run app.py - %run seed.py



heroku logs --tail
git push heroku WIP:main