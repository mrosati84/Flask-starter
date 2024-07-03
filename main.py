import os
from dotenv import load_dotenv
from flask import Flask
from functions import get_employees, get_employee_by_name, get_employees_from_practice
load_dotenv()

app = Flask(__name__)


@app.route('/')
def hello():
    eid = get_employee_by_name('matteo rosati')
    return f'Found: {eid}'


if __name__ == "__main__":
    app.run()
