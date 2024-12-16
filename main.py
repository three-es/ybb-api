import logging
from flask import Flask, render_template, request, jsonify
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = "your-secret-key-here"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/submit', methods=['POST'])
def submit():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'dedication', 'date']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400

        # Validate date format
        try:
            date_obj = datetime.strptime(data['date'], '%Y-%m-%d')
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Invalid date format'
            }), 400

        # Here you would typically forward this to your Google view
        # For now, we'll just return the data
        return jsonify({
            'success': True,
            'message': 'Data received successfully',
            'data': {
                'name': data['name'],
                'dedication': data['dedication'],
                'date': data['date']
            }
        })

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
