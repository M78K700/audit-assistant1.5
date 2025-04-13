import streamlit as st
import openai
from dotenv import load_dotenv
import os
import json
from datetime import datetime
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import io

# Load environment variables
load_dotenv()

# Configure OpenAI
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("OpenAI API key not found. Please add it to your .env file.")
    st.stop()

try:
    client = openai.OpenAI(api_key=api_key)
except Exception as e:
    st.error(f"Error initializing OpenAI client: {str(e)}")
    st.stop()

# Set page config
st.set_page_config(
    page_title="Financial Audit Assistant",
    page_icon="📊",
    layout="wide"
)

# Initialize session state for audit history and personnel
if 'audit_history' not in st.session_state:
    st.session_state.audit_history = []
if 'audit_personnel' not in st.session_state:
    st.session_state.audit_personnel = []

def add_auditor():
    st.session_state.audit_personnel.append({"name": "", "role": ""})

def remove_auditor(index):
    st.session_state.audit_personnel.pop(index)

def generate_pdf(audit_data, company_name, sector, audit_start_date, audit_end_date, 
                audit_personnel, compliance_requirements, audit_focus, special_considerations):
    # Create a buffer to store the PDF
    buffer = io.BytesIO()
    
    # Create the PDF document with A4 size and margins
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Get the styles
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#2C3E50'),
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=20,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#34495E'),
        fontName='Helvetica'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        spaceBefore=20,
        textColor=colors.HexColor('#2C3E50'),
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=12,
        leading=14,
        alignment=TA_JUSTIFY,
        fontName='Helvetica'
    )
    
    # Create the content
    content = []
    
    # Add title page
    content.append(Spacer(1, 100))
    content.append(Paragraph("Financial Audit Plan", title_style))
    content.append(Paragraph(f"for {company_name}", subtitle_style))
    content.append(Spacer(1, 50))
    content.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y')}", normal_style))
    content.append(PageBreak())
    
    # Add table of contents
    content.append(Paragraph("Table of Contents", title_style))
    content.append(Spacer(1, 20))
    
    toc_items = [
        "1. Executive Summary",
        "2. Company Information",
        "3. Audit Objectives",
        "4. Scope of Audit",
        "5. Risk Assessment",
        "6. Audit Procedures",
        "7. Recommendations",
        "8. Timeline and Milestones",
        "9. Resource Allocation"
    ]
    
    for item in toc_items:
        content.append(Paragraph(item, normal_style))
    
    content.append(PageBreak())
    
    # Add executive summary
    content.append(Paragraph("1. Executive Summary", heading_style))
    content.append(Paragraph(
        f"This audit plan outlines the comprehensive approach for conducting a financial audit of {company_name}, "
        f"a company operating in the {sector} sector. The audit will be conducted from {audit_start_date} to {audit_end_date} "
        f"with a team of {len(audit_personnel)} auditors. The audit will focus on compliance with {', '.join(compliance_requirements)} "
        f"and will address specific areas including {', '.join(audit_focus)}.",
        normal_style
    ))
    content.append(PageBreak())
    
    # Add company information
    content.append(Paragraph("2. Company Information", heading_style))
    
    # Create a more professional table style
    info_data = [
        ["Company Name:", company_name],
        ["Sector:", sector],
        ["Audit Period:", f"{audit_start_date.strftime('%B %d, %Y')} to {audit_end_date.strftime('%B %d, %Y')}"],
        ["Compliance Requirements:", ", ".join(compliance_requirements) if compliance_requirements else "None specified"],
        ["Audit Focus Areas:", ", ".join(audit_focus) if audit_focus else "None specified"],
        ["Special Considerations:", special_considerations if special_considerations else "None specified"]
    ]
    
    # Add audit team information
    content.append(Paragraph("Audit Team:", heading_style))
    team_data = [["Name", "Role"]]
    for person in audit_personnel:
        team_data.append([person["name"], person["role"]])
    
    team_table = Table(team_data, colWidths=[3*inch, 3*inch])
    team_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#DDDDDD')),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C3E50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ]))
    
    content.append(team_table)
    content.append(PageBreak())
    
    # Add audit plan sections
    content.append(Paragraph("3. Audit Plan Details", heading_style))
    content.append(Spacer(1, 10))
    
    sections = audit_data.split('\n\n')
    for section in sections:
        if section.strip():
            # Split section into title and content
            lines = section.strip().split('\n', 1)
            if len(lines) > 1:
                title, content_text = lines
                # Clean up the title (remove numbering if present)
                clean_title = title.split('. ', 1)[-1] if '. ' in title else title
                content.append(Paragraph(clean_title, heading_style))
                
                # Format the content with proper paragraphs
                paragraphs = content_text.split('\n')
                for para in paragraphs:
                    if para.strip():
                        content.append(Paragraph(para.strip(), normal_style))
                
                content.append(Spacer(1, 12))
    
    # Build the PDF
    doc.build(content)
    
    # Get the value of the buffer
    pdf = buffer.getvalue()
    buffer.close()
    
    return pdf

