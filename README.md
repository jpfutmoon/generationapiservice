# ZUGFeRD API Service

Microservice zur Generierung von PDFs und ZUGFeRD-konformen PDFs für n8n Workflows.

## Features

- ✅ **PDF Generierung** aus HTML/CSS
- ✅ **ZUGFeRD Embedding** - Fügt XML zu bestehendem PDF hinzu
- ✅ **Komplett-Workflow** - Generiert PDF + ZUGFeRD in einem Schritt
- ✅ REST API für n8n Integration
- ✅ Docker-ready mit Health Checks
- ✅ Production-ready mit Gunicorn

## Endpoints

### `GET /health`
Health Check für Monitoring und Docker

**Response:**
```json
{
  "status": "healthy",
  "service": "zugferd-generator"
}
```

### `POST /generate-pdf`
**NEU:** Generiert PDF aus HTML Content

**Request:**
```json
{
  "html_content": "<html><body><h1>Rechnung</h1></body></html>",
  "css": "body { font-family: Arial; }",
  "filename": "rechnung.pdf"
}
```

**Response:**
```json
{
  "success": true,
  "pdf_base64": "JVBERi0xLjQKJe...",
  "pdf_size": 45821,
  "filename": "rechnung.pdf"
}
```

### `POST /generate`
Generiert ZUGFeRD PDF aus bestehendem PDF + XML

**Request:**
```json
{
  "pdf_base64": "JVBERi0xLjQKJeLjz9...",
  "xml_content": "<?xml version='1.0' encoding='UTF-8'?>...",
  "filename": "rechnung_123.pdf"
}
```

**Response:**
```json
{
  "success": true,
  "zugferd_pdf_base64": "JVBERi0xLjQKJe...",
  "pdf_size": 45821,
  "filename": "rechnung_123.pdf"
}
```

### `POST /generate-complete`
**NEU:** Generiert PDF aus HTML und fügt ZUGFeRD XML in einem Schritt hinzu

**Request:**
```json
{
  "html_content": "<html><body><h1>Rechnung</h1></body></html>",
  "css": "body { font-family: Arial; }",
  "xml_content": "<?xml version='1.0' encoding='UTF-8'?>...",
  "filename": "rechnung_zugferd.pdf"
}
```

**Response:**
```json
{
  "success": true,
  "zugferd_pdf_base64": "JVBERi0xLjQKJe...",
  "pdf_size": 45821,
  "filename": "rechnung_zugferd.pdf"
}
```

### `GET /`
Service Informationen

## Installation

### Docker (empfohlen)

```bash
# Build
docker build -t zugferd-api .

# Run
docker run -d -p 5000:5000 --name zugferd-api zugferd-api

# Test
curl http://localhost:5000/health
```

### Lokal

```bash
# Dependencies installieren
pip install -r requirements.txt

# Server starten
python app.py
```

## Usage

### cURL Beispiele

**PDF aus HTML generieren:**
```bash
curl -X POST http://localhost:5000/generate-pdf \
  -H "Content-Type: application/json" \
  -d '{
    "html_content": "<html><body><h1>Test Rechnung</h1><p>Betrag: 100€</p></body></html>",
    "css": "body { font-family: Arial; }",
    "filename": "rechnung.pdf"
  }'
```

**ZUGFeRD zu bestehendem PDF hinzufügen:**
```bash
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "pdf_base64": "JVBERi0xLjQKJeLjz9MK...",
    "xml_content": "<?xml version=\"1.0\" encoding=\"UTF-8\"?><rsm:CrossIndustryInvoice>...</rsm:CrossIndustryInvoice>",
    "filename": "rechnung_zugferd.pdf"
  }'
```

**Komplett-Workflow (PDF + ZUGFeRD):**
```bash
curl -X POST http://localhost:5000/generate-complete \
  -H "Content-Type: application/json" \
  -d '{
    "html_content": "<html><body><h1>Rechnung</h1></body></html>",
    "xml_content": "<?xml version=\"1.0\" encoding=\"UTF-8\"?>...",
    "filename": "rechnung_komplett.pdf"
  }'
```

### n8n Integration

#### Workflow 1: Nur PDF generieren
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

#### Workflow 2: PDF + ZUGFeRD in einem Schritt
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

Keine Environment Variables erforderlich. Service ist sofort einsatzbereit.

## Development

```bash
# Install dev dependencies
pip install -r requirements.txt

# Run with auto-reload
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=5000
```

## Error Handling

Alle Fehler werden mit entsprechenden HTTP Status Codes zurückgegeben:

- `400` - Invalid request (missing parameters, invalid base64)
- `500` - Server error (PDF generation failed)

## License

Proprietary - futalis GmbH

## Support

Bei Fragen: IT Team futalis GmbH
