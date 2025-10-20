# ZUGFeRD API Service & PDF Manipulation Tools

Comprehensive microservice for generating PDFs, ZUGFeRD-compliant invoices, and advanced PDF manipulation for n8n workflows.

## Features

### ZUGFeRD & Invoice Generation
- ✅ **PDF Generation** from HTML/CSS
- ✅ **ZUGFeRD Embedding** - Add XML to existing PDFs
- ✅ **Complete Workflow** - Generate PDF + ZUGFeRD in one step

### PDF Manipulation
- ✅ **Merge PDFs** - Combine multiple PDFs into one
- ✅ **Split PDFs** - Extract pages or split by ranges
- ✅ **Compress PDFs** - Reduce file size with quality control
- ✅ **Watermarking** - Add text watermarks with customization
- ✅ **Text Extraction** - Extract text from PDFs
- ✅ **Metadata** - Get PDF information and properties

### Infrastructure
- ✅ REST API for n8n integration
- ✅ Accepts both JSON and form data
- ✅ Docker-ready with health checks
- ✅ Production-ready with Gunicorn

## API Endpoints

### `GET /health`
**Health Check Endpoint** - Checks if the service is running

**Usage:** Monitoring, Docker health checks, load balancers

**Response:**
```json
{
  "status": "healthy",
  "service": "zugferd-generator"
}
```

**HTTP Status:** `200 OK`

---

### `POST /generate-pdf`
**Generate PDF from HTML** - Converts HTML/CSS to a PDF document

**Description:**
This endpoint generates a standards-compliant PDF from HTML content. Ideal for creating invoices, reports, or other documents from HTML templates.

**Request Body (JSON):**
```json
{
  "html_content": "<html><body><h1>Invoice No. 2024-001</h1><p>Amount: $1,234.56</p></body></html>",
  "css": "body { font-family: Arial, sans-serif; margin: 20px; } h1 { color: #333; }",
  "filename": "invoice_2024_001.pdf"
}
```

**Parameters:**
- `html_content` (string, **required**): Complete HTML code as string
- `css` (string, optional): CSS styles as string
- `filename` (string, optional): Filename for the generated PDF (default: "document.pdf")

**Response (Success):**
```json
{
  "success": true,
  "pdf_base64": "JVBERi0xLjQKJe...",
  "pdf_size": 45821,
  "filename": "invoice_2024_001.pdf"
}
```

**Response Fields:**
- `success` (boolean): `true` on success
- `pdf_base64` (string): Base64-encoded PDF
- `pdf_size` (integer): Size of PDF in bytes
- `filename` (string): Filename of the generated PDF

**HTTP Status:** `200 OK` on success, `400 Bad Request` for missing parameters, `500 Internal Server Error` for processing errors

**Use Cases:**
- Generate invoices from HTML templates
- Export reports as PDF
- Create delivery notes or quotes

---

### `POST /generate`
**Add ZUGFeRD XML to existing PDF** - Converts a standard PDF to a ZUGFeRD-compliant PDF

**Description:**
This endpoint adds structured ZUGFeRD XML data to an existing PDF, creating a machine-readable electronic invoice according to the ZUGFeRD standard (EN 16931).

**Request Body (JSON):**
```json
{
  "pdf_base64": "JVBERi0xLjQKJeLjz9MK...",
  "xml_content": "<?xml version='1.0' encoding='UTF-8'?><rsm:CrossIndustryInvoice xmlns:rsm=\"urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100\">...</rsm:CrossIndustryInvoice>",
  "filename": "invoice_zugferd_2024_001.pdf"
}
```

**Parameters:**
- `pdf_base64` (string, **required**): Base64-encoded PDF document
- `xml_content` (string, **required**): ZUGFeRD/Factur-X XML as string (EN 16931 compliant)
- `filename` (string, optional): Filename for the ZUGFeRD PDF (default: "zugferd.pdf")

**Response (Success):**
```json
{
  "success": true,
  "zugferd_pdf_base64": "JVBERi0xLjQKJe...",
  "pdf_size": 48234,
  "filename": "invoice_zugferd_2024_001.pdf"
}
```

**Response Fields:**
- `success` (boolean): `true` on success
- `zugferd_pdf_base64` (string): Base64-encoded ZUGFeRD PDF
- `pdf_size` (integer): Size of ZUGFeRD PDF in bytes
- `filename` (string): Filename of the generated ZUGFeRD PDF

**Technical Details:**
- Embedded File: XML is embedded as `factur-x.xml` in the PDF
- PDF/A-3 metadata is added
- Compatible with ZUGFeRD 2.x and Factur-X standards

**HTTP Status:** `200 OK` on success, `400 Bad Request` for missing/invalid parameters, `500 Internal Server Error` for processing errors

