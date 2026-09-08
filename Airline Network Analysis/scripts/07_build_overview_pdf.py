from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image,
                                 Table, TableStyle, PageBreak, HRFlowable)
from reportlab.lib.enums import TA_LEFT, TA_CENTER

BASE = "/home/claude/airline-network-analysis"
CHARTS = f"{BASE}/outputs/charts"
OUT = f"{BASE}/Project_Overview.pdf"

NAVY = colors.HexColor("#0b3d91")
GREY = colors.HexColor("#5b6472")
LIGHT = colors.HexColor("#f4f6f9")
GREEN = colors.HexColor("#1a7f37")
RED = colors.HexColor("#d1453b")

styles = getSampleStyleSheet()
styles.add(ParagraphStyle("H1", parent=styles["Heading1"], fontSize=20, textColor=NAVY,
                           spaceAfter=10, spaceBefore=4))
styles.add(ParagraphStyle("H2", parent=styles["Heading2"], fontSize=14, textColor=NAVY,
                           spaceAfter=8, spaceBefore=16))
styles.add(ParagraphStyle("Body", parent=styles["Normal"], fontSize=10.3, leading=15,
                           textColor=colors.HexColor("#1a1f27"), spaceAfter=8))
styles.add(ParagraphStyle("Caption", parent=styles["Normal"], fontSize=8.5, leading=11,
                           textColor=GREY, alignment=TA_CENTER, spaceAfter=14))
styles.add(ParagraphStyle("Cover title", parent=styles["Title"], fontSize=26, textColor=NAVY,
                           spaceAfter=6))
styles.add(ParagraphStyle("Cover sub", parent=styles["Normal"], fontSize=12.5, textColor=GREY,
                           alignment=TA_LEFT, spaceAfter=4))
styles.add(ParagraphStyle("BulletItem", parent=styles["Body"], leftIndent=14, bulletIndent=2,
                           spaceAfter=5))

story = []

# ---------------------------------------------------------------- Cover
story.append(Spacer(1, 1.6 * inch))
story.append(Paragraph("Airline Route Network", styles["Cover title"]))
story.append(Paragraph("Profitability &amp; Optimization Analysis", styles["Cover title"]))
story.append(Spacer(1, 0.25 * inch))
story.append(HRFlowable(width="100%", thickness=1.2, color=NAVY))
story.append(Spacer(1, 0.2 * inch))
story.append(Paragraph("Project Overview — Goal, Background &amp; Key Findings", styles["Cover sub"]))
story.append(Paragraph("Srushti Gandhi", styles["Cover sub"]))
story.append(Paragraph("Portfolio Project — Airline / Aviation Analytics", styles["Cover sub"]))
story.append(PageBreak())

# ---------------------------------------------------------------- Goal
story.append(Paragraph("1. Goal", styles["H2"]))
story.append(Paragraph(
    "The goal of this project is to answer a question a real airline network-planning "
    "analyst is asked every quarter: <b>which routes should the airline expand, maintain, "
    "watch, or cut?</b> Instead of looking at one metric in isolation (like total revenue), "
    "the project builds a full picture of each route by combining route-level profitability, "
    "operational efficiency (load factor), demand trend, and each route's structural "
    "importance to the overall network — then turns that into a ranked, actionable "
    "recommendation list.", styles["Body"]))
story.append(Paragraph(
    "It was also built specifically as a portfolio piece for entry-level data/business "
    "analyst roles in the airline and aviation industry, to show both technical range "
    "(Python data pipelines, network/graph analysis, dashboarding) and business framing "
    "(every output is tied to a decision, not just a chart).", styles["Body"]))

# ---------------------------------------------------------------- Background
story.append(Paragraph("2. How I Came Across This Problem", styles["H2"]))
story.append(Paragraph(
    "I've been building out a portfolio of analytics projects (sales forecasting, job "
    "market analytics) while job-searching for entry-level data analyst roles, and wanted "
    "one project that spoke directly to an industry I'm genuinely interested in breaking "
    "into: airlines. Most analytics portfolio projects in this space stop at flight-delay "
    "prediction, which is heavily saturated on Kaggle and LinkedIn. Network planning — the "
    "question of which routes an airline should fly, add, or drop — is the actual "
    "commercial decision airlines make constantly, and it's a much less commonly "
    "portfolio-ed problem, which made it a better fit for standing out.", styles["Body"]))
