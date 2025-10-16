# ZUGFeRD API Service

Microservice zur Generierung von PDFs und ZUGFeRD-konformen PDFs für n8n Workflows.

## Features

- ✅ **PDF Generierung** aus HTML/CSS
- ✅ **ZUGFeRD Embedding** - Fügt XML zu bestehendem PDF hinzu
- ✅ **Komplett-Workflow** - Generiert PDF + ZUGFeRD in einem Schritt
- ✅ REST API für n8n Integration
- ✅ Docker-ready mit Health Checks
- ✅ Production-ready mit Gunicorn

## API Endpoints

### `GET /health`
**Health Check Endpoint** - Prüft ob der Service läuft

**Verwendung:** Monitoring, Docker Health Checks, Load Balancer

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
**PDF aus HTML generieren** - Konvertiert HTML/CSS zu einem PDF-Dokument

**Beschreibung:**
Dieser Endpoint generiert ein standardkonformes PDF aus HTML-Content. Ideal für die Erstellung von Rechnungen, Berichten oder anderen Dokumenten aus HTML-Templates.

**Request Body (JSON):**
```json
{
  "html_content": "<html><body><h1>Rechnung Nr. 2024-001</h1><p>Betrag: 1.234,56 €</p></body></html>",
  "css": "body { font-family: Arial, sans-serif; margin: 20px; } h1 { color: #333; }",
  "filename": "rechnung_2024_001.pdf"
}
```

**Parameter:**
- `html_content` (string, **erforderlich**): Vollständiger HTML-Code als String
- `css` (string, optional): CSS-Styles als String
- `filename` (string, optional): Dateiname für das generierte PDF (Standard: "document.pdf")

**Response (Success):**
```json
{
  "success": true,
  "pdf_base64": "JVBERi0xLjQKJe...",
  "pdf_size": 45821,
  "filename": "rechnung_2024_001.pdf"
}
```

**Response Felder:**
- `success` (boolean): `true` bei Erfolg
- `pdf_base64` (string): Base64-kodiertes PDF
- `pdf_size` (integer): Größe des PDFs in Bytes
- `filename` (string): Dateiname des generierten PDFs

**HTTP Status:** `200 OK` bei Erfolg, `400 Bad Request` bei fehlenden Parametern, `500 Internal Server Error` bei Verarbeitungsfehlern

**Use Cases:**
- Rechnungen aus HTML-Templates generieren
- Berichte als PDF exportieren
- Lieferscheine oder Angebote erstellen

---

### `POST /generate`
**ZUGFeRD XML zu bestehendem PDF hinzufügen** - Konvertiert ein Standard-PDF zu einem ZUGFeRD-konformen PDF

**Beschreibung:**
Dieser Endpoint fügt strukturierte ZUGFeRD-XML-Daten zu einem bereits existierenden PDF hinzu und erstellt damit eine maschinenlesbare, elektronische Rechnung nach dem ZUGFeRD-Standard (EN 16931).

**Request Body (JSON):**
```json
{
  "pdf_base64": "JVBERi0xLjQKJeLjz9MK...",
  "xml_content": "<?xml version='1.0' encoding='UTF-8'?><rsm:CrossIndustryInvoice xmlns:rsm=\"urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100\">...</rsm:CrossIndustryInvoice>",
  "filename": "rechnung_zugferd_2024_001.pdf"
}
```

**Parameter:**
- `pdf_base64` (string, **erforderlich**): Base64-kodiertes PDF-Dokument
- `xml_content` (string, **erforderlich**): ZUGFeRD/Factur-X XML als String (EN 16931 konform)
- `filename` (string, optional): Dateiname für das ZUGFeRD-PDF (Standard: "zugferd.pdf")

**Response (Success):**
```json
{
  "success": true,
  "zugferd_pdf_base64": "JVBERi0xLjQKJe...",
  "pdf_size": 48234,
  "filename": "rechnung_zugferd_2024_001.pdf"
}
```