**Use Cases:**
- Make existing PDF invoices ZUGFeRD-compliant
- Create machine-readable invoices for e-invoicing
- Compliance with German e-invoice requirements (from 2025)

---

### `POST /generate-complete`
**PDF + ZUGFeRD in one step** - Generates a ZUGFeRD PDF directly from HTML and XML

**Description:**
This endpoint combines both functions: first generates a PDF from HTML/CSS, then immediately adds the ZUGFeRD XML data. Ideal for end-to-end workflows without intermediate steps.

**Request Body (JSON):**
```json
{
  "html_content": "<html><body><h1>Invoice No. 2024-001</h1><table>...</table></body></html>",
  "css": "body { font-family: Arial; } table { border-collapse: collapse; width: 100%; }",
  "xml_content": "<?xml version='1.0' encoding='UTF-8'?><rsm:CrossIndustryInvoice>...</rsm:CrossIndustryInvoice>",
  "filename": "invoice_complete_2024_001.pdf"
}
```

**Parameters:**
- `html_content` (string, **required**): Complete HTML code for the visual invoice
- `xml_content` (string, **required**): ZUGFeRD/Factur-X XML data (EN 16931 compliant)
- `css` (string, optional): CSS styles as string
- `filename` (string, optional): Filename for the ZUGFeRD PDF (default: "zugferd.pdf")

**Response (Success):**
```json
{
  "success": true,
  "zugferd_pdf_base64": "JVBERi0xLjQKJe...",
  "pdf_size": 52103,
  "filename": "invoice_complete_2024_001.pdf"
}
```

**Response Fields:**
- `success` (boolean): `true` on success
- `zugferd_pdf_base64` (string): Base64-encoded ZUGFeRD PDF
- `pdf_size` (integer): Size of the final PDF in bytes
- `filename` (string): Filename of the generated ZUGFeRD PDF

**Workflow:**
1. HTML/CSS is converted to PDF (via WeasyPrint)
2. ZUGFeRD XML is embedded as attachment (via pypdf)
3. PDF/A-3 metadata is set
4. Final ZUGFeRD PDF is returned

**HTTP Status:** `200 OK` on success, `400 Bad Request` for missing/invalid parameters, `500 Internal Server Error` for processing errors

**Use Cases:**
- Create complete ZUGFeRD invoices from an n8n workflow
- Automated e-invoicing solution
- Integration with ERP/business management systems

---

## PDF Manipulation Endpoints

### `POST /pdf/merge`
**Merge Multiple PDFs** - Combine multiple PDF files into one document

**Description:**
Merges 2 or more PDF files into a single PDF while maintaining all pages and content.

**Request Body (JSON or Form Data):**
```json
{
  "pdfs": ["base64_pdf1", "base64_pdf2", "base64_pdf3"],
  "filename": "merged_document.pdf"
}
```

**Parameters:**
- `pdfs` (array, **required**): Array of base64-encoded PDF files (minimum 2)
- `filename` (string, optional): Output filename (default: "merged.pdf")

**Response (Success):**
```json
{
  "success": true,
  "pdf_base64": "JVBERi0xLjQKJe...",
  "pdf_size": 125890,
  "filename": "merged_document.pdf",
  "page_count": 15
}
```

**Use Cases:**
- Combine monthly invoices into one file
- Merge invoice with attachments or delivery notes
- Create combined reports

---

### `POST /pdf/split`
**Split PDF** - Split PDF into multiple files or extract specific pages

**Description:**
Extracts specific pages or ranges from a PDF, creating separate PDF files.

**Request Body (JSON or Form Data):**
```json
{
  "pdf_base64": "JVBERi0xLjQKJe...",
  "mode": "pages",
  "pages": [1, 3, 5],
  "filename_prefix": "invoice"
}
```

**OR for page ranges:**
```json
{
  "pdf_base64": "JVBERi0xLjQKJe...",
  "mode": "ranges",
  "ranges": [[1, 3], [4, 6], [7, 10]],
  "filename_prefix": "section"
}
```

**Parameters:**
- `pdf_base64` (string, **required**): Base64-encoded PDF
- `mode` (string): "pages" or "ranges" (default: "pages")
- `pages` (array): Array of page numbers to extract (for mode="pages")
- `ranges` (array): Array of [start, end] page ranges (for mode="ranges")
- `filename_prefix` (string, optional): Prefix for output files (default: "split")

**Response (Success):**
```json
{
  "success": true,
  "pdfs": [
    {
      "pdf_base64": "JVBERi0...",
      "filename": "invoice_page_1.pdf",
      "pages": [1],
      "size": 15230
    },
    {
      "pdf_base64": "JVBERi0...",
      "filename": "invoice_page_3.pdf",
      "pages": [3],
      "size": 14890
    }
  ],
  "total_pages": 10,
  "split_count": 2
}
```

