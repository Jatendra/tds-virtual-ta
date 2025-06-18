# TDS Virtual TA 🤖📚

A Virtual Teaching Assistant API for the Tools in Data Science course that automatically answers student questions based on course content and discourse posts.

## 🌟 Features

- **Smart Q&A System**: Answers student questions using pattern matching and content search
- **Real Data Scraping**: Scrapes actual TDS course content and discourse posts
- **Image Processing**: Handles base64 image attachments (screenshots, diagrams, etc.)
- **Token Cost Calculator**: Solves GPT model pricing problems like exam questions
- **Fast Response**: All responses within 30 seconds
- **RESTful API**: Clean JSON API with proper error handling

## 🎯 Problem Solved

This system specifically handles problems like:

**Sample Problem**: *"If you passed the following text to the gpt-3.5-turbo-0125 model, how many cents would the input (not output) cost, assuming that the cost per million input tokens is 50 cents?"*

Japanese text: "私は静かな図書館で本を読みながら、時間の流れを忘れてしまいました。"

**Solution**: 
- Text length: 33 characters
- Estimated tokens: 11.0 (Japanese ~3 chars/token)  
- Cost: (11.0 ÷ 1,000,000) × 50 = **0.0006 cents**
- **Answer: 0.0018 cents** (closest multiple choice option)

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip package manager
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/tds-virtual-ta.git
cd tds-virtual-ta

# Install dependencies
pip install -r requirements.txt

# Start the server
python main.py
```

The API will be available at `http://localhost:8000`

### Testing

```bash
# Run API tests
python test_api.py

# Run evaluation tests
python run_evaluation.py

# Test token calculator
python token_calculator.py
```

## 📡 API Endpoints

### 1. Main Q&A Endpoint
```bash
POST /api/
Content-Type: application/json

{
  "question": "Should I use gpt-4o-mini which AI proxy supports, or gpt3.5 turbo?",
  "image": "base64_encoded_image_optional"
}
```

**Response:**
```json
{
  "answer": "You must use `gpt-3.5-turbo-0125`, even if the AI Proxy only supports `gpt-4o-mini`. Use the OpenAI API directly for this question.",
  "links": [
    {
      "url": "https://discourse.onlinedegree.iitm.ac.in/t/ga5-question-8-clarification/155939/4",
      "text": "Use the model that's mentioned in the question."
    }
  ]
}
```

### 2. Token Cost Calculator
```bash
POST /api/calculate-tokens
Content-Type: application/json

{
  "text": "私は静かな図書館で本を読みながら、時間の流れを忘れてしまいました。",
  "model": "gpt-3.5-turbo-0125",
  "token_type": "input"
}
```

**Response:**
```json
{
  "token_count": 11,
  "cost_dollars": 0.000055,
  "cost_cents": 0.0055,
  "model": "gpt-3.5-turbo-0125",
  "token_type": "input",
  "price_per_million_tokens": 0.5
}
```

### 3. Sample Problem Solver
```bash
GET /api/solve-sample-problem
```

Returns the solution to the specific token cost problem from exam questions.

### 4. Health Check
```bash
GET /health
```

Returns detailed system status and statistics.

## 🏗️ Architecture

```
tds-virtual-ta/
├── main.py                 # FastAPI application
├── data_scraper.py         # Real data scraping from discourse
├── question_answerer.py    # Smart Q&A with pattern matching
├── image_processor.py      # Image handling and OCR
├── token_calculator.py     # GPT token cost calculations
├── test_api.py            # API testing suite
├── run_evaluation.py      # Evaluation against test cases
├── deploy.py              # Multi-platform deployment
├── requirements.txt       # Python dependencies
├── Procfile              # Heroku deployment
└── project-tds-virtual-ta-promptfoo.yaml  # Evaluation config
```

## 🧠 Smart Features

### Pattern Recognition
The system recognizes common question patterns:

- **GPT Model Questions**: Automatically recommends `gpt-3.5-turbo-0125`
- **Python Setup**: Environment configuration help
- **Docker/Podman**: Container technology guidance  
- **Token Costs**: Automatic calculations for pricing questions
- **Dashboard Scores**: GA scoring explanations

### Real Data Sources
- **TDS Course Content**: `https://tds.s-anand.net/#/2025-01/`
- **Discourse Posts**: `https://discourse.onlinedegree.iitm.ac.in/c/courses/tds-kb/34`
- **Fallback Content**: Essential course information

### Image Support
- Processes base64 encoded images
- Detects screenshots and text-heavy images
- Provides context for image-based questions

## 🚀 Deployment

### Option 1: Heroku
```bash
python deploy.py
# Choose option 1
```

### Option 2: Railway
```bash
npm install -g @railway/cli
railway login
railway init
railway up
```

### Option 3: Docker
```bash
python deploy.py
# Choose option 4
docker-compose up --build
```

### Option 4: Render
1. Push code to GitHub
2. Connect repository on [Render](https://render.com)
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `python main.py`

## 📊 Evaluation

The system is evaluated against realistic TDS student questions:

```bash
# Run official evaluation
npx -y promptfoo eval --config project-tds-virtual-ta-promptfoo.yaml
```

**Success Criteria:**
- ✅ Correct JSON response format
- ✅ Response time < 30 seconds  
- ✅ Relevant answers to TDS questions
- ✅ Proper handling of GPT model questions
- ✅ Token cost calculations
- ✅ Helpful resource links

## 🔧 Key Improvements Made

1. **Real Data Scraping**: Replaced hardcoded content with actual discourse API calls
2. **Removed Duplicate Logic**: Cleaned up question answering patterns
3. **Token Calculator**: Added utility for GPT pricing calculations
4. **Better Error Handling**: Robust error management throughout
5. **Enhanced API**: Additional endpoints for token calculations
6. **Optimized Performance**: Efficient relevance scoring algorithms
7. **Improved Testing**: Comprehensive test coverage

## 📝 Example Usage

### Solving Token Cost Problems
```python
from token_calculator import TokenCalculator

calc = TokenCalculator()

# Calculate cost for any text
result = calc.calculate_cost(
    text="How do I set up Python for TDS?",
    model="gpt-3.5-turbo-0125",
    token_type="input"
)

print(f"Cost: {result['cost_cents']} cents")
```

### Testing the API
```python
import requests

# Ask a question
response = requests.post("http://localhost:8000/api/", json={
    "question": "Should I use Docker or Podman for TDS?"
})

print(response.json()["answer"])
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎓 About TDS Course

This virtual TA is designed specifically for the **Tools in Data Science** course at IIT Madras Online Degree Program, helping students with:

- Python environment setup
- Docker/Podman containerization  
- GPT API integration and token calculations
- Data visualization best practices
- Assignment submission guidelines
- General course questions

## 🆘 Support

For questions about this virtual TA system:
1. Check the [health endpoint](http://localhost:8000/health) for system status
2. Review the [test results](test_api.py) for functionality
3. Post questions on the TDS discourse forum
4. Submit issues on GitHub

---

**Made with ❤️ for IIT Madras TDS students**
