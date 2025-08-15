from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import os
import sqlite3
import requests
try:
    import pandas as pd
except ImportError:
    pd = None
import pdfplumber
import docx2txt
import numpy as np
import googleapiclient.discovery
import spacy
from spacy.cli import download
import json
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)
CORS(app)

# Configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Load NLP model
model_name = "en_core_web_md"
try:
    nlp = spacy.load(model_name)
except OSError:
    download(model_name)
    nlp = spacy.load(model_name)

# No heavy transformer model – rely on spaCy vectors for similarity

# YouTube API Key (Replace with your own key)
YOUTUBE_API_KEY = "AIzaSyBoRgw0WE_KzTVNUvH8d4MiTo1zZ2SqKPI"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def init_db():
    conn = sqlite3.connect('analysis_results.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT,
            resume_skills TEXT,
            job_skills TEXT,
            missing_skills TEXT,
            matching_score REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_file(file_path):
    try:
        ext = file_path.split(".")[-1].lower()
        if ext == "pdf":
            with pdfplumber.open(file_path) as pdf:
                return "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()]) or "No text extracted."
        elif ext in ["docx", "doc"]:
            return docx2txt.process(file_path) or "No text extracted."
        elif ext == "txt":
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read() or "No text extracted."
    except Exception as e:
        return f"Error reading file: {str(e)}"
    return "No text extracted."

def extract_skills(text):
    doc = nlp(text)
    skills = set()
    for ent in doc.ents:
        if ent.label_ == "ORG":
            skills.add(ent.text)
    return list(skills)

def calculate_matching_score(resume_text, job_text):
    # Use spaCy document vector similarity (fast, no heavy deps)
    # Limit very long texts for performance
    doc_resume = nlp(resume_text[:100000])
    doc_job = nlp(job_text[:100000])
    similarity = doc_resume.similarity(doc_job)
    return round(float(similarity) * 100, 2)

def fetch_youtube_courses(skill):
    try:
        youtube = googleapiclient.discovery.build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=YOUTUBE_API_KEY)
        request = youtube.search().list(q=f"{skill} course", part="snippet", maxResults=5, type="video")
        response = request.execute()
        
        courses = []
        for item in response.get("items", []):
            if (
                "id" in item and
                "videoId" in item["id"] and
                "snippet" in item and
                "title" in item["snippet"] and
                "channelTitle" in item["snippet"]
            ):
                courses.append({
                    "title": item["snippet"]["title"],
                    "channel": item["snippet"]["channelTitle"],
                    "video_link": f'https://www.youtube.com/watch?v={item["id"]["videoId"]}'
                })
        return courses
    except Exception as e:
        return []

def generate_summary(text):
    sentences = text.split(". ")[:3]
    return "... ".join(sentences) + "..." if sentences else "No content extracted."

# Initialize database
init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        if 'resume' not in request.files or 'job_description' not in request.files:
            return jsonify({'error': 'Both resume and job description files are required'}), 400
        
        resume_file = request.files['resume']
        job_file = request.files['job_description']
        
        if resume_file.filename == '' or job_file.filename == '':
            return jsonify({'error': 'No files selected'}), 400
        
        if not (allowed_file(resume_file.filename) and allowed_file(job_file.filename)):
            return jsonify({'error': 'Invalid file type. Only PDF, DOCX, and TXT files are allowed'}), 400
        
        # Save files with unique names
        resume_filename = f"resume_{uuid.uuid4()}.{resume_file.filename.rsplit('.', 1)[1].lower()}"
        job_filename = f"job_{uuid.uuid4()}.{job_file.filename.rsplit('.', 1)[1].lower()}"
        
        resume_path = os.path.join(app.config['UPLOAD_FOLDER'], resume_filename)
        job_path = os.path.join(app.config['UPLOAD_FOLDER'], job_filename)
        
        resume_file.save(resume_path)
        job_file.save(job_path)
        
        # Extract text
        resume_text = extract_text_from_file(resume_path)
        job_text = extract_text_from_file(job_path)
        
        # Generate summaries
        resume_summary = generate_summary(resume_text)
        job_summary = generate_summary(job_text)
        
        # Extract skills
        resume_skills = extract_skills(resume_text)
        job_skills = extract_skills(job_text)
        missing_skills = list(set(job_skills) - set(resume_skills))
        
        # Calculate matching score
        matching_score = calculate_matching_score(resume_text, job_text)
        
        # Fetch courses for missing skills
        courses = []
        for skill in missing_skills[:3]:  # Limit to 3 skills to avoid API limits
            courses.extend(fetch_youtube_courses(skill))
        
        # Clean up uploaded files
        os.remove(resume_path)
        os.remove(job_path)
        
        result = {
            'resume_summary': resume_summary,
            'job_summary': job_summary,
            'resume_skills': resume_skills,
            'job_skills': job_skills,
            'missing_skills': missing_skills,
            'matching_score': matching_score,
            'courses': courses[:10]  # Limit to 10 courses
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/save-analysis', methods=['POST'])
def save_analysis():
    try:
        data = request.json
        user_name = data.get('user_name')
        resume_skills = data.get('resume_skills', [])
        job_skills = data.get('job_skills', [])
        missing_skills = data.get('missing_skills', [])
        matching_score = data.get('matching_score', 0)
        
        if not user_name:
            return jsonify({'error': 'User name is required'}), 400
        
        conn = sqlite3.connect('analysis_results.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO analysis (user_name, resume_skills, job_skills, missing_skills, matching_score)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            user_name,
            ','.join(resume_skills),
            ','.join(job_skills),
            ','.join(missing_skills),
            matching_score
        ))
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Analysis saved successfully'})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/get-analyses', methods=['GET'])
def get_analyses():
    try:
        user_filter = request.args.get('user_name', '')
        
        conn = sqlite3.connect('analysis_results.db')
        cursor = conn.cursor()
        
        if user_filter:
            cursor.execute("SELECT * FROM analysis WHERE user_name = ? ORDER BY created_at DESC", (user_filter,))
        else:
            cursor.execute("SELECT * FROM analysis ORDER BY created_at DESC")
        
        rows = cursor.fetchall()
        conn.close()
        
        analyses = []
        for row in rows:
            analyses.append({
                'id': row[0],
                'user_name': row[1],
                'resume_skills': row[2].split(',') if row[2] else [],
                'job_skills': row[3].split(',') if row[3] else [],
                'missing_skills': row[4].split(',') if row[4] else [],
                'matching_score': row[5],
                'created_at': row[6]
            })
        
        return jsonify(analyses)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
