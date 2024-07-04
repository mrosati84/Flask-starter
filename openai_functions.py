PRACTICES = ["Technology", "Experience", "strategy", "project management", "creative", "copywriter"]

openai_func_check_availability = {
    "type": "function",
    "function": {
        "name": "check_availability",
        "description": "Get availability for a specific practice and time interval",
        "parameters": {
            "type": "object",
            "properties": {
                "practice": {
                    "type": "string",
                    "enum": PRACTICES,
                    "description": "The practice name",

                },
                "from_date": {
                    "type": "string",
                    "format": "date",
                    "description": "The start date in 'YYYY-MM-DD' format"
                },
                "to_date": {
                    "type": "string",
                    "format": "date",
                    "description": "The start date in 'YYYY-MM-DD' format"
                },
            },
            "required": ["practice", "from_date", "to_date"],
        },
    },
}

openai_func_check_employee_availability = {
    "type": "function",
    "function": {
        "name": "check_employee_availability",
        "description": "Get a specific employee availability for a specific time interval",
        "parameters": {
            "type": "object",
            "properties": {
                "employee_name": {
                    "type": "string",
                    "description": "The employee name and surname",
                },
                "from_date": {
                    "type": "string",
                    "format": "date",
                    "description": "The start date in 'YYYY-MM-DD' format"
                },
                "to_date": {
                    "type": "string",
                    "format": "date",
                    "description": "The start date in 'YYYY-MM-DD' format"
                },
            },
            "required": ["employee_name", "from_date", "to_date"],
        },
    },
}