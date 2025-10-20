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

        # Log first 500 chars of HTML for debugging
        if html_content:
            preview = html_content[:500].replace('\n', '\\n')
            logger.info(f'HTML preview: {preview}...')

        if not html_content:
            return jsonify({
                'success': False,
                'error': 'html_content ist erforderlich'
            }), 400

        # Clean up HTML content - remove leading/trailing whitespace
        html_content = html_content.strip()

        # Validate HTML has basic structure
        if not ('<html' in html_content.lower() or '<body' in html_content.lower() or '<div' in html_content.lower()):
            logger.warning(f'HTML content may be incomplete or malformed')
            # Try wrapping bare content in HTML structure
            if not html_content.startswith('<'):
                html_content = f'<html><body>{html_content}</body></html>'

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

@app.route('/test-pdf-generation', methods=['GET'])
def test_pdf_generation():
    """Test endpoint that generates a simple PDF to verify PDF generation works"""
    try:
        # Simple test HTML
        test_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; padding: 40px; }
                h1 { color: #333; }
                .info { background: #f0f0f0; padding: 20px; margin: 20px 0; }
            </style>
        </head>
        <body>
            <h1>PDF Generation Test</h1>
            <p>If you can see this, WeasyPrint is working correctly!</p>
            <div class="info">
                <strong>Service:</strong> ZUGFeRD API<br>
                <strong>Version:</strong> 3.0.0<br>
                <strong>Test Time:</strong> """ + str(base64.b64encode(b'test').decode()) + """
            </div>
            <p>This is a test paragraph with some <strong>bold text</strong> and <em>italic text</em>.</p>
        </body>
        </html>
        """

        from weasyprint import HTML
        html_obj = HTML(string=test_html)
        pdf_bytes = html_obj.write_pdf()

        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')

        return jsonify({
            'success': True,
            'message': 'PDF generation test successful',
            'pdf_base64': pdf_base64,
            'pdf_size': len(pdf_bytes),
            'html_used': test_html[:100] + '...'
        }), 200

    except Exception as e:
        logger.error(f'PDF generation test failed: {str(e)}', exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'PDF generation is not working'
        }), 500

@app.route('/pdf/merge', methods=['POST'])
def merge_pdfs():
    """
    Merge multiple PDFs into one

    Accepts both JSON and form data.

    Expected body:
    {
        "pdfs": ["base64_pdf1", "base64_pdf2", ...],
        "filename": "optional filename"
    }
    """
    try:
        logger.info('=== merge_pdfs called ===')

        # Accept both JSON and form data
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
            # Parse pdfs array from form data if it's a JSON string
            if 'pdfs' in data and isinstance(data['pdfs'], str):
                import json
                data['pdfs'] = json.loads(data['pdfs'])

        if not data or 'pdfs' not in data:
            return jsonify({'success': False, 'error': 'pdfs array required'}), 400

        pdfs = data.get('pdfs', [])
        filename = data.get('filename', 'merged.pdf')

        if not pdfs or len(pdfs) < 2:
            return jsonify({'success': False, 'error': 'At least 2 PDFs required'}), 400

        from pypdf import PdfReader, PdfWriter
        from io import BytesIO

        pdf_writer = PdfWriter()

        # Merge all PDFs
        for idx, pdf_base64 in enumerate(pdfs):
            try:
                pdf_bytes = base64.b64decode(pdf_base64)
                pdf_reader = PdfReader(BytesIO(pdf_bytes))

                for page in pdf_reader.pages:
                    pdf_writer.add_page(page)

                logger.info(f'Added PDF {idx + 1}: {len(pdf_reader.pages)} pages')
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': f'Error processing PDF {idx + 1}: {str(e)}'
                }), 400

        # Write merged PDF
        output = BytesIO()
        pdf_writer.write(output)
        merged_bytes = output.getvalue()

        merged_base64 = base64.b64encode(merged_bytes).decode('utf-8')

        logger.info(f'Successfully merged {len(pdfs)} PDFs: {filename} ({len(merged_bytes)} bytes)')

        return jsonify({
            'success': True,
            'pdf_base64': merged_base64,
            'pdf_size': len(merged_bytes),
            'filename': filename,
            'page_count': len(pdf_writer.pages)
        }), 200

    except Exception as e:
        logger.error(f'Error merging PDFs: {str(e)}', exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/pdf/split', methods=['POST'])
def split_pdf():
    """
    Split PDF into multiple PDFs or extract specific pages

    Accepts both JSON and form data.

    Expected body:
    {
        "pdf_base64": "base64 encoded PDF",
        "mode": "pages" or "ranges",
        "pages": [1, 3, 5] or "ranges": [[1,3], [4,6]],
        "filename_prefix": "optional prefix"
    }
    """
    try:
        logger.info('=== split_pdf called ===')

        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
            # Parse arrays from form data
            if 'pages' in data and isinstance(data['pages'], str):
                import json
                data['pages'] = json.loads(data['pages'])
            if 'ranges' in data and isinstance(data['ranges'], str):
                import json
                data['ranges'] = json.loads(data['ranges'])

        if not data or 'pdf_base64' not in data:
            return jsonify({'success': False, 'error': 'pdf_base64 required'}), 400

        pdf_base64 = data.get('pdf_base64', '')
        mode = data.get('mode', 'pages')
        pages = data.get('pages', [])
        ranges = data.get('ranges', [])
        filename_prefix = data.get('filename_prefix', 'split')

        from pypdf import PdfReader, PdfWriter
        from io import BytesIO

        pdf_bytes = base64.b64decode(pdf_base64)
        pdf_reader = PdfReader(BytesIO(pdf_bytes))
        total_pages = len(pdf_reader.pages)

        result_pdfs = []

        if mode == 'pages':
            # Split by individual pages
            if not pages:
                pages = list(range(1, total_pages + 1))

            for page_num in pages:
                if page_num < 1 or page_num > total_pages:
                    continue

                pdf_writer = PdfWriter()
                pdf_writer.add_page(pdf_reader.pages[page_num - 1])

                output = BytesIO()
                pdf_writer.write(output)
                pdf_bytes_out = output.getvalue()

                result_pdfs.append({
                    'pdf_base64': base64.b64encode(pdf_bytes_out).decode('utf-8'),
                    'filename': f'{filename_prefix}_page_{page_num}.pdf',
                    'pages': [page_num],
                    'size': len(pdf_bytes_out)
                })

        elif mode == 'ranges':
            # Split by page ranges
            if not ranges:
                return jsonify({'success': False, 'error': 'ranges required for mode=ranges'}), 400

            for idx, page_range in enumerate(ranges):
                start, end = page_range[0], page_range[1]

                if start < 1 or end > total_pages or start > end:
                    continue

                pdf_writer = PdfWriter()
                for page_num in range(start - 1, end):
                    pdf_writer.add_page(pdf_reader.pages[page_num])

                output = BytesIO()
                pdf_writer.write(output)
                pdf_bytes_out = output.getvalue()

                result_pdfs.append({
                    'pdf_base64': base64.b64encode(pdf_bytes_out).decode('utf-8'),
                    'filename': f'{filename_prefix}_range_{start}-{end}.pdf',
                    'pages': list(range(start, end + 1)),
                    'size': len(pdf_bytes_out)
                })

        logger.info(f'Successfully split PDF into {len(result_pdfs)} parts')

        return jsonify({
            'success': True,
            'pdfs': result_pdfs,
            'total_pages': total_pages,
            'split_count': len(result_pdfs)
        }), 200

    except Exception as e:
        logger.error(f'Error splitting PDF: {str(e)}', exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/pdf/extract-text', methods=['POST'])
def extract_text():
    """
    Extract text from PDF

    Accepts both JSON and form data.

    Expected body:
    {
        "pdf_base64": "base64 encoded PDF",
        "pages": [1, 2, 3] or "all" (optional, defaults to all)
    }
    """
    try:
        logger.info('=== extract_text called ===')

        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
            if 'pages' in data and isinstance(data['pages'], str):
                import json
                try:
                    data['pages'] = json.loads(data['pages'])
                except:
                    pass

        if not data or 'pdf_base64' not in data:
            return jsonify({'success': False, 'error': 'pdf_base64 required'}), 400

        pdf_base64 = data.get('pdf_base64', '')
        pages_filter = data.get('pages', 'all')

        import pdfplumber
        from io import BytesIO

        pdf_bytes = base64.b64decode(pdf_base64)

        extracted_text = {}
        full_text = ""

        with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
            total_pages = len(pdf.pages)

            if pages_filter == 'all' or not pages_filter:
                pages_to_extract = range(total_pages)
            else:
                pages_to_extract = [p - 1 for p in pages_filter if 0 < p <= total_pages]

            for page_idx in pages_to_extract:
                page = pdf.pages[page_idx]
                text = page.extract_text() or ""
                page_num = page_idx + 1
                extracted_text[f'page_{page_num}'] = text
                full_text += text + "\n\n"

        logger.info(f'Extracted text from {len(extracted_text)} pages')

        return jsonify({
            'success': True,
            'text': full_text.strip(),
            'pages': extracted_text,
            'total_pages': total_pages,
            'character_count': len(full_text)
        }), 200

    except Exception as e:
        logger.error(f'Error extracting text: {str(e)}', exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/pdf/metadata', methods=['POST'])
def get_metadata():
    """
    Extract PDF metadata and information

    Accepts both JSON and form data.

    Expected body:
    {
        "pdf_base64": "base64 encoded PDF"
    }
    """
    try:
        logger.info('=== get_metadata called ===')

        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()

        if not data or 'pdf_base64' not in data:
            return jsonify({'success': False, 'error': 'pdf_base64 required'}), 400

        pdf_base64 = data.get('pdf_base64', '')

        from pypdf import PdfReader
        from io import BytesIO

        pdf_bytes = base64.b64decode(pdf_base64)
        pdf_reader = PdfReader(BytesIO(pdf_bytes))

        metadata = {}
        if pdf_reader.metadata:
            for key, value in pdf_reader.metadata.items():
                metadata[key] = str(value)

        page_info = []
        for idx, page in enumerate(pdf_reader.pages):
            page_info.append({
                'page_number': idx + 1,
                'width': float(page.mediabox.width),
                'height': float(page.mediabox.height),
                'rotation': page.get('/Rotate', 0)
            })

        logger.info(f'Extracted metadata from PDF with {len(pdf_reader.pages)} pages')

        return jsonify({
            'success': True,
            'metadata': metadata,
            'page_count': len(pdf_reader.pages),
            'pages': page_info,
            'file_size': len(pdf_bytes),
            'encrypted': pdf_reader.is_encrypted
        }), 200

    except Exception as e:
        logger.error(f'Error extracting metadata: {str(e)}', exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/pdf/watermark', methods=['POST'])
def add_watermark():
    """
    Add text watermark to PDF

    Accepts both JSON and form data.

    Expected body:
    {
        "pdf_base64": "base64 encoded PDF",
        "text": "CONFIDENTIAL",
        "opacity": 0.3 (optional, 0-1),
        "position": "center|diagonal" (optional, default: diagonal),
        "font_size": 60 (optional),
        "color": "gray|red|blue" (optional, default: gray)
    }
    """
    try:
        logger.info('=== add_watermark called ===')

        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()

        if not data or 'pdf_base64' not in data or 'text' not in data:
            return jsonify({'success': False, 'error': 'pdf_base64 and text required'}), 400

        pdf_base64 = data.get('pdf_base64', '')
        watermark_text = data.get('text', 'WATERMARK')
        opacity = float(data.get('opacity', 0.3))
        position = data.get('position', 'diagonal')
        font_size = int(data.get('font_size', 60))
        color = data.get('color', 'gray')
        filename = data.get('filename', 'watermarked.pdf')

        from pypdf import PdfReader, PdfWriter
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from io import BytesIO

        # Decode original PDF
        pdf_bytes = base64.b64decode(pdf_base64)
        pdf_reader = PdfReader(BytesIO(pdf_bytes))
        pdf_writer = PdfWriter()

        # Color mapping
        color_map = {
            'gray': colors.Color(0.5, 0.5, 0.5, alpha=opacity),
            'red': colors.Color(1, 0, 0, alpha=opacity),
            'blue': colors.Color(0, 0, 1, alpha=opacity),
            'black': colors.Color(0, 0, 0, alpha=opacity)
        }
        watermark_color = color_map.get(color, color_map['gray'])

        # Create watermark for each page
        for page in pdf_reader.pages:
            # Get page dimensions
            page_width = float(page.mediabox.width)
            page_height = float(page.mediabox.height)

            # Create watermark
            packet = BytesIO()
            can = canvas.Canvas(packet, pagesize=(page_width, page_height))
            can.setFillColor(watermark_color)
            can.setFont("Helvetica-Bold", font_size)

            if position == 'diagonal':
                can.saveState()
                can.translate(page_width / 2, page_height / 2)
                can.rotate(45)
                can.drawCentredString(0, 0, watermark_text)
                can.restoreState()
            else:  # center
                can.drawCentredString(page_width / 2, page_height / 2, watermark_text)

            can.save()

            # Merge watermark with page
            packet.seek(0)
            watermark_pdf = PdfReader(packet)
            page.merge_page(watermark_pdf.pages[0])
            pdf_writer.add_page(page)

        # Write output
        output = BytesIO()
        pdf_writer.write(output)
        watermarked_bytes = output.getvalue()

        watermarked_base64 = base64.b64encode(watermarked_bytes).decode('utf-8')

        logger.info(f'Added watermark to PDF: {filename} ({len(watermarked_bytes)} bytes)')

        return jsonify({
            'success': True,
            'pdf_base64': watermarked_base64,
            'pdf_size': len(watermarked_bytes),
            'filename': filename,
            'pages_processed': len(pdf_reader.pages)
        }), 200

    except Exception as e:
        logger.error(f'Error adding watermark: {str(e)}', exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/pdf/compress', methods=['POST'])
def compress_pdf():
    """
    Compress PDF to reduce file size

    Accepts both JSON and form data.

    Expected body:
    {
        "pdf_base64": "base64 encoded PDF",
        "quality": "high|medium|low" (optional, default: medium)
    }
    """
    try:
        logger.info('=== compress_pdf called ===')

        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()

        if not data or 'pdf_base64' not in data:
            return jsonify({'success': False, 'error': 'pdf_base64 required'}), 400

        pdf_base64 = data.get('pdf_base64', '')
        quality = data.get('quality', 'medium')
        filename = data.get('filename', 'compressed.pdf')

        from pypdf import PdfReader, PdfWriter
        from io import BytesIO

        pdf_bytes = base64.b64decode(pdf_base64)
        original_size = len(pdf_bytes)

        pdf_reader = PdfReader(BytesIO(pdf_bytes))
        pdf_writer = PdfWriter()

        # Copy all pages
        for page in pdf_reader.pages:
            pdf_writer.add_page(page)

        # Compress based on quality setting
        for page in pdf_writer.pages:
            if quality == 'low':
                page.compress_content_streams(level=9)
            elif quality == 'medium':
                page.compress_content_streams(level=6)
            else:  # high
                page.compress_content_streams(level=3)

        # Remove duplicate objects
        if hasattr(pdf_writer, 'remove_duplicates'):
            pdf_writer.remove_duplicates()

        # Write compressed PDF
        output = BytesIO()
        pdf_writer.write(output)
        compressed_bytes = output.getvalue()
        compressed_size = len(compressed_bytes)

        compression_ratio = ((original_size - compressed_size) / original_size * 100) if original_size > 0 else 0

        compressed_base64 = base64.b64encode(compressed_bytes).decode('utf-8')

        logger.info(f'Compressed PDF: {original_size} -> {compressed_size} bytes ({compression_ratio:.1f}% reduction)')

        return jsonify({
            'success': True,
            'pdf_base64': compressed_base64,
            'original_size': original_size,
            'compressed_size': compressed_size,
            'compression_ratio': round(compression_ratio, 2),
            'filename': filename
        }), 200

    except Exception as e:
        logger.error(f'Error compressing PDF: {str(e)}', exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/', methods=['GET'])
def index():
    """Service information endpoint"""
    return jsonify({
        'service': 'ZUGFeRD PDF Generator & PDF Services',
        'version': '3.0.0',
        'endpoints': {
            'health': 'GET /health - Health check',
            'test': 'GET /test - Test library compatibility',
            'test_pdf': 'GET /test-pdf-generation - Test PDF generation',
            'info': 'GET / - Service information',
            'zugferd': {
                'generate_pdf': 'POST /generate-pdf - Generate PDF from HTML',
                'generate_zugferd': 'POST /generate - Add ZUGFeRD XML to existing PDF',
                'generate_complete': 'POST /generate-complete - Generate PDF + ZUGFeRD in one step'
            },
            'pdf_manipulation': {
                'merge': 'POST /pdf/merge - Merge multiple PDFs',
                'split': 'POST /pdf/split - Split PDF by pages or ranges',
                'compress': 'POST /pdf/compress - Compress PDF to reduce size'
            },
            'pdf_extraction': {
                'extract_text': 'POST /pdf/extract-text - Extract text from PDF',
                'metadata': 'POST /pdf/metadata - Get PDF metadata and info'
            },
            'pdf_enhancement': {
                'watermark': 'POST /pdf/watermark - Add watermark to PDF'
            }
        },
        'features': [
            'ZUGFeRD/Factur-X compliant invoice generation',
            'HTML to PDF conversion',
            'PDF merge and split operations',
            'Text extraction from PDFs',
            'Watermarking and stamps',
            'PDF compression',
            'Metadata extraction',
            'Accepts both JSON and form data'
        ]
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
