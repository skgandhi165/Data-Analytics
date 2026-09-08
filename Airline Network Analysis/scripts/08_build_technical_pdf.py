from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image,
                                 Table, TableStyle, PageBreak, HRFlowable, ListFlowable, ListItem)
from reportlab.lib.enums import TA_LEFT, TA_CENTER

BASE = "/home/claude/airline-network-analysis"
CHARTS = f"{BASE}/outputs/charts"
OUT = f"{BASE}/Technical_Walkthrough.pdf"

NAVY = colors.HexColor("#0b3d91")
GREY = colors.HexColor("#5b6472")
LIGHT = colors.HexColor("#f4f6f9")
CODE_BG = colors.HexColor("#0d1117")
CODE_FG = colors.HexColor("#c9d1d9")

styles = getSampleStyleSheet()
styles.add(ParagraphStyle("H1", parent=styles["Heading1"], fontSize=20, textColor=NAVY, spaceAfter=10))
styles.add(ParagraphStyle("StepTitle", parent=styles["Heading2"], fontSize=14, textColor=NAVY,
                           spaceAfter=6, spaceBefore=18))
styles.add(ParagraphStyle("Body", parent=styles["Normal"], fontSize=10.3, leading=15,
                           textColor=colors.HexColor("#1a1f27"), spaceAfter=7))
styles.add(ParagraphStyle("Caption", parent=styles["Normal"], fontSize=8.5, leading=11,
                           textColor=GREY, alignment=TA_CENTER, spaceAfter=14))
styles.add(ParagraphStyle("Cover title", parent=styles["Title"], fontSize=24, textColor=NAVY, spaceAfter=6))
styles.add(ParagraphStyle("Cover sub", parent=styles["Normal"], fontSize=12.5, textColor=GREY, spaceAfter=4))
styles.add(ParagraphStyle("CodeBlock", parent=styles["Normal"], fontName="Courier", fontSize=8.6,
                           leading=12, textColor=CODE_FG, backColor=CODE_BG,
                           leftIndent=8, rightIndent=8, spaceBefore=4, spaceAfter=10,
                           borderPadding=8))
styles.add(ParagraphStyle("SubBullet", parent=styles["Body"], leftIndent=14, spaceAfter=4))
styles.add(ParagraphStyle("WhyBox", parent=styles["Body"], backColor=LIGHT, borderPadding=8,
                           leftIndent=6, rightIndent=6, spaceAfter=10))

story = []

# ---------------------------------------------------------------- Cover
story.append(Spacer(1, 1.6 * inch))
story.append(Paragraph("Airline Route Network Analysis", styles["Cover title"]))
story.append(Paragraph("Technical Walkthrough", styles["Cover title"]))
story.append(Spacer(1, 0.2 * inch))
story.append(HRFlowable(width="100%", thickness=1.2, color=NAVY))
story.append(Spacer(1, 0.2 * inch))
story.append(Paragraph("A step-by-step explanation of how the project was built, written for my own "
                        "reference so I can walk through and explain every decision in an interview.",
                        styles["Cover sub"]))
story.append(Paragraph("Srushti Gandhi", styles["Cover sub"]))
story.append(PageBreak())

# ---------------------------------------------------------------- Pipeline overview
story.append(Paragraph("Pipeline Overview", styles["H1"]))
story.append(Paragraph(
    "The project runs as six sequential scripts, each reading the previous step's output. "
    "This mirrors a real analytics pipeline: raw data in, clean/scored data out, then "
    "visualization on top.", styles["Body"]))

pipeline_data = [
    ["Script", "What it does", "Input → Output"],
    ["01_generate_data.py", "Builds the route dataset", "— → raw/t100_style_route_data.csv"],
    ["02_data_pipeline.py", "Cleans data, engineers metrics", "raw CSV → processed/routes_clean.csv, routes_annual.csv"],
    ["03_network_analysis.py", "Graph/network analysis", "routes_annual.csv → airport_centrality.csv, network_summary.json"],
    ["04_profitability_model.py", "Scores + classifies routes", "annual + centrality → routes_scored.csv"],
    ["05_visualizations.py", "Builds interactive dashboard", "scored data → dashboard.html + interactive charts"],
    ["06_static_charts_for_pdf.py", "Builds PNGs for this PDF", "scored data → static PNG charts"],
]
t = Table(pipeline_data, colWidths=[1.75 * inch, 1.75 * inch, 2.9 * inch])
t.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), NAVY),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTNAME", (0, 1), (0, -1), "Courier"),
    ("FONTSIZE", (0, 0), (0, -1), 6.6),
    ("FONTSIZE", (1, 0), (-1, -1), 7.8),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d0d7de")),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("TOPPADDING", (0, 0), (-1, -1), 5),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
]))
story.append(t)
story.append(PageBreak())