# Title and description
st.title("Financial Audit Assistant")
st.markdown("""
This application helps generate comprehensive audit plans based on company information and sector-specific requirements.
""")

# Sidebar for navigation
page = st.sidebar.selectbox("Choose a page", ["Generate Audit Plan", "Audit History"])

if page == "Generate Audit Plan":
    # Input form
    with st.form("audit_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            company_name = st.text_input("Company Name")
            sector = st.selectbox(
                "Sector",
                [
                    "Technology - Software",
                    "Technology - Hardware",
                    "Healthcare - Hospitals",
                    "Healthcare - Pharmaceuticals",
                    "Finance - Banking",
                    "Finance - Insurance",
                    "Manufacturing - Automotive",
                    "Manufacturing - Electronics",
                    "Retail - E-commerce",
                    "Retail - Brick & Mortar",
                    "Energy - Oil & Gas",
                    "Energy - Renewable",
                    "Real Estate - Commercial",
                    "Real Estate - Residential",
                    "Telecommunications",
                    "Transportation - Logistics",
                    "Transportation - Airlines",
                    "Other"
                ]
            )
            audit_start_date = st.date_input("Audit Start Date")
            
        with col2:
            audit_end_date = st.date_input("Audit End Date")
            compliance_requirements = st.multiselect(
                "Compliance Requirements",
                ["IFRS", "US GAAP", "SOX", "GDPR", "HIPAA", "PCI DSS", "ISO 27001", "Other"]
            )
            audit_focus = st.multiselect(
                "Audit Focus Areas",
                ["Financial Controls", "Operational Efficiency", "IT Security", 
                 "Compliance", "Risk Management", "Internal Controls"]
            )
            special_considerations = st.text_area("Special Considerations")
        
        # Audit Team Section
        st.subheader("Audit Team")
        
        # Display auditors
        for i, person in enumerate(st.session_state.audit_personnel):
            col1, col2 = st.columns([3, 3])
            with col1:
                st.session_state.audit_personnel[i]["name"] = st.text_input(
                    "Auditor Name",
                    key=f"name_{i}",
                    value=person["name"]
                )
            with col2:
                st.session_state.audit_personnel[i]["role"] = st.selectbox(
                    "Role",
                    [
                        "Senior Auditor",
                        "Lead Auditor",
                        "Internal Auditor",
                        "External Auditor",
                        "Compliance Officer",
                        "Risk Manager",
                        "IT Auditor",
                        "Forensic Auditor",
                        "Tax Auditor",
                        "Operations Auditor"
                    ],
                    key=f"role_{i}",
                    index=0 if person["role"] == "" else [
                        "Senior Auditor",
                        "Lead Auditor",
                        "Internal Auditor",
                        "External Auditor",
                        "Compliance Officer",
                        "Risk Manager",
                        "IT Auditor",
                        "Forensic Auditor",
                        "Tax Auditor",
                        "Operations Auditor"
                    ].index(person["role"])
                )
        
        # Add/Remove buttons
        col_add, col_remove = st.columns([1, 5])
        with col_add:
            if st.form_submit_button("➕ Add Auditor"):
                add_auditor()
                st.rerun()
        
        # Generate Audit Plan button
        submit_button = st.form_submit_button("Generate Audit Plan")

    # Handle remove action outside the form
    if st.session_state.audit_personnel:
        st.subheader("Remove Auditors")
        for i, person in enumerate(st.session_state.audit_personnel):
            if st.button(f"Remove {person['name'] or 'Unnamed Auditor'}", key=f"remove_{i}"):
                remove_auditor(i)
                st.rerun()

    if submit_button:
        if not company_name:
            st.error("Please enter a company name")
        elif not st.session_state.audit_personnel:
            st.error("Please add at least one auditor to the team")
        else:
            with st.spinner("Generating audit plan..."):
                try:
                    # Prepare the prompt for OpenAI
                    audit_team = "\n".join([f"- {person['name']} ({person['role']})" for person in st.session_state.audit_personnel])
                    
                    prompt = f"""
                    Generate a comprehensive audit plan for {company_name}, a company in the {sector} sector.
                    The audit will be conducted from {audit_start_date} to {audit_end_date}.
                    
                    Audit Team:
                    {audit_team}
                    
                    Compliance Requirements: {', '.join(compliance_requirements)}
                    Audit Focus Areas: {', '.join(audit_focus)}
                    Special Considerations: {special_considerations}

                    Please provide the following sections:
                    1. Audit Objectives
                    2. Scope of Audit
                    3. Risk Assessment
                    4. Audit Procedures
                    5. Recommendations
                    6. Timeline and Milestones
                    7. Resource Allocation

                    Make the response detailed and specific to the {sector} sector.
                    For each compliance requirement (IFRS, US GAAP, etc.), include specific audit procedures and considerations.
                    Consider the diverse roles of the audit team members when assigning responsibilities.
                    """

                    # Call OpenAI API with the new client
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are a professional financial auditor with expertise in various sectors and accounting standards."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7,
                        max_tokens=2000
                    )

                    # Display the results
                    audit_plan = response.choices[0].message.content
                    
                    # Save to audit history
                    audit_record = {
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "company": company_name,
                        "sector": sector,
                        "plan": audit_plan,
                        "start_date": audit_start_date,
                        "end_date": audit_end_date,
                        "personnel": st.session_state.audit_personnel,
                        "compliance": compliance_requirements,
                        "focus": audit_focus,
                        "considerations": special_considerations
                    }
                    st.session_state.audit_history.append(audit_record)
                    
                    # Split the response into sections
                    sections = audit_plan.split('\n\n')
                    
                    # Create columns for download buttons
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Add text download button
                        st.download_button(
                            label="Download as Text",
                            data=audit_plan,
                            file_name=f"audit_plan_{company_name}_{datetime.now().strftime('%Y%m%d')}.txt",
                            mime="text/plain"
                        )
                    
                    with col2:
                        # Generate and add PDF download button
                        pdf_data = generate_pdf(
                            audit_plan, company_name, sector, audit_start_date, 
                            audit_end_date, st.session_state.audit_personnel,
                            compliance_requirements, audit_focus, special_considerations
                        )
                        st.download_button(
                            label="Download as PDF",
                            data=pdf_data,
                            file_name=f"audit_plan_{company_name}_{datetime.now().strftime('%Y%m%d')}.pdf",
                            mime="application/pdf"
                        )
                    
                    # Display sections
                    for section in sections:
                        if section.strip():
                            st.markdown(section)
                            
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                    st.info("Please make sure you have set up your OpenAI API key in the .env file")

