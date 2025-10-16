#!/usr/bin/env python3
from flask import Flask, request, jsonify
import base64
import logging
from facturx import generate_facturx_from_binary

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

        # Generate ZUGFeRD PDF
        zugferd_pdf_bytes = generate_facturx_from_binary(
            pdf_bytes,
            xml_bytes,
            flavor='factur-x',
            level='extended',
            pdf_metadata={
                'author': 'futalis GmbH',
                'title': 'ZUGFeRD Rechnung'
            }
        )

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

@app.route('/', methods=['GET'])
def index():
    """Service information endpoint"""
    return jsonify({
        'service': 'ZUGFeRD PDF Generator',
        'version': '1.0.0',
        'endpoints': {
            'health': 'GET /health',
            'generate': 'POST /generate',
            'info': 'GET /'
        }
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
