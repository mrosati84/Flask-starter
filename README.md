# Install and run

Create virtual env

```
python -m venv venv
```

Activate it

```
source ./venv/bin/activate
```

Install dependencies

```
pip install -r requirements.txt
```

Provide all environment variables in `.env`

Run the local server

```
flask --app main run --reload --debug
```
