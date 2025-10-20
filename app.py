#!/usr/bin/env python3
from flask import Flask, request, jsonify
import base64
import logging
from weasyprint import HTML, CSS
from jinja2 import Template
import io

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint for Docker and monitoring"""
    return jsonify({'status': 'healthy', 'service': 'zugferd-generator'}), 200

@app.route('/generate', methods=['POST'])
def generate_zugferd():
    """
    Generate ZUGFeRD PDF from base64 PDF and XML content

    Expected JSON body:
    {
        "pdf_base64": "base64 encoded PDF",
        "xml_content": "ZUGFeRD XML string",
        "filename": "optional filename"
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'success': False, 'error': 'JSON body required'}), 400

        pdf_base64 = data.get('pdf_base64', '')
        xml_content = data.get('xml_content', '')
        filename = data.get('filename', 'zugferd.pdf')

        if not pdf_base64 or not xml_content:
            return jsonify({
                'success': False,
                'error': 'pdf_base64 und xml_content sind erforderlich'
            }), 400

        # Decode PDF from base64
        try:
            pdf_bytes = base64.b64decode(pdf_base64)
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Invalid base64 PDF: {str(e)}'
            }), 400

        # Convert XML to bytes
        xml_bytes = xml_content.encode('utf-8')

        # Import pypdf for ZUGFeRD embedding
        from pypdf import PdfReader, PdfWriter
        from io import BytesIO

        # Read the original PDF
        pdf_reader = PdfReader(BytesIO(pdf_bytes))
        pdf_writer = PdfWriter()

        # Copy all pages
        for page in pdf_reader.pages:
            pdf_writer.add_page(page)

        # Attach ZUGFeRD XML as embedded file
        pdf_writer.add_attachment("factur-x.xml", xml_bytes)

        # Set PDF/A-3 metadata for ZUGFeRD compliance
        pdf_writer.add_metadata({
            '/Title': 'ZUGFeRD Rechnung',
            '/Author': 'futalis GmbH',
            '/Subject': 'ZUGFeRD Invoice',
            '/Producer': 'futalis ZUGFeRD Generator'
        })

        # Write to bytes
        output = BytesIO()
        pdf_writer.write(output)
        zugferd_pdf_bytes = output.getvalue()

        # Encode result to base64
        zugferd_base64 = base64.b64encode(zugferd_pdf_bytes).decode('utf-8')

        logger.info(f'Successfully generated ZUGFeRD PDF: {filename} ({len(zugferd_pdf_bytes)} bytes)')

        return jsonify({
            'success': True,
            'zugferd_pdf_base64': zugferd_base64,
            'pdf_size': len(zugferd_pdf_bytes),
            'filename': filename
        }), 200

    except Exception as e:
        logger.error(f'Error generating ZUGFeRD PDF: {str(e)}', exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    """
    Generate PDF from HTML content

    Accepts both JSON and form data.

    Expected body (JSON or form data):
    {
        "html_content": "HTML string or template",
        "css": "optional CSS string",
        "filename": "optional filename"
    }
    """
    try:
        logger.info('=== generate_pdf called ===')

        # Accept both JSON and form data
        if request.is_json:
            data = request.get_json()
            logger.info('Request type: JSON')
        else:
            data = request.form.to_dict()
            logger.info('Request type: Form data')

        logger.info(f'Request data keys: {data.keys() if data else "None"}')

        if not data:
            return jsonify({'success': False, 'error': 'Request body required (JSON or form data)'}), 400

        html_content = data.get('html_content', '')
        css = data.get('css', '')
        filename = data.get('filename', 'document.pdf')

        logger.info(f'html_content length: {len(html_content)}, css length: {len(css)}')

        if not html_content:
            return jsonify({
                'success': False,
                'error': 'html_content ist erforderlich'
            }), 400

        # Generate PDF from HTML
        logger.info('Creating HTML object...')
        html_obj = HTML(string=html_content)

        logger.info(f'Generating PDF (with CSS: {bool(css)})...')
        if css:
            # Create CSS stylesheet separately
            css_obj = CSS(string=css)
            pdf_bytes = html_obj.write_pdf(stylesheets=[css_obj])
        else:
            pdf_bytes = html_obj.write_pdf()

        logger.info(f'PDF generated: {len(pdf_bytes)} bytes')

        # Encode to base64
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')

        logger.info(f'Successfully generated PDF: {filename} ({len(pdf_bytes)} bytes)')

        return jsonify({
            'success': True,
            'pdf_base64': pdf_base64,
            'pdf_size': len(pdf_bytes),
            'filename': filename
        }), 200

    except Exception as e:
        logger.error(f'Error generating PDF: {str(e)}', exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/generate-complete', methods=['POST'])
def generate_complete():
    """
    Generate PDF from HTML and embed ZUGFeRD XML in one step

    Expected JSON body:
    {
        "html_content": "HTML string",
        "css": "optional CSS string",
        "xml_content": "ZUGFeRD XML string",
        "filename": "optional filename"
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'success': False, 'error': 'JSON body required'}), 400

        html_content = data.get('html_content', '')
        css = data.get('css', '')
        xml_content = data.get('xml_content', '')
        filename = data.get('filename', 'zugferd.pdf')

        if not html_content or not xml_content:
            return jsonify({
                'success': False,
                'error': 'html_content und xml_content sind erforderlich'
            }), 400

        # Step 1: Generate PDF from HTML
        html_obj = HTML(string=html_content)

        if css:
            pdf_bytes = html_obj.write_pdf(stylesheets=[CSS(string=css)])
        else:
            pdf_bytes = html_obj.write_pdf()

        # Step 2: Embed ZUGFeRD XML
        xml_bytes = xml_content.encode('utf-8')

        # Import pypdf for ZUGFeRD embedding
        from pypdf import PdfReader, PdfWriter
        from io import BytesIO

        # Read the generated PDF
        pdf_reader = PdfReader(BytesIO(pdf_bytes))
        pdf_writer = PdfWriter()

        # Copy all pages
        for page in pdf_reader.pages:
            pdf_writer.add_page(page)

        # Attach ZUGFeRD XML as embedded file
        pdf_writer.add_attachment("factur-x.xml", xml_bytes)

        # Set PDF/A-3 metadata for ZUGFeRD compliance
        pdf_writer.add_metadata({
            '/Title': 'ZUGFeRD Rechnung',
            '/Author': 'futalis GmbH',
            '/Subject': 'ZUGFeRD Invoice',
            '/Producer': 'futalis ZUGFeRD Generator'
        })

        # Write to bytes
        output = BytesIO()
        pdf_writer.write(output)
        zugferd_pdf_bytes = output.getvalue()

        # Encode to base64
        zugferd_base64 = base64.b64encode(zugferd_pdf_bytes).decode('utf-8')

        logger.info(f'Successfully generated complete ZUGFeRD PDF: {filename} ({len(zugferd_pdf_bytes)} bytes)')

        return jsonify({
            'success': True,
            'zugferd_pdf_base64': zugferd_base64,
            'pdf_size': len(zugferd_pdf_bytes),
            'filename': filename
        }), 200

    except Exception as e:
        logger.error(f'Error generating complete ZUGFeRD PDF: {str(e)}', exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/test', methods=['GET'])
def test():
    """Test endpoint to diagnose library issues"""
    import sys
    results = {
        'python_version': sys.version,
        'tests': {}
    }

    # Test 1: Import weasyprint
    try:
        from weasyprint import HTML, CSS
        results['tests']['weasyprint_import'] = 'OK'
    except Exception as e:
        results['tests']['weasyprint_import'] = f'FAILED: {str(e)}'

    # Test 2: Import pypdf
    try:
        from pypdf import PdfReader, PdfWriter
        results['tests']['pypdf_import'] = 'OK'
    except Exception as e:
        results['tests']['pypdf_import'] = f'FAILED: {str(e)}'

    # Test 3: Generate simple HTML to PDF
    try:
        from weasyprint import HTML
        html = HTML(string='<html><body><h1>Test</h1></body></html>')
        pdf_bytes = html.write_pdf()
        results['tests']['html_to_pdf'] = f'OK ({len(pdf_bytes)} bytes)'
    except Exception as e:
        results['tests']['html_to_pdf'] = f'FAILED: {str(e)}'

    # Test 4: Check lxml
    try:
        import lxml
        results['tests']['lxml_version'] = lxml.__version__
    except Exception as e:
        results['tests']['lxml'] = f'FAILED: {str(e)}'

    return jsonify(results), 200

@app.route('/', methods=['GET'])
def index():
    """Service information endpoint"""
    return jsonify({
        'service': 'ZUGFeRD PDF Generator',
        'version': '2.0.0',
        'endpoints': {
            'health': 'GET /health',
            'test': 'GET /test - Test library compatibility',
            'generate_pdf': 'POST /generate-pdf - Generate PDF from HTML',
            'generate_zugferd': 'POST /generate - Add ZUGFeRD XML to existing PDF',
            'generate_complete': 'POST /generate-complete - Generate PDF + ZUGFeRD in one step',
            'info': 'GET /'
        }
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
