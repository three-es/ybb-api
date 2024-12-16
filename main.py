import logging
import os
from flask import Flask, render_template, request, jsonify
from datetime import datetime
import io
from PyPDF2 import PdfFileWriter, PdfFileReader
from django.contrib.humanize.templatetags.humanize import ordinal
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth
import reportlab.rl_config
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import cm

# Configure ReportLab
reportlab.rl_config.warnOnMissingFontGlyphs = 0

# Create static/media directory if it doesn't exist
os.makedirs('static/media', exist_ok=True)

# Default configuration without custom fonts initially
rl_config = reportlab.rl_config
rl_config._SAVED['canvas_basefontname'] = 'Helvetica'
rl_config._startUp()

from datetime import date

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
        # Get JSON data from request
        data = request.get_json()
        if not data:
            logger.error("No JSON data received")
            return jsonify({
                'success': False,
                'error': 'No data received'
            }), 400
        
        # Log the received data
        logger.info("Received form submission:")
        logger.info(f"Name: {data.get('name', 'Not provided')}")
        logger.info(f"Dedication: {data.get('dedication', 'Not provided')}")
        logger.info(f"Date: {data.get('date', 'Not provided')}")
        
        # Validate required fields
        required_fields = ['name', 'dedication', 'date']

        #### starting the real interactions    

        
        for field in required_fields:
            if not data.get(field):
                logger.error(f"Validation failed: Missing {field}")
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400

        # Validate date format
        try:
            date_obj = datetime.strptime(data['date'], '%Y-%m-%d')
        except ValueError:
            logger.error("Invalid date format")
            return jsonify({
                'success': False,
                'error': 'Invalid date format'
            }), 400

        # Process the data (placeholder for Google view integration)
        response_data = {
            'success': True,
            'message': 'Form data received successfully',
            'submitted_data': {
                'name': data['name'],
                'dedication': data['dedication'],
                'date': data['date']
            }
        }
        
        logger.info("Processing successful, sending response")
        logger.debug(f"Response data: {response_data}")
        return jsonify(response_data)

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
