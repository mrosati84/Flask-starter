import os
import requests
from datetime import datetime, timedelta
from cachetools import TTLCache, cached

cache = TTLCache(maxsize=128, ttl=int(os.environ.get('CACHE_TTL')))


"""
Fetches HTTP headers from environment variables.

This function constructs a dictionary of HTTP headers with values retrieved from environment variables.
The headers included are:
- "Cookie": Value obtained from the 'COOKIE' environment variable.
- "Accept": A static value set to "application/json, text/javascript, */*; q=0.01".
- "Referer": Value obtained from the 'REFERER' environment variable.
- "Origin": Value obtained from the 'ORIGIN' environment variable.

Returns:
    dict: A dictionary containing the HTTP headers.
"""


def get_headers() -> dict:
    return {
        "Cookie": os.environ.get('COOKIE'),
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Referer": os.environ.get('REFERER'),
        "Origin": os.environ.get('ORIGIN')
    }


"""
Constructs a full URL by appending a given path to a base URL.

This function takes a relative path and appends it to the base URL, which is fetched from the 'BASE_URL' environment variable.

Args:
    path (str): The relative path to be appended to the base URL.

Returns:
    str: The full URL constructed by concatenating the base URL and the provided path.
"""


def get_full_url(path: str) -> str:
    return ''.join([os.environ.get('BASE_URL'), path])


"""
Calculates the total number of work hours between two dates, excluding weekends.

This function computes the total work hours between a given 'from_date' and 'to_date'. 
Each workday (Monday to Friday) is considered to have 8 work hours. 
Saturdays and Sundays are excluded from the calculation. 
If 'from_date' is greater than 'to_date', the function returns 0.

Args:
    from_date (str): The start date in 'YYYY-MM-DD' format.
    to_date (str): The end date in 'YYYY-MM-DD' format.

Returns:
    int: The total number of work hours between the two dates, excluding weekends.
"""


def calculate_hours(from_date: str, to_date: str) -> int:
    # Convert strings to datetime objects
    from_date = datetime.strptime(from_date, '%Y-%m-%d')
    to_date = datetime.strptime(to_date, '%Y-%m-%d')

    # Special case: from_date is greater than to_date
    if from_date > to_date:
        return 0

    # Initialize the total hours
    total_hours = 0

    # Iterate over each day in the range, inclusive of boundaries
    current_date = from_date
    while current_date <= to_date:
        # Check if the current day is a weekday (Monday=0, Sunday=6)
        if current_date.weekday() < 5:  # 0 to 4 are weekdays
            total_hours += 8
        current_date += timedelta(days=1)

    return total_hours


"""
Calculates the percentage of load hours against total work hours between two dates.

This function computes the percentage of 'load_hours' relative to the total work hours 
between 'from_date' and 'to_date'. If 'total_work_hours' is 0, the function returns 0 
to avoid division by zero.

Args:
    load_hours (int): The number of hours to calculate the percentage for.
    from_date (str): The start date in 'YYYY-MM-DD' format.
    to_date (str): The end date in 'YYYY-MM-DD' format.

Returns:
    int: The percentage of load hours relative to the total work hours, rounded to the nearest integer.
"""


def calculate_load(load_hours: int, from_date: str, to_date: str) -> int:
    # Calculate the total work hours between the given dates
    total_work_hours = calculate_hours(from_date, to_date)

    # Special case: If total_work_hours is 0, avoid division by zero
    if total_work_hours == 0:
        return 0

    # Calculate the percentage
    percentage = (load_hours / total_work_hours) * 100

    return percentage


"""
Fetches a dictionary of employees from a remote API endpoint.

This function makes a GET request to the '/planningboard/employees' endpoint 
using the 'requests' library. It includes headers fetched from environment variables 
via the 'get_headers()' function. If the request is successful (status code 200), 
it returns the JSON response parsed as a dictionary. If the request fails, 
it raises a requests.exceptions.HTTPError.

Returns:
    dict: A dictionary containing the employees fetched from the API endpoint.
"""


@cached(cache)
def get_employees() -> dict:
    res = requests.get(get_full_url(
        '/planningboard/employees'), headers=get_headers())

    if res.status_code == 200:
        return res.json()

    raise requests.exceptions.HTTPError


"""
Fetches a list of employee IDs associated with a specific practice from a cached dictionary of employees.

This function retrieves a cached dictionary of employees using the 'get_employees()' function. 
It then filters through the employees based on a provided 'practice' string, which is compared 
against the 'name' attribute in each employee's 'tags' list (case-insensitive comparison). 
If a match is found, the employee's ID is appended to the 'found' list.

Args:
    practice (str): The practice to filter employees by.

Returns:
    list: A list of employee IDs associated with the specified practice.
"""


