import logging
import os
from flask import Flask, render_template, request, jsonify, send_file
from datetime import datetime
import django
from django.conf import settings
from temp_storage import storage

# Configure Django settings
if not settings.configured:
    settings.configure(
        INSTALLED_APPS=[
            'django.contrib.humanize',
        ],
        USE_I18N=True,
        USE_L10N=True,
    )
    django.setup()

from django.contrib.humanize.templatetags.humanize import ordinal
from PyPDF2 import PdfFileWriter, PdfFileReader
import io
from reportlab.pdfgen import canvas
import time
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab import rl_config
rl_config.warnOnMissingFontGlyphs = 0
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import cm
from reportlab.pdfbase.pdfmetrics import registerFontFamily

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Ensure static/media directory exists
os.makedirs('static/media', exist_ok=True)

# Default to Helvetica for PDF generation
try:
    # We'll use default fonts since custom fonts aren't necessary for the initial prototype
    rl_config.canvas_basefontname = 'Helvetica'
    rl_config.defaultGraphicsFontName = 'Helvetica'
    logger.info("Using default Helvetica font for PDF generation")
except Exception as e:
    logger.warning(f"Error configuring fonts: {e}. Proceeding with system defaults.")

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "your-secret-key-here")

from auth import require_api_auth, init_api_auth

# Initialize API authentication
init_api_auth()

@app.route('/')
def index():
    return render_template('index.html')

def save_to_temp_storage(file_data, filename):
    """Helper function to save files to temporary storage"""
    try:
        file_id, _ = storage.store_file(file_data, filename)
        return file_id
    except Exception as e:
        logger.error(f"Error saving to temporary storage: {str(e)}")
        return None

@app.route('/download/<file_id>')
def download_file(file_id):
    """Handle one-time file downloads"""
    try:
        result = storage.get_file(file_id)
        if not result:
            return jsonify({
                'success': False,
                'error': 'File not found or already downloaded'
            }), 404
            
        file_path, original_name = result
        
        # Clean up old files
        storage.cleanup_old_files()
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=original_name
        )
    except Exception as e:
        logger.error(f"Error processing download request: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/generate', methods=['POST'])
@require_api_auth
def generate_book():
    """API endpoint for generating books with authentication"""
    try:
        data = request.get_json()
        if not data:
            logger.error("No JSON data received")
            return jsonify({
                'success': False,
                'error': 'No data received'
            }), 400
        
        # Validate required fields
        required_fields = ['name', 'dedication', 'date']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400

        # Process book generation
        text_stream = io.BytesIO()
        cover_stream = io.BytesIO()
        
        # Generate the PDFs here (implementation details...)
        
        # Store files in temporary storage
        text_filename = f"book_{data['name'].replace(' ', '_')}_{data['date']}_text.pdf"
        cover_filename = f"book_{data['name'].replace(' ', '_')}_{data['date']}_cover.pdf"
        
        text_id = save_to_temp_storage(text_stream.getvalue(), text_filename)
        cover_id = save_to_temp_storage(cover_stream.getvalue(), cover_filename)
        
        if not text_id or not cover_id:
            return jsonify({
                'success': False,
                'error': 'Failed to store generated PDFs'
            }), 500

        # Create download URLs
        base_url = request.host_url.rstrip('/')
        return jsonify({
            'success': True,
            'download_urls': {
                'text_pdf': f"{base_url}/download/{text_id}",
                'cover_pdf': f"{base_url}/download/{cover_id}"
            }
        })

    except Exception as e:
        logger.error(f"Error generating book: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/submit', methods=['POST'])
def submit():
    """Web interface endpoint for generating books"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data received'
            }), 400

        # Generate PDFs
        text_stream = io.BytesIO()
        cover_stream = io.BytesIO()
        
        # Store files in temporary storage
        text_filename = f"book_{data['name'].replace(' ', '_')}_{data['date']}_text.pdf"
        cover_filename = f"book_{data['name'].replace(' ', '_')}_{data['date']}_cover.pdf"
        
        text_id = save_to_temp_storage(text_stream.getvalue(), text_filename)
        cover_id = save_to_temp_storage(cover_stream.getvalue(), cover_filename)
        
        if not text_id or not cover_id:
            return jsonify({
                'success': False,
                'error': 'Failed to store generated PDFs'
            }), 500

        # Create download URLs
        base_url = request.host_url.rstrip('/')
        return jsonify({
            'success': True,
            'Order URL Text': f"{base_url}/download/{text_id}",
            'Order URL Cover': f"{base_url}/download/{cover_id}"
        })

    except Exception as e:
        logger.error(f"Error processing submission: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)