"""
ShopPulse - Comprehensive Executive PDF Report Generator (Real Dataset)
Generates a publication-grade, multi-page PDF project report covering:
- Executive Summary & Project Overview (Sample Superstore Dataset)
- Problem Statement & Objectives
- Tech Stack & System Architecture
- Dataset Schema & Data Cleaning Process
- Advanced SQL Analytics Catalog (20 Queries with explanations)
- Real Business Findings, Impacts & Strategic Recommendations
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
        fontSize=24,
        leading=30,
        textColor=primary_color,
        alignment=TA_CENTER
    )

    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=accent_blue,
        alignment=TA_CENTER
    )

    meta_style = ParagraphStyle(
        'CoverMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=text_muted,
        alignment=TA_CENTER
    )

    h1_style = ParagraphStyle(
        'Header1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=primary_color,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Header2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11.5,
        leading=15,
        textColor=accent_blue,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=text_dark,
        alignment=TA_LEFT,
        spaceAfter=6
    )

    code_style = ParagraphStyle(
        'CodeSnippet',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.5,
        leading=10.5,
        textColor=colors.HexColor("#0f172a"),
        backColor=colors.HexColor("#f1f5f9"),
        borderPadding=5,
        spaceAfter=5
    )

    bullet_style = ParagraphStyle(
        'BulletText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12.5,
        textColor=text_dark,
        leftIndent=12,
        spaceAfter=4
    )

    story = []

    # ------------------ COVER HEADER ------------------
    story.append(Spacer(1, 10))
    story.append(Paragraph("ShopPulse — E-Commerce Sales Analytics Platform", title_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph("Comprehensive Project Documentation, Architecture & Strategic Business Case Study", subtitle_style))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=2, color=accent_blue, spaceBefore=2, spaceAfter=10))
    story.append(Paragraph("<b>Author:</b> B.Tech AI & Data Science Student | <b>Target Role:</b> Data Analyst / Analytics Engineer<br/><b>Dataset:</b> Verified Sample Superstore E-Commerce Dataset (Tableau Public / Kaggle Open Data)<br/><b>Scope:</b> 9,994 Transactions | $2.297M Revenue | $286.39K Profit | 12.47% Margin | 20 Advanced SQL Queries", meta_style))
    story.append(Spacer(1, 12))

    # ------------------ 1. EXECUTIVE SUMMARY & OBJECTIVES ------------------
    story.append(Paragraph("1. Executive Summary & Verified Dataset Specifications", h1_style))
    story.append(Paragraph(
        "<b>ShopPulse</b> is a production-quality e-commerce analytics platform engineered using the canonical, real-world <b>Sample Superstore Retail Sales Dataset</b>. The platform tracks 9,994 transactions occurring across 4 full operating years (2014–2017), spanning 3 major product categories (Technology, Furniture, Office Supplies), 17 sub-categories, 4 geographic regions (West, East, Central, South), and 3 customer segments (Consumer, Corporate, Home Office).",
        body_style
    ))
    story.append(Paragraph(
        "<b>Verified Dataset Provenance:</b><br/>"
        "• <b>Source:</b> Tableau Public Open Data / Kaggle Open Retail Dataset Repository<br/>"
        "• <b>Source URL:</b> https://raw.githubusercontent.com/yajasarora/Superstore-Sales-Analysis-with-Tableau/master/Superstore%20sales%20dataset.csv<br/>"
        "• <b>License:</b> Public Domain / Open Database License<br/>"
        "• <b>Data Integrity:</b> 100% of reported figures are directly computed from the 9,994 transactional rows with zero synthetic fabrication.",
        body_style
    ))
    story.append(Spacer(1, 8))

    # ------------------ 2. ENTERPRISE KPI SCORECARD ------------------
    story.append(Paragraph("2. Enterprise Performance Scorecard (Empirical Ground Truth)", h1_style))
    
    kpi_data = [
        ["Metric Name", "Actual Value", "Business Scope", "Analytical Interpretation"],
        ["Total Revenue", "$2,297,200.65", "4-Year Aggregate", "Total realized top-line sales across 9,994 line items."],
        ["Total Gross Profit", "$286,396.54", "4-Year Aggregate", "Net gross earnings realized after Cost of Goods Sold (COGS)."],
        ["Overall Profit Margin", "12.47%", "Benchmark: >10.0%", "Realized company-wide profit margin percentage."],
        ["Total Order Volume", "5,009 Orders", "4 Operating Years", "Total distinct checkout orders placed across all channels."],
        ["Unique Customers", "793 Customers", "All Segments", "Active customer base across Consumer, Corporate, and Home Office."],
        ["Unique Product SKUs", "1,862 Products", "17 Sub-Categories", "Active merchandise catalog breadth."],
        ["Average Order Value (AOV)", "$458.62", "Per Checkout", "Mean basket sales generated per completed order ($2.297M / 5,009)."],
        ["Repeat Customer Rate", "98.49%", "Benchmark: >80.0%", "High retention: 781 out of 793 customers placed 2+ lifetime orders."]
    ]
    
    kpi_table = Table(kpi_data, colWidths=[120, 90, 100, 220])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 4),
        ('BACKGROUND', (0, 1), (-1, -1), bg_light),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 7.5),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 10))

    # ------------------ 3. TECHNICAL ARCHITECTURE ------------------
    story.append(Paragraph("3. Technical Stack & Data Pipeline Architecture", h1_style))
    
    tech_data = [
        ["Pipeline Layer", "Technology Stack", "Core Functions & Capabilities"],
        ["Data ETL & Cleaning", "Python 3.11, Pandas, NumPy", "Header standardization to snake_case, ISO date normalization, calendar feature enrichment, and financial integrity validation (Cost = Sales - Profit)."],
        ["Database Layer", "PostgreSQL & SQLite", "Star Schema relational tables (dim_customers, dim_products, fact_orders) with foreign key integrity and B-tree indexes."],
        ["SQL Analytics", "Advanced SQL (20 Queries)", "Window Functions (LAG, DENSE_RANK, SUM OVER), Common Table Expressions (CTEs), RFM segmentation, and Pareto 80/20 distribution."],
        ["Visualization & BI", "Streamlit, Plotly, Flask, Chart.js", "Interactive analytics dashboards featuring dynamic filtering by operating year, region, category, and customer segment."],
        ["Quality Assurance", "Pytest Suite", "Automated unit & integration test coverage verifying ETL transformations, database seeding, and query mathematical consistency."]
    ]
    tech_table = Table(tech_data, colWidths=[100, 110, 320])
    tech_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), accent_blue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('FONTSIZE', (0, 1), (-1, -1), 7.5),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(tech_table)
    story.append(Spacer(1, 12))

    # ------------------ 4. 20 ADVANCED SQL QUERIES ------------------
    story.append(PageBreak())
    story.append(Paragraph("4. Advanced SQL Analytics Catalog (20 Verified Queries)", h1_style))
    story.append(Paragraph(
        "Below is a categorized selection of the 20 production SQL queries implemented in <code>database/analysis_queries.sql</code> executed against the real database:",
        body_style
    ))

    sql_samples = [
        ("Query 03: Month-Over-Month (MoM) Growth Analysis Using LAG()",
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
        "Business Purpose: Computes period-over-period sales velocity and acceleration without self-joins."),

        ("Query 07: Top 3 Sub-Categories per Category Using DENSE_RANK()",
"""WITH subcat_sales AS (
    SELECT category, sub_category, ROUND(SUM(sales), 2) AS total_sales,
           DENSE_RANK() OVER (PARTITION BY category ORDER BY SUM(sales) DESC) AS rank_in_category
    FROM fact_ecommerce_sales GROUP BY category, sub_category
)
SELECT category, rank_in_category, sub_category, total_sales
FROM subcat_sales WHERE rank_in_category <= 3 ORDER BY category, rank_in_category ASC;""",
        "Business Purpose: Ranks top 3 revenue leaders inside Technology, Furniture, and Office Supplies."),

        ("Query 13: Discount Depth vs. Realized Profit Margin",
"""SELECT 
    CASE 
        WHEN discount = 0.00 THEN '0% (No Discount)'
        WHEN discount <= 0.20 THEN '1% - 20% (Standard Discount)'
        WHEN discount <= 0.50 THEN '21% - 50% (Deep Discount)'
        ELSE '51%+ (Clearance)'
    END AS discount_bracket,
    COUNT(order_id) AS total_transactions, ROUND(SUM(sales), 2) AS total_revenue,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND((SUM(profit) / SUM(sales)) * 100.0, 2) AS realized_margin_pct