# ---------------------------------------------------------------- Step 1
story.append(Paragraph("Step 1 — Generate the Dataset", styles["StepTitle"]))
story.append(Paragraph(
    "<b>Script:</b> <font face='Courier'>01_generate_data.py</font>", styles["Body"]))
story.append(Paragraph(
    "I built a synthetic dataset shaped like the real BTS T-100 Domestic Segment dataset, "
    "since I didn't have live internet access to pull the real file in this environment. "
    "The structure: 5 hub airports + 20 spoke airports, connected in a hub-and-spoke pattern "
    "(every hub flies to every spoke, hubs connect to each other, plus a few high-demand "
    "spoke-to-spoke leisure routes), across 4 quarters.", styles["Body"]))
story.append(Paragraph(
    "For each route-quarter, I simulated: departures, seats, load factor (with seasonality "
    "built in), passengers, average fare (using a yield-per-mile model where shorter/thinner "
    "routes charge more per mile), revenue, and operating cost (using a cost-per-available-"
    "seat-mile model where costs go down on longer routes — the real 'stage-length effect' "
    "in airline economics, where fixed costs like taxi/boarding amortize over more miles).",
    styles["Body"]))
story.append(Paragraph(
    "<b>Why it matters:</b> I made sure the simulation had real airline economics baked in "
    "(stage-length cost effect, seasonal leisure vs. business demand, hub premium pricing) "
    "rather than just random numbers — that's what makes the downstream analysis meaningful "
    "instead of noise. On a real job, this step would just be pd.read_csv() on the actual "
    "BTS download.", styles["WhyBox"]))

# ---------------------------------------------------------------- Step 2
story.append(Paragraph("Step 2 — Clean the Data &amp; Engineer Metrics", styles["StepTitle"]))
story.append(Paragraph(
    "<b>Script:</b> <font face='Courier'>02_data_pipeline.py</font>", styles["Body"]))
story.append(Paragraph("Cleaning:", styles["Body"]))
story.append(Paragraph("• Dropped rows with nulls or non-physical values (zero/negative passengers, seats, or distance)", styles["SubBullet"]))
story.append(Paragraph("• Dropped any row with a load factor over 100% (a data-quality guardrail, even though the simulator shouldn't produce this)", styles["SubBullet"]))
story.append(Paragraph("Metrics engineered (the same ones a real network-planning analyst uses):", styles["Body"]))
story.append(Paragraph("• <b>ASM</b> (Available Seat Miles) = seats × distance — total flying capacity", styles["SubBullet"]))
story.append(Paragraph("• <b>RPM</b> (Revenue Passenger Miles) = passengers × distance — capacity actually sold", styles["SubBullet"]))
story.append(Paragraph("• <b>RASM</b> = revenue ÷ ASM — revenue efficiency per unit of capacity flown", styles["SubBullet"]))
story.append(Paragraph("• <b>Yield</b> = revenue ÷ RPM — price per passenger-mile actually flown", styles["SubBullet"]))
story.append(Paragraph("• <b>Operating margin</b> = (revenue − op. cost) ÷ revenue", styles["SubBullet"]))
story.append(Paragraph(
    "Then I rolled the 4 quarterly rows per route up into one annual row per route "
    "(groupby origin/dest, sum the volume fields, recompute the ratio fields from the "
    "summed totals rather than averaging the ratios directly — averaging percentages "
    "would have been a mistake here). I also computed a seasonality index per route as "
    "(max quarter − min quarter) ÷ mean, to flag which routes swing the most seasonally.",
    styles["Body"]))
story.append(Paragraph(
    "<b>Why it matters:</b> This is the step I'd get asked about most in an interview — "
    "why RASM/yield instead of just revenue, and why I recomputed ratios post-aggregation "
    "instead of averaging them. Recomputing avoids Simpson's-paradox-style distortion where "
    "a route with one huge quarter and three tiny ones gets an average margin that doesn't "
    "reflect its actual annual economics.", styles["WhyBox"]))

