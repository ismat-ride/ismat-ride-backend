# ismat-ride-backend

## How to run

Navigate to root folder of the project

```
src/
venv/
...
```

Activate the virtual environment

```
venv\Scripts\activate
```

Install the project dependencies

```
pip install -r requirements.txt
```

Startup the server

- Navigate to `src/`

```
for hot reload
flask --app app.py --debug run
Note : With hot reload you will just need to refresh the page to check the changes!

with out hot reload
flask run
```

## What to do if more packages are added to the project

Keep the venv activated

Add the new packages to the `requirements.txt` file

```
pip freeze > requirements.txt
```