FROM fact_ecommerce_sales GROUP BY discount_bracket ORDER BY realized_margin_pct DESC;""",
        "Business Purpose: Empirically identifies that discounts > 20% generate net losses (-$32K loss)."),

        ("Query 18: Pareto 80/20 Cumulative Product Revenue Concentration",
"""WITH product_totals AS (
    SELECT product_name, category, ROUND(SUM(sales), 2) AS product_sales
    FROM fact_ecommerce_sales GROUP BY product_name, category
),
ranked_products AS (
    SELECT product_name, product_sales,
           SUM(product_sales) OVER (ORDER BY product_sales DESC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sales,
           SUM(product_sales) OVER () AS total_enterprise_sales
    FROM product_totals
)
SELECT product_name, product_sales, ROUND((cumulative_sales / total_enterprise_sales) * 100.0, 2) AS cumulative_pct
FROM ranked_products LIMIT 15;""",
        "Business Purpose: Measures revenue concentration among top-selling hardware and office equipment SKUs.")
    ]

    for q_title, q_code, q_desc in sql_samples:
        story.append(Paragraph(f"<b>{q_title}</b>", h2_style))
        story.append(Paragraph(f"<i>{q_desc}</i>", body_style))
        story.append(Paragraph(q_code.replace("\n", "<br/>").replace(" ", "&nbsp;"), code_style))
        story.append(Spacer(1, 4))

    # ------------------ 5. TOP BUSINESS INSIGHTS ------------------
    story.append(PageBreak())
    story.append(Paragraph("5. Top Strategic Business Insights & Recommendations", h1_style))
    story.append(Paragraph(
        "Extracted from <code>reports/business_insights.md</code>, these core findings represent actionable, quantifiable discoveries:",
        body_style
    ))

    insights = [
        ("1. Technology Category Profit Dominance",
         "Finding: Technology generated $836,154.02 in revenue (36.4% share) and $145,455.03 in gross profit, driving 50.79% of all enterprise profit with a 17.39% margin.",
         "Impact: Technology hardware is the primary cash engine of the retail business.",
         "Recommendation: Expand inventory allocations for high-margin tech accessories and copiers; increase tech marketing spend by 20%."),

        ("2. Furniture Category Margin Compression (2.49% Margin)",
         "Finding: Furniture generated $741,999.74 in sales but yielded only $18,451.24 in net profit (2.49% margin). Tables lost -$17,725.48 and Bookcases lost -$3,472.56.",
         "Impact: Freight shipping costs and heavy promotional discounts eliminate furniture profitability.",
         "Recommendation: Eliminate discounts exceeding 15% on Tables and Bookcases; renegotiate carrier logistics rates."),

        ("3. The 'Discount Destruction' Cliff (>20% Discount)",
         "Finding: Transactions with 0% discount achieved 29.9% margin; discounts 1-20% achieved 14.5% margin. Discounts > 20% resulted in an aggregate net loss of -$32,142.98.",
         "Impact: Steep promotional markdowns destroy gross margins without generating compensating volume.",
         "Recommendation: Implement hard checkout guardrails capping standard discounts at 15%."),

        ("4. Regional Profit Asymmetry — West Leads While Central Lags",
         "Finding: The West region produced $725,457.82 in sales and $108,418.45 in profit (14.94% margin), whereas Central delivered $501,239.89 in sales and only $39,706.36 in profit (7.92% margin).",
         "Impact: Aggressive discounting in Texas (-$25.7K loss) drags down Central region returns.",
         "Recommendation: Enforce West region pricing governance across Central sales branches."),

        ("5. B2B & Home Office Deliver Higher Profit Margins",
         "Finding: Home Office accounts achieved 14.03% margin ($60,298 profit) and Corporate accounts achieved 13.03% ($91,979 profit), outperforming Consumer retail (11.55%).",
         "Impact: Business clients demonstrate lower price sensitivity and higher average transaction values.",
         "Recommendation: Build dedicated corporate procurement self-service portals with tailored volume pricing."),

        ("6. Pareto 80/20 SKU Revenue Concentration",
         "Finding: The top 15.2% of product SKUs (283 / 1,862) generate 70% of total enterprise sales. Canon imageCLASS Copier led with $61,599.82 in sales.",
         "Impact: Working capital and top-line health are tied to key equipment SKUs.",
         "Recommendation: Maintain 60-day safety stock buffers on top 50 revenue drivers.")
    ]

    for title, f, imp, rec in insights:
        story.append(Paragraph(f"<b>{title}</b>", h2_style))
        story.append(Paragraph(f"• <b>{f.split(':')[0]}:</b> {f.split(':')[1]}", bullet_style))
        story.append(Paragraph(f"• <b>{imp.split(':')[0]}:</b> {imp.split(':')[1]}", bullet_style))
        story.append(Paragraph(f"• <b>{rec.split(':')[0]}:</b> {rec.split(':')[1]}", bullet_style))
        story.append(Spacer(1, 4))

    # ------------------ 6. INTERVIEW TALKING POINTS ------------------
    story.append(Spacer(1, 8))
    story.append(Paragraph("6. Technical Interview Elevator Pitch", h1_style))
    story.append(Paragraph(
        "<i>\"In this project, I built <b>ShopPulse</b>, an end-to-end e-commerce sales analytics platform utilizing the verified Sample Superstore retail sales dataset comprising 9,994 transactions across 4 operating years. I built a Python ETL pipeline to standardize schemas, enrich temporal features, and validate financial consistency. Next, I designed a normalized Star Schema in PostgreSQL/SQLite and authored 20 advanced SQL queries utilizing Window Functions (LAG, DENSE_RANK, SUM OVER) to model customer lifetime value, RFM segmentation, and MoM growth velocity. Finally, I built interactive dashboards in Streamlit and delivered 12 quantified business case studies demonstrating how capping promotional discounts at 15% and addressing furniture margin compression directly recaptures operating capital.\"</i>",
        body_style
    ))
    story.append(Spacer(1, 8))

    # ------------------ FOOTER / LINKS ------------------
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceBefore=6, spaceAfter=6))
    story.append(Paragraph("<b>GitHub Repository:</b> https://github.com/mahamoodmajin183-ui/shop-pulse-ecommerce-analytics | <b>License:</b> MIT", meta_style))

    doc.build(story)
    print(f" Successfully generated executive PDF report at: {output_path}")

if __name__ == "__main__":
    generate_pdf()