story.append(PageBreak())

# ---------------------------------------------------------------- Step 3
story.append(Paragraph("Step 3 — Network / Graph Analysis", styles["StepTitle"]))
story.append(Paragraph(
    "<b>Script:</b> <font face='Courier'>03_network_analysis.py</font> (uses "
    "<font face='Courier'>networkx</font>)", styles["Body"]))
story.append(Paragraph(
    "This is the differentiating piece of the project — most portfolio analytics projects "
    "never touch graph theory. I modeled the airline's route map as a directed, weighted "
    "graph: airports are nodes, routes are edges, and each edge is weighted by passenger "
    "volume.", styles["Body"]))
story.append(Paragraph("Three analyses on top of the graph:", styles["Body"]))
story.append(Paragraph(
    "1. <b>Centrality</b> — degree centrality (how many routes an airport has, weighted by "
    "volume), betweenness centrality (how often an airport sits on the shortest path between "
    "other airport pairs), and eigenvector centrality (an airport's influence, weighted by "
    "how influential its neighbors are — this is the same family of algorithm behind Google's "
    "original PageRank). Eigenvector centrality is what I used as the network value score, "
    "since it captures 'strategically important,' not just 'busy.'", styles["SubBullet"]))
story.append(Paragraph(
    "2. <b>Resilience simulation</b> — for each hub, I removed it from the graph and measured "
    "what % of the remaining airports could still reach each other. This is a simple stand-in "
    "for a real disruption-planning question: if weather shuts down a hub, how much of the "
    "network still functions?", styles["SubBullet"]))
story.append(Paragraph(
    "3. <b>New-route candidate detection</b> — I looked at every spoke-to-spoke pair with no "
    "existing direct route, and estimated the 'implied connecting demand' by looking at how "
    "many passengers already fly through a shared hub to get between those two cities "
    "(assuming roughly 35% of hub-connecting passengers would switch to a nonstop if one "
    "existed). Pairs with high implied demand and no current nonstop are the new-route "
    "candidates.", styles["SubBullet"]))
story.append(Paragraph(
    "<b>Why it matters:</b> This is the section I'd walk an interviewer through in the most "
    "detail, since it's the part that shows I can think beyond flat tables. A revenue "
    "leaderboard alone would never have surfaced Seattle as more structurally important than "
    "Atlanta, or flagged LA–Phoenix as a missing route — both only show up once you model the "
    "network as a graph.", styles["WhyBox"]))

# ---------------------------------------------------------------- Step 4
story.append(Paragraph("Step 4 — Profitability / Route Health Scoring Model", styles["StepTitle"]))
story.append(Paragraph(
    "<b>Script:</b> <font face='Courier'>04_profitability_model.py</font>", styles["Body"]))
story.append(Paragraph(
    "I combined four signals into one composite <b>Route Health Score</b> (0–100), each "
    "min-max normalized across the portfolio first so they're comparable:", styles["Body"]))
score_data = [
    ["Signal", "Weight", "Why this weight"],
    ["Operating margin", "40%", "Profitability is still the primary driver of a real add/cut decision"],
    ["Load factor", "25%", "Operational efficiency — a route can be profitable but fragile if it's barely full"],
    ["Q1→Q4 passenger growth", "20%", "Momentum matters — a growing route is worth more than a flat one at the same margin"],
    ["Network value (centrality)", "15%", "Strategic fit — some routes are worth protecting even at a thinner margin, because they feed the rest of the network"],
]
t2 = Table(score_data, colWidths=[1.75 * inch, 0.7 * inch, 3.95 * inch])
t2.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), NAVY),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 8.3),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d0d7de")),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("TOPPADDING", (0, 0), (-1, -1), 5),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
]))
story.append(t2)
story.append(Spacer(1, 10))
story.append(Paragraph(
    "I classified routes into EXPAND / MAINTAIN / MONITOR / CUT by quantile within the "
    "portfolio (top 20% / next 30% / next 30% / bottom 20%) rather than a fixed score "
    "cutoff — this matters because a fixed cutoff (e.g. 'score ≥ 70 = EXPAND') can produce "
    "an empty or lopsided bucket depending on how the portfolio happens to be distributed. "
    "Quantile-based classification is also how real network-planning teams actually screen "
    "a portfolio each quarter: relative to the rest of the current network, not against an "
    "arbitrary absolute bar.", styles["Body"]))

