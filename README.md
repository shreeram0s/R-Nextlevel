# AI Resume Analyzer & Skill Enhancer

A full-stack web application that analyzes resumes against job descriptions using AI, identifies skill gaps, and provides personalized learning recommendations from YouTube.

## Features

- 📄 **Document Processing**: Upload resumes and job descriptions in PDF, DOCX, or TXT formats
- 🔍 **AI-Powered Analysis**: Uses spaCy NLP and Sentence Transformers for skill extraction and matching
- 📊 **Visual Analytics**: Interactive skill comparison with matching scores
- 📚 **Learning Recommendations**: Automatic YouTube course suggestions for missing skills
- 💾 **Data Persistence**: Save and retrieve analysis history
- 🎨 **Modern UI**: Beautiful, responsive design with drag-and-drop functionality

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **AI/ML**: spaCy, Sentence Transformers
- **Database**: SQLite
- **APIs**: YouTube Data API
- **File Processing**: pdfplumber, docx2txt

## Installation

### Prerequisites

- Python 3.9+
- pip package manager

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Profile-Match
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download spaCy model**
   ```bash
   python -m spacy download en_core_web_md
   ```

5. **Set up YouTube API Key** (Optional)
   - Get a YouTube Data API key from [Google Cloud Console](https://console.cloud.google.com/)
   - Replace the API key in `app.py` line 32

## Running the Application

### Development Mode
```bash
python app.py
```

The application will be available at `http://localhost:5000`

### Production Mode
```bash
# Set environment variables
export FLASK_ENV=production
export FLASK_DEBUG=0

# Run with gunicorn (install first: pip install gunicorn)
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Deployment

### Option 1: Heroku

1. **Install Heroku CLI** and login
   ```bash
   heroku login
   ```

2. **Create Heroku app**
   ```bash
   heroku create your-app-name
   ```

3. **Deploy**
   ```bash
   git add .
   git commit -m "Initial deployment"
   git push heroku main
   ```

4. **Set environment variables**
   ```bash
   heroku config:set FLASK_ENV=production
   heroku config:set YOUTUBE_API_KEY=your_api_key
   ```

### Option 2: Railway

1. **Connect your GitHub repository** to Railway
2. **Set environment variables** in Railway dashboard
3. **Deploy automatically** on push to main branch

### Option 3: DigitalOcean App Platform

1. **Connect your GitHub repository** to DigitalOcean
2. **Configure build settings**:
   - Build Command: `pip install -r requirements.txt && python -m spacy download en_core_web_md`
   - Run Command: `python app.py`
3. **Set environment variables** in the dashboard

### Option 4: VPS Deployment

1. **Set up a VPS** (Ubuntu recommended)
2. **Install dependencies**:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip nginx
   ```

3. **Clone and setup the application**:
   ```bash
   git clone <repository-url>
   cd Profile-Match
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python -m spacy download en_core_web_md
   ```

4. **Configure Nginx**:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

5. **Run with systemd**:
   ```bash
   sudo systemctl enable your-app
   sudo systemctl start your-app
   ```

## API Endpoints

- `GET /` - Main application page
- `POST /api/analyze` - Analyze resume and job description
- `POST /api/save-analysis` - Save analysis results
- `GET /api/get-analyses` - Retrieve saved analyses

## Configuration

### Environment Variables

- `FLASK_ENV` - Flask environment (development/production)
- `FLASK_DEBUG` - Debug mode (0/1)
- `YOUTUBE_API_KEY` - YouTube Data API key
- `SECRET_KEY` - Flask secret key for production

### File Upload Limits

- Maximum file size: 16MB
- Supported formats: PDF, DOCX, TXT

## Usage

1. **Upload Files**: Drag and drop or click to upload your resume and job description
2. **Analyze**: Click "Analyze Skills & Matching Score" to process the documents
3. **Review Results**: View skill comparison, matching score, and missing skills
4. **Get Recommendations**: Browse recommended YouTube courses for missing skills
5. **Save Analysis**: Enter your name to save the analysis for future reference

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, email support@example.com or create an issue in the repository.

## Acknowledgments

- spaCy for NLP capabilities
- Sentence Transformers for semantic similarity
- YouTube Data API for course recommendations
- Flask for the web framework
