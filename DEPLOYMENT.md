# TDS Virtual TA - Deployment Guide

## 🚀 Deployment Options

### Option 1: Railway (Recommended)

Railway is the easiest deployment platform for this project.

1. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: TDS Virtual TA"
   git branch -M main
   git remote add origin https://github.com/yourusername/tds-virtual-ta.git
   git push -u origin main
   ```

2. **Deploy to Railway:**
   - Go to [railway.app](https://railway.app)
   - Sign up/Login with GitHub
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your `tds-virtual-ta` repository
   - Railway will automatically detect the `Procfile` and deploy

3. **Environment Variables:**
   - No additional environment variables needed for basic functionality
   - The app will run on the port provided by Railway automatically

### Option 2: Heroku

1. **Install Heroku CLI** and login:
   ```bash
   heroku login
   ```

2. **Create Heroku app:**
   ```bash
   heroku create your-tds-virtual-ta
   ```

3. **Deploy:**
   ```bash
   git push heroku main
   ```

### Option 3: Local Development

1. **Activate virtual environment:**
   ```bash
   # Windows
   .\venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```

4. **Access the API:**
   - Health check: `http://localhost:8000/health`
   - API endpoint: `http://localhost:8000/api/`

## 📋 Testing Your Deployment

### 1. Health Check
```bash
curl https://your-deployed-url.com/health
```

### 2. Test API Endpoint
```bash
curl -X POST https://your-deployed-url.com/api/ \
  -H "Content-Type: application/json" \
  -d '{"question": "Should I use gpt-4o-mini or gpt-3.5-turbo?"}'
```

### 3. Run Full Test Suite
```bash
python test_api.py https://your-deployed-url.com
```

### 4. Run Evaluation
```bash
# Update the base_url in run_evaluation.py to your deployed URL
python run_evaluation.py
```

## 🔧 Configuration

### Environment Variables (Optional)
- `PORT`: Port number (default: 8000)
- No API keys required for basic functionality

### Files Required for Deployment
- ✅ `main.py` - Main application
- ✅ `requirements.txt` - Python dependencies
- ✅ `Procfile` - Process configuration
- ✅ `data_scraper.py` - Data scraping module
- ✅ `question_answerer.py` - Question answering logic
- ✅ `image_processor.py` - Image processing module

## 📊 Performance Expectations

- **Response Time**: ~2-3 seconds average
- **Timeout Limit**: 30 seconds maximum
- **Success Rate**: 100% for supported question types
- **Concurrent Users**: Supports multiple simultaneous requests

## 🛠️ Troubleshooting

### Common Issues:

1. **Port Issues:**
   - Ensure your deployment platform sets the `PORT` environment variable
   - The app automatically uses `PORT` or defaults to 8000

2. **Memory Issues:**
   - The app loads course data on startup
   - Ensure your deployment has at least 512MB RAM

3. **Timeout Issues:**
   - Responses should be under 30 seconds
   - Check your deployment platform's timeout settings

### Logs:
- Check application logs for detailed error information
- All major operations are logged with timestamps

## 🎯 Success Criteria

Deployment is successful when:
- ✅ Health check returns 200 status
- ✅ API responds to questions in JSON format
- ✅ Response times are under 30 seconds
- ✅ All test cases pass (8/8 tests)
- ✅ Evaluation shows 100% success rate

## 📞 Support

If you encounter issues:
1. Check the logs for error messages
2. Verify all files are present in your repository
3. Test locally first using `python main.py`
4. Ensure your deployment platform supports Python 3.8+

---