# ZUGFeRD API Service

Microservice zur Erstellung von ZUGFeRD-PDFs für n8n Workflows.

## Features

- ✅ Konvertiert Standard-PDFs zu ZUGFeRD-konformen PDFs
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

### `POST /generate`
Generiert ZUGFeRD PDF aus PDF + XML

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

### cURL Beispiel

```bash
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "pdf_base64": "JVBERi0xLjQKJeLjz9MK...",
    "xml_content": "<?xml version=\"1.0\" encoding=\"UTF-8\"?><rsm:CrossIndustryInvoice>...</rsm:CrossIndustryInvoice>",
    "filename": "rechnung_2024_001.pdf"
  }'
```

### n8n Integration

1. **HTTP Request Node** konfigurieren:
   - Method: POST
   - URL: `http://zugferd-api:5000/generate`
   - Body: JSON
   - JSON Beispiel:
```json
{
  "pdf_base64": "{{ $json.pdf_base64 }}",
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