story.append(Paragraph(
    "The standard public data source for this kind of analysis is the US DOT/Bureau of "
    "Transportation Statistics T-100 Domestic Segment dataset, which every real airline "
    "network-planning team uses. This version of the project uses a synthetic dataset "
    "generated to match that dataset's structure and realistic route economics (see the "
    "Technical Walkthrough PDF and README for details, and for how to swap in the live "
    "BTS data).", styles["Body"]))

# ---------------------------------------------------------------- Approach summary
story.append(Paragraph("3. Approach, in Brief", styles["H2"]))
approach_items = [
    "<b>Data:</b> 25-airport network (5 hubs, 20 spokes), 234 routes, 4 quarters of route-level traffic, pricing, and cost data.",
    "<b>Metrics engineered:</b> yield (revenue per passenger-mile), RASM (revenue per available seat mile), operating margin, and a seasonality index — the standard metrics airline network planners use.",
    "<b>Network analysis:</b> modeled the route map as a graph with <font face='Courier'>networkx</font> to find each airport's structural importance (centrality) and test network resilience if a hub is disrupted.",
    "<b>Scoring model:</b> combined profitability, load factor, demand growth, and network value into a single Route Health Score, then classified every route into EXPAND / MAINTAIN / MONITOR / CUT relative to the rest of the portfolio.",
    "<b>Output:</b> an interactive dashboard, a ranked action list, and a set of new-route recommendations based on unmet connecting demand.",
]
for item in approach_items:
    story.append(Paragraph(f"• {item}", styles["BulletItem"]))

story.append(PageBreak())

# ---------------------------------------------------------------- Findings
story.append(Paragraph("4. What I Discovered", styles["H2"]))

story.append(Paragraph("4.1 The network runs a healthy but uneven portfolio", styles["Body"]))
kpi_data = [
    ["Metric", "Value"],
    ["Total annual operating profit (network-wide)", "$484.8M"],
    ["Blended operating margin", "36.2%"],
    ["Average load factor", "80.3%"],
    ["Routes flagged EXPAND", "47 of 234 (20%)"],
    ["Routes flagged CUT / RESTRUCTURE", "47 of 234 (20%)"],
]
t = Table(kpi_data, colWidths=[3.6 * inch, 2.4 * inch])
t.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), NAVY),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 9.5),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d0d7de")),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("TOPPADDING", (0, 0), (-1, -1), 6),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
]))
story.append(t)
story.append(Spacer(1, 10))
story.append(Paragraph(
    "The network is profitable overall, but the 20/20 split between EXPAND and CUT "
    "candidates shows profitability isn't evenly spread — a fifth of the portfolio is "
    "carrying disproportionate value while another fifth is quietly dragging on network "
    "efficiency, even though every individual route was profitable in absolute terms.", styles["Body"]))

story.append(Paragraph("4.2 Seattle is the most structurally important airport in the network", styles["Body"]))
story.append(Paragraph(
    "Graph centrality analysis (eigenvector centrality) ranked Seattle-Tacoma (SEA) as the "
    "single most influential airport in the network — ahead of larger legacy hubs like "
    "Atlanta and Chicago O'Hare. This wasn't obvious from raw traffic volume alone; it only "
    "showed up once the network was modeled as a graph, which is exactly the kind of insight "
    "that route-level revenue tables miss.", styles["Body"]))
story.append(Image(f"{CHARTS}/pdf_centrality.png", width=6.4 * inch, height=3.55 * inch))
story.append(Paragraph("Figure 1 — Airport network influence (eigenvector centrality)", styles["Caption"]))

story.append(Paragraph("4.3 Profitable routes and healthy routes aren't the same thing", styles["Body"]))
story.append(Paragraph(
    "The highest-profit routes (e.g. Seattle–JFK at $7.1M/year) aren't automatically the "
    "healthiest. A handful of routes with strong absolute profit (Denver–Kansas City, "
    "LA–Chicago) still landed in the bottom margin quintile, because they're being carried "
    "by volume rather than efficiency — a distinction that matters for an airline deciding "
    "where to invest in additional capacity versus where to hold steady.", styles["Body"]))
