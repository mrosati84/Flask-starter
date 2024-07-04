import uuid
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
from functions import check_availability, check_employee_availability, GPT_conversation
load_dotenv()

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/availability')
def availability():
    try:
        # Get query string parameters
        practice = request.args.get('practice')
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        employee = request.args.get('employee')

        # Check if any parameter is missing
        if not from_date or not to_date:
            return jsonify({'error': 'Parameters from_date, and to_date are mandatory.'}), 422

        if practice and employee:
            return jsonify({'error': 'Cannot specify both practice and employee.'}), 422

        if practice:
            return jsonify(check_availability(practice, from_date, to_date))

        if employee:
            return jsonify(check_employee_availability(employee, from_date, to_date))

        # Fallback, neither practice or employee have been specified
        return jsonify({'error': 'Must specify either practice or employee.'}), 422

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/testgpt')
def testgpt():
    client = OpenAI()

    try:
        prompt = request.args.get(
            'prompt', default="chi c'è della practice technology libero dal 4 al 10 luglio ?", type=str)

        res = GPT_conversation(prompt)

        with client.audio.speech.with_streaming_response.create(
            model="tts-1",
            voice="nova",
            input=res,
        ) as response:
            print(response)
            # create a unique uuid using uuid library
            id = str(uuid.uuid4())

            # create mp3 dir if it doesn't exist
            Path("audio").mkdir(parents=True, exist_ok=True)

            speech_file_path = f"static/audio/{id}.mp3"
            response.stream_to_file(speech_file_path)

        return jsonify({'txt': res, 'mp3': ''.join(['/', speech_file_path])})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0")