elif page == "Audit History":
    st.header("Audit History")
    
    if not st.session_state.audit_history:
        st.info("No audit plans have been generated yet.")
    else:
        for record in reversed(st.session_state.audit_history):
            with st.expander(f"{record['company']} - {record['timestamp']}"):
                st.markdown(f"**Sector:** {record['sector']}")
                st.markdown("**Audit Team:**")
                for person in record['personnel']:
                    st.markdown(f"- {person['name']} ({person['role']})")
                st.markdown("**Audit Plan:**")
                st.markdown(record['plan'])
                
                # Create columns for download buttons
                col1, col2 = st.columns(2)
                
                with col1:
                    # Add text download button
                    st.download_button(
                        label="Download as Text",
                        data=record['plan'],
                        file_name=f"audit_plan_{record['company']}_{record['timestamp'].replace(' ', '_')}.txt",
                        mime="text/plain"
                    )
                
                with col2:
                    # Generate and add PDF download button
                    pdf_data = generate_pdf(
                        record['plan'], record['company'], record['sector'],
                        record['start_date'], record['end_date'], record['personnel'],
                        record['compliance'], record['focus'], record['considerations']
                    )
                    st.download_button(
                        label="Download as PDF",
                        data=pdf_data,
                        file_name=f"audit_plan_{record['company']}_{record['timestamp'].replace(' ', '_')}.pdf",
                        mime="application/pdf"
                    ) 