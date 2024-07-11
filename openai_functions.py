PRACTICES = ["Technology", "Experience", "strategy",
             "project management", "creative", "copywriter"]

JOB_TITLES = ['account director', 'account executive', 'account manager', 'art direction intern', 'art director', 'associate art director', 'associate content marketing manager', 'associate creative director', 'associate creative technologist', 'associate data analyst', 'associate design director', 'associate designer', 'associate experience design director', 'associate experience designer', 'associate program director', 'associate project director', 'associate project manager', 'associate strategy director', 'back-end developer', 'client partner', 'content marketing director', 'content marketing intern', 'content marketing manager', 'copywriter', 'copywriter intern', 'creative director c', 'data & research director', 'designer', 'director of client services', 'director of project management', 'director of strategy', 'director of technology', 'experience & design director', 'experience design intern', 'experience designer', 'experience writer', 'front-end developer', 'front-end leader', 'group account director', 'group creative director', 'junior frontend developer', 'operation lead', 'outsourcing manager', 'programme director', 'project manager', 'senior account director a', 'senior analyst', 'senior art director', 'senior consumer researcher', 'senior content marketing manager', 'senior copywriter', 'senior designer', 'senior experience designer', 'senior experience writer', 'senior project manager', 'senior strategist', 'social media strategist', 'strategist', 'strategy lead', 'technical artist', 'technical leader']

openai_func_check_availability_by_job_title = {
    "type": "function",
    "function": {
        "name": "check_employee_availability_by_jobtitle",
        "description": "Get availability for an employee with a job title  and time interval",
        "parameters": {
            "type": "object",
            "properties": {
                "job_title": {
                    "type": "string",
                    "enum": JOB_TITLES,
                    "description": "The job title  name",

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
            "required": ["job_title", "from_date", "to_date"],
        },
    },
}

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