**Response Felder:**
- `success` (boolean): `true` bei Erfolg
- `zugferd_pdf_base64` (string): Base64-kodiertes ZUGFeRD-PDF
- `pdf_size` (integer): Größe des ZUGFeRD-PDFs in Bytes
- `filename` (string): Dateiname des generierten ZUGFeRD-PDFs

**Technische Details:**
- Embedded File: XML wird als `factur-x.xml` im PDF eingebettet
- PDF/A-3 Metadaten werden hinzugefügt
- Kompatibel mit ZUGFeRD 2.x und Factur-X Standards

**HTTP Status:** `200 OK` bei Erfolg, `400 Bad Request` bei fehlenden/ungültigen Parametern, `500 Internal Server Error` bei Verarbeitungsfehlern

**Use Cases:**
- Bestehende PDF-Rechnungen ZUGFeRD-konform machen
- Maschinenlesbare Rechnungen für E-Invoicing erstellen
- Compliance mit deutschen E-Rechnungs-Anforderungen (ab 2025)

---

### `POST /generate-complete`
**PDF + ZUGFeRD in einem Schritt** - Generiert ein ZUGFeRD-PDF direkt aus HTML und XML

**Beschreibung:**
Dieser Endpoint kombiniert beide Funktionen: Generiert zuerst ein PDF aus HTML/CSS und fügt dann sofort die ZUGFeRD-XML-Daten hinzu. Ideal für End-to-End Workflows ohne Zwischenschritte.

**Request Body (JSON):**
```json
{
  "html_content": "<html><body><h1>Rechnung Nr. 2024-001</h1><table>...</table></body></html>",
  "css": "body { font-family: Arial; } table { border-collapse: collapse; width: 100%; }",
  "xml_content": "<?xml version='1.0' encoding='UTF-8'?><rsm:CrossIndustryInvoice>...</rsm:CrossIndustryInvoice>",
  "filename": "rechnung_komplett_2024_001.pdf"
}
```

**Parameter:**
- `html_content` (string, **erforderlich**): Vollständiger HTML-Code für die visuelle Rechnung
- `xml_content` (string, **erforderlich**): ZUGFeRD/Factur-X XML-Daten (EN 16931 konform)
- `css` (string, optional): CSS-Styles als String
- `filename` (string, optional): Dateiname für das ZUGFeRD-PDF (Standard: "zugferd.pdf")

**Response (Success):**
```json
{
  "success": true,
  "zugferd_pdf_base64": "JVBERi0xLjQKJe...",
  "pdf_size": 52103,
  "filename": "rechnung_komplett_2024_001.pdf"
}
```

**Response Felder:**
- `success` (boolean): `true` bei Erfolg
- `zugferd_pdf_base64` (string): Base64-kodiertes ZUGFeRD-PDF
- `pdf_size` (integer): Größe des finalen PDFs in Bytes
- `filename` (string): Dateiname des generierten ZUGFeRD-PDFs

**Workflow:**
1. HTML/CSS wird zu PDF konvertiert (via WeasyPrint)
2. ZUGFeRD-XML wird als Attachment eingebettet (via pypdf)
3. PDF/A-3 Metadaten werden gesetzt
4. Finales ZUGFeRD-PDF wird zurückgegeben

**HTTP Status:** `200 OK` bei Erfolg, `400 Bad Request` bei fehlenden/ungültigen Parametern, `500 Internal Server Error` bei Verarbeitungsfehlern

**Use Cases:**
- Komplette ZUGFeRD-Rechnungen aus einem n8n Workflow erstellen
- Automatisierte E-Invoicing-Lösung
- Integration in ERP/Warenwirtschaftssysteme

---

### `GET /`
**Service Information** - Zeigt verfügbare Endpoints und Version

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
**Diagnose-Endpoint** - Testet Library-Kompatibilität

**Beschreibung:**
Interner Test-Endpoint um die Funktionalität aller verwendeten Libraries zu prüfen.

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
