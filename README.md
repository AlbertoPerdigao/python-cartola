``` 
An app to manage a private league in the fantasy game Cartola FC.

This project is implemented using Flask, Flask-RESTful, Flask-SQLAlchemy, Flask-Marshmallow 
and is a REST API.

Note: Before running the application, rename the "app/database copy.py" file to "app/database.py" 
and edit it for your database configuration.
```

**Installation commands**
```
(https://pipenv.pypa.io/en/latest/)
pip install pipenv

(Inside the project folder)
pipenv install
```

**Activate environment**
```
pipenv shell
or
pipenv run
```

**Deactivate environment**
```
exit
```

**Execution File**
```
python run_cartola.py
```

**Flask-Migrate**
```
flask db init
flask db migrate -m "Initial migration."
flask db upgrade
```