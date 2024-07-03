import os
import requests
from cachetools import TTLCache, cached

cache = TTLCache(maxsize=128, ttl=10)


def get_headers():
    return {
        "Cookie": os.environ.get('COOKIE'),
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Referer": os.environ.get('REFERER'),
        "Origin": os.environ.get('ORIGIN'),
    }


def get_full_url(path):
    return ''.join([os.environ.get('BASE_URL'), path])


@cached(cache)
def get_employees() -> dict:
    res = requests.get(get_full_url(
        '/planningboard/employees'), headers=get_headers())

    if res.status_code == 200:
        return res.json()

    raise requests.exceptions.HTTPError


@cached(cache)
def get_employees_from_practice(practice: str) -> dict:
    employees = get_employees()
    practice = practice.lower()
    found = []

    for employee in employees['data']:
        for tag in employee['tags']:
            if tag['name'].lower() == practice:
                found.append({
                    'id': employee['id'],
                    'name': employee['name'],
                    'surname': employee['surname']
                })

    return found


def get_employee_by_name(name: str) -> int:
    employees = get_employees()
    name = name.lower()
    found = -1

    for employee in employees['data']:
        if name == ' '.join([employee['name'], employee['surname']]).lower():
            return employee['id']

    return found
