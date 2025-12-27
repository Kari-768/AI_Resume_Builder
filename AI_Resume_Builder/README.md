# AI-Powered Resume Builder

A Python Flask–based web application that analyzes uploaded resumes and job
descriptions to generate a clean, universal, and ATS-friendly resume format.

The system accepts resumes in multiple formats (PDF, DOCX, TXT), intelligently
extracts important sections, and restructures them into a standardized resume
layout suitable for Applicant Tracking Systems (ATS).

## Features
- Upload resume in PDF / DOCX / TXT format
- Job description–based resume analysis
- Automatic section detection (Summary, Skills, Education, Projects, etc.)
- Universal ATS-friendly resume output
- Resume preview in the browser
- Downloadable resume file

## Tech Stack
- Python
- Flask
- HTML & CSS
- pdfplumber
- python-docx

## How to Run
1. Install dependencies:
   pip install -r requirements.txt 
3. Run the application:
   python app.py
4. Open in browser:
   http://127.0.0.1:5000/
   

