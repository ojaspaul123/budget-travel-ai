import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether, PageBreak
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """Canvas that computes total pages dynamically for footer."""
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_header_footer(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 755, "Budget Travel AI — Complete Technical Documentation")
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.5)
            self.line(54, 747, 558, 747)
            
        # Footer
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 36, page_text)
        self.drawString(54, 36, "Confidential & Proprietary • Maintained by ojaspaul123")
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(54, 48, 558, 48)
        self.restoreState()

def generate_pdf(output_filename="Budget_Travel_AI_Documentation.pdf"):
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
    )

    styles = getSampleStyleSheet()

    # Custom Color Palette
    PRIMARY_TEAL = colors.HexColor("#0d9488")
    DARK_BLUE = colors.HexColor("#0f172a")
    TEXT_MAIN = colors.HexColor("#1e293b")
    BG_LIGHT = colors.HexColor("#f8fafc")
    BORDER_LIGHT = colors.HexColor("#e2e8f0")
    ACCENT_GREEN = colors.HexColor("#10b981")

    # Typography Styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=28,
        textColor=DARK_BLUE,
        spaceAfter=6,
    )
    
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=12,
        leading=16,
        textColor=PRIMARY_TEAL,
        spaceAfter=15,
    )

    h1_style = ParagraphStyle(
        "Heading1_Custom",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=19,
        textColor=DARK_BLUE,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True,
    )

    h2_style = ParagraphStyle(
        "Heading2_Custom",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        textColor=PRIMARY_TEAL,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True,
    )

    body_style = ParagraphStyle(
        "Body_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=TEXT_MAIN,
        spaceAfter=6,
    )

    bullet_style = ParagraphStyle(
        "Bullet_Custom",
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=3,
    )

    code_style = ParagraphStyle(
        "Code_Custom",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=8,
        leading=11,
        textColor=DARK_BLUE,
        backColor=BG_LIGHT,
        borderPadding=6,
        spaceBefore=4,
        spaceAfter=8,
    )

    callout_style = ParagraphStyle(
        "Callout_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=9,
        leading=13,
        textColor=DARK_BLUE,
        backColor=colors.HexColor("#f0fdfa"),
        borderPadding=8,
        spaceBefore=6,
        spaceAfter=8,
    )

    story = []

    # Title & Metadata Banner
    story.append(Paragraph("🧭 Budget Travel AI", title_style))
    story.append(Paragraph("Complete Technical Documentation & System Architecture Guide", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY_TEAL, spaceBefore=0, spaceAfter=12))

    # Metadata Box
    meta_data = [
        [
            Paragraph("<b>Version:</b> 2.0.0 (SPA + Vercel)", body_style),
            Paragraph("<b>Author / Maintainer:</b> ojaspaul123", body_style),
        ],
        [
            Paragraph("<b>Architecture:</b> FastAPI + Vanilla SPA", body_style),
            Paragraph("<b>Deployment:</b> Vercel Serverless", body_style),
        ]
    ]
    t_meta = Table(meta_data, colWidths=[245, 259])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 1, BORDER_LIGHT),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_LIGHT),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 10))

    # Section 1: Executive Summary
    story.append(Paragraph("1. Executive Summary", h1_style))
    story.append(Paragraph(
        "Mainstream mapping applications (such as Google Maps or Yelp) prioritize commercial visibility or general popularity, "
        "frequently burying budget-friendly eateries, student spots, and affordable lodging beneath high-cost establishments. "
        "<b>Budget Travel AI</b> solves this by layering deterministic price-tier normalization and rating-weighted scoring over the "
        "Google Places API (New), presented through a high-performance, single-page web app with interactive satellite maps.",
        body_style
    ))

    # Section 2: Key Benefits & Value Proposition
    story.append(Paragraph("2. Key Benefits & Value Proposition", h1_style))
    benefits = [
        "<b>Strict Budget Filtering:</b> Five explicit budget tiers (Free, Inexpensive $, Moderate $$, Expensive $$$, Any) ensure results match real travel budgets.",
        "<b>Zero-Friction Location Discovery:</b> Instant live location lookup via browser GPS geolocation or geocoding autocomplete for any global city/landmark.",
        "<b>Interactive Satellite Topo Map:</b> Seamless Leaflet map rendering Esri World Topo tiles (watermark-free, no tile API keys needed) with glowing budget pins.",
        "<b>1-Click Turn-by-Turn Directions:</b> Direct Google Maps deep navigation links embedded on every popup pin and place card.",
        "<b>Trip Bucket List:</b> Client-side trip bookmarking drawer powered by browser localStorage with session persistence.",
        "<b>Serverless & Production Ready:</b> Pre-configured with vercel.json for zero-maintenance Python serverless deployment.",
    ]
    for b in benefits:
        story.append(Paragraph(f"• {b}", bullet_style))

    # Section 3: Architecture & Tech Stack
    story.append(Paragraph("3. System Architecture & Tech Stack", h1_style))
    story.append(Paragraph(
        "The project follows a decoupled, cloud-ready architecture comprising an asynchronous FastAPI backend and a modern vanilla HTML5/CSS3/JavaScript single-page frontend:",
        body_style
    ))

    tech_table_data = [
        [Paragraph("<b>Component</b>", body_style), Paragraph("<b>Technology</b>", body_style), Paragraph("<b>Key Role & Responsibility</b>", body_style)],
        [Paragraph("Frontend UI", body_style), Paragraph("HTML5 + Vanilla CSS3", body_style), Paragraph("Dark glassmorphism design system, responsive cards, slide-out drawer.", body_style)],
        [Paragraph("Frontend Logic", body_style), Paragraph("Vanilla JavaScript (ES6+)", body_style), Paragraph("State management, debounced geocoding, filters, localStorage bucket list.", body_style)],
        [Paragraph("Geospatial Map", body_style), Paragraph("Leaflet.js 1.9.4", body_style), Paragraph("Interactive satellite map, glowing pins, search radius circle overlay.", body_style)],
        [Paragraph("Base Tiles", body_style), Paragraph("Esri ArcGIS World Topo", body_style), Paragraph("High-resolution, watermark-free topographic imagery with zero key cost.", body_style)],
        [Paragraph("API Backend", body_style), Paragraph("FastAPI (Python 3.10+)", body_style), Paragraph("Asynchronous REST endpoints, CORS middleware, Pydantic validation.", body_style)],
        [Paragraph("External APIs", body_style), Paragraph("Google Places & Geocoding", body_style), Paragraph("Places API (New) searchText endpoint and address geocoding.", body_style)],
        [Paragraph("Deployment", body_style), Paragraph("Vercel Serverless", body_style), Paragraph("@vercel/python serverless API + @vercel/static asset CDN.", body_style)],
    ]

    t_tech = Table(tech_table_data, colWidths=[95, 125, 284])
    t_tech.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0f172a")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_LIGHT),
        ('BOX', (0,0), (-1,-1), 1, BORDER_LIGHT),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_LIGHT]),
    ]))
    story.append(t_tech)
    story.append(Spacer(1, 10))

    # Section 4: End-to-End Workflow
    story.append(Paragraph("4. End-to-End Workflow", h1_style))
    workflow_steps = [
        "<b>1. Location Resolution:</b> User enters a query (e.g. 'Patia Bhubaneswar') triggering GET /api/geocode, or activates GPS to detect device latitude and longitude.",
        "<b>2. Search Query Execution:</b> User selects category, maximum budget tier, and search radius in km (0.5 to 25.0 km). Frontend posts payload to POST /api/search.",
        "<b>3. Google Places API Query:</b> Backend queries Google Places API (New) searchText endpoint requesting a field mask (id, displayName, location, priceLevel, rating, etc.).",
        "<b>4. Budget Filtering & Scoring:</b> Backend score_by_budget() normalizes raw prices, filters places exceeding max_budget_level, and sorts candidates by rating and review count.",
        "<b>5. Client-Side Geospatial Rendering:</b> Leaflet initializes Esri Satellite Topo map, centers on origin, draws the search radius boundary circle, and mounts glowing budget pins with rich interactive popups.",
    ]
    for ws in workflow_steps:
        story.append(Paragraph(ws, bullet_style))

    story.append(Spacer(1, 10))

    # Section 5: API Reference
    story.append(Paragraph("5. API Specifications & Contracts", h1_style))
    story.append(Paragraph("<b>POST /api/search</b> — Core Search & Budget Ranking Endpoint", h2_style))
    story.append(Paragraph("<b>Request Payload:</b>", body_style))
    story.append(Paragraph(
        '{\n'
        '  "query": "cafes",\n'
        '  "lat": 20.3605,\n'
        '  "lng": 85.8248,\n'
        '  "radius": 5000,\n'
        '  "max_budget_level": 2\n'
        '}',
        code_style
    ))
    story.append(Paragraph("<b>Response Payload (200 OK):</b>", body_style))
    story.append(Paragraph(
        '{\n'
        '  "count": 1,\n'
        '  "results": [\n'
        '    {\n'
        '      "id": "places/ChIJ...",\n'
        '      "name": "Two Hearts Cafe",\n'
        '      "address": "Patharagadia, Bhubaneswar, Odisha",\n'
        '      "rating": 4.9,\n'
        '      "user_rating_count": 1420,\n'
        '      "price_level": "Inexpensive",\n'
        '      "price_symbol": "$",\n'
        '      "price_score": 1,\n'
        '      "category": "Cafe",\n'
        '      "open_now": true,\n'
        '      "google_maps_url": "https://maps.google.com/...",\n'
        '      "location": {"latitude": 20.3612, "longitude": 85.8239}\n'
        '    }\n'
        '  ]\n'
        '}',
        code_style
    ))

    # Section 6: Deployment & Local Run
    story.append(Paragraph("6. Deployment & Local Execution", h1_style))
    story.append(Paragraph("<b>Running Locally (Single Command):</b>", h2_style))
    story.append(Paragraph(
        "# 1. Install dependencies\n"
        "pip install -r requirements.txt\n\n"
        "# 2. Configure .env with your Google Maps API Key\n"
        "echo GOOGLE_MAPS_API_KEY=your_key_here > .env\n\n"
        "# 3. Run the FastAPI server (Serves both API and Frontend at http://127.0.0.1:8000)\n"
        "python -m uvicorn app.main:app --reload",
        code_style
    ))

    story.append(Paragraph("<b>1-Click Vercel Deployment:</b>", h2_style))
    story.append(Paragraph(
        "1. Push repository to GitHub (`git push origin main`).<br/>"
        "2. Import repository on <b>vercel.com/new</b>.<br/>"
        "3. Under <b>Environment Variables</b>, set <code>GOOGLE_MAPS_API_KEY</code>.<br/>"
        "4. Click <b>Deploy</b>. Vercel automatically builds static assets and mounts serverless Python endpoints.",
        body_style
    ))

    # Section 7: Key Troubleshooting
    story.append(Paragraph("7. Key Troubleshooting & Engineering Learnings", h1_style))
    pitfalls = [
        "<b>Google Places API 400 Invalid Argument:</b> Passing <code>PRICE_LEVEL_FREE</code> inside Google's <code>priceLevels</code> request payload causes Google to reject the request. Solution: Query Google without payload price level restrictions and perform deterministic budget scoring in Python via <code>ranker.py</code>.",
        "<b>Map Watermark Restrictions:</b> Public CartoDB tile endpoints introduced API key/referrer requirements. Solution: Default to Esri World Topo Map for crystal clear satellite imagery with zero key requirements.",
        "<b>Payload Schema Differences:</b> Google raw API responses format names as <code>displayName.text</code>. Solution: Implemented <code>normalize_place()</code> to seamlessly support both legacy and normalized schemas.",
        "<b>CORS Interoperability:</b> Configured <code>CORSMiddleware</code> in <code>app/main.py</code> to allow external frontends on Vercel to query the backend securely.",
    ]
    for p in pitfalls:
        story.append(Paragraph(f"• {p}", bullet_style))

    story.append(Spacer(1, 15))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER_LIGHT, spaceBefore=0, spaceAfter=8))
    story.append(Paragraph("Budget Travel AI • Open Source Project • Created for High-Impact Travel Discovery", callout_style))

    # Build Document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF generated successfully: {output_filename}")

if __name__ == "__main__":
    generate_pdf()