**Use Cases:**
- Extract individual invoices from batch file
- Separate cover pages from main document
- Split multi-page documents for processing

---

### `POST /pdf/extract-text`
**Extract Text from PDF** - Extract text content from PDF pages

**Description:**
Extracts all text from a PDF, optionally from specific pages. Returns both full text and per-page text.

**Request Body (JSON or Form Data):**
```json
{
  "pdf_base64": "JVBERi0xLjQKJe...",
  "pages": [1, 2, 3]
}
```

**Parameters:**
- `pdf_base64` (string, **required**): Base64-encoded PDF
- `pages` (array or "all", optional): Page numbers to extract or "all" (default: all)

**Response (Success):**
```json
{
  "success": true,
  "text": "Invoice No. 2024-001\n\nDate: 2024-01-15...",
  "pages": {
    "page_1": "Invoice No. 2024-001...",
    "page_2": "Items:\n1. Product A..."
  },
  "total_pages": 2,
  "character_count": 1523
}
```

**Use Cases:**
- Validate invoice content
- Search for specific text in documents
- Extract data for processing
- Archive text content

---

### `POST /pdf/metadata`
**Get PDF Metadata** - Extract PDF properties and information

**Description:**
Returns detailed metadata about the PDF including page count, dimensions, metadata fields, and encryption status.

**Request Body (JSON or Form Data):**
```json
{
  "pdf_base64": "JVBERi0xLjQKJe..."
}
```

**Parameters:**
- `pdf_base64` (string, **required**): Base64-encoded PDF

**Response (Success):**
```json
{
  "success": true,
  "metadata": {
    "/Title": "Invoice 2024-001",
    "/Author": "futalis GmbH",
    "/Creator": "Microsoft Word",
    "/CreationDate": "D:20240115120000"
  },
  "page_count": 3,
  "pages": [
    {
      "page_number": 1,
      "width": 595.0,
      "height": 842.0,
      "rotation": 0
    }
  ],
  "file_size": 45820,
  "encrypted": false
}
```

**Use Cases:**
- Validate PDF properties
- Check document author/creator
- Verify page dimensions
- Audit document information

---

### `POST /pdf/watermark`
**Add Watermark** - Add text watermark to PDF pages

**Description:**
Adds a customizable text watermark to all pages of a PDF. Supports diagonal or centered positioning with adjustable opacity, size, and color.

**Request Body (JSON or Form Data):**
```json
{
  "pdf_base64": "JVBERi0xLjQKJe...",
  "text": "CONFIDENTIAL",
  "opacity": 0.3,
  "position": "diagonal",
  "font_size": 60,
  "color": "gray",
  "filename": "watermarked_invoice.pdf"
}
```

**Parameters:**
- `pdf_base64` (string, **required**): Base64-encoded PDF
- `text` (string, **required**): Watermark text
- `opacity` (float, optional): Transparency 0-1 (default: 0.3)
- `position` (string, optional): "diagonal" or "center" (default: "diagonal")
- `font_size` (integer, optional): Font size in points (default: 60)
- `color` (string, optional): "gray", "red", "blue", "black" (default: "gray")
- `filename` (string, optional): Output filename (default: "watermarked.pdf")

**Response (Success):**
```json
{
  "success": true,
  "pdf_base64": "JVBERi0xLjQKJe...",
  "pdf_size": 48230,
  "filename": "watermarked_invoice.pdf",
  "pages_processed": 3
}
```

**Use Cases:**
- Mark invoices as "PAID" or "DRAFT"
- Add "CONFIDENTIAL" to sensitive documents
- Add company branding or stamps
- Document tracking and security

---

### `POST /pdf/compress`
**Compress PDF** - Reduce PDF file size

**Description:**
Compresses PDF to reduce file size with adjustable quality settings. Removes duplicate objects and compresses content streams.

**Request Body (JSON or Form Data):**
```json
{
  "pdf_base64": "JVBERi0xLjQKJe...",
  "quality": "medium",
  "filename": "compressed_invoice.pdf"
}
```

**Parameters:**
- `pdf_base64` (string, **required**): Base64-encoded PDF
- `quality` (string, optional): "high", "medium", or "low" (default: "medium")
  - `high`: Light compression, best quality
  - `medium`: Balanced compression
  - `low`: Maximum compression, smaller file
- `filename` (string, optional): Output filename (default: "compressed.pdf")

**Response (Success):**
```json
{
  "success": true,
  "pdf_base64": "JVBERi0xLjQKJe...",
  "original_size": 125890,
  "compressed_size": 89420,
  "compression_ratio": 28.95,
  "filename": "compressed_invoice.pdf"
}
```

**Use Cases:**
- Reduce file size for email attachments
- Optimize for web viewing
- Save storage space
- Meet file size limits

---

### `GET /`
**Service Information** - Shows available endpoints and version