story.append(Image(f"{CHARTS}/pdf_top10_profit.png", width=6.0 * inch, height=3.4 * inch))
story.append(Paragraph("Figure 2 — Top 10 routes by annual operating profit, colored by recommendation", styles["Caption"]))

story.append(PageBreak())

story.append(Paragraph("4.4 Demand is seasonal, and it's not uniform across the network", styles["Body"]))
story.append(Paragraph(
    "Network-wide passenger volume peaks in Q3 (summer) and dips in Q1, as expected for a "
    "US domestic network — but leisure-heavy routes into Las Vegas, Miami, and Phoenix "
    "actually peak in Q1 instead, which matters for how the airline should staff and price "
    "capacity differently by route type rather than applying one seasonal curve network-wide.", styles["Body"]))
story.append(Image(f"{CHARTS}/pdf_seasonal_demand.png", width=5.6 * inch, height=3.2 * inch))
story.append(Paragraph("Figure 3 — Network-wide seasonal demand curve", styles["Caption"]))

story.append(Paragraph("4.5 The network has hub redundancy — but O'Hare is the most exposed", styles["Body"]))
story.append(Paragraph(
    "Simulating the removal of each hub showed the network retains 96% connectivity "
    "regardless of which hub is disrupted, since the other four hubs still connect to every "
    "spoke — a sign of a genuinely resilient hub-and-spoke design. Chicago O'Hare came out "
    "as the (marginally) most exposed hub, which is a useful flag for contingency and "
    "schedule-resilience planning.", styles["Body"]))
story.append(Image(f"{CHARTS}/pdf_resilience.png", width=5.4 * inch, height=3.1 * inch))
story.append(Paragraph("Figure 4 — % of network still connected if each hub is removed", styles["Caption"]))

story.append(Paragraph("4.6 There's a clear, data-backed case for at least one new route", styles["Body"]))
story.append(Paragraph(
    "By looking for spoke-to-spoke city pairs with no existing direct route but high "
    "estimated connecting demand through shared hubs, the network graph flagged "
    "<b>Los Angeles – Phoenix</b> as the strongest new-route candidate (~76,000 estimated "
    "annual connecting passengers today with no nonstop option), followed closely by "
    "LA–Miami and Miami–Boston.", styles["Body"]))
story.append(Image(f"{CHARTS}/pdf_new_route_candidates.png", width=6.2 * inch, height=3.5 * inch))
story.append(Paragraph("Figure 5 — Top new nonstop route candidates by estimated connecting demand", styles["Caption"]))

story.append(PageBreak())

# ---------------------------------------------------------------- Takeaways
story.append(Paragraph("5. Why This Matters (Business Takeaway)", styles["H2"]))
takeaways = [
    "A route can be profitable and still be unhealthy — margin and efficiency separate the routes worth investing in from the ones just riding volume.",
    "Network position (centrality) is invisible in a standard revenue report but changes which routes actually matter strategically — SEA outranking ATL and ORD is the clearest example.",
    "Seasonality isn't one curve for the whole network — leisure routes and business routes move in opposite directions, and pricing/staffing decisions should reflect that.",
    "The network already has strong resilience to hub disruption, which is worth confirming rather than assuming.",
    "Graph-based demand estimation (not just historical route revenue) surfaces new-route opportunities that a simple leaderboard of existing routes would never show, since the opportunity is in a route that doesn't exist yet.",
]
for item in takeaways:
    story.append(Paragraph(f"• {item}", styles["BulletItem"]))

story.append(Spacer(1, 14))
story.append(HRFlowable(width="100%", thickness=0.6, color=colors.HexColor("#d0d7de")))
story.append(Spacer(1, 8))
story.append(Paragraph(
    "Full technical implementation details are in the companion document, "
    "<i>Technical_Walkthrough.pdf</i>. All code, data, and the interactive dashboard are "
    "included in this project folder.", styles["Caption"]))

doc = SimpleDocTemplate(OUT, pagesize=letter,
                         topMargin=0.7 * inch, bottomMargin=0.7 * inch,
                         leftMargin=0.75 * inch, rightMargin=0.75 * inch,
                         title="Airline Route Network Analysis - Project Overview")
doc.build(story)
print(f"Saved -> {OUT}")