@cached(cache)
def get_employees_from_practice(practice: str) -> list:
    employees = get_employees()
    practice = practice.lower()
    found = []

    for employee in employees['data']:
        for tag in employee['tags']:
            if tag['name'].lower() == practice:
                found.append(employee['id'])

    return found


"""
Fetches the ID of an employee by their full name from a cached dictionary of employees.

This function retrieves a cached dictionary of employees using the 'get_employees()' function. 
It searches for an employee whose full name (concatenation of 'name' and 'surname' attributes) 
matches the provided 'name' parameter (case-insensitive comparison). If a matching employee is found, 
the function returns their ID. If no match is found, it returns -1.

Args:
    name (str): The full name of the employee to fetch.

Returns:
    int: The ID of the employee if found, otherwise -1.
"""


@cached(cache)
def get_employee_by_name(name: str) -> int:
    employees = get_employees()
    name = name.lower()
    found = -1

    for employee in employees['data']:
        if name == ' '.join([employee['name'], employee['surname']]).lower():
            return employee['id']

    return found


"""
Fetches the full name of an employee by their ID from a cached dictionary of employees.

This function retrieves a cached dictionary of employees using the 'get_employees()' function. 
It searches for an employee whose ID matches the provided 'employee_id' parameter. If a matching 
employee is found, the function returns their full name (concatenation of 'name' and 'surname' attributes). 
If no match is found, it returns -1.

Args:
    employee_id (int): The ID of the employee to fetch.

Returns:
    str: The full name of the employee if found, otherwise -1.
"""


@cached(cache)
def get_employee_name_by_id(employee_id: int) -> int:
    employees = get_employees()
    found = -1

    for employee in employees['data']:
        if employee_id == int(employee['id']):
            return ' '.join([employee['name'], employee['surname']])

    return found


"""
Fetches planning data from a remote API endpoint based on specified date range.

This function makes a GET request to the '/planningboard/' endpoint 
using the 'requests' library. It includes headers fetched from environment variables 
via the 'get_headers()' function and query parameters 'from' and 'to' set to 
the provided 'from_date' and 'to_date' parameters. If the request is successful 
(status code 200), it returns the JSON response parsed as a dictionary. If the 
request fails, it raises a requests.exceptions.HTTPError.

Args:
    from_date (str): The start date in 'YYYY-MM-DD' format.
    to_date (str): The end date in 'YYYY-MM-DD' format.

Returns:
    dict: A dictionary containing the planning data fetched from the API endpoint.
"""


def get_plannings(from_date: str, to_date: str) -> dict:
    response = requests.get(get_full_url(
        '/planningboard/'), headers=get_headers(), params={
        "from": from_date,
        "to": to_date
    })

    if response.status_code == 200:
        return response.json()

    raise requests.exceptions.HTTPError()


"""
Checks the availability of employees in a specific practice within a given date range.

This function retrieves the list of employee IDs associated with the specified practice 
using the 'get_employees_from_practice()' function. It then fetches planning data 
from the '/planningboard/' endpoint using the 'get_plannings()' function for the 
provided 'from_date' and 'to_date'. Based on the retrieved data, it determines the 
availability of each employee during that period.

If an employee ID does not appear in the planning data, it means the employee has 
no allocations and is considered 100% available. If an employee ID appears in the 
planning data, the function calculates the total allocated hours and computes 
the percentage of availability using the 'calculate_load()' function.

Args:
    practice (str): The practice name to filter employees by.
    from_date (str): The start date in 'YYYY-MM-DD' format.
    to_date (str): The end date in 'YYYY-MM-DD' format.

Returns:
    list: A list of dictionaries containing the names and availability percentages 
    of employees in the specified practice during the given date range.
"""


def check_availability(practice: str, from_date: str, to_date: str) -> list:
    # mi serve un <practice> da <from_date> a <to_date>

    # prendo gli employee di quella practice (solo id)
    employees = get_employees_from_practice(practice)

    # prendo tutte le allocazioni da <from_date> a <to_date>
    plannings = get_plannings(from_date, to_date)

    free = []

    for employee_id in employees:
        if str(employee_id) not in plannings['data']['plannings']:
            # l'id non appare, quindi significa che non esiste alcuna allocazione.
            # nessuna allocazione significa che la risorsa e' al 100% libera.
            free.append({
                "name": get_employee_name_by_id(employee_id),
                "amount": f'{calculate_load(0, from_date, to_date)}%'
            })
        else:
            # la risorsa non e' libera al 100% perche' appare nelle allocazioni
            total_amount = 0

            for slot in plannings['data']['plannings'][str(employee_id)]:
                total_amount = total_amount + slot['amount']
            
            amount_occupied = int(calculate_load(total_amount, from_date, to_date))

            free.append({
                "name": get_employee_name_by_id(employee_id),
                "amount_occupied": f'{amount_occupied}%',
                "amount_free": f'{100 - amount_occupied}%',
            })

    return free