**Response:**
```json
{
  "service": "ZUGFeRD PDF Generator & PDF Services",
  "version": "3.0.0",
  "endpoints": {
    "health": "GET /health - Health check",
    "test": "GET /test - Test library compatibility",
    "info": "GET / - Service information",
    "zugferd": {
      "generate_pdf": "POST /generate-pdf - Generate PDF from HTML",
      "generate_zugferd": "POST /generate - Add ZUGFeRD XML to existing PDF",
      "generate_complete": "POST /generate-complete - Generate PDF + ZUGFeRD in one step"
    },
    "pdf_manipulation": {
      "merge": "POST /pdf/merge - Merge multiple PDFs",
      "split": "POST /pdf/split - Split PDF by pages or ranges",
      "compress": "POST /pdf/compress - Compress PDF to reduce size"
    },
    "pdf_extraction": {
      "extract_text": "POST /pdf/extract-text - Extract text from PDF",
      "metadata": "POST /pdf/metadata - Get PDF metadata and info"
    },
    "pdf_enhancement": {
      "watermark": "POST /pdf/watermark - Add watermark to PDF"
    }
  },
  "features": [
    "ZUGFeRD/Factur-X compliant invoice generation",
    "HTML to PDF conversion",
    "PDF merge and split operations",
    "Text extraction from PDFs",
    "Watermarking and stamps",
    "PDF compression",
    "Metadata extraction",
    "Accepts both JSON and form data"
  ]
}
```

---

### `GET /test`
**Diagnostic Endpoint** - Tests library compatibility

**Description:**
Internal test endpoint to verify the functionality of all used libraries.

**Response:**
```json
{
  "python_version": "3.11.14 (main, Oct  9 2025, 22:39:13) [GCC 14.2.0]",
  "tests": {
    "weasyprint_import": "OK",
    "pypdf_import": "OK",
    "html_to_pdf": "OK (2516 bytes)",
    "lxml_version": "6.0.2"
  }
}
```

## Installation

### Docker (Recommended)

```bash
# Build
docker build -t zugferd-api .

# Run
docker run -d -p 5000:5000 --name zugferd-api zugferd-api

# Test
curl http://localhost:5000/health
```

### Local

```bash
# Install dependencies
pip install -r requirements.txt

# Start server
python app.py
```

## Usage

### cURL Examples

**Generate PDF from HTML:**
```bash
curl -X POST http://localhost:5000/generate-pdf \
  -H "Content-Type: application/json" \
  -d '{
    "html_content": "<html><body><h1>Test Invoice</h1><p>Amount: $100</p></body></html>",
    "css": "body { font-family: Arial; }",
    "filename": "invoice.pdf"
  }'
```

**Add ZUGFeRD to existing PDF:**
```bash
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "pdf_base64": "JVBERi0xLjQKJeLjz9MK...",
    "xml_content": "<?xml version=\"1.0\" encoding=\"UTF-8\"?><rsm:CrossIndustryInvoice>...</rsm:CrossIndustryInvoice>",
    "filename": "invoice_zugferd.pdf"
  }'
```

**Complete workflow (PDF + ZUGFeRD):**
```bash
curl -X POST http://localhost:5000/generate-complete \
  -H "Content-Type: application/json" \
  -d '{
    "html_content": "<html><body><h1>Invoice</h1></body></html>",
    "xml_content": "<?xml version=\"1.0\" encoding=\"UTF-8\"?>...",
    "filename": "invoice_complete.pdf"
  }'
```

### n8n Integration

#### Workflow 1: Generate PDF only
**HTTP Request Node:**
- Method: POST
- URL: `http://zugferd-api:5000/generate-pdf`
- Body: JSON
```json
{
  "html_content": "{{ $json.html_content }}",
  "css": "{{ $json.css }}",
  "filename": "{{ $json.filename }}"
}
```

#### Workflow 2: PDF + ZUGFeRD in one step
**HTTP Request Node:**
- Method: POST
- URL: `http://zugferd-api:5000/generate-complete`
- Body: JSON
```json
{
  "html_content": "{{ $json.html_content }}",
  "xml_content": "{{ $json.xml_content }}",
  "filename": "{{ $json.filename }}"
}
```

## Deployment

### Docker Compose

```yaml
version: '3.8'
services:
  zugferd-api:
    build: .
    ports:
      - "5000:5000"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 3s
      retries: 3
```

### Environment Variables

No environment variables required. Service is ready to use immediately.

## Development

```bash
# Install dev dependencies
pip install -r requirements.txt

# Run with auto-reload
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=5000
```

## Error Handling

All errors are returned with appropriate HTTP status codes:

- `400` - Invalid request (missing parameters, invalid base64)
- `500` - Server error (PDF generation failed)

## License

Proprietary - futalis GmbH

## Support

For questions: IT Team futalis GmbH
