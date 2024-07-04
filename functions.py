import os
import requests
from datetime import datetime, timedelta
from cachetools import TTLCache, cached
from openai import OpenAI
import json
from entities.allocation import Allocation
from openai_functions import openai_func_check_availability, openai_func_check_employee_availability

cache = TTLCache(maxsize=128, ttl=int(os.environ.get('CACHE_TTL')))


def get_headers() -> dict:
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
    return {
        "Cookie": os.environ.get('COOKIE'),
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Referer": os.environ.get('REFERER'),
        "Origin": os.environ.get('ORIGIN')
    }


def get_full_url(path: str) -> str:
    """
    Constructs a full URL by appending a given path to a base URL.

    This function takes a relative path and appends it to the base URL, which is fetched from the 'BASE_URL' environment variable.

    Args:
        path (str): The relative path to be appended to the base URL.

    Returns:
        str: The full URL constructed by concatenating the base URL and the provided path.
    """
    return ''.join([os.environ.get('BASE_URL'), path])


def calculate_hours(from_date: str, to_date: str) -> int:
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


def calculate_load(load_hours: int, from_date: str, to_date: str) -> int:
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
    # Calculate the total work hours between the given dates
    total_work_hours = calculate_hours(from_date, to_date)

    # Special case: If total_work_hours is 0, avoid division by zero
    if total_work_hours == 0:
        return 0

    # Calculate the percentage
    percentage = (load_hours / total_work_hours) * 100

    return percentage


@cached(cache)
def get_employees() -> dict:
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
    res = requests.get(get_full_url(
        '/planningboard/employees'), headers=get_headers())

    if res.status_code == 200:
        return res.json()

    raise requests.exceptions.HTTPError


@cached(cache)
def get_employees_from_practice(practice: str) -> list:
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
    employees = get_employees()
    practice = practice.lower()
    found = []

    for employee in employees['data']:
        for tag in employee['tags']:
            if tag['name'].lower() == practice:
                found.append(employee['id'])

    return found


@cached(cache)
def get_employee_by_name(name: str) -> int:
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
    employees = get_employees()
    name = name.lower()
    found = -1

    for employee in employees['data']:
        if name == ' '.join([employee['name'], employee['surname']]).lower():
            return employee['id']

    return found


@cached(cache)
def get_employee_name_by_id(employee_id: int) -> int:
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
    employees = get_employees()
    found = -1

    for employee in employees['data']:
        if employee_id == int(employee['id']):
            return ' '.join([employee['name'], employee['surname']])

    return found


def get_plannings(from_date: str, to_date: str) -> dict:
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
    response = requests.get(get_full_url(
        '/planningboard/'), headers=get_headers(), params={
        "from": from_date,
        "to": to_date
    })

    if response.status_code == 200:
        return response.json()

    raise requests.exceptions.HTTPError()


def check_availability(practice: str, from_date: str, to_date: str) -> list:
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
    # mi serve un <practice> da <from_date> a <to_date>

    # prendo gli employee di quella practice (solo id)
    employees = get_employees_from_practice(practice)

    # prendo tutte le allocazioni da <from_date> a <to_date>
    plannings = get_plannings(from_date, to_date)

    availabilities = []

    for employee_id in employees:
        if str(employee_id) not in plannings['data']['plannings']:
            # l'id non appare, quindi significa che non esiste alcuna allocazione.
            # nessuna allocazione significa che la risorsa e' al 100% libera.
            availabilities.append({
                "name": get_employee_name_by_id(employee_id),
                "amount": f'{calculate_load(0, from_date, to_date)}%'
            })
        else:
            # la risorsa non e' libera al 100% perche' appare nelle allocazioni
            total_amount = 0

            for slot in plannings['data']['plannings'][str(employee_id)]:
                total_amount = total_amount + slot['amount']

            amount_occupied = int(calculate_load(
                total_amount, from_date, to_date))

            availabilities.append({
                "name": get_employee_name_by_id(employee_id),
                "amount_occupied": f'{amount_occupied}%',
                "amount_free": f'{100 - amount_occupied}%',
            })

    return availabilities


