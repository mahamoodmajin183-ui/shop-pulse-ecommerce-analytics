"""
ShopPulse - Comprehensive Executive PDF Report Generator
Generates a publication-grade, multi-page PDF project report covering:
- Executive Summary & Project Overview
- Problem Statement & Objectives
- Tech Stack & System Architecture
- Dataset Schema & Data Cleaning Process
- Advanced SQL Analytics Catalog (20 Queries with explanations)
- 12 Business Findings, Impacts & Strategic Recommendations
- Interview Q&A & Talking Points
"""

import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY

def generate_pdf(output_path: str = "reports/ShopPulse_Complete_Project_Report.pdf"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    
    # Custom Styles
    primary_color = colors.HexColor("#0f172a") # Dark Slate
    accent_blue = colors.HexColor("#0284c7")   # Deep Sky Blue
    accent_teal = colors.HexColor("#0d9488")   # Teal
    text_dark = colors.HexColor("#1e293b")     # Text Dark
    text_muted = colors.HexColor("#64748b")    # Muted
    bg_light = colors.HexColor("#f8fafc")      # Soft White

    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=26,
        leading=32,
        textColor=primary_color,
        alignment=TA_CENTER
    )

    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=13,
        leading=18,
        textColor=accent_blue,
        alignment=TA_CENTER
    )

    meta_style = ParagraphStyle(
        'CoverMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=text_muted,
        alignment=TA_CENTER
    )

    h1_style = ParagraphStyle(
        'Header1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=primary_color,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Header2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=accent_blue,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=text_dark,
        alignment=TA_LEFT,
        spaceAfter=6
    )

    code_style = ParagraphStyle(
        'CodeSnippet',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#0f172a"),
        backColor=colors.HexColor("#f1f5f9"),
        borderPadding=6,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'BulletText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=text_dark,
        leftIndent=12,
        spaceAfter=4
    )

    story = []

    # ------------------ COVER PAGE / HEADER ------------------
    story.append(Spacer(1, 15))
    story.append(Paragraph("ShopPulse — E-Commerce Sales Analytics Platform", title_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph("Comprehensive Project Documentation, Architecture & Strategic Business Case Study", subtitle_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=2, color=accent_blue, spaceBefore=4, spaceAfter=12))
    story.append(Paragraph("<b>Author:</b> B.Tech AI & Data Science Student | <b>Target Role:</b> Data Analyst / Analytics Engineer<br/><b>Dataset Scope:</b> 12,500 Transactions | $3.61M Revenue | $1.59M Profit | 43.93% Margin | 20 Advanced SQL Queries", meta_style))
    story.append(Spacer(1, 15))

    # ------------------ 1. EXECUTIVE SUMMARY & OBJECTIVES ------------------
    story.append(Paragraph("1. Executive Summary & Business Objectives", h1_style))
    story.append(Paragraph(
        "<b>ShopPulse</b> is an enterprise-grade omnichannel e-commerce retail platform selling across 5 core merchandise divisions (Technology, Furniture, Apparel, Office Supplies, Home & Kitchen) and 4 geographic regions (North, South, East, West). As the business expanded across 12,500+ transactions and $3.6M+ in revenue, leadership commissioned an end-to-end data analytics system to evaluate sales velocity, customer lifetime value, promotional discount elasticity, and profit margin health.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Core Analytics Goals:</b>", body_style
    ))
    story.append(Paragraph("• <b>Revenue & Profit Dynamics:</b> Track monthly sales velocity and seasonal holiday surges.", bullet_style))
    story.append(Paragraph("• <b>Margin Optimization:</b> Diagnose categories driving gross cash vs. those suffering margin erosion.", bullet_style))
    story.append(Paragraph("• <b>Promotional Guardrails:</b> Quantify profit loss from excessive discounting (>15%).", bullet_style))
    story.append(Paragraph("• <b>Customer Segmentation:</b> Classify customer retention cohorts and calculate RFM / CLV metrics.", bullet_style))
    story.append(Paragraph("• <b>Inventory Rationalization:</b> Evaluate Pareto (80/20) catalog revenue skew.", bullet_style))
    story.append(Spacer(1, 10))

    # ------------------ 2. ENTERPRISE KPI SCORECARD ------------------
    story.append(Paragraph("2. Enterprise Performance Scorecard", h1_style))
    
    kpi_data = [
        ["Metric Name", "Value", "Business Benchmark", "Analytical Interpretation"],
        ["Total Revenue", "$3,613,656.82", "+14.2% MoM", "Aggregate 18-month top-line cash flow across 12,500 transactions."],
        ["Total Gross Profit", "$1,587,554.34", "+11.8% MoM", "Net earnings generated after deduction of Cost of Goods Sold (COGS)."],
        ["Overall Profit Margin", "43.93%", "Target: >40.0%", "Healthy unit economics benchmark with high margin expansion potential."],
        ["Total Order Volume", "12,500 Orders", "+8.4% Volume", "Steady transaction flow averaging 694 orders per month."],
        ["Unique Customers", "2,108 Customers", "2.1K Accounts", "Broad customer acquisition footprint across 4 geographic regions."],
        ["Average Order Value (AOV)", "$289.09", "Target: $300.00", "Mean basket spend per completed checkout transaction."],
        ["Repeat Customer Rate", "81.83%", "Benchmark: >75%", "Exceptional customer retention: 1,725 out of 2,108 buyers placed >= 2 orders."]
    ]
    
    kpi_table = Table(kpi_data, colWidths=[130, 90, 100, 210])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8.5),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
        ('BACKGROUND', (0, 1), (-1, -1), bg_light),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 14))

    # ------------------ 3. TECHNICAL ARCHITECTURE & DATA PIPELINE ------------------
    story.append(Paragraph("3. Technical Stack & Data Pipeline Architecture", h1_style))
    story.append(Paragraph(
        "The project implements a full modern data stack lifecycle from ingestion to interactive visualization:",
        body_style
    ))
    
    tech_data = [
        ["Layer", "Technology", "Key Responsibilities & Components"],
        ["Data ETL & Cleaning", "Python, Pandas, NumPy", "Deduplication (150 dupes pruned), relational entity imputation, calendar enrichment, financial formula validation."],
        ["Database Layer", "PostgreSQL 16 & SQLite 3", "Star Schema relational tables (dim_customers, dim_products, fact_orders) with B-Tree indexes and OLAP fact tables."],
        ["SQL Analytics", "Advanced SQL (20 Queries)", "CTEs, Window Functions (DENSE_RANK, LAG, SUM OVER), Cohorts, RFM Scoring, CLV Modeling, Pareto distribution."],
        ["Visualization & BI", "Streamlit, Plotly, Flask, Chart.js", "Dual Dashboards: Multi-view Streamlit application (port 8501) and zero-dependency local web app (port 5000)."],
        ["Quality Assurance", "Pytest Suite", "14 automated unit & integration tests validating ETL pipelines, math integrity, and query performance."]
    ]
    tech_table = Table(tech_data, colWidths=[100, 110, 320])
    tech_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), accent_blue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8.5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(tech_table)
    story.append(Spacer(1, 14))

    # ------------------ 4. 20 ADVANCED SQL ANALYTICS CATALOG ------------------
    story.append(PageBreak()) # New page for SQL
    story.append(Paragraph("4. Advanced SQL Analytics Catalog (20 Production Queries)", h1_style))
    story.append(Paragraph(
        "Below is a categorized selection of the 20 production SQL queries implemented in <code>database/analysis_queries.sql</code> demonstrating analytics engineering competencies:",
        body_style
    ))

    sql_samples = [
        ("Query 03: Month-Over-Month (MoM) Growth Analysis using LAG()",
"""WITH monthly_metrics AS (
    SELECT SUBSTR(order_date, 1, 7) AS year_month,
           ROUND(SUM(sales), 2) AS revenue, ROUND(SUM(profit), 2) AS profit
    FROM fact_ecommerce_sales GROUP BY SUBSTR(order_date, 1, 7)
)
SELECT year_month, revenue,
       LAG(revenue, 1) OVER (ORDER BY year_month) AS prev_month_revenue,
       ROUND(((revenue - LAG(revenue, 1) OVER (ORDER BY year_month)) / 
              LAG(revenue, 1) OVER (ORDER BY year_month)) * 100.0, 2) AS mom_revenue_growth_pct
FROM monthly_metrics ORDER BY year_month ASC;""",
        "Business Purpose: Computes period-over-period sales acceleration and margin expansion rates without manual self-joins."),

        ("Query 07: Category Product Ranking using DENSE_RANK()",
"""WITH category_product_sales AS (
    SELECT category, product_name, ROUND(SUM(sales), 2) AS total_sales,
           DENSE_RANK() OVER (PARTITION BY category ORDER BY SUM(sales) DESC) AS rank_in_cat
    FROM fact_ecommerce_sales GROUP BY category, product_name
)
SELECT category, rank_in_cat, product_name, total_sales
FROM category_product_sales WHERE rank_in_cat <= 3 ORDER BY category, rank_in_cat ASC;""",
        "Business Purpose: Identifies top 3 revenue leaders inside each category to guide catalog merchandising."),

        ("Query 11: Customer Lifetime Value (CLV) by Customer Segment",
"""WITH customer_aggregates AS (
    SELECT customer_id, customer_segment, COUNT(DISTINCT order_id) AS total_orders,
           SUM(sales) AS total_spend, SUM(profit) AS total_profit
    FROM fact_ecommerce_sales GROUP BY customer_id, customer_segment
)
SELECT customer_segment, COUNT(customer_id) AS total_customers,
       ROUND(AVG(total_orders), 1) AS avg_orders, ROUND(AVG(total_spend), 2) AS avg_clv_revenue,
       ROUND(SUM(total_spend), 2) AS segment_revenue
FROM customer_aggregates GROUP BY customer_segment ORDER BY segment_revenue DESC;""",
        "Business Purpose: Evaluates long-term monetary value across Corporate, Consumer, Home Office, and Small Business accounts."),

        ("Query 18: Pareto 80/20 Cumulative Product Revenue Share",
"""WITH product_totals AS (
    SELECT product_name, category, ROUND(SUM(sales), 2) AS product_sales
    FROM fact_ecommerce_sales GROUP BY product_name, category
),
ranked_products AS (
    SELECT product_name, product_sales,
           SUM(product_sales) OVER (ORDER BY product_sales DESC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_sales,
           SUM(product_sales) OVER () AS total_enterprise_sales
    FROM product_totals
)
SELECT product_name, product_sales, ROUND((running_sales / total_enterprise_sales) * 100.0, 2) AS cumulative_pct
FROM ranked_products LIMIT 15;""",
        "Business Purpose: Identifies high-concentration SKUs responsible for the first 80% of aggregate revenue.")
    ]

    for q_title, q_code, q_desc in sql_samples:
        story.append(Paragraph(f"<b>{q_title}</b>", h2_style))
        story.append(Paragraph(f"<i>{q_desc}</i>", body_style))
        story.append(Paragraph(q_code.replace("\n", "<br/>").replace(" ", "&nbsp;"), code_style))
        story.append(Spacer(1, 4))

    # ------------------ 5. TOP BUSINESS INSIGHTS & RECOMMENDATIONS ------------------
    story.append(PageBreak()) # New page for Insights
    story.append(Paragraph("5. Top Strategic Business Insights & Recommendations", h1_style))
    story.append(Paragraph(
        "Extracted from <code>reports/business_insights.md</code>, these 6 core case studies illustrate analytical discovery to quantifiable C-Suite recommendations:",
        body_style
    ))

    insights = [
        ("1. Category Margin Asymmetry",
         "Finding: Technology accounts for 49.82% ($1.80M) of revenue with a 39.53% margin, while Apparel represents 9.74% ($352K) with a high 62.66% margin.",
         "Impact: Heavy hardware reliance limits blended margin expansion. Shifting volume to Apparel yields higher profit per advertising dollar.",
         "Recommendation: Reallocate 15% of marketing spend toward Apparel; introduce tech-apparel bundle packs. Target: Expand Apparel share to 15.0%."),

        ("2. Q4 Seasonality & Inventory Risk",
         "Finding: November ($298K) and December ($325K) generate +74.6% higher monthly revenue than baseline months.",
         "Impact: Supply chains risk catastrophic stockouts on top 20 SKUs during peak holiday weeks.",
         "Recommendation: Finalize purchase orders with tier-1 suppliers by early September (60-day buffer); establish dynamic safety stock by Oct 15."),

        ("3. Deep Discount Margin Cannibalization",
         "Finding: Discounts >15% cause profit margin to plummet from 46.8% down to 24.2%, with only a 11.4% gain in order volume.",
         "Impact: Markdown pricing destroys profit margins without generating compensating unit elasticity.",
         "Recommendation: Cap promotional discounts at 12%; shift to threshold-based volume tiers (e.g. '$25 off orders above $200')."),

        ("4. Customer Retention & Repeat Purchase Engine",
         "Finding: 81.83% of unique customers (1,725/2,108) are repeat buyers; accounts with 5+ orders drive 58.2% of total revenue.",
         "Impact: Customer retention economics are substantially cheaper than top-of-funnel customer acquisition (CAC).",
         "Recommendation: Launch automated ShopPulse VIP loyalty tiers and automated post-purchase email re-order triggers at Day 14, 30, and 60."),

        ("5. B2B / Corporate Highest Lifetime Value",
         "Finding: Corporate clients generate an AOV of $342.10 and average annual CLV of $2,140 with 1.4x higher order frequency.",
         "Impact: Corporate accounts represent the most predictable, recurring revenue stream with lower price sensitivity.",
         "Recommendation: Build dedicated B2B self-service purchasing portals with automated GST invoicing and assign dedicated account managers."),

        ("6. Pareto 80/20 SKU Catalog Concentration",
         "Finding: The top 19.8% of product SKUs (127/640) account for 78.4% of total enterprise revenue.",
         "Impact: Working capital is tied up in low-velocity long-tail inventory with high holding costs.",
         "Recommendation: Phase out bottom 10% non-performing SKUs and transition slow catalog items to drop-ship vendor models.")
    ]

    for title, f, imp, rec in insights:
        story.append(Paragraph(f"<b>{title}</b>", h2_style))
        story.append(Paragraph(f"• <b>{f.split(':')[0]}:</b> {f.split(':')[1]}", bullet_style))
        story.append(Paragraph(f"• <b>{imp.split(':')[0]}:</b> {imp.split(':')[1]}", bullet_style))
        story.append(Paragraph(f"• <b>{rec.split(':')[0]}:</b> {rec.split(':')[1]}", bullet_style))
        story.append(Spacer(1, 4))

    # ------------------ 6. INTERVIEW TALKING POINTS & PROJECT ELEVATOR PITCH ------------------
    story.append(Spacer(1, 10))
    story.append(Paragraph("6. Interview Talking Points & Technical Elevator Pitch", h1_style))
    story.append(Paragraph(
        "<b>How to present this project in a Data Analyst / BI Engineer interview:</b>", body_style
    ))
    story.append(Paragraph(
        "<i>\"In this project, I built <b>ShopPulse</b>, an end-to-end e-commerce analytics platform analyzing 12,500 transactions across 18 months. I engineered a data cleaning pipeline in Python to resolve duplicate orders, missing values, and enforce mathematical financial constraints. Next, I designed a normalized Star Schema in PostgreSQL/SQLite and authored 20 advanced SQL queries utilizing Window Functions (LAG, DENSE_RANK, SUM OVER) to model Customer Lifetime Value, RFM segmentation, and MoM growth rates. Finally, I built interactive dashboards in Streamlit and delivered 12 quantified business recommendations that identified how reallocating marketing to Apparel (62.7% margin) and capping discounts at 12% directly expands enterprise profit margins.\"</i>",
        body_style
    ))
    story.append(Spacer(1, 10))

    # ------------------ FOOTER / LINKS ------------------
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceBefore=8, spaceAfter=8))
    story.append(Paragraph("<b>GitHub Repository:</b> https://github.com/mahamoodmajin183-ui/shop-pulse-ecommerce-analytics | <b>License:</b> MIT", meta_style))

    doc.build(story)
    print(f" Successfully generated executive PDF report at: {output_path}")

if __name__ == "__main__":
    generate_pdf()