story.append(PageBreak())

# ---------------------------------------------------------------- Step 5
story.append(Paragraph("Step 5 — Dashboard &amp; Visualizations", styles["StepTitle"]))
story.append(Paragraph(
    "<b>Scripts:</b> <font face='Courier'>05_visualizations.py</font> (interactive, Plotly) "
    "and <font face='Courier'>06_static_charts_for_pdf.py</font> (static, matplotlib)",
    styles["Body"]))
story.append(Paragraph(
    "I built two versions of the same charts on purpose: interactive Plotly charts combined "
    "into a single-page HTML dashboard (for the live portfolio-site link, and as a stand-in "
    "for what would be a Power BI dashboard in a real company environment with Power BI "
    "access), and static matplotlib PNGs for this PDF and for the project card image on my "
    "portfolio site.", styles["Body"]))
story.append(Paragraph("The dashboard includes:", styles["Body"]))
story.append(Paragraph("• A US route map, color-coded by recommendation, line thickness scaled to profit", styles["SubBullet"]))
story.append(Paragraph("• Top/bottom routes by profit and margin", styles["SubBullet"]))
story.append(Paragraph("• Seasonal demand trend", styles["SubBullet"]))
story.append(Paragraph("• Airport centrality ranking", styles["SubBullet"]))
story.append(Paragraph("• Recommendation mix (donut)", styles["SubBullet"]))
story.append(Paragraph("• New route candidates", styles["SubBullet"]))
story.append(Paragraph(
    "<b>Why it matters:</b> I also exported a Power BI-ready CSV "
    "(outputs/exports/route_action_list.csv) alongside the HTML dashboard, so this project "
    "can show up two ways on my resume/portfolio: as a live clickable dashboard link, and as "
    "a 'built the model in Python, visualized in Power BI' story if I want to actually open "
    "the export in Power BI Desktop and screenshot it.", styles["WhyBox"]))

story.append(Image(f"{CHARTS}/pdf_recommendation_mix.png", width=4.3 * inch, height=4.3 * inch))
story.append(Paragraph("Figure — Route portfolio recommendation mix, as shown on the dashboard", styles["Caption"]))

story.append(PageBreak())

# ---------------------------------------------------------------- Reproducing / extending
story.append(Paragraph("How to Re-Run or Extend This", styles["StepTitle"]))
story.append(Paragraph("To rebuild everything from scratch:", styles["Body"]))
story.append(Paragraph(
    "pip install pandas numpy networkx plotly matplotlib<br/>"
    "python scripts/01_generate_data.py<br/>"
    "python scripts/02_data_pipeline.py<br/>"
    "python scripts/03_network_analysis.py<br/>"
    "python scripts/04_profitability_model.py<br/>"
    "python scripts/05_visualizations.py<br/>"
    "python scripts/06_static_charts_for_pdf.py",
    styles["CodeBlock"]))
story.append(Paragraph(
    "To use real data instead of the synthetic set: download T-100 Domestic Segment data "
    "from transtats.bts.gov, save it in the same column shape as "
    "data/raw/t100_style_route_data.csv, and re-run from Step 2 onward.", styles["Body"]))
story.append(Paragraph("Possible extensions if I want to go further with this later:", styles["Body"]))
story.append(Paragraph("• Add a real ML model (e.g. predict next quarter's load factor per route) instead of the rule-based scoring model", styles["SubBullet"]))
story.append(Paragraph("• Pull live BTS data and compare synthetic vs. real network structure", styles["SubBullet"]))
story.append(Paragraph("• Add fuel price sensitivity to the cost model", styles["SubBullet"]))
story.append(Paragraph("• Build the actual .pbix Power BI file once I have access to Power BI Desktop", styles["SubBullet"]))

doc = SimpleDocTemplate(OUT, pagesize=letter,
                         topMargin=0.7 * inch, bottomMargin=0.7 * inch,
                         leftMargin=0.75 * inch, rightMargin=0.75 * inch,
                         title="Airline Route Network Analysis - Technical Walkthrough")
doc.build(story)
print(f"Saved -> {OUT}")