def check_employee_availability(employee_name, from_date, to_date):
    """
    Check the availability of an employee within a specified date range.

    Args:
        employee_name (str): The name of the employee to check.
        from_date (str): The start date of the period to check, in YYYY-MM-DD format.
        to_date (str): The end date of the period to check, in YYYY-MM-DD format.

    Returns:
        dict: A dictionary containing:
            - "name" (str): The name of the employee.
            - "amount_occupied" (str): The percentage of time the employee is occupied.
            - "amount_free" (str): The percentage of time the employee is free.

    Raises:
        ValueError: If the employee_name is not found.

    Example:
        >>> check_employee_availability("John Doe", "2023-07-01", "2023-07-31")
        {
            "name": "John Doe",
            "amount_occupied": "40%",
            "amount_free": "60%"
        }
    """
    employee_id = get_employee_by_name(employee_name)

    if employee_id < 0:
        return {'error': 'Employee not found.'}

    plannings = get_plannings(from_date, to_date)

    # la risorsa e' libera al 100% perche' non appare nelle allocazioni
    if str(employee_id) not in plannings['data']['plannings']:
        return [{
            "name": employee_name,
            "amount_occupied": "0%",
            "amount_free": "100%"
        }]

    # la risorsa non e' libera al 100% perche' appare nelle allocazioni
    total_amount = 0

    for slot in plannings['data']['plannings'][str(employee_id)]:
        total_amount = total_amount + slot['amount']

    amount_occupied = int(calculate_load(total_amount, from_date, to_date))

    return [{
        "name": employee_name,
        "amount_occupied": f'{amount_occupied}%',
        "amount_free": f'{100 - amount_occupied}%',
    }]


def GPT_conversation(prompt: str) -> str:
    # PRACTICES = ["Technology", "Experience", "strategy", "project management", "creative", "copywriter"]
    
    client = OpenAI()
    current_year = datetime.now().year
    current_date = datetime.now().strftime("%Y-%m-%d")
    prompt = prompt + \
        " \n If no year is specified assume the year is %s \n Today is %s \n Answer by providing the answer in a natural language without adding any questions or further details" % (current_year, current_date)
    

    tools = [
        openai_func_check_availability,
        openai_func_check_employee_availability        
    ]

    messages = [
        {"role": "user", "content": prompt},
    ]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=tools,
        tool_choice="auto",  # auto is default, but we'll be explicit
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    # Step 2: check if the model wanted to call a function
    if tool_calls:
        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors

        # we filter tools to fetch each item function.name parameter and create a dictionary with the function name as key and value
        
        available_functions = {
            "check_availability":check_availability,
            "check_employee_availability":check_employee_availability,
        }
        
        # extend conversation with assistant's reply
        messages.append(response_message)

        # Step 4: send the info for each function call and function response to the model
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)

            if function_name == "check_availability":
                function_response = function_to_call(
                    practice=function_args.get("practice"),
                    from_date=function_args.get("from_date"),
                    to_date=function_args.get("to_date"),
                )
            elif function_name == "check_employee_availability":
                function_response = function_to_call(
                    employee_name=function_args.get("employee_name"),
                    from_date=function_args.get("from_date"),
                    to_date=function_args.get("to_date"),
                )

                # for each item in the response, create a new Allocation with it and add its toString() to the list

            function_response_to_str = []

            for item in function_response:
                function_response_to_str.append(Allocation(item.get("name"), item.get(
                    "amount_free"), item.get("amount_occupied")).toString())

            function_response_to_str = "\n".join(function_response_to_str)
            # print("FR: ",function_response_to_str, function_args.get("practice"), function_args.get("from_date"), function_args.get("to_date"))

            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response_to_str,
                }
            )

        second_response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
        )  # get a new response from the model where it can see the function response

        # print (second_response.choices[0].message.content)
        return second_response.choices[0].message.content
