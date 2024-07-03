from dotenv import load_dotenv
from flask import Flask, request, jsonify
from functions import check_availability
load_dotenv()

app = Flask(__name__)


@app.route('/availability')
def availability():
    try:
        # Get query string parameters
        practice = request.args.get('practice')
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')

        # Check if any parameter is missing
        if not practice or not from_date or not to_date:
            return jsonify({'error': 'Parameters practice, from_date, and to_date are mandatory.'}), 422

        # Call check_availability function with query parameters
        availability_result = check_availability(practice, from_date, to_date)

        return jsonify(availability_result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    app.run()
