import logging
from werkzeug.utils import secure_filename
from flask import Flask, jsonify, request, send_from_directory, render_template
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Ensure upload directory exists
UPLOAD_FOLDER = os.path.join('static', 'media', 'full_book', 'output')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Configure maximum content length for file uploads (50MB)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
@app.route('/download/<path:filename>')
def download_file(filename):
    try:
        # Ensure the filename doesn't contain directory traversal
        safe_filename = secure_filename(os.path.basename(filename))
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
        
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return jsonify({
                'success': False,
                'error': 'File not found'
            }), 404
            
        return send_from_directory(app.config['UPLOAD_FOLDER'], safe_filename)
    except Exception as e:
        logger.error(f"Error serving file: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'File not found'
        }), 404
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
import os
from flask import Flask, render_template, request, jsonify, send_from_directory, url_for
from datetime import datetime
import django
from django.conf import settings
from flask_cors import CORS

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
import reportlab.rl_config
reportlab.rl_config.warnOnMissingFontGlyphs = 0
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab import rl_config
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFont

# Ensure static/media directory exists
os.makedirs('static/media', exist_ok=True)

# Default to Helvetica if custom fonts are not available
try:
    registerFont(TTFont('arial', 'static/media/arial123.ttf'))
    rl_config._SAVED['canvas_basefontname'] = 'arial'
    rl_config._startUp()
    pdfmetrics.registerFont(TTFont('font1', 'static/media/test2.ttf'))
except Exception as e:
    logging.warning(f"Could not load custom fonts: {e}. Using default fonts.")
    rl_config._SAVED['canvas_basefontname'] = 'Helvetica'
    rl_config._startUp()

from datetime import date

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize CORS after creating the Flask app
app = Flask(__name__)
CORS(app)

# Add this after creating the Flask app
app.config['STATIC_FOLDER'] = os.path.join(app.root_path, 'static')
os.makedirs(os.path.join(app.root_path, 'static', 'media', 'full_book', 'output'), exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

# Create secure downloads directory
DOWNLOADS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'secure_downloads')
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

@app.route('/download/<path:filename>')
def download_file(filename):
    try:
        # Define the directory where your generated files are stored
        uploads_dir = os.path.join(app.root_path, 'static', 'media', 'full_book', 'output')
        return send_from_directory(
            uploads_dir,
            filename,
            as_attachment=True
        )
    except Exception as e:
        logger.error(f"Error serving file: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'File not found'
        }), 404

def generate_download_url(filename):
    """Generate a proper download URL for a file"""
    secure_name = secure_filename(filename)
    return url_for('download_file', filename=secure_name, _external=True)

from auth import require_api_auth, init_api_auth

# Initialize API authentication
init_api_auth()

