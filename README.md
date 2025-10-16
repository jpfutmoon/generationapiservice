# ZUGFeRD API Service

Microservice for generating PDFs and ZUGFeRD-compliant PDFs for n8n workflows.

## Features

- ✅ **PDF Generation** from HTML/CSS
- ✅ **ZUGFeRD Embedding** - Add XML to existing PDFs
- ✅ **Complete Workflow** - Generate PDF + ZUGFeRD in one step
- ✅ REST API for n8n integration
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

### `GET /`
**Service Information** - Shows available endpoints and version

**Response:**
```json
{
  "service": "ZUGFeRD PDF Generator",
  "version": "2.0.0",
  "endpoints": {
    "health": "GET /health",
    "test": "GET /test - Test library compatibility",
    "generate_pdf": "POST /generate-pdf - Generate PDF from HTML",
    "generate_zugferd": "POST /generate - Add ZUGFeRD XML to existing PDF",
    "generate_complete": "POST /generate-complete - Generate PDF + ZUGFeRD in one step",
    "info": "GET /"
  }
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
