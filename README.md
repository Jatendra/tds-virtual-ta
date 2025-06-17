# TDS Virtual TA

A Virtual Teaching Assistant API for the Tools in Data Science (TDS) course at IIT Madras Online Degree Program.

## Overview

This application provides an API endpoint that can automatically answer student questions based on:
- TDS course content (Jan 2025)
- TDS Discourse posts (Jan 1, 2025 - Apr 14, 2025)

The API accepts POST requests with student questions and optional base64-encoded image attachments, returning JSON responses with answers and relevant links within 30 seconds.

## Features

- **Question Answering**: Intelligent responses based on course materials and discourse posts
- **Image Processing**: Handles base64-encoded image attachments (screenshots, code snippets, etc.)
- **Fast Response**: Optimized to respond within 30 seconds
- **Relevant Links**: Provides contextual links to course materials and discourse posts
- **RESTful API**: Clean JSON API interface
- **Caching**: Efficient data caching for improved performance

## API Usage

### Endpoint
```
POST /api/
```

### Request Format
```json
{
  "question": "Should I use gpt-4o-mini which AI proxy supports, or gpt3.5 turbo?",
  "image": "base64_encoded_image_string_optional"
}
```

### Response Format
```json
{
  "answer": "You must use `gpt-3.5-turbo-0125`, even if the AI Proxy only supports `gpt-4o-mini`. Use the OpenAI API directly for this question.",
  "links": [
    {
      "url": "https://discourse.onlinedegree.iitm.ac.in/t/ga5-question-8-clarification/155939/4",
      "text": "Use the model that's mentioned in the question."
    },
    {
      "url": "https://discourse.onlinedegree.iitm.ac.in/t/ga5-question-8-clarification/155939/3",
      "text": "My understanding is that you just have to use a tokenizer, similar to what Prof. Anand used, to get the number of tokens and multiply that by the given rate."
    }
  ]
}
```

### Example cURL Request
```bash
curl "https://your-deployed-url.com/api/" \
  -H "Content-Type: application/json" \
  -d '{"question": "Should I use gpt-4o-mini which AI proxy supports, or gpt3.5 turbo?", "image": "$(base64 -w0 screenshot.webp)"}'
```

## Local Development Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd tds-virtual-ta
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python main.py
   ```

   The API will be available at `http://localhost:8000`

### Development Endpoints

- `GET /` - Health check
- `POST /api/` - Main question answering endpoint
- `GET /health` - Detailed health check with component status
- `GET /docs` - Interactive API documentation (Swagger UI)

## Testing

### Manual Testing
```bash
# Test the API locally
curl "http://localhost:8000/api/" \
  -H "Content-Type: application/json" \
  -d '{"question": "How do I set up Python for TDS?"}'
```

### Automated Evaluation
The project includes a promptfoo configuration for automated testing:

1. **Install promptfoo**
   ```bash
   npm install -g promptfoo
   ```

2. **Update the API URL in the config**
   Edit `project-tds-virtual-ta-promptfoo.yaml` and replace the URL with your deployed endpoint.

3. **Run evaluation**
   ```bash
   npx promptfoo eval --config project-tds-virtual-ta-promptfoo.yaml
   ```

## Deployment

### Option 1: Railway (Recommended)
1. Create account at [Railway](https://railway.app)
2. Connect your GitHub repository
3. Deploy with automatic builds
4. Railway will automatically detect the Python app and install dependencies

### Option 2: Heroku
1. Create a `Procfile`:
   ```
   web: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
2. Deploy to Heroku following their Python deployment guide

### Option 3: Google Cloud Run
1. Create a `Dockerfile`:
   ```dockerfile
   FROM python:3.9-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
   ```
2. Deploy using Google Cloud Run

### Option 4: DigitalOcean App Platform
1. Connect your GitHub repository
2. Configure build and run commands
3. Deploy with automatic scaling

## Project Structure

```
tds-virtual-ta/
├── main.py                    # FastAPI application entry point
├── data_scraper.py           # TDS content and discourse scraping
├── question_answerer.py      # Question processing and answering logic
├── image_processor.py        # Image attachment processing
├── requirements.txt          # Python dependencies
├── project-tds-virtual-ta-promptfoo.yaml  # Evaluation configuration
├── README.md                 # This file
└── tds_data_cache.json      # Cached course data (generated)
```

## Key Components

### Data Scraper (`data_scraper.py`)
- Scrapes TDS course content and discourse posts
- Implements caching for improved performance
- Provides search functionality across all content

### Question Answerer (`question_answerer.py`)
- Pattern matching for common question types
- Content relevance scoring
- Link generation for supporting resources

### Image Processor (`image_processor.py`)
- Base64 image decoding and validation
- Basic image analysis (screenshot detection, text detection)
- Placeholder for OCR integration

## Common Question Types Handled

1. **AI Model Selection**: Questions about GPT models, API usage
2. **Python Environment**: Setup, installation, dependency issues
3. **Data Visualization**: Best practices, library recommendations
4. **Assignment Submission**: Guidelines, formats, requirements
5. **General Course Content**: Any topic covered in TDS materials

## Performance Considerations

- **Response Time**: Optimized to respond within 30 seconds
- **Caching**: Course data is cached locally to avoid repeated scraping
- **Async Processing**: Uses async/await for non-blocking operations
- **Error Handling**: Graceful degradation when components fail

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions about the TDS Virtual TA:
1. Check the course discourse forum
2. Review the TDS course materials
3. Open an issue in this repository

## Acknowledgments

- IIT Madras Online Degree Program
- TDS Course Instructors and Teaching Assistants
- Course participants who provided feedback and questions 