@app.route('/api/generate', methods=['POST'])
@require_api_auth
def generate_book():
    try:
        # Get JSON data from request
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

        # Process the book generation using existing logic
        name = data.get('name')
        dedication = data.get('dedication')
        date = data.get('date')

        # Log the received data
        logger.info("Received API request:")
        logger.info(f"Name: {name}")
        logger.info(f"Dedication: {dedication}")
        logger.info(f"Date: {date}")

        # Generate PDFs (reuse existing logic)
        book_name_input = name.replace("'", "'").replace('"', '"')
        dedication_name_input = dedication.replace("'", "'").replace('"', '"')
        date_input = date

        # [Existing PDF generation logic happens here in the submit() function]

        # Define file paths using the secure downloads directory
        # Generate secure filenames
        text_filename = secure_filename(f"ybb_{book_name_input}_{date_input}_hard_text.pdf")
        cover_filename = secure_filename(f"ybb_{book_name_input}_{date_input}_hard_cover.pdf")

        # Define file paths in the static/media/full_book/output directory
        output_dir = os.path.join(app.root_path, 'static', 'media', 'full_book', 'output')
        text_filepath = os.path.join(output_dir, text_filename)
        cover_filepath = os.path.join(output_dir, cover_filename)

        # Create a new PDF writer for the final output
        output = PdfFileWriter()
        
        # Add all pages to the output
        for page in [page1, page2, page3, page4, page5, page6, page7, 
                    page8, page9, page10, page11, page12]:
            output.addPage(page)

        # Save the text PDF
        os.makedirs(os.path.dirname(text_filepath), exist_ok=True)
        with open(text_filepath, 'wb') as outfile:
            output.write(outfile)
            
        # Save the cover PDF
        os.makedirs(os.path.dirname(cover_filepath), exist_ok=True)
        with open(cover_filepath, 'wb') as outfile:
            output.write(outfile)

        # Generate download URLs
        base_url = request.url_root.rstrip('/')

        return jsonify({
            'success': True,
            'files': {
                'text_pdf': f'{base_url}/download/{text_filename}',
                'cover_pdf': f'{base_url}/download/{cover_filename}'
            },
            'message': 'PDF files generated successfully'
        })

    except Exception as e:
        logger.error(f"Error processing API request: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

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

        book_name_input = data.get('name', 'Not provided')
        book_name_input = book_name_input.replace("'", "")
        book_name_input = book_name_input.replace('"', "")
        print(book_name_input)

        date_input = data.get('date', 'Not provided')
        print("here is each date_input:", date_input)
        dedication_name_input = data.get('dedication', 'Not provided')
        dedication_name_input = dedication_name_input.replace("'", "")
        dedication_name_input = dedication_name_input.replace('"', "")



        from datetime import date

        print("Pdf Book Builder Initialized")
        ##### Variables #####
        start_time = time.time() # Starts time recorder
        #book_name_input = "Etta Jean Mai Stanton" # Sets Variable manually, can easily switcheroo for the data when in prod
        #dedication_name_input = "Happy Birthday to You Happy Birthday to You Happy Birthday Dear (name) Happy Birthday to You.  From good friends and true, From old friends and new, May good luck go with you, And happiness too.  Alternative ending: How old are you? How old are you? How o"
        #date_input = date_input
        #Element = "wood"

        ###### Conditional Logic - Which Front cover ######
        astro_sign = 'Leo'
        date_input = str(date_input)
        month = date_input[5:7]
        day = int(date_input[8:10])

        if month == '12':
            astro_sign = 'Sagittarius' if (day < 22) else 'Capricorn'
        elif month == '01':
            astro_sign = 'Capricorn' if (day < 20) else 'Aquarius'
        elif month == '02':
            astro_sign = 'Aquarius' if (day < 19) else 'Pisces'
        elif month == '03':
            astro_sign = 'Pisces' if (day < 21) else 'Aries'
        elif month == '04':
            astro_sign = 'Aries' if (day < 20) else 'Taurus'
        elif month == '05':
            astro_sign = 'Taurus' if (day < 21) else 'Gemini'
        elif month == '06':
            astro_sign = 'Gemini' if (day < 21) else 'Cancer'
        elif month == '07':
            astro_sign = 'Cancer' if (day < 23) else 'Leo'
        elif month == '08':
            astro_sign = 'Leo' if (day < 23) else 'Virgo'
        elif month == '09':
            astro_sign = 'Virgo' if (day < 23) else 'Libra'
        elif month == '10':
            astro_sign = 'Libra' if (day < 23) else 'Scorpio'
        elif month == '11':
            astro_sign = 'Scorpio' if (day < 22) else 'Sagittarius'

        print(astro_sign)


        text_width = stringWidth(book_name_input, "font1", 50) # Measure the width of the book_name_input variable
        packet = io.BytesIO() # opens reportlab session
        can = canvas.Canvas(packet, pagesize=(1273, 661)) # Sets canvas size -> this is incorrect
        can.setFillColorRGB(255,255,255) #choose your font colour
        can.setFont("font1", 50) #choose your font type and font size
        y_pos = 584
        x_pos = ((692 / 2)+684)

        if 1 <= len(book_name_input) <= 5:
            can.setFont("font1", 80 ) #choose your font type and font size
        elif 6 <= len(book_name_input) <= 12:
            can.setFont("font1", 70 ) #choose your font type and font size
        elif 13 <= len(book_name_input) <= 20:
            can.setFont("font1", 60 ) #choose your font type and font size
        else:
            can.setFont("font1", 50 ) #choose your font type and font size
        can.drawCentredString(x_pos, y_pos, book_name_input)
        can.setFont("font1", 22 )
        month = int(date_input[5:7])
        day = int(date_input[8:10])
        year = int(date_input[0:4])
        dave = date(day=day, month=month, year=year).strftime('%A')
        dave2 = date(day=day, month=month, year=year).strftime('%e')
        dave3 = date(day=day, month=month, year=year).strftime('%B %Y')
        dave2 = ordinal(int(dave2))
        #dave_final = (dave, dave2, dave3)
        dave_123 = " ".join([dave, dave2, dave3])
        can.drawCentredString(1160, 108, dave_123)

        can.save()

        #move to the beginning of the StringIO buffer
        packet.seek(0)
        print('after seeker')
        # create a new PDF with Reportlab
        new_pdf = PdfFileReader(packet)
        # read your existing PDF
        existing_pdf = PdfFileReader('static/media/full_book/front_cover_hard/{0}.pdf'.format(astro_sign), "rb")
        #pdfReader = PyPDF2.PdfFileReader(open('PATH_TO_PDF','rb'))
        output = PdfFileWriter()
        # add the "watermark" (which is the new pdf) on the existing page
        page1 = existing_pdf.getPage(0)
        page1.mergePage(new_pdf.getPage(0))
        #output.addPage(page1)

        end_time1 = (time.time() - start_time)
        print("Page 1 (Front Cover) PDF built in:", end_time1, "Seconds")
        print("Page 1 (Front Cover) - Personalized with an Astrological sign:-",astro_sign)
        print("Page 1 (Front Cover) - Personalized with scaled name:-",book_name_input)

        ##### PAGE 2 BUILDER #####
        start_time = time.time()
        existing_pdf = PdfFileReader(open('static/media/full_book/insert/insert.pdf', "rb"))
        output = PdfFileWriter()
        # add the "watermark" (which is the new pdf) on the existing page
        page2 = existing_pdf.getPage(0)
        end_time2 = (time.time() - start_time)
        print("Page 2 (Inside Front Cover) PDF built in:", end_time2, "Seconds")
        print("Page 2 (Inside Front Cover) No Personalizations")

        ##### PAGE 2.1 BUILDER #####
        #### missing copyright.pdf - needs to be split from the .ai #####
        start_time = time.time()
        existing_pdf = PdfFileReader(open('static/media/full_book/insert/insert.pdf', "rb"))
        output = PdfFileWriter()
        # add the "watermark" (which is the new pdf) on the existing page
        page2_1 = existing_pdf.getPage(0)
        end_time2_1 = (time.time() - start_time)
        print("Page 2 (Inside Front Cover) PDF built in:", end_time2_1, "Seconds")
        print("Page 2 (Inside Front Cover) No Personalizations")


        ######## PAGE 3 BUILDER #########
        # 1264 × 612 Resolution of images
        start_time = time.time()
        text_width = stringWidth(book_name_input, "font1", 24) # Measure the width of the book_name_input variable
        packet = io.BytesIO() # opens reportlab session
        can = canvas.Canvas(packet, pagesize=(661, 661)) # Sets canvas size -> this is incorrect
        can.setFillColorRGB(0,0,0) #choose your font colour
        can.setFont("font1", 24) #choose your font type and font size
        y_pos = 475
        x_pos = (661 / 2)
        #can.drawCentredString(x_pos, y_pos, dedication_name_input)
        #can.save()

        import textwrap
        lines = textwrap.wrap(dedication_name_input, 49, break_long_words=False)

        if 50 <= len(dedication_name_input) <= 100:
            y_pos = 430
            for i in lines:
                y_pos = y_pos - 30
                can.drawCentredString(x_pos, y_pos, i)
                print(lines)
                print(y_pos)
            #wrap_text = textwrap.wrap(dedication_name_input, width=50)
            #can.drawCentredString(x_pos, y_pos-45, wrap_text[0])
            #can.drawCentredString(x_pos, y_pos-75, wrap_text[1])
        elif 100 <= len(dedication_name_input) <= 150:
            y_pos = 445
            for i in lines:
                y_pos = y_pos - 30
                can.drawCentredString(x_pos, y_pos, i)
                print(lines)
                print(y_pos)
            #wrap_text = textwrap.wrap(dedication_name_input, width=50)
            #can.drawCentredString(x_pos, y_pos-30, wrap_text[0])
            #can.drawCentredString(x_pos, y_pos-60, wrap_text[1])
            #can.drawCentredString(x_pos, y_pos-90, wrap_text[2])
        elif 150 <= len(dedication_name_input) <= 200:
            y_pos = 445
            for i in lines:
                y_pos = y_pos - 30
                can.drawCentredString(x_pos, y_pos, i)
                print(lines)
                print(y_pos)
            #wrap_text = textwrap.wrap(dedication_name_input, width=50)
            #can.drawCentredString(x_pos, y_pos, wrap_text[0])
            #can.drawCentredString(x_pos, y_pos-30, wrap_text[1])
            #can.drawCentredString(x_pos, y_pos-60, wrap_text[2])
            #can.drawCentredString(x_pos, y_pos-90, wrap_text[3])
        elif 200 <= len(dedication_name_input) <= 250:
            y_pos = 445
            for i in lines:
                y_pos = y_pos - 30
                can.drawCentredString(x_pos, y_pos, i)
                print(lines)
                print(y_pos)
            #wrap_text = textwrap.wrap(dedication_name_input, width=50)
            #can.drawCentredString(x_pos, y_pos, wrap_text[0])
            #can.drawCentredString(x_pos, y_pos-30, wrap_text[1])
            #can.drawCentredString(x_pos, y_pos-60, wrap_text[2])
            #can.drawCentredString(x_pos, y_pos-90, wrap_text[3])
            #can.drawCentredString(x_pos, y_pos-120, wrap_text[4])
        elif 250 <= len(dedication_name_input) <= 275:
            y_pos = 445
            for i in lines:
                y_pos = y_pos - 30
                can.drawCentredString(x_pos, y_pos, i)
                print(lines)
                print(y_pos)
            #wrap_text = textwrap.wrap(dedication_name_input, width=50)
            #can.drawCentredString(x_pos, y_pos+15, wrap_text[0])
            #can.drawCentredString(x_pos, y_pos-15, wrap_text[1])
            #can.drawCentredString(x_pos, y_pos-45, wrap_text[2])
            #can.drawCentredString(x_pos, y_pos-75, wrap_text[3])
            #can.drawCentredString(x_pos, y_pos-105, wrap_text[4])
            #can.drawCentredString(x_pos, y_pos-135, wrap_text[5])
        else:
            # Handle short dedications (less than 50 characters)
            can.drawCentredString(x_pos, y_pos-60, dedication_name_input)

        can.save()

        #move to the beginning of the StringIO buffer
        packet.seek(0)

        # create a new PDF with Reportlab
        new_pdf = PdfFileReader(packet)
        # read your existing PDF
        existing_pdf = PdfFileReader(open('static/media/full_book/dedication/Dedication.pdf', "rb"))
        #pdfReader = PyPDF2.PdfFileReader(open('PATH_TO_PDF','rb'))
        output = PdfFileWriter()
        # add the "watermark" (which is the new pdf) on the existing page
        page3 = existing_pdf.getPage(0)
        page3.mergePage(new_pdf.getPage(0))

        end_time3 = (time.time() - start_time)
        print("Page 3 (Dedication) PDF built in:", end_time3, "Seconds")
        print("Page 3 (Dedication) Personalized with a dedication:-", dedication_name_input)

        ######## PAGE 4 BUILDER #########
        # 1264 × 612 Resolution of images
        start_time = time.time()
        text_width = stringWidth(book_name_input, "font1", 30) # Measure the width of the book_name_input variable
        packet = io.BytesIO() # opens reportlab session
        can = canvas.Canvas(packet, pagesize=(661, 661)) # Sets canvas size -> this is incorrect
        can.setFillColorRGB(0,0,0) #choose your font colour
        can.setFont("font1", 30) #choose your font type and font size
        y_pos = 445
        x_pos = (661 / 2)+40
        if 1 <= len(book_name_input) <= 5:
            can.setFont("font1", 80 ) #choose your font type and font size
        elif 6 <= len(book_name_input) <= 12:
            can.setFont("font1", 70 ) #choose your font type and font size
        elif 13 <= len(book_name_input) <= 20:
            can.setFont("font1", 60 ) #choose your font type and font size
        else:
            can.setFont("font1", 50 ) #choose your font type and font size
        can.drawCentredString(x_pos, y_pos, book_name_input)
        can.save()

        #move to the beginning of the StringIO buffer
        packet.seek(0)

        # create a new PDF with Reportlab
        new_pdf = PdfFileReader(packet)
        # read your existing PDF
        existing_pdf = PdfFileReader(open('static/media/full_book/p4/p4.pdf', "rb"))
        #pdfReader = PyPDF2.PdfFileReader(open('PATH_TO_PDF','rb'))
        output = PdfFileWriter()
        # add the "watermark" (which is the new pdf) on the existing page
        page4 = existing_pdf.getPage(0)
        page4.mergePage(new_pdf.getPage(0))

        end_time4 = (time.time() - start_time)
        print("Page 4 PDF built in:", end_time4, "Seconds")
        print("Page 4 Personalized with scaled name input:-", book_name_input)

        ######## PAGE 5 BUILDER #########
        # 1264 × 612 Resolution of images
        session_id_django = 'ybb'
        start_time = time.time()
        month = int(date_input[5:7])
        day = int(date_input[8:10])
        year = int(date_input[0:4])
        dave = date(day=day, month=month, year=year).strftime('%A')
        dave2 = date(day=day, month=month, year=year).strftime('%e')
        dave3 = date(day=day, month=month, year=year).strftime('%B %Y')
        dave2 = ordinal(int(dave2))
        #dave_final = (dave, dave2, dave3)
        dave_123 = " ".join([dave, dave2, dave3])
        text_width = stringWidth(dave_123, "font1", 30) # Measure the width of the book_name_input variable
        packet = io.BytesIO() # opens reportlab session
        can = canvas.Canvas(packet, pagesize=(661, 661)) # Sets canvas size -> this is incorrect
        can.setFillColorRGB(0,0,0) #choose your font colour
        can.setFont("font1", 30) #choose your font type and font size
        y_pos = 395
        x_pos = (661 / 2)-45
        can.drawCentredString(x_pos, y_pos, dave_123)
        can.save()

        #move to the beginning of the StringIO buffer
        packet.seek(0)

        # create a new PDF with Reportlab
        new_pdf = PdfFileReader(packet)
        # read your existing PDF
        existing_pdf = PdfFileReader(open('static/media/full_book/p5/p5.pdf', "rb"))
        #pdfReader = PyPDF2.PdfFileReader(open('PATH_TO_PDF','rb'))
        output = PdfFileWriter()
        # add the "watermark" (which is the new pdf) on the existing page
        page5 = existing_pdf.getPage(0)
        page5.mergePage(new_pdf.getPage(0))
        output.addPage(page5)

        end_time5 = (time.time() - start_time)
        print("Page 5 PDF built in:", end_time5, "Seconds")
        print("Page 5 Personalized with formatted date:-", dave_123)

        start_time = time.time()
        existing_pdf = PdfFileReader(open('static/media/full_book/p6/{0}.pdf'.format(astro_sign), "rb"))
        output = PdfFileWriter()
        # add the "watermark" (which is the new pdf) on the existing page
        page6 = existing_pdf.getPage(0)
        end_time6 = (time.time() - start_time)
        print("Page 6 PDF built in:", end_time6, "Seconds")
        print("Page 6 Personalized page selection from astrological lookup:-", astro_sign)

        start_time = time.time()
        existing_pdf = PdfFileReader(open('static/media/full_book/p7/p7.pdf', "rb"))
        output = PdfFileWriter()
        # add the "watermark" (which is the new pdf) on the existing page
        page7 = existing_pdf.getPage(0)
        end_time7 = (time.time() - start_time)
        print("Page 7 built in:", end_time7, "Seconds")
        print("Page 7 No Personalizations")

        start_time = time.time()
        existing_pdf = PdfFileReader(open('static/media/full_book/p8/{0}.pdf'.format(astro_sign), "rb"))
        output = PdfFileWriter()
        # add the "watermark" (which is the new pdf) on the existing page
        page8 = existing_pdf.getPage(0)
        end_time8 = (time.time() - start_time)
        print("Page 8 PDF built in:", end_time8, "Seconds")
        print("Page 8 Personalized page selection from astrological lookup:-", astro_sign)

        start_time = time.time()
        existing_pdf = PdfFileReader(open('static/media/full_book/p9/{0}.pdf'.format(astro_sign), "rb"))
        output = PdfFileWriter()
        # add the "watermark" (which is the new pdf) on the existing page
        page9 = existing_pdf.getPage(0)
        end_time9 = (time.time() - start_time)
        print("Page 9 PDF built in:", end_time9, "Seconds")
        print("Page 9 Personalized page selection from astrological lookup:-", astro_sign)

        start_time = time.time()
        existing_pdf = PdfFileReader(open('static/media/full_book/p10/{0}.pdf'.format(astro_sign), "rb"))
        output = PdfFileWriter()
        # add the "watermark" (which is the new pdf) on the existing page
        page10 = existing_pdf.getPage(0)
        end_time10 = (time.time() - start_time)
        print("Page 10 PDF built in:", end_time10, "Seconds")
        print("Page 10 Personalized page selection from astrological lookup:-", astro_sign)

        start_time = time.time()
        existing_pdf = PdfFileReader(open('static/media/full_book/p11/{0}.pdf'.format(astro_sign), "rb"))
        output = PdfFileWriter()
        # add the "watermark" (which is the new pdf) on the existing page
        page11 = existing_pdf.getPage(0)
        end_time11 = (time.time() - start_time)
        print("Page 11 PDF built in:", end_time11, "Seconds")
        print("Page 11 Personalized page selection from astrological lookup:-", astro_sign)

        ######## PAGE 12 BUILDER #########
        # 1264 × 612 Resolution of images

        start_time = time.time()
        text_width = stringWidth(book_name_input, "font1", 44) # Measure the width of the book_name_input variable
        packet = io.BytesIO() # opens reportlab session
        can = canvas.Canvas(packet, pagesize=(661, 661)) # Sets canvas size -> this is incorrect
        can.rotate(15)
        can.setFillColorRGB(0,0,0) #choose your font colour
        can.setFont("font1", 46) #choose your font type and font size
        y_pos = 205
        x_pos = (661 / 2)+65
        dave1 = date(day=day, month=month, year=year).strftime('%B')
        month = int(date_input[5:7])
        day = int(date_input[8:10])
        dave2 = date(day=day, month=month, year=year).strftime('%e')
        dave3 = date(day=day, month=month, year=year).strftime('%B')
        dave2 = ordinal(int(dave2))
        #dave3 = 'October'
        can.drawCentredString(x_pos+10, y_pos+14, dave3)
        can.setFont("font1", 56) #choose your font type and font size
        can.drawCentredString(x_pos+12, y_pos-60, dave2)
        #can.rotate(45)
        can.save()

        #move to the beginning of the StringIO buffer
        packet.seek(0)

        # create a new PDF with Reportlab
        new_pdf = PdfFileReader(packet)
        # read your existing PDF
        existing_pdf = PdfFileReader(open('static/media/full_book/p12/p12.pdf', "rb"))
        #pdfReader = PyPDF2.PdfFileReader(open('PATH_TO_PDF','rb'))
        output = PdfFileWriter()
        # add the "watermark" (which is the new pdf) on the existing page
        page12 = existing_pdf.getPage(0)
        page12.mergePage(new_pdf.getPage(0))
        #output.addPage(page12)
        end_time12 = (time.time() - start_time)
        print("Page 12 PDF built in:", end_time12, "Seconds")
        print("Page 12 Personalized with formatted date:-", dave3, dave2)

        #### Page 13 Builder ####

        #### Page 13 Atributes Lookup ####

        start_time = time.time()
        month = (date_input[5:7])
        day = (date_input[8:10])
        att_date = ("{}/{}").format(day, month)

        if att_date == '01/01':
            Atribute1 = "You know what you want"
            Atribute2 = "You will work hard to get there"
            Atribute3 = "You like to play by the rules"
        elif att_date == '02/01':
            Atribute1 = "You are a busy bee"
            Atribute2= "You care deeply about your friends"
            Atribute3 = "You are a great negotiator"
        elif att_date == '03/01':
            Atribute1 = "You love to play with your friends"
            Atribute2= "You have loads of good ideas"
            Atribute3 = "You are young at heart"
        elif att_date == '04/01':
            Atribute1 = "You aim for the stars"
            Atribute2= "You are a busy bee"
            Atribute3 = "You love to have fun"
        elif att_date == '05/01':
            Atribute1 = "You are good at lots of things"
            Atribute2= "You have loads of good ideas"
            Atribute3 = "You like to help your friends"
        elif att_date == '06/01':
            Atribute1 = "You are a busy bee"
            Atribute2= "You stick with your friends"
            Atribute3 = "You aim for the stars"
        elif att_date == '07/01':
            Atribute1 = "You have loads of good ideas"
            Atribute2= "You love to play with friends"
            Atribute3 = "You love to draw and paint"
        elif att_date == '08/01':
            Atribute1 = "You like to be number one"
            Atribute2= "You know what you want"
            Atribute3 = "You are a busy bee"
        elif att_date == '09/01':
            Atribute1 = "You like to know what's going on"
            Atribute2= "You stick with your friends"
            Atribute3 = "You aim for the stars"
        elif att_date == '10/01':
            Atribute1 = "You're a busy bee"
            Atribute2= "You like your ducks in a row"
            Atribute3 = "You have loads of good ideas"
        elif att_date == '11/01':
            Atribute1 = "You like to help people"
            Atribute2= "You have loads of good ideas"
            Atribute3= "You love to draw and paint"
        elif att_date == '12/01':
            Atribute1= "You are a charmer"
            Atribute2= "You have loads of good ideas"
            Atribute3= "You are an original thinker"
        elif att_date == '13/01':
            Atribute1= "You are always on the go"
            Atribute2= "You know what you want"
            Atribute3= "You are very smart"
        elif att_date == '14/01':
            Atribute1= "You like to be number one"
            Atribute2= "You are very smart"
            Atribute3= "You like to chat with your friends"
        elif att_date == '15/01':
            Atribute1= "You'll stick to your goals"
            Atribute2= "You love to draw and paint"
            Atribute3 = "You like to be number one"
        elif att_date == '16/01':
            Atribute1 = "You care deeply about your friends"
            Atribute2 = "You love to play with friends"
            Atribute3 = "You're very smart"
        elif att_date == '17/01':
            Atribute1 = "You are a busy bee"
            Atribute2 = "You like to be number one"
            Atribute3 = "You know what you want"
        elif att_date == '18/01':
            Atribute1 = "You are a busy bee"
            Atribute2 = "You are full of new ideas"
            Atribute3 = "You are very kind"
        elif att_date == '19/01':
            Atribute1 = "You are an original thinker"
            Atribute2 = "You are full of fun"
            Atribute3 = "You like to be number one"
        elif att_date == '20/01':
            Atribute1 = "You are an original thinker"
            Atribute2 = "You are a busy bee"
            Atribute3 = "You love playing with your friends"
        elif att_date == '21/01':
            Atribute1 = "You love to chat with your friends"
            Atribute2 = "You like to act"
            Atribute3 = "You love to have fun"
        elif att_date == '22/01':
            Atribute1 = "You are smart"
            Atribute2 = "You love an adventure"
            Atribute3 = "You like to do it your way"
        elif att_date == '23/01':
            Atribute1 = "You are one-of-a-kind"
            Atribute2 = "You always find the answer"
            Atribute3 = "You are an original thinker"
        elif att_date == '24/01':
            Atribute1 = "You are a charmer"
            Atribute2 = "You are a busy bee"
            Atribute3 = "You love to have fun"
        elif att_date == '25/01':
            Atribute1 = "You are a charmer"
            Atribute2 = "You are an original thinker"
            Atribute3 = "You have a great imagination"
        elif att_date == '26/01':
            Atribute1 = "You are a busy bee"
            Atribute2 = "You like to make new friends"
            Atribute3 = "You love playing with your friends"
        elif att_date == '27/01':
            Atribute1 = "You are a busy bee"
            Atribute2 = "You make lots of friends"
            Atribute3 = "You like new ideas"
        elif att_date == '28/01':
            Atribute1 = "You love an adventure"
            Atribute2 = "You like to be number one"
            Atribute3 = "You are an original thinker"
        elif att_date == '29/01':
            Atribute1 = "You are quite brilliant"
            Atribute2 = "You like chatting with your friends"
            Atribute3 = "You are a charmer"
        elif att_date == '30/01':
            Atribute1 = "You are a natural born leader"
            Atribute2 = "You have big ideas"
            Atribute3 = "You are a charmer"
        elif att_date == '31/01':
            Atribute1 = "You're a busy bee"
            Atribute2 = "You are very smart"
            Atribute3 = "You are a charmer"
        elif att_date == '01/02':
            Atribute1 = "You have loads of good ideas"
            Atribute2 = "You say what you're thinking"
            Atribute3 = "You're a busy bee"
        elif att_date == '02/02':
            Atribute1 = "You love to help out"
            Atribute2 = "You're very imaginative"
            Atribute3 = "You stick with it"
        elif att_date == '03/02':
            Atribute1 = "You have loads of good ideas"
            Atribute2 = "You like to chat with your friends"
            Atribute3 = "You are generous and kind"
        elif att_date == '04/02':
            Atribute1 = "You're a busy bee"
            Atribute2 = "Your friends can count on you"
            Atribute3 = "You love an adventure"
        elif att_date == '05/02':
            Atribute1 = "You are full of energy"
            Atribute2 = "You love to run around and play games"
            Atribute3 = "You love to learn"
        elif att_date == '06/02':
            Atribute1 = "You are fun loving"
            Atribute2 = "You like playing with your friends"
            Atribute3 = "You love new ideas"
        elif att_date == '07/02':
            Atribute1 = "You love to help out"
            Atribute2 = "You enjoy an adventure"
            Atribute3 = "You are gentle hearted"
        elif att_date == '08/02':
            Atribute1 = "You're a busy bee"
            Atribute2 = "You care about everyone"
            Atribute3 = "You are very strong hearted"
        elif att_date == '09/02':
            Atribute1 = "You stick with it"
            Atribute2 = "You love to shake things up"
            Atribute3 = "You have lots of friends"
        elif att_date == '10/02':
            Atribute1 = "Your friends are important to you"
            Atribute2 = "You like to take the lead"
            Atribute3 = "You are full of good ideas"
        elif att_date == '11/02':
            Atribute1 = "You know what you want"
            Atribute2 = "You have a lovely personality"
            Atribute3 = "You love to draw and paint"
        elif att_date == '12/02':
            Atribute1 = "You love to make new friends"
            Atribute2 = "You love to laugh"
            Atribute3 = "You're a natural born leader"
        elif att_date == '13/02':
            Atribute1 = "You are a busy bee"
            Atribute2 = "You work hard"
            Atribute3 = "You are super focussed"
        elif att_date == '14/02':
            Atribute1 = "You love to play with your friends"
            Atribute2 = "You have big ideas"
            Atribute3 = "You are spirited and playful"
        elif att_date == '15/02':
            Atribute1 = "You love to make new friends"
            Atribute2 = "You love writing, drawing and painting"
            Atribute3 = "You are bright and cheerful"
        elif att_date == '16/02':
            Atribute1 = "You love a good mystery"
            Atribute2 = "You are fast on your feet"
            Atribute3 = "You have great imagination"
        elif att_date == '17/02':
            Atribute1 = "You are a busy bee"
            Atribute2 = "You stick with it"
            Atribute3 = "You love competitions"
        elif att_date == '18/02':
            Atribute1 = "You stand out in a crowd"
            Atribute2 = "You are a reformer"
            Atribute3 = "You care about everyone"
        elif att_date == '19/02':
            Atribute1 = "You are a charmer"
            Atribute2 = "You aim for the stars"
            Atribute3 = "You are very artistic"
        elif att_date == '20/02':
            Atribute1 = "You are a born diplomat"
            Atribute2 = "You love to help out"
            Atribute3 = "Your friends can count on you"
        elif att_date == '21/02':
            Atribute1 = "You get along with everyone"
            Atribute2 = "You love to laugh"
            Atribute3 = "You are a charmer"
        elif att_date == '22/02':
            Atribute1 = "You have loads of good ideas"
            Atribute2 = "You are very artistic"
            Atribute3 = "You will make your mark in the world"
        elif att_date == '23/02':
            Atribute1 = "You love to chat with your friends"
            Atribute2 = "You are a good listener"
            Atribute3 = "You are very artistic"
        elif att_date == '24/02':
            Atribute1 = "You love to chat with your friends"
            Atribute2 = "Your friends can count on you"
            Atribute3 = "You are a charmer"
        elif att_date == '25/02':
            Atribute1 = "You are wise beyond your years"
            Atribute2 = "You like to chat with your friends"
            Atribute3 = "You are quite brilliant"
        elif att_date == '26/02':
            Atribute1 = "You are a busy bee"
            Atribute2 = "You love to laugh"
            Atribute3 = "You care about everyone"
        elif att_date == '27/02':
            Atribute1 = "You are a charmer"
            Atribute2 = "You have a vivid imagination"
            Atribute3 = "You are very artistic"
        elif att_date == '28/02':
            Atribute1 = "You are a born leader"
            Atribute2 = "You like to learn new things"
            Atribute3 = "You love to make things right"
        elif att_date == '29/02':
            Atribute1 = "You are a born diplomat"
            Atribute2 = "You are very artistic"
            Atribute3 = "You are great at making new friends"
        elif att_date == '01/03':
            Atribute1 = "You are a busy bee"
            Atribute2 = "You love exciting new ideas"
            Atribute3 = "You care about everyone"
        elif att_date == '02/03':
            Atribute1 = "You are a busy bee"
            Atribute2 = "You are very loving"
            Atribute3 = "You are a people person"
        elif att_date == '03/03':
            Atribute1 = "You have a twinkle in your eye"
            Atribute2 = "You are no pushover"
            Atribute3 = "You are quick and sharp minded"
        elif att_date == '04/03':
            Atribute1 = "You are a busy bee"
            Atribute2 = "You are very smart"
            Atribute3 = "You love to draw and paint"
        elif att_date == '05/03':
            Atribute1 = "You love an adventure"
            Atribute2 = "You love to chat and laugh with friends"
            Atribute3 = "You are a busy bee"
        elif att_date == '06/03':
            Atribute1 = "You are a busy bee"
            Atribute2 = "You love have your friends around"
            Atribute3 = "You have a magnetic personality"
        elif att_date == '07/03':
            Atribute1 = "You have a vivid imagination"
            Atribute2 = "You are very smart"
            Atribute3 = "You are an artist at heart"
        elif att_date == '08/03':
            Atribute1 = "You are a busy bee"
            Atribute2 = "You have a vivid imagination"
            Atribute3 = "You love a challenge"
        elif att_date == '09/03':
            Atribute1 = "You care deeply about your friends"
            Atribute2 = "You have a vivid imagination"
            Atribute3 = "You are curious about the world"
        elif att_date == '10/03':
            Atribute1 = "You love to be in the spot light"
            Atribute2 = "You are a natural born leader"
            Atribute3 = "You're full of good ideas"
        elif att_date == '11/03':
            Atribute1 = "You were born wise"
            Atribute2 = "You are a busy bee"
            Atribute3 = "You care about everyone"
        elif att_date == '12/03':
            Atribute1 = "You are a great friend"
            Atribute2 = "You have an easygoing personality"
            Atribute3 = "You are naturally tallented"
        elif att_date == '13/03':
            Atribute1 = "You have a sunny smile"
            Atribute2 = "You have a magnetic personality"
            Atribute3 = "You are a busy bee"
        elif att_date == '14/03':
            Atribute1 = "You are a creative visionary"
            Atribute2 = "You have an open mind"
            Atribute3 = "You are ready for anything"
        elif att_date == '15/03':
            Atribute1 = "You have a magnetic personality"
            Atribute2 = "You have inner strength"
            Atribute3 = "You love to draw and paint"
        elif att_date == '16/03':
            Atribute1 = "You are smart and creative"
            Atribute2 = "You are wise"
            Atribute3 = "You are a charmer"
        elif att_date == '17/03':
            Atribute1 = "You are a busy bee"
            Atribute2 = "You have a vivid imagination"
            Atribute3 = "You are a loyal friend"
        elif att_date == '18/03':
            Atribute1 = "You are a dreamer and visionary"
            Atribute2 = "You have a vivid imagination"
            Atribute3 = "You have an original sense of humour"
        elif att_date == '19/03':
            Atribute1 = "You are a charmer"
            Atribute2 = "You have an original sense of humour"
            Atribute3 = "You have a vivid imagination"
        elif att_date == '20/03':
            Atribute1 = "You love to draw and paint"
            Atribute2 = "You have unique talents and abilities"
            Atribute3 = "You are a team player"
        elif att_date == '21/03':
            Atribute1 = "You will give anything a go"
            Atribute2 = "You are a charmer"
            Atribute3 = "Your life is one big adventure"
        elif att_date == '22/03':
            Atribute1 = "You are a busy bee"
            Atribute2 = "You are fearless"
            Atribute3 = "You love to explore"
        elif att_date == '23/03':
            Atribute1 = "You are a busy bee"
            Atribute2 = "You are a thinker and a doer"
            Atribute3 = "You have lots of friends"
        elif att_date == '24/03':
            Atribute1 = "You have a magnetic personality"
            Atribute2 = "You are a charmer"
            Atribute3 = "You love to have your friends over"
        elif att_date == '25/03':
            Atribute1 = "You have a magnetic personality"
            Atribute2 = "You are multi talented"
            Atribute3 = "You learn as you go along"
        elif att_date == '26/03':
            Atribute1 = "You are full of energy"
            Atribute2 = "You like to be inspired"
            Atribute3 = "You stick with it"
        elif att_date == '27/03':
            Atribute1 = "You are a go-getter"
            Atribute2 = "You are not afraid of anything"
            Atribute3 = "You are full of good ideas"
        elif att_date == '28/03':
            Atribute1 = "You are a born leader"
            Atribute2 = "You stick with it"
            Atribute3 = "You have a sunny personality"
        elif att_date == '29/03':
            Atribute1 = "You are very loving"
            Atribute2 = "You are couragous and brave"
            Atribute3 = "You are a team player"
        elif att_date == '30/03':
            Atribute1 = "You are a charmer"
            Atribute2 = "You look after your friends"
            Atribute3 = "You have a magnetic personality"
        elif att_date == '31/03':
            Atribute1 = "You are a creative visionary"
            Atribute2 = "You are a born leader"
            Atribute3 = "You love an adventure"
        elif att_date == '01/04':
            Atribute1 = "You love an adventure"
            Atribute2 = "You are a go-getter"
            Atribute3 = "You are not afraid of anything"
        elif att_date == '02/04':
            Atribute1 = "You have unique talents and abilities"
            Atribute2 = "You are a busy bee"
            Atribute3 = "You love an adventure"
        elif att_date == '03/04':
            Atribute1 = "You love exciting new ideas"
            Atribute2 = "You love an adventure"
            Atribute3 = "You are a born diplomat"
        elif att_date == '04/04':
            Atribute1 = "You are a charmer"
            Atribute2 = "You are a go-getter"
            Atribute3 = "You are a busy bee"
        elif att_date == '05/04':
            Atribute1 = "You say it like it is"
            Atribute2 = "You have star quality"
            Atribute3 = "You are a free spirit"
        elif att_date == '06/04':
            Atribute1 = "You are a charmer"
            Atribute2 = "Your friends can count on you"
            Atribute3 = "You are born to lead"
        elif att_date == '07/04':
            Atribute1 = "You are a go-getter"
            Atribute2 = "You are smart and creative"
            Atribute3 = "You are an inspiration to your friends"
        elif att_date == '08/04':
            Atribute1 = "You are a go-getter"
            Atribute2 = "You are a true pioneer"
            Atribute3 = "You are a busy bee"
        elif att_date == '09/04':
            Atribute1 = "You are a poet"
            Atribute2 = "You are a true pioneer"
            Atribute3 = "You stick with it"
        elif att_date == '10/04':
            Atribute1 = "You have a sunny smile"
            Atribute2 = "You love spending time with friends"
            Atribute3 = "You make good choices"
        elif att_date == '11/04':
            Atribute1 = "You have a good heart"
            Atribute2 = "Your friends can count on you"
            Atribute3 = "You brim with enthusiasm"
        elif att_date == '12/04':
            Atribute1 = "You have a sunny nature"
            Atribute2 = "You are fun-loving"
            Atribute3 = "You are a born entertainer"
        elif att_date == '13/04':
            Atribute1 = "You are a busy bee"
            Atribute2 = "You are a natural born leader"
            Atribute3 = "You stick with it"
        elif att_date == '14/04':
            Atribute1 = "You are a busy bee"
            Atribute2 = "You are very smart"
            Atribute3 = "You are a go-getter"
        elif att_date == '15/04':
            Atribute1 = "You are a people person"
            Atribute2 = "You are always fair"
            Atribute3 = "You are a charmer"
        elif att_date == '16/04':
            Atribute1 = "You are a born diplomat"
            Atribute2 = "You are not afraid of anything"
            Atribute3 = "You have unique talents and abilities"
        elif att_date == '17/04':
            Atribute1 = "You stick with it"
            Atribute2 = "You are very smart"
            Atribute3 = "You are poised for success"
        elif att_date == '18/04':
            Atribute1 = "You will fight for what you believe"
            Atribute2 = "You love spending time with friends"
            Atribute3 = "You are creative, capable and hard working"
        elif att_date == '19/04':
            Atribute1 = "You are a busy bee"
            Atribute2 = "You are a charmer"
            Atribute3 = "You are an ideas person"
        elif att_date == '20/04':
            Atribute1 = "You know what you want"
            Atribute2 = "You will work hard to get there"
            Atribute3 = "You are not afraid of anything"
        elif att_date == '21/04':
            Atribute1 = "You are a born leader"
            Atribute2 = "You are a charmer"
            Atribute3 = "You like to explore"
        elif att_date == '22/04':
            Atribute1 = "You know what you want"
            Atribute2 = "You will work hard to get there"
            Atribute3 = "You are a charmer"
        elif att_date == '23/04':
            Atribute1 = "You are very smart"
            Atribute2 = "You have unique talents and abilities"
            Atribute3 = "You have a vivid imagination"
        elif att_date == '24/04':
            Atribute1 = "You like the good life"
            Atribute2 = "You love spending time with your family"
            Atribute3 = "You are creative, capable and hard working"
        elif att_date == '25/04':
            Atribute1 = "You are ready for a challenge"
            Atribute2 = "You are a charmer"
            Atribute3 = "You love the journey"
        elif att_date == '26/04':
            Atribute1 = "You are a charmer"
            Atribute2 = "You stick with it"
            Atribute3 = "You are one of life's problem solvers"
        elif att_date == '27/04':
            Atribute1 = "You look after your friends"
            Atribute2 = "You love action"
            Atribute3 = "You are a charmer"
        elif att_date == '28/04':
            Atribute1 = "You are a go-getter"
            Atribute2 = "You look after your friends"
            Atribute3 = "You are a natural leader"
        elif att_date == '29/04':
            Atribute1 = "You are ready for a challenge"
            Atribute2 = "You are a creative visionary"
            Atribute3 = "You love spending time with friends"
        elif att_date == '30/04':
            Atribute1 = "You are a charmer"
            Atribute2 = "You love spending time with friends"
            Atribute3 = "You stick with it"
        elif att_date == '01/05':
            Atribute1 = "You seize every opportunity"
            Atribute2 = "You stick with it"
            Atribute3 = "You have bags of energy"
        elif att_date == '02/05':
            Atribute1 = "You are a busy bee"
            Atribute2 = "You set your sights high"
            Atribute3 = "You are a problem solver"
        elif att_date == '03/05':
            Atribute1 = "You are a charmer"
            Atribute2 = "You love to nurture"
            Atribute3 = "You are multi-talented"
        elif att_date == '04/05':
            Atribute1 = "You are a people person"
            Atribute2 = "You know what you want"
            Atribute3 = "You work hard to achieve your goals"
        elif att_date == '05/05':
            Atribute1 = "You are one-of-a-kind"
            Atribute2 = "You care about everyone"
            Atribute3 = "You are a great listener"
        elif att_date == '06/05':
            Atribute1 = "You are a people person"
            Atribute2 = "You love spending time with friends"
            Atribute3 = "You are good with money"
        elif att_date == '07/05':
            Atribute1 = "You are a charmer"
            Atribute2 = "You have a creative imagination"
            Atribute3 = "You are wise"
        elif att_date == '08/05':
            Atribute1 = "You are playful"
            Atribute2 = "You have a great sense of humour"
            Atribute3 = "You have a unique perspective"
        elif att_date == '09/05':
            Atribute1 = "You love to invent"
            Atribute2 = "You look after your friends"
            Atribute3 = "You are courageous"
        elif att_date == '10/05':
            Atribute1 = "You are a go-getter"
            Atribute2 = "You look after your friends"
            Atribute3 = "You are a self-starter"
        elif att_date == '11/05':
            Atribute1 = "You are a busy bee"
            Atribute2 = "You are a charmer"
            Atribute3 = "You are multi-talented"
        elif att_date == '12/05':
            Atribute1 = "You are a charmer"
            Atribute2 = "You look after your friends"
            Atribute3 = "You have a great sense of humour"
        elif att_date == '13/05':
            Atribute1 = "You are sweet natured"
            Atribute2 = "You love art and music"
            Atribute3 = "You are a busy bee"
        elif att_date == '14/05':
            Atribute1 = "You are very creative"
            Atribute2 = "You are very smart"
            Atribute3 = "You are an ideas person"
        elif att_date == '15/05':
            Atribute1 = "You are a busy bee"
            Atribute2 = "You are a charmer"
            Atribute3 = "You love spending time with friends"
        elif att_date == '16/05':
            Atribute1 = "You are very smart and honourable"
            Atribute2 = "You have an inquiring mind"
            Atribute3 = "You have a love of music"
        elif att_date == '17/05':
            Atribute1 = "You are a charmer"
            Atribute2 = "You have a winning personality"
            Atribute3 = "You are a self-starter"
        elif att_date == '18/05':
            Atribute1 = "You are very smart"
            Atribute2 = "You understand people"
            Atribute3 = "You have a great imagination"
        elif att_date == '19/05':
            Atribute1 = "You are very smart"
            Atribute2 = "You look after your friends"
            Atribute3 = "You are a born leader"
        elif att_date == '20/05':
            Atribute1 = "You are a charmer"
            Atribute2 = "You have a winning personality"
            Atribute3 = "You have a creative imagination"
        elif att_date == '21/05':
            Atribute1 = "You are a busy bee"
            Atribute2 = "You love adventure"
            Atribute3 = "You fit in anywhere"
        elif att_date == '22/05':
            Atribute1 = "You are quick-witted"
            Atribute2 = "You are a born leader"
            Atribute3 = "You are a busy bee"
        elif att_date == '23/05':
            Atribute1 = "You are quick-witted"
            Atribute2 = "You are an original thinker"
            Atribute3 = "You are one step ahead"
        elif att_date == '24/05':
            Atribute1 = "You are a charmer"
            Atribute2 = "You love parties"
            Atribute3 = "You love to laugh"
        elif att_date == '25/05':
            Atribute1 = "You love the arts"
            Atribute2 = "You love to laugh"
            Atribute3 = "You have a creative imagination"
        elif att_date == '26/05':
            Atribute1 = "You are a busy bee"
            Atribute2 = "You are quick-witted"
            Atribute3 = "You love to run the show"
        elif att_date == '27/05':
            Atribute1 = "You love an adventure"
            Atribute2 = "You are a charmer"
            Atribute3 = "You love to laugh"
        elif att_date == '28/05':
            Atribute1 = "You love excitement"
            Atribute2 = "You love to travel"
            Atribute3 = "You are fun to be with"
        elif att_date == '29/05':
            Atribute1 = "You have a magnetic personality"
            Atribute2 = "You have lots of friends"
            Atribute3 = "You love to chat with your friends"
        elif att_date == '30/05':
            Atribute1 = "You are a people person"
            Atribute2 = "You love to laugh"
            Atribute3 = "You are a whirlwind"
        elif att_date == '31/05':
            Atribute1 = "You are super smart"
            Atribute2 = "You are very creative"
            Atribute3 = "You are entertaining"
        elif att_date == '01/06':
            Atribute1 = "You have a quick wit"
            Atribute2 = "You love exciting new ideas"
            Atribute3 = "You are clever and persuasive"
        elif att_date == '02/06':
            Atribute1 = "You are a charmer"
            Atribute2 = "You are very smart"
            Atribute3 = "You are a born diplomat"
        elif att_date == '03/06':
            Atribute1 = "Your friends love to be with you"
            Atribute2 = "You are a busy bee"
            Atribute3 = "You are always in a hurry"
        elif att_date == '04/06':
            Atribute1 = "You know what you want"
            Atribute2 = "You are an ideas person"
            Atribute3 = "You are a born diplomat"
        elif att_date == '05/06':
            Atribute1 = "You are quick-witted"
            Atribute2 = "You are full of curiosity"
            Atribute3 = "You love to chat with your friends"
        elif att_date == '06/06':
            Atribute1 = "You are a charmer"
            Atribute2 = "You are a born peace maker"
            Atribute3 = "You have a magnetic personality"
        elif att_date == '07/06':
            Atribute1 = "You make your own luck"
            Atribute2 = "You love to make new friends"
            Atribute3 = "You have a sparkling personality"
        elif att_date == '08/06':
            Atribute1 = "You are a busy bee"
            Atribute2 = "You love to make new friends"
            Atribute3 = "You love a challenge"
        elif att_date == '09/06':
            Atribute1 = "You have a magnetic personality"
            Atribute2 = "You know what you want"
            Atribute3 = "You absorb knowledge"
        elif att_date == '10/06':
            Atribute1 = "You are full of bright ideas"
            Atribute2 = "You are a charmer"
            Atribute3 = "You love to make new friends"
        elif att_date == '11/06':
            Atribute1 = "You are very smart"
            Atribute2 = "You are an inspired thinker"
            Atribute3 = "You are a pioneer"
        elif att_date == '12/06':
            Atribute1 = "You are always on the go"
            Atribute2 = "You shoot for the stars"
            Atribute3 = "You love to make new friends"
        elif att_date == '13/06':
            Atribute1 = "You are a busy bee"
            Atribute2 = "You have a creative imagination"
            Atribute3 = "You are a born diplomat"
        elif att_date == '14/06':
            Atribute1 = "You are quick-witted"
            Atribute2 = "You love an adventure"
            Atribute3 = "You are a born leader"
        elif att_date == '15/06':
            Atribute1 = "You love to spend time with friends"
            Atribute2 = "You are a charmer"
            Atribute3 = "You are quick-witted"
        elif att_date == '16/06':
            Atribute1 = "You have a creative imagination"
            Atribute2 = "You care about everyone"
            Atribute3 = "You are an inspired thinker"
        elif att_date == '17/06':
            Atribute1 = "You are wise beyond your years"
            Atribute2 = "You love exciting new ideas"
            Atribute3 = "You have lots of friends"
        elif att_date == '18/06':
            Atribute1 = "You have lots of friends"
            Atribute2 = "You are very smart"
            Atribute3 = "You are quick-witted"
        elif att_date == '19/06':
            Atribute1 = "You are mischievous and playful"
            Atribute2 = "You have great enthusiasm"
            Atribute3 = "You are fun to be with"
        elif att_date == '20/06':
            Atribute1 = "You are a charmer"
            Atribute2 = "You have strong self-belief"
            Atribute3 = "You have lots of friends"
        elif att_date == '21/06':
            Atribute1 = "You are quick-witted"
            Atribute2 = "You have a vivid imagination"
            Atribute3 = "You are very creative"
        elif att_date == '22/06':
            Atribute1 = "You are a charmer"
            Atribute2 = "You are devoted to family and friends"
            Atribute3 = "You have a great sense of humour"
        elif att_date == '23/06':
            Atribute1 = "You are a visionary"
            Atribute2 = "You are an inspired thinker"
            Atribute3 = "You care about everyone"
        elif att_date == '24/06':
            Atribute1 = "You are a busy bee"
            Atribute2 = "You are a home-body"
            Atribute3 = "You are devoted to family and friends"
        elif att_date == '25/06':
            Atribute1 = "You love a good mystery"
            Atribute2 = "You are very honest"
            Atribute3 = "You love to help your friends"
        elif att_date == '26/06':
            Atribute1 = "You love to organise"
            Atribute2 = "You are a forward thinker"
            Atribute3 = "You are a busy bee"
        elif att_date == '27/06':
            Atribute1 = "You love to chat with your friends"
            Atribute2 = "You have lots of good ideas"
            Atribute3 = "You love to help your friends"
        elif att_date == '28/06':
            Atribute1 = "You have a great sense of fun"
            Atribute2 = "You have a creative imagination"
            Atribute3 = "You are a busy bee"
        elif att_date == '29/06':
            Atribute1 = "You are devoted to family and friends"
            Atribute2 = "You love an adventure"
            Atribute3 = "You are a busy bee"
        elif att_date == '30/06':
            Atribute1 = "You are quick-witted"
            Atribute2 = "You have lots of good ideas"
            Atribute3 = "You have a great memory"
        elif att_date == '01/07':
            Atribute1 = "You are an adventurer"
            Atribute2 = "You are an inspired thinker"
            Atribute3 = "You are devoted to family and friends"
        elif att_date == '02/07':
            Atribute1 = "You are a busy bee'"
            Atribute2 = "You are warm and gracious"
            Atribute3 = "You are devoted to family and friends"
        elif att_date == '03/07':
            Atribute1 = "You are a busy bee"
            Atribute2 = "You love to learn"
            Atribute3 = "You are charismatic"
        elif att_date == '04/07':
            Atribute1 = "You are a busy bee"
            Atribute2 = "You know what you want"
            Atribute3 = "You are wise beyond your years"
        elif att_date == '05/07':
            Atribute1 = "You are a busy bee"
            Atribute2 = "You are a forward thinker"
            Atribute3 = "You have an enquiring mind"
        elif att_date == '06/07':
            Atribute1 = "You are devoted to family and friends"
            Atribute2 = "You have an easy going charm"
            Atribute3 = "You have a creative imagination"
        elif att_date == '07/07':
            Atribute1 = "You have a creative imagination"
            Atribute2 = "You love a good mystery"
            Atribute3 = "You enjoy taking the lead"
        elif att_date == '08/07':
            Atribute1 = "You have a unique creativity"
            Atribute2 = "You know what you want"
            Atribute3 = "You work hard to achieve your goals"
        elif att_date == '09/07':
            Atribute1 = "You are a forward thinker"
            Atribute2 = "You make lots of friends"
            Atribute3 = "You work well under pressure"
        elif att_date == '10/07':
            Atribute1 = "You are quick-witted"
            Atribute2 = "You have a creative imagination"
            Atribute3 = "You are a born explorer"
        elif att_date == '11/07':
            Atribute1 = "You are a busy bee"
            Atribute2 = "You have a unique creativity"
            Atribute3 = "You love to help your friends"
        elif att_date == '12/07':
            Atribute1 = "You are quick-witted"
            Atribute2 = "You have a way with words"
            Atribute3 = "You love to laugh"
        elif att_date == '13/07':
            Atribute1 = "You are a busy bee"
            Atribute2 = "You are devoted to family and friends"
            Atribute3 = "You have a quirky sense of humour"
        elif att_date == '14/07':
            Atribute1 = "You are a busy bee"
            Atribute2 = "You love to travel"
            Atribute3 = "You work hard to achieve your goals"
        elif att_date == '15/07':
            Atribute1 = "You are a charmer"
            Atribute2 = "You are devoted to family and friends"
            Atribute3 = "You are a busy bee"
        elif att_date == '16/07':
            Atribute1 = "You have a creative imagination"
            Atribute2 = "You love to learn"
            Atribute3 = "You are wise beyond your years"
        elif att_date == '17/07':
            Atribute1 = "You are determined to succeed"
            Atribute2 = "You are quick-witted"
            Atribute3 = "You love to laugh"
        elif att_date == '18/07':
            Atribute1 = "You are a born diplomat"
            Atribute2 = "You are a forward thinker"
            Atribute3 = "You are open to new ideas"
        elif att_date == '19/07':
            Atribute1 = "You have a quirky sense of humour"
            Atribute2 = "You are worldly-wise"
            Atribute3 = "You are a great motivator"
        elif att_date == '20/07':
            Atribute1 = "You are a born diplomat"
            Atribute2 = "You are devoted to family and friends"
            Atribute3 = "You stick with it"
        elif att_date == '21/07':
            Atribute1 = "You have a way with words"
            Atribute2 = "You have a unique creativity"
            Atribute3 = "You are very smart"
        elif att_date == '22/07':
            Atribute1 = "You have a unique creativity"
            Atribute2 = "You believe in yourself"
            Atribute3 = "You have a sunny personality"
        elif att_date == '23/07':
            Atribute1 = "You have a sunny personality"
            Atribute2 = "You are naturally curious"
            Atribute3 = "You love adventure"
        elif att_date == '24/07':
            Atribute1 = "You are a natural born leader"
            Atribute2 = "You love exciting new ideas"
            Atribute3 = "You are a charmer"
        elif att_date == '25/07':
            Atribute1 = "You are full of fun"
            Atribute2 = "You love to help your friends"
            Atribute3 = "You have a creative imagination"
        elif att_date == '26/07':
            Atribute1 = "You have a magnetic personality"
            Atribute2 = "You believe in yourself"
            Atribute3 = "You love to chat with your friends"
        elif att_date == '27/07':
            Atribute1 = "You are a natural born leader"
            Atribute2 = "You believe in yourself"
            Atribute3 = "You are devoted to family and friends"
        elif att_date == '28/07':
            Atribute1 = "You love adventure"
            Atribute2 = "You have boundless energy"
            Atribute3 = "You are a natural born leader"
        elif att_date == '29/07':
            Atribute1 = "You have a magnetic personality"
            Atribute2 = "You are a natural born leader"
            Atribute3 = "You are a born diplomat"
        elif att_date == '30/07':
            Atribute1 = "You are fun loving"
            Atribute2 = "You have lots of friends"
            Atribute3 = "You are a forward thinker"
        elif att_date == '31/07':
            Atribute1 = "You know what you want"
            Atribute2 = "You are a natural born leader"
            Atribute3 = "You have a creative imagination"
        elif att_date == '01/08':
            Atribute1 = "You are a natural born leader"
            Atribute2 = "You have a sunny optimism"
            Atribute3 = "You stick with it"
        elif att_date == '02/08':
            Atribute1 = "You are a charmer"
            Atribute2 = "You are quick-witted"
            Atribute3 = "You are devoted to family and friends"
        elif att_date == '03/08':
            Atribute1 = "You are very smart"
            Atribute2 = "You love to play with friends"
            Atribute3 = "You are a born diplomat"
        elif att_date == '04/08':
            Atribute1 = "You are playful"
            Atribute2 = "You know what you want"
            Atribute3 = "You are a forward thinker"
        elif att_date == '05/08':
            Atribute1 = "You are a busy bee"
            Atribute2 = "You are a natural born leader"
            Atribute3 = "You think outside the box"
        elif att_date == '06/08':
            Atribute1 = "You are a natural diplomat"
            Atribute2 = "You are devoted to family and friends"
            Atribute3 = "You have a creative imagination"
        elif att_date == '07/08':
            Atribute1 = "You are a forward thinker"
            Atribute2 = "You have a creative imagination"
            Atribute3 = "You have lots of friends"
        elif att_date == '08/08':
            Atribute1 = "You are a busy bee"
            Atribute2 = "You know what you want"
            Atribute3 = "You work hard to be number one"
        elif att_date == '09/08':
            Atribute1 = "You are a busy bee"
            Atribute2 = "You are a natural born leader"
            Atribute3 = "You have lots of friends"
        elif att_date == '10/08':
            Atribute1 = "You are a natural born leader"
            Atribute2 = "You are a charmer"
            Atribute3 = "You love adventure"
        elif att_date == '11/08':
            Atribute1 = "You have lots of friends"
            Atribute2 = "You are unstoppable"
            Atribute3 = "You have a creative imagination"
        elif att_date == '12/08':
            Atribute1 = "You are quick-witted"
            Atribute2 = "You are a busy bee"
            Atribute3 = "You are a multi-tasker"
        elif att_date == '13/08':
            Atribute1 = "You are very smart"
            Atribute2 = "You are a natural born leader"
            Atribute3 = "You have a creative imagination"
        elif att_date == '14/08':
            Atribute1 = "You have a sunny personality"
            Atribute2 = "You have a zest for life"
            Atribute3 = "You have lots of friends"
        elif att_date == '15/08':
            Atribute1 = "You are devoted to family and friends"
            Atribute2 = "You love to solve problems"
            Atribute3 = "You have a creative imagination"
        elif att_date == '16/08':
            Atribute1 = "You are very smart"
            Atribute2 = "You are a forward thinker"
            Atribute3 = "You have a creative imagination"
        elif att_date == '17/08':
            Atribute1 = "You know what you want"
            Atribute2 = "You are a forward thinker"
            Atribute3 = "You are generous and loving"
        elif att_date == '18/08':
            Atribute1 = "You are a natural born leader"
            Atribute2 = "You have a unique creativity"
            Atribute3 = "You have a brave heart"
        elif att_date == '19/08':
            Atribute1 = "You love excitement"
            Atribute2 = "You will try anything"
            Atribute3 = "You are a natural born leader"
        elif att_date == '20/08':
            Atribute1 = "You are a busy bee"
            Atribute2 = "You are a natural diplomat"
            Atribute3 = "You love to chat with your friends"
        elif att_date == '21/08':
            Atribute1 = "You have a creative imagination"
            Atribute2 = "You love a challenge"
            Atribute3 = "You love to help your friends"
        elif att_date == '22/08':
            Atribute1 = "You are a multi-tasker"
            Atribute2 = "You are open to new ideas"
            Atribute3 = "You have bags of common sense"
        elif att_date == '23/08':
            Atribute1 = "You are quick-witted"
            Atribute2 = "You are full of fun"
            Atribute3 = "You have a unique creativity"
        elif att_date == '24/08':
            Atribute1 = "You are very smart"
            Atribute2 = "You love to play with friends"
            Atribute3 = "You are a born diplomat"
        elif att_date == '25/08':
            Atribute1 = "You are curious about the world"
            Atribute2 = "You are very smart"
            Atribute3 = "You love to chat with your friends"
        elif att_date == '26/08':
            Atribute1 = "You love excitement"
            Atribute2 = "You have a warm personality"
            Atribute3 = "You are a busy bee"
        elif att_date == '27/08':
            Atribute1 = "You love to help your friends"
            Atribute2 = "You are a creative visionary"
            Atribute3 = "You are a busy bee"
        elif att_date == '28/08':
            Atribute1 = "You are quick-witted"
            Atribute2 = "You are full of fun"
            Atribute3 = "You love to help your friends"
        elif att_date == '29/08':
            Atribute1 = "You are a busy bee"
            Atribute2 = "You are a natural born leader"
            Atribute3 = "You know what you want"
        elif att_date == '30/08':
            Atribute1 = "You are quick-witted"
            Atribute2 = "You are very kindhearted"
            Atribute3 = "You love to learn"
        elif att_date == '31/08':
            Atribute1 = "You have a magnetic personality"
            Atribute2 = "You are a charmer"
            Atribute3 = "You have a creative imagination"
        elif att_date == '01/09':
            Atribute1 = "You have an eye for detail"
            Atribute2 = "You are a busy bee"
            Atribute3 = "You love to learn"
        elif att_date == '02/09':
            Atribute1 = "You are a born diplomat"
            Atribute2 = "You have lots of friends"
            Atribute3 = "You are a team player"
        elif att_date == '03/09':
            Atribute1 = "You are a busy bee"
            Atribute2 = "You love to help your friends"
            Atribute3 = "You have a sunny nature"
        elif att_date == '04/09':
            Atribute1 = "You have a creative imagination"
            Atribute2 = "You love to help your friends"
            Atribute3 = "You are a born diplomat"
        elif att_date == '05/09':
            Atribute1 = "You are devoted to family and friends"
            Atribute2 = "You have a unique creativity"
            Atribute3 = "You are a forward thinker"
        elif att_date == '06/09':
            Atribute1 = "You are devoted to family and friends"
            Atribute2 = "You love to help your friends"
            Atribute3 = "You are a creative visionary"
        elif att_date == '07/09':
            Atribute1 = "You stick with it"
            Atribute2 = "You are a busy bee"
            Atribute3 = "You are a creative visionary"
        elif att_date == '08/09':
            Atribute1 = "You have a unique creativity"
            Atribute2 = "You love to help your friends"
            Atribute3 = "You love a puzzle"
        elif att_date == '09/09':
            Atribute1 = "You are gentle and caring"
            Atribute2 = "You love adventure"
            Atribute3 = "You are a born diplomat"
        elif att_date == '10/09':
            Atribute1 = "You are a busy bee"
            Atribute2 = "You are quick-witted"
            Atribute3 = "You know what you want"
        elif att_date == '11/09':
            Atribute1 = "You are a charmer"
            Atribute2 = "You are a quick learner"
            Atribute3 = "You are a creative visionary"
        elif att_date == '12/09':
            Atribute1 = "You are very smart"
            Atribute2 = "You are quick-witted"
            Atribute3 = "You love to chat with your friends"
        elif att_date == '13/09':
            Atribute1 = "You are a busy bee"
            Atribute2 = "You have a unique creativity"
            Atribute3 = "You stick with it"
        elif att_date == '14/09':
            Atribute1 = "You are a charmer"
            Atribute2 = "You love to solve problems"
            Atribute3 = "You love excitement"
        elif att_date == '15/09':
            Atribute1 = "You love to help your friends"
            Atribute2 = "You have a creative imagination"
            Atribute3 = "You are devoted to family and friends"
        elif att_date == '16/09':
            Atribute1 = "You are quick-witted"
            Atribute2 = "You are very kindhearted"
            Atribute3 = "You love to learn"
        elif att_date == '17/09':
            Atribute1 = "You are a creative visionary"
            Atribute2 = "You are very kindhearted"
            Atribute3 = "You stick with it"
        elif att_date == '18/09':
            Atribute1 = "You love to help your friends"
            Atribute2 = "You are self-reliant"
            Atribute3 = "You are a busy bee"
        elif att_date == '19/09':
            Atribute1 = "You love to learn"
            Atribute2 = "You are a busy bee"
            Atribute3 = "You are quick-witted"
        elif att_date == '20/09':
            Atribute1 = "You are very kindhearted"
            Atribute2 = "You are a born diplomat"
            Atribute3 = "You are quick-witted"
        elif att_date == '21/09':
            Atribute1 = "You have a creative imagination"
            Atribute2 = "You love to help your friends"
            Atribute3 = "You are very kindhearted"
        elif att_date == '22/09':
            Atribute1 = "You are a busy bee"
            Atribute2 = "You are a forward thinker"
            Atribute3 = "You are a born diplomat"
        elif att_date == '23/09':
            Atribute1 = "You are quick-witted"
            Atribute2 = "You are a natural born leader"
            Atribute3 = "You love to chat with your friends"
        elif att_date == '24/09':
            Atribute1 = "You have a unique creativity"
            Atribute2 = "You are devoted to family and friends"
            Atribute3 = "You are curious about the world"
        elif att_date == '25/09':
            Atribute1 = "You are a charmer"
            Atribute2 = "You like to play with your friends"
            Atribute3 = "You are quick-witted"
        elif att_date == '26/09':
            Atribute1 = "You are a charmer"
            Atribute2 = "You are a born diplomat"
            Atribute3 = "You are a natural leader"
        elif att_date == '27/09':
            Atribute1 = "You love to play detective"
            Atribute2 = "You are a born diplomat"
            Atribute3 = "You love to help your friends"
        elif att_date == '28/09':
            Atribute1 = "You are devoted to family and friends"
            Atribute2 = "You are very kindhearted"
            Atribute3 = "You stick with it"
        elif att_date == '29/09':
            Atribute1 = "You are a born diplomat"
            Atribute2 = "You have a magnetic personality"
            Atribute3 = "You have a creative imagination"
        elif att_date == '30/09':
            Atribute1 = "You are quick-witted"
            Atribute2 = "You have a creative imagination"
            Atribute3 = "You are a charmer"
        elif att_date == '01/10':
            Atribute1 = "You are a charmer"
            Atribute2 = "You are a natural born leader"
            Atribute3 = "You are a busy bee"
        elif att_date == '02/10':
            Atribute1 = "You have lots of friends"
            Atribute2 = "You have a sunny nature"
            Atribute3 = "You have a creative imagination"
        elif att_date == '03/10':
            Atribute1 = "You love to chat with your friends"
            Atribute2 = "You are a charmer"
            Atribute3 = "You are quick-witted"
        elif att_date == '04/10':
            Atribute1 = "You are curious about the world"
            Atribute2 = "You are a forward thinker"
            Atribute3 = "You are a busy bee"
        elif att_date == '05/10':
            Atribute1 = "You like to be on the team"
            Atribute2 = "You are curious about the world"
            Atribute3 = "You are a busy bee"
        elif att_date == '06/10':
            Atribute1 = "You have a unique creativity"
            Atribute2 = "You are devoted to your friends"
            Atribute3 = "You are a natural diplomat"
        elif att_date == '07/10':
            Atribute1 = "You are a charmer"
            Atribute2 = "You are a forward thinker"
            Atribute3 = "You are smart and creative"
        elif att_date == '08/10':
            Atribute1 = "You are smart and creative"
            Atribute2 = "You are a born diplomat"
            Atribute3 = "You have a quirky sense of humour"
        elif att_date == '09/10':
            Atribute1 = "You love to chat with your friends"
            Atribute2 = "You have a unique creativity"
            Atribute3 = "You love to play detective"
        elif att_date == '10/10':
            Atribute1 = "You are a natural born leader"
            Atribute2 = "You are a charmer"
            Atribute3 = "You have a unique creativity"
        elif att_date == '11/10':
            Atribute1 = "You are a natural diplomat"
            Atribute2 = "You have a creative imagination"
            Atribute3 = "You have a quirky sense of humour"
        elif att_date == '12/10':
            Atribute1 = "You are a natural diplomat"
            Atribute2 = "You love to chat with your friends"
            Atribute3 = "You have a sunny optimism"
        elif att_date == '13/10':
            Atribute1 = "You know what you want"
            Atribute2 = "You work hard to get it"
            Atribute3 = "You are a natural born leader"
        elif att_date == '14/10':
            Atribute1 = "You have a creative imagination"
            Atribute2 = "You are a natural diplomat"
            Atribute3 = "You love to chat with your friends"
        elif att_date == '15/10':
            Atribute1 = "You have lots of friends"
            Atribute2 = "You are a born diplomat"
            Atribute3 = "You are a natural story teller"
        elif att_date == '16/10':
            Atribute1 = "You are a charmer"
            Atribute2 = "You love to learn"
            Atribute3 = "You have many passions"
        elif att_date == '17/10':
            Atribute1 = "You are a busy bee"
            Atribute2 = "You are a natural diplomat"
            Atribute3 = "You have a unique creativity"
        elif att_date == '18/10':
            Atribute1 = "You are a natural diplomat"
            Atribute2 = "You are a busy bee"
            Atribute3 = "You love to play detective"
        elif att_date == '19/10':
            Atribute1 = "You are a charmer"
            Atribute2 = "You stick with it"
            Atribute3 = "You love to chat with your friends"
        elif att_date == '20/10':
            Atribute1 = "You have a unique creativity"
            Atribute2 = "You are quick-witted"
            Atribute3 = "You have a great sense of fun"
        elif att_date == '21/10':
            Atribute1 = "You are a charmer"
            Atribute2 = "You are an original thinker"
            Atribute3 = "You love to learn"
        elif att_date == '22/10':
            Atribute1 = "You love to play detective"
            Atribute2 = "You are a busy bee"
            Atribute3 = "You are a go-getter"
        elif att_date == '23/10':
            Atribute1 = "You are very smart"
            Atribute2 = "You have a magnetic personality"
            Atribute3 = "You are quick-witted"
        elif att_date == '24/10':
            Atribute1 = "You are a born diplomat"
            Atribute2 = "You have a unique creativity"
            Atribute3 = "You love to chat with your friends"
        elif att_date == '25/10':
            Atribute1 = "You know what you want"
            Atribute2 = "You work hard to get it"
            Atribute3 = "You are a charmer"
        elif att_date == '26/10':
            Atribute1 = "You are a busy bee"
            Atribute2 = "You are quick-witted"
            Atribute3 = "You love to help your friends"
        elif att_date == '27/10':
            Atribute1 = "You are a busy bee"
            Atribute2 = "You have a creative imagination"
            Atribute3 = "You are a go-getter"
        elif att_date == '28/10':
            Atribute1 = "You know what you want"
            Atribute2 = "You work hard to get it"
            Atribute3 = "You have a magnetic personality"
        elif att_date == '29/10':
            Atribute1 = "You have a magnetic personality"
            Atribute2 = "You love adventure"
            Atribute3 = "You love to chat with your friends"
        elif att_date == '30/10':
            Atribute1 = "You love to chat with your friends"
            Atribute2 = "You love to learn"
            Atribute3 = "You are quick-witted"
        elif att_date == '31/10':
            Atribute1 = "You stick with it"
            Atribute2 = "You are a natural diplomat"
            Atribute3 = "You have lots of friends"
        elif att_date == '01/11':
            Atribute1 = "You are quick-witted"
            Atribute2 = "You are devoted to your family"
            Atribute3 = "You are a busy bee"
        elif att_date == '02/11':
            Atribute1 = "You are a charmer"
            Atribute2 = "You are a natural diplomat"
            Atribute3 = "You are a team player"
        elif att_date == '03/11':
            Atribute1 = "You love exciting new ideas"
            Atribute2 = "You have a fun sense of humour"
            Atribute3 = "You love to chat with your friends"
        elif att_date == '04/11':
            Atribute1 = "You are a busy bee"
            Atribute2 = "You are a natural born leader"
            Atribute3 = "You are a charmer"
        elif att_date == '05/11':
            Atribute1 = "You are a forward thinker"
            Atribute2 = "You like to be number one"
            Atribute3 = "You are a charmer"
        elif att_date == '06/11':
            Atribute1 = "You are a charmer"
            Atribute2 = "You stick with it"
            Atribute3 = "You are a team player"
        elif att_date == '07/11':
            Atribute1 = "You are a natural diplomat"
            Atribute2 = "You have a creative imagination"
            Atribute3 = "You love to help your friends"
        elif att_date == '08/11':
            Atribute1 = "You are a natural born leader"
            Atribute2 = "You love to play detective"
            Atribute3 = "You stick with it"
        elif att_date == '09/11':
            Atribute1 = "You are a problem solver"
            Atribute2 = "You are a go-getter"
            Atribute3 = "You have a unique creativity"
        elif att_date == '10/11':
            Atribute1 = "You are quick and sharp minded"
            Atribute2 = "You love exciting new ideas"
            Atribute3 = "You like to be number one"
        elif att_date == '11/11':
            Atribute1 = "You are a charmer"
            Atribute2 = "You love to help your friends"
            Atribute3 = "You love to play detective"
        elif att_date == '12/11':
            Atribute1 = "You know what you want"
            Atribute2 = "You are fun-loving"
            Atribute3 = "You like to be number one"
        elif att_date == '13/11':
            Atribute1 = "You are a busy bee"
            Atribute2 = "You are a natural born leader"
            Atribute3 = "You have a great sense of fun"
        elif att_date == '14/11':
            Atribute1 = "You love to help your friends"
            Atribute2 = "You have a unique creativity"
            Atribute3 = "You are very smart and honourable"
        elif att_date == '15/11':
            Atribute1 = "You are quick and sharp minded"
            Atribute2 = "You are a charmer"
            Atribute3 = "You love to help your friends"
        elif att_date == '16/11':
            Atribute1 = "You are a busy bee"
            Atribute2 = "You love to chat with your friends"
            Atribute3 = "You are intriguing"
        elif att_date == '17/11':
            Atribute1 = "You work hard to achieve your goals"
            Atribute2 = "You are a busy bee"
            Atribute3 = "You love to help your friends"
        elif att_date == '18/11':
            Atribute1 = "You love a challenge"
            Atribute2 = "You are devoted to family and friends"
            Atribute3 = "You fit in anywhere"
        elif att_date == '19/11':
            Atribute1 = "You are a natural born leader"
            Atribute2 = "You know what you want"
            Atribute3 = "You work hard to get it"
        elif att_date == '20/11':
            Atribute1 = "You are a natural diplomat"
            Atribute2 = "You are devoted to your family"
            Atribute3 = "You are a natural born leader"
        elif att_date == '21/11':
            Atribute1 = "You have a sunny personality"
            Atribute2 = "You love to chat with your friends"
            Atribute3 = "You are a natural diplomat"
        elif att_date == '22/11':
            Atribute1 = "You are a natural diplomat"
            Atribute2 = "You are spirited and playful"
            Atribute3 = "You are a busy bee"
        elif att_date == '23/11':
            Atribute1 = "You love adventure"
            Atribute2 = "You are quick-witted"
            Atribute3 = "You have a unique creativity"
        elif att_date == '24/11':
            Atribute1 = "You have a creative imagination"
            Atribute2 = "You love to chat with your friends"
            Atribute3 = "You aim for the stars"
        elif att_date == '25/11':
            Atribute1 = "You are a charmer"
            Atribute2 = "You love to help your friends"
            Atribute3 = "You are spirited and playful"
        elif att_date == '26/11':
            Atribute1 = "You are a busy bee"
            Atribute2 = "You love adventure"
            Atribute3 = "You are a charmer"
        elif att_date == '27/11':
            Atribute1 = "You have a unique creativity"
            Atribute2 = "You are quick-witted"
            Atribute3 = "You love to travel"
        elif att_date == '28/11':
            Atribute1 = "You love adventure"
            Atribute2 = "You have a magnetic personality"
            Atribute3 = "You are spirited and playful"
        elif att_date == '29/11':
            Atribute1 = "You are a forward thinker"
            Atribute2 = "You love to paint and draw"
            Atribute3 = "You are quick-witted"
        elif att_date == '30/11':
            Atribute1 = "You are a charmer"
            Atribute2 = "You have a creative imagination"
            Atribute3 = "You love to travel"
        elif att_date == '01/12':
            Atribute1 = "You love adventure"
            Atribute2 = "You are a charmer"
            Atribute3 = "You love to travel"
        elif att_date == '02/12':
            Atribute1 = "You are a charmer"
            Atribute2 = "You have a unique creativity"
            Atribute3 = "You are determined to succeed"
        elif att_date == '03/12':
            Atribute1 = "You are a charmer"
            Atribute2 = "You love to learn"
            Atribute3 = "You love adventure"
        elif att_date == '04/12':
            Atribute1 = "You are a busy bee"
            Atribute2 = "You are determined to succeed"
            Atribute3 = "You make lots of friends"
        elif att_date == '05/12':
            Atribute1 = "You have a unique creativity"
            Atribute2 = "You love adventure"
            Atribute3 = "You are loads of fun"
        elif att_date == '06/12':
            Atribute1 = "You love to learn"
            Atribute2 = "You are quick-witted"
            Atribute3 = "You love to play with friends"
        elif att_date == '07/12':
            Atribute1 = "You love to learn"
            Atribute2 = "You are a busy bee"
            Atribute3 = "You are clever and persuasive"
        elif att_date == '08/12':
            Atribute1 = "You are a busy bee"
            Atribute2 = "You are quick-witted"
            Atribute3 = "You are a deep thinker"
        elif att_date == '09/12':
            Atribute1 = "You have big dreams"
            Atribute2 = "You are quick-witted"
            Atribute3 = "You love to multi-task"
        elif att_date == '10/12':
            Atribute1 = "You are a busy bee"
            Atribute2 = "You love adventure"
            Atribute3 = "You make lots of friends"
        elif att_date == '11/12':
            Atribute1 = "You are a natural diplomat"
            Atribute2 = "You have a sunny optimism"
            Atribute3 = "You stick with it"
        elif att_date == '12/12':
            Atribute1 = "You are quick-witted"
            Atribute2 = "You love to chat with your friends"
            Atribute3 = "You love to travel"
        elif att_date == '13/12':
            Atribute1 = "You love adventure"
            Atribute2 = "You are a busy bee"
            Atribute3 = "You love a challenge"
        elif att_date == '14/12':
            Atribute1 = "You love adventure"
            Atribute2 = "You are a busy bee"
            Atribute3 = "You have a sunny optimism"
        elif att_date == '15/12':
            Atribute1 = "You are devoted to family and friends"
            Atribute2 = "You are a natural diplomat"
            Atribute3 = "You are quick-witted"
        elif att_date == '16/12':
            Atribute1 = "You love adventure"
            Atribute2 = "You make lots of friends"
            Atribute3 = "You love to travel"
        elif att_date == '17/12':
            Atribute1 = "You have a sunny optimism"
            Atribute2 = "You're a natural born leader"
            Atribute3 = "You love to travel"
        elif att_date == '18/12':
            Atribute1 = "You are a busy bee"
            Atribute2 = "You love to play detective"
            Atribute3 = "You are couragous and brave"
        elif att_date == '19/12':
            Atribute1 = "You have a magnetic personality"
            Atribute2 = "You have a unique creativity"
            Atribute3 = "You stick with it"
        elif att_date == '20/12':
            Atribute1 = "You are devoted to family and friends"
            Atribute2 = "You have a sunny optimism"
            Atribute3 = "You are a natural diplomat"
        elif att_date == '21/12':
            Atribute1 = "You have a magnetic personality"
            Atribute2 = "You stick with it"
            Atribute3 = "You aim for the stars"
        elif att_date == '22/12':
            Atribute1 = "You are very kindhearted"
            Atribute2 = "You are a busy bee"
            Atribute3 = "You aim for the stars"
        elif att_date == '23/12':
            Atribute1 = "You are a charmer"
            Atribute2 = "You have a creative imagination"
            Atribute3 = "You love to chat with your friends"
        elif att_date == '24/12':
            Atribute1 = "You are a busy bee"
            Atribute2 = "You are a charmer"
            Atribute3 = "You are a natural diplomat"
        elif att_date == '25/12':
            Atribute1 = "You stick with it"
            Atribute2 = "You love adventure"
            Atribute3 = "You love to chat with your friends"
        elif att_date == '26/12':
            Atribute1 = "You aim for the stars"
            Atribute2 = "You love adventure"
            Atribute3 = "You are quick-witted"
        elif att_date == '27/12':
            Atribute1 = "You are devoted to family and friends"
            Atribute2 = "You are generous and kind"
            Atribute3 = "You have a unique creativity"
        elif att_date == '28/12':
            Atribute1 = "You are a busy bee"
            Atribute2 = "You are a natural born leader"
            Atribute3 = "You stick with it"
        elif att_date == '29/12':
            Atribute1 = "You are very smart"
            Atribute2 = "You make lots of friends"
            Atribute3 = "You are a charmer"
        elif att_date == '30/12':
            Atribute1 = "You are a busy bee"
            Atribute2 = "You work hard to achieve your goals"
            Atribute3 = "You love to chat with your friends"
        elif att_date == '31/12':
            Atribute1 = "You are devoted to family and friends"
            Atribute2 = "You have a quirky sense of humour"
            Atribute3 = "You are a charmer"
        else :
            Atribute1 = "Wrong"
            Atribute2 = "Wrong"
            Atribute3 = "Wrong"

        ##### Page 13 Atribute Lookup End ####

        text_width = stringWidth(book_name_input, "font1", 30) # Measure the width of the book_name_input variable
        packet = io.BytesIO() # opens reportlab session
        can = canvas.Canvas(packet, pagesize=(661, 661)) # Sets canvas size -> this is incorrect

        #### Atribute 1 ####
        can.rotate(6)
        can.setFillColorRGB(0,0,0) #choose your font colour
        can.setFont("font1", 28) #choose your font type and font size
        y_pos = 195
        x_pos = (661 / 2)+25
        can.drawCentredString(x_pos+15, y_pos+55, Atribute3)

        #### Atribute 2 ####
        can.rotate(-6)
        can.setFillColorRGB(0,0,0) #choose your font colour
        can.setFont("font1", 28) #choose your font type and font size
        y_pos = 220
        x_pos = (661 / 2)+25
        can.drawCentredString(x_pos-25, y_pos+190, Atribute2)

        #### Atribute 3 ####
        can.rotate(+11)
        can.setFillColorRGB(0,0,0) #choose your font colour
        can.setFont("font1", 28) #choose your font type and font size
        y_pos = 195
        x_pos = (661 / 2)+25
        can.drawCentredString(x_pos+67, y_pos+252, Atribute1)
        #can.rotate(45)

        month = int(date_input[5:7])
        day = int(date_input[8:10])
        year = int(date_input[0:4])
        dave = date(day=day, month=month, year=year).strftime('%A')
        dave2 = date(day=day, month=month, year=year).strftime('%e')
        dave3 = date(day=day, month=month, year=year).strftime('%B %Y')
        dave2 = ordinal(int(dave2))
        #dave_final = (dave, dave2, dave3)
        dave_123 = " ".join([dave, dave2, dave3])
        y_pos = 135
        x_pos = (661 / 2)
        can.rotate(-11)
        can.drawCentredString(x_pos, y_pos, dave_123)

        can.save()

        #move to the beginning of the StringIO buffer
        packet.seek(0)

        # create a new PDF with Reportlab
        new_pdf = PdfFileReader(packet)
        # read your existing PDF
        existing_pdf = PdfFileReader(open('static/media/full_book/p13/p13.pdf', "rb"))
        output = PdfFileWriter()
        # add the "watermark" (which is the new pdf) on the existing page
        page13 = existing_pdf.getPage(0)
        page13.mergePage(new_pdf.getPage(0))
        end_time13 = (time.time() - start_time)
        print("Page 13 PDF built in:", end_time13, "Seconds")
        print("Page 13 Personalized with three atributes from date:-",Atribute1,",", Atribute2,",", Atribute3)
        print("Page 13 Personalized with formatted date:-", dave_123)

        ###### Page 14 BUILDER #####
        start_time = time.time()
        day1 = int(date_input[8:9])
        day2 = int(date_input[9:10])
        special_number = day1 + day2
        special_number_lookup = int(date_input[8:10])
        existing_pdf = PdfFileReader(open('static/media/full_book/p14/{}+{}.pdf'.format(day1, day2), "rb"))
        output = PdfFileWriter()
        # add the "watermark" (which is the new pdf) on the existing page
        page14 = existing_pdf.getPage(0)
        end_time14 = (time.time() - start_time)
        print("{}+{}".format(day1, day2))
        print("Page 14 PDF built in:", end_time14, "Seconds")
        print("Page 14 Personalized with page selection from special number lookup:-", special_number_lookup)

        ###### Page 15 BUILDER #####
        start_time = time.time()
        if special_number > 9:
            day1 = int(str(special_number)[:1])
            day2 = int(str(special_number)[1:2])
            special_number = day1 + day2
            print("super special number created:", special_number)
        print("special number is:", special_number)
        existing_pdf = PdfFileReader(open('static/media/full_book/p15/{}.pdf'.format(special_number), "rb"))
        output = PdfFileWriter()
        # add the "watermark" (which is the new pdf) on the existing page

        page15 = existing_pdf.getPage(0)
        end_time15 = (time.time() - start_time)
        print("Page 15 PDF built in:", end_time15, "Seconds")
        print("Page 15 Personalized with page selection from special number lookup:-", special_number)


        ###### Page 16 BUILDER #####
        start_time = time.time()
        existing_pdf = PdfFileReader(open('static/media/full_book/p16/p16.pdf', "rb"))
        output = PdfFileWriter()
        # add the "watermark" (which is the new pdf) on the existing page
        page16 = existing_pdf.getPage(0)
        end_time16 = (time.time() - start_time)
        print("Page 16 PDF built in:", end_time16, "Seconds")
        print("Page 16 No Personalizations")

        ###### Page 17 BUILDER #####
        start_time = time.time()
        existing_pdf = PdfFileReader(open('static/media/full_book/p17/p17.pdf', "rb"))
        output = PdfFileWriter()
        # add the "watermark" (which is the new pdf) on the existing page
        page17 = existing_pdf.getPage(0)
        end_time17 = (time.time() - start_time)
        print("Page 17 PDF built in:", end_time17, "Seconds")
        print("Page 17 No Personalizations")

        ###### Page 18 BUILDER #####
        start_time = time.time()
        existing_pdf = PdfFileReader(open('static/media/full_book/p18/p18.pdf', "rb"))
        output = PdfFileWriter()
        # add the "watermark" (which is the new pdf) on the existing page
        page18 = existing_pdf.getPage(0)
        end_time18 = (time.time() - start_time)
        print("Page 18 PDF built in:", end_time18, "Seconds")
        print("Page 18 No Personalizations")

            ###### Chinese Year Lookup #####
        start_time = time.time()
        year = date_input[0:4]
        month = date_input[5:7]
        day = int(date_input[8:10])

        if '2027-02-06' <= date_input <= '2028-01-25':
            animal = 'Ram'
            element = 'Fire'
        elif '2026-02-17' <= date_input <= '2027-02-05':
            animal = 'Horse'
            element = 'Fire'
        elif '2025-01-29' <= date_input <= '2026-02-16':
            animal = 'Snake'
            element = 'Wood'
        elif '2024-02-10' <= date_input <= '2025-01-28':
            animal = 'Dragon'
            element = 'Wood'
        elif '2023-01-22' <= date_input <= '2024-02-09':
            animal = 'Rabbit'
            element = 'Water'
        elif '2022-02-01' <= date_input <= '2023-01-21':
            animal = 'Tiger'
            element = 'Water'
        elif '2021-02-12' <= date_input <= '2022-01-31':
            animal = 'Ox'
            element = 'Metal'
        elif '2020-01-25' <= date_input <= '2021-02-11':
            animal = 'Rat'
            element = 'Metal'
        elif '2019-02-05' <= date_input <= '2020-01-24':
            animal = 'Pig'
            element = 'Earth'
        elif '2018-02-16' <= date_input <= '2019-02-04':
            animal = 'Dog'
            element = 'Earth'
        elif '2017-01-28' <= date_input <= '2018-02-15':
            animal = 'Rooster'
            element = 'Fire'
        elif '2016-02-08' <= date_input <= '2017-01-27':
            animal = 'Monkey'
            element = 'Fire'
        elif '2015-02-19' <= date_input <= '2016-02-07':
            animal = 'Ram'
            element = 'Wood'
        elif '2014-01-31' <= date_input <= '2015-02-18':
            animal = 'Horse'
            element = 'Wood'
        elif '2013-02-10' <= date_input <= '2014-01-30':
            animal = 'Snake'
            element = 'Water'
        elif '2012-01-23' <= date_input <= '2013-02-09':
            animal = 'Dragon'
            element = 'Water'
        elif '2011-02-03' <= date_input <= '2012-01-22':
            animal = 'Rabbit'
            element = 'Metal'
        elif '2010-02-14' <= date_input <= '2011-02-02':
            animal = 'Tiger'
            element = 'Metal'
        elif '2009-01-26' <= date_input <= '2010-02-13':
            animal = 'Ox'
            element = 'Earth'
        elif '2008-02-07' <= date_input <= '2009-01-25':
            animal = 'Rat'
            element = 'Earth'
        elif '2007-02-18' <= date_input <= '2008-02-06':
            animal = 'Pig'
            element = 'Fire'
        elif '2006-01-29' <= date_input <= '2007-02-17':
            animal = 'Dog'
            element = 'Fire'
        elif '2005-02-09' <= date_input <= '2006-01-28':
            animal = 'Rooster'
            element = 'Wood'
        elif '2004-01-22' <= date_input <= '2005-02-08':
            animal = 'Monkey'
            element = 'Wood'
        elif '2003-02-01' <= date_input <= '2004-01-21':
            animal = 'Ram'
            element = 'Water'
        elif '2002-02-12' <= date_input <= '2003-01-31':
            animal = 'Horse'
            element = 'Water'
        elif '2001-01-24' <= date_input <= '2002-02-11':
            animal = 'Snake'
            element = 'Metal'
        elif '2000-02-05' <= date_input <= '2001-01-23':
            animal = 'Dragon'
            element = 'Metal'
        elif '1999-02-16' <= date_input <= '2000-02-04':
            animal = 'Rabbit'
            element = 'Earth'
        elif '1998-01-28' <= date_input <= '1999-02-15':
            animal = 'Tiger'
            element = 'Earth'
        elif '1997-02-07' <= date_input <= '1998-01-27':
            animal = 'Ox'
            element = 'Fire'
        elif '1996-02-19' <= date_input <= '1997-02-06':
            animal = 'Rat'
            element = 'Fire'
        elif '1995-01-31' <= date_input <= '1996-02-18':
            animal = 'Pig'
            element = 'Wood'
        elif '1994-02-10' <= date_input <= '1995-01-30':
            animal = 'Dog'
            element = 'Wood'
        elif '1993-01-23' <= date_input <= '1994-02-09':
            animal = 'Rooster'
            element = 'Water'
        elif '1992-02-04' <= date_input <= '1993-01-22':
            animal = 'Monkey'
            element = 'Water'
        elif '1991-02-15' <= date_input <= '1992-02-03':
            animal = 'Ram'
            element = 'Metal'
        elif '1990-01-27' <= date_input <= '1991-02-14':
            animal = 'Horse'
            element = 'Metal'
        elif '1989-02-06' <= date_input <= '1990-01-26':
            animal = 'Snake'
            element = 'Earth'
        elif '1988-02-17' <= date_input <= '1989-02-05':
            animal = 'Dragon'
            element = 'Earth'
        elif '1987-01-29' <= date_input <= '1988-02-16':
            animal = 'Rabbit'
            element = 'Fire'
        elif '1986-02-09' <= date_input <= '1987-01-28':
            animal = 'Tiger'
            element = 'Fire'
        elif '1985-02-20' <= date_input <= '1986-02-08':
            animal = 'Ox'
            element = 'Wood'
        elif '1984-02-02' <= date_input <= '1985-02-19':
            animal = 'Rat'
            element = 'Wood'
        elif '1983-02-13' <= date_input <= '1984-02-01':
            animal = 'Pig'
            element = 'Water'
        elif '1982-01-25' <= date_input <= '1983-02-12':
            animal = 'Dog'
            element = 'Water'
        elif '1981-02-05' <= date_input <= '1982-01-24':
            animal = 'Rooster'
            element = 'Metal'
        elif '1980-02-16' <= date_input <= '1981-02-04':
            animal = 'Monkey'
            element = 'Metal'
        elif '1979-01-28' <= date_input <= '1980-02-15':
            animal = 'Ram'
            element = 'Earth'
        elif '1978-02-07' <= date_input <= '1979-01-27':
            animal = 'Horse'
            element = 'Earth'
        elif '1977-02-18' <= date_input <= '1978-02-06':
            animal = 'Snake'
            element = 'Fire'
        elif '1976-01-31' <= date_input <= '1977-02-17':
            animal = 'Dragon'
            element = 'Fire'
        elif '1975-02-11' <= date_input <= '1976-01-30':
            animal = 'Rabbit'
            element = 'Wood'
        elif '1974-01-23' <= date_input <= '1975-02-10':
            animal = 'Tiger'
            element = 'Wood'
        elif '1973-02-03' <= date_input <= '1974-01-22':
            animal = 'Ox'
            element = 'Water'
        elif '1972-02-15' <= date_input <= '1973-02-02':
            animal = 'Rat'
            element = 'Water'
        elif '1971-01-27' <= date_input <= '1972-02-14':
            animal = 'Pig'
            element = 'Metal'
        elif '1970-02-06' <= date_input <= '1971-01-26':
            animal = 'Dog'
            element = 'Metal'
        elif '1969-02-17' <= date_input <= '1970-02-05':
            animal = 'Rooster'
            element = 'Earth'
        elif '1968-01-30' <= date_input <= '1969-02-16':
            animal = 'Monkey'
            element = 'Earth'
        elif '1967-02-09' <= date_input <= '1968-01-29':
            animal = 'Ram'
            element = 'Fire'
        elif '1966-01-21' <= date_input <= '1967-02-08':
            animal = 'Horse'
            element = 'Fire'
        elif '1965-02-02' <= date_input <= '1966-01-20':
            animal = 'Snake'
            element = 'Wood'
        elif '1964-02-13' <= date_input <= '1965-02-01':
            animal = 'Dragon'
            element = 'Wood'
        elif '1963-01-25' <= date_input <= '1964-02-12':
            animal = 'Rabbit'
            element = 'Water'
        elif '1962-02-05' <= date_input <= '1963-01-24':
            animal = 'Tiger'
            element = 'Water'
        elif '1961-02-15' <= date_input <= '1962-02-04':
            animal = 'Ox'
            element = 'Metal'
        elif '1960-01-28' <= date_input <= '1961-02-14':
            animal = 'Rat'
            element = 'Metal'
        elif '1959-02-08' <= date_input <= '1960-01-27':
            animal = 'Pig'
            element = 'Earth'
        elif '1958-02-18' <= date_input <= '1959-02-07':
            animal = 'Dog'
            element = 'Earth'
        elif '1957-01-31' <= date_input <= '1958-02-17':
            animal = 'Roster'
            element = 'Fire'
        elif '1956-02-12' <= date_input <= '1957-01-30':
            animal = 'Monkey'
            element = 'Fire'
        elif '1955-01-24' <= date_input <= '1956-02-11':
            animal = 'Ram'
            element = 'Wood'
        elif '1954-02-03' <= date_input <= '1955-01-23':
            animal = 'Horse'
            element = 'Wood'
        elif '1953-02-14' <= date_input <= '1954-02-02':
            animal = 'Snake'
            element = 'Water'
        elif '1952-01-27' <= date_input <= '1953-02-13':
            animal = 'Dragon'
            element = 'Water'
        elif '1951-02-06' <= date_input <= '1952-01-26':
            animal = 'Rabbit'
            element = 'Metal'
        elif '1950-02-17' <= date_input <= '1951-02-05':
            animal = 'Tiger'
            element = 'Metal'
        elif '1949-01-29' <= date_input <= '1950-02-16':
            animal = 'Ox'
            element = 'Earth'
        elif '1948-02-10' <= date_input <= '1949-01-28':
            animal = 'Rat'
            element = 'Earth'
        elif '1947-01-22' <= date_input <= '1948-02-09':
            animal = 'Pig'
            element = 'Fire'
        elif '1946-02-02' <= date_input <= '1947-01-21':
            animal = 'Dog'
            element = 'Fire'
        elif '1945-02-13' <= date_input <= '1946-02-01':
            animal = 'Rooster'
            element = 'Wood'
        elif '1944-01-25' <= date_input <= '1945-02-12':
            animal = 'Monkey'
            element = 'Wood'
        elif '1943-02-05' <= date_input <= '1944-01-24':
            animal = 'Ram'
            element = 'Water'
        elif '1942-02-15' <= date_input <= '1943-02-04':
            animal = 'Horse'
            element = 'Water'
        elif '1941-01-27' <= date_input <= '1942-02-14':
            animal = 'Snake'
            element = 'Metal'
        elif '1940-02-08' <= date_input <= '1941-01-26':
            animal = 'Dragon'
            element = 'Metal'
        elif '1939-02-19' <= date_input <= '1940-02-07':
            animal = 'Rabbit'
            element = 'Earth'
        elif '1938-01-31' <= date_input <= '1939-02-18':
            animal = 'Tiger'
            element = 'Earth'
        elif '1937-02-11' <= date_input <= '1938-01-30':
            animal = 'Ox'
            element = 'Fire'
        elif '1936-01-24' <= date_input <= '1937-02-10':
            animal = 'Rat'
            element = 'Fire'
        elif '1935-02-04' <= date_input <= '1936-01-23':
            animal = 'Pig'
            element = 'Wood'
        elif '1934-02-14' <= date_input <= '1935-02-03':
            animal = 'Dog'
            element = 'Wood'
        elif '1933-01-26' <= date_input <= '1934-02-13':
            animal = 'Rooster'
            element = 'Water'
        elif '1932-02-06' <= date_input <= '1933-01-25':
            animal = 'Monkey'
            element = 'Water'
        elif '1931-02-17' <= date_input <= '1932-02-05':
            animal = 'Ram'
            element = 'Metal'
        elif '1930-01-30' <= date_input <= '1931-02-16':
            animal = 'Horse'
            element = 'Metal'
        elif '1929-02-10' <= date_input <= '1930-01-29':
            animal = 'Snake'
            element = 'Earth'
        elif '1928-01-23' <= date_input <= '1929-02-09':
            animal = 'Dragon'
            element = 'Earth'
        elif '1927-02-02' <= date_input <= '1928-01-22':
            animal = 'Rabbit'
            element = 'Fire'
        elif '1926-02-13' <= date_input <= '1927-02-01':
            animal = 'Tiger'
            element = 'Fire'
        elif '1925-01-25' <= date_input <= '1926-02-12':
            animal = 'Ox'
            element = 'Wood'
        elif '1924-02-05' <= date_input <= '1925-01-24':
            animal = 'Rat'
            element = 'Wood'
        print("Your Animal is:", animal)
        print("Your Element is:", element)

        ###### Page 19 BUILDER #####
        start_time = time.time()
        existing_pdf = PdfFileReader(open('static/media/full_book/p19/{}.pdf'.format(animal), "rb"))
        output = PdfFileWriter()
        # add the "watermark" (which is the new pdf) on the existing page
        page19 = existing_pdf.getPage(0)
        end_time19 = (time.time() - start_time)
        print("Page 19 PDF built in:", end_time19, "Seconds")
        print("Page 19 Personalized with Chinese Animal page selection:-", animal)

        ###### Page 20 BUILDER #####
        start_time = time.time()
        existing_pdf = PdfFileReader(open('static/media/full_book/p20/p20.pdf', "rb"))
        output = PdfFileWriter()
        # add the "watermark" (which is the new pdf) on the existing page
        page20 = existing_pdf.getPage(0)
        end_time20 = (time.time() - start_time)
        print("Page 20 PDF built in:", end_time20, "Seconds")
        print("Page 20 No Personalizations")

        ######## PAGE 21 BUILDER #########
        # 1264 × 612 Resolution of images

        #text_width = stringWidth(book_name_input, "font1", 35) # Measure the width of the book_name_input variable
        packet = io.BytesIO() # opens reportlab session
        can = canvas.Canvas(packet, pagesize=(661, 661)) # Sets canvas size -> this is incorrect
        #can.rotate(15)
        can.setFillColorRGB(0,0,0) #choose your font colour
        can.setFont("font1", 35) #choose your font type and font size
        y_pos = 200
        x_pos = (661 / 2)
        year = int(date_input[0:4])
        month = int(date_input[5:7])
        day = int(date_input[8:10])
        date_year = date(day=day, month=month, year=year).strftime('%Y')
        #can.drawCentredString(x_pos, y_pos, date_year)
        #can.rotate(45)
        can.save()

        #move to the beginning of the StringIO buffer
        packet.seek(0)

        # create a new PDF with Reportlab
        new_pdf = PdfFileReader(packet)
        # read your existing PDF
        existing_pdf = PdfFileReader(open('static/media/full_book/p21/{}.pdf'.format(animal), "rb"))
        #pdfReader = PyPDF2.PdfFileReader(open('PATH_TO_PDF','rb'))
        output = PdfFileWriter()
        # add the "watermark" (which is the new pdf) on the existing page
        page21 = existing_pdf.getPage(0)
        page21.mergePage(new_pdf.getPage(0))
        end_time21 = (time.time() - start_time)
        print("Page 21 PDF built in:", end_time21, "Seconds")
        print("Page 21 Personalized with Chinese Animal lookup:-", animal)

        ###### Page 22 BUILDER #####
        start_time = time.time()
        existing_pdf = PdfFileReader(open('static/media/full_book/p22/p22.pdf', "rb"))
        output = PdfFileWriter()
        # add the "watermark" (which is the new pdf) on the existing page
        page22 = existing_pdf.getPage(0)
        end_time22 = (time.time() - start_time)
        print("Page 22 PDF built in:", end_time22, "Seconds")
        print("Page 22 No Personalizations")

        ###### Page 23 BUILDER #####
        start_time = time.time()
        existing_pdf = PdfFileReader(open('static/media/full_book/p23/{0}.pdf'.format(element), "rb"))
        output = PdfFileWriter()
        # add the "watermark" (which is the new pdf) on the existing page
        page23 = existing_pdf.getPage(0)
        end_time23 = (time.time() - start_time)
        print("Page 23 PDF built in:", end_time23, "Seconds")
        print("Page 23 Personalized with Chinese element page selection:-", element)

        ######## PAGE 24 BUILDER #########
        # 1264 × 612 Resolution of images
        start_time = time.time()
        text_width = stringWidth(book_name_input, "font1", 23) # Measure the width of the book_name_input variable
        packet = io.BytesIO() # opens reportlab session
        book_name_input1 = ('{}, We had so much fun finding out about your special birthday! Everyone who knows you knows how special you are.').format(book_name_input)

        can = canvas.Canvas(packet, pagesize=(661, 661)) # Sets canvas size -> this is incorrect
        can.setFillColorRGB(255,255,255) #choose your font colour
        can.setFont("font1", 30) #choose your font type and font size
        y_pos = 525
        x_pos = (661 / 2)-12
        #can.drawCentredString(x_pos, y_pos, book_name_input)
        #wrap_text = textwrap.wrap(book_name_input1, width=35)
        #can.drawCentredString(x_pos, y_pos, wrap_text[0])
        #can.drawCentredString(x_pos, y_pos-30, wrap_text[1])
        #can.drawCentredString(x_pos, y_pos-60, wrap_text[2])
        #can.drawCentredString(x_pos, y_pos-90, wrap_text[2])
        can.save()

        #move to the beginning of the StringIO buffer
        packet.seek(0)

        # create a new PDF with Reportlab
        new_pdf = PdfFileReader(packet)
        # read your existing PDF
        existing_pdf = PdfFileReader(open('static/media/full_book/p24/p24.pdf', "rb"))
        #pdfReader = PyPDF2.PdfFileReader(open('PATH_TO_PDF','rb'))
        output = PdfFileWriter()
        # add the "watermark" (which is the new pdf) on the existing page
        page24 = existing_pdf.getPage(0)
        page24.mergePage(new_pdf.getPage(0))
        end_time24 = (time.time() - start_time)
        print("Page 24 PDF built in:", end_time24, "Seconds")
        print("Page 24 Personalized with name:-", book_name_input)

        ###### PAGE 25 BUILDER #####
        #start_time = time.time()
        #existing_pdf = PdfFileReader(open('static/media/full_book/insert/inside_back.pdf', "rb"))
      #  #output = PdfFileWriter()
      #  ## add the "watermark" (which is the new pdf) on the existing page
      #  #page25 = existing_pdf.getPage(0)
      #  #end_time25 = (time.time() - start_time)
      #  #print("Page 25 (Inside Front Cover) PDF built in:", end_time25, "Seconds")
      #  #print("Page 25 (Inside Front Cover) No Personalizations")
#
#        ###### PAGE 25_1 BUILDER #####
#        #start_time = time.time()
#        #existing_pdf = PdfFileReader(open('static/media/full_book/insert/insert.pdf', "rb"))
#        #output = PdfFileWriter()
#        ## add the "watermark" (which is the new pdf) on the existing page
#        #page25_1 = existing_pdf.getPage(0)
#        #end_time25_1 = (time.time() - start_time)
#        #print("Page 25_1 (Inside Front Cover) PDF built in:", end_time25_1, "Seconds")
        #print("Page 25_1 (Inside Front Cover) No Personalizations")


        end_time_total = (end_time1 + end_time2 + end_time3 + end_time4 + end_time5 + end_time6 + end_time7 + end_time8 + end_time9 + end_time10 + end_time11 + end_time12 + end_time13 + end_time14 + end_time15 + end_time16 + end_time17 + end_time18 + end_time19 + end_time20 + end_time21 + end_time22 + end_time23 + end_time24)
        print("PDF PAGE CREATION COMPLETED IN:-", end_time_total)

        print("PDF PAGE MERGE STARTING")
        start_time = time.time()
        ###### Merge all Canvas Together ####
        output.addPage(page1)
        book_type = 'hard'
        outputStream = open("static/media/full_book/output/{}_{}_{}_cover.pdf".format(session_id_django, book_name_input, date_input), "wb")
        output.write(outputStream)
        outputStream.close()

        output1 = PdfFileWriter()
        output1.addPage(page2)
        output1.addPage(page2_1)
        output1.addPage(page3)
        output1.addPage(page4)
        output1.addPage(page5)
        output1.addPage(page6)
        output1.addPage(page7)
        output1.addPage(page8)
        output1.addPage(page9)
        output1.addPage(page10)
        output1.addPage(page11)
        output1.addPage(page12)
        output1.addPage(page13)
        output1.addPage(page14)
        output1.addPage(page15)
        output1.addPage(page16)
        output1.addPage(page17)
        output1.addPage(page18)
        output1.addPage(page19)
        output1.addPage(page20)
        output1.addPage(page21)
        output1.addPage(page22)
        output1.addPage(page23)
        output1.addPage(page24)
        #output1.addPage(page25)
        #output1.addPage(page25_1)

        session_id_django = 'ybb'
        # finally, write "output" to a real file
        outputStream = open(f"static/media/full_book/output/{session_id_django}_{book_name_input}_{date_input}_text.pdf", "wb")
        output1.write(outputStream)
        outputStream.close()
        end_time_merge = (time.time() - start_time)
        print("PDF PAGE MERGE COMPLETED IN:-",end_time_merge," seconds")
        total_time = (end_time_merge + end_time_total)


        print("PDF BOOK BUILDING COMPLETED IN:-", total_time)
        order_url_text = "static/media/full_book/output/{}_{}_{}_text.pdf".format(session_id_django, book_name_input, date_input)
        print(order_url_text)
        order_url_cover = "static/media/full_book/output/{}_{}_{}_cover.pdf".format(session_id_django, book_name_input, date_input)
        print(order_url_cover)
        print(book_name_input)
        print(date_input)
        print(session_id_django)




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
        base_url = request.url_root.rstrip('/')
        # Process the data (placeholder for Google view integration)
        # Create sanitized filenames
        # Create output directory if it doesn't exist
        output_dir = os.path.join('static', 'media', 'full_book', 'output')
        os.makedirs(output_dir, exist_ok=True)
        
        # Sanitize filenames
        sanitized_name = secure_filename(book_name_input.replace(' ', '_'))
        text_filename = f"{session_id_django}_{sanitized_name}_{date_input}_text.pdf"
        cover_filename = f"{session_id_django}_{sanitized_name}_{date_input}_cover.pdf"
        
        # Save files with sanitized names
        text_path = os.path.join(output_dir, text_filename)
        with open(text_path, "wb") as outputStream:
            output1.write(outputStream)
        
        response_data = {
            'success': True,
            'Processing Time': total_time,
            'Order URL Text': f"{base_url}/download/{text_filename}",
            'Order URL Cover': f"{base_url}/download/{cover_filename}",
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
