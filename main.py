from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import base64
import json
import asyncio
import logging
from datetime import datetime
import os

from data_scraper import TDSDataScraper
from question_answerer import QuestionAnswerer
from image_processor import ImageProcessor
from token_calculator import TokenCalculator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="TDS Virtual TA",
    description="Virtual Teaching Assistant for Tools in Data Science course",
    version="1.0.0"
)

# Add CORS middleware to allow frontend API calls
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Pydantic models for request/response
class Link(BaseModel):
    url: str
    text: str

class QuestionRequest(BaseModel):
    question: str
    image: Optional[str] = None  # base64 encoded image

class QuestionResponse(BaseModel):
    answer: str
    links: List[Link]

class TokenCalculationRequest(BaseModel):
    text: str
    model: str = "gpt-3.5-turbo-0125"
    token_type: str = "input"

class TokenCalculationResponse(BaseModel):
    token_count: int
    cost_dollars: float
    cost_cents: float
    model: str
    token_type: str
    price_per_million_tokens: float

# Global instances
data_scraper = None
question_answerer = None
image_processor = None
token_calculator = None

@app.on_event("startup")
async def startup_event():
    """Initialize the application components on startup"""
    global data_scraper, question_answerer, image_processor, token_calculator
    
    logger.info("Starting TDS Virtual TA application...")
    
    try:
        # Initialize components
        data_scraper = TDSDataScraper()
        image_processor = ImageProcessor()
        token_calculator = TokenCalculator()
        
        # Load or scrape data
        logger.info("Loading TDS course data...")
        await data_scraper.load_data()
        
        # Initialize question answerer with scraped data
        question_answerer = QuestionAnswerer(data_scraper.get_data())
        
        logger.info("TDS Virtual TA is ready!")
        
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        # Don't crash the app, but log the error

@app.get("/", response_class=HTMLResponse)
async def root():
    """Main landing page with beautiful UI"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>TDS Virtual TA</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
            }
            
            .container {
                max-width: 800px;
                margin: 0 auto;
                padding: 2rem;
                text-align: center;
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 15px;
                box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
                border: 1px solid rgba(255, 255, 255, 0.18);
            }
            
            h1 {
                font-size: 3rem;
                margin-bottom: 1rem;
                background: linear-gradient(45deg, #FFD700, #FFA500);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .subtitle {
                font-size: 1.2rem;
                margin-bottom: 2rem;
                opacity: 0.9;
            }
            
            .status {
                background: rgba(76, 175, 80, 0.2);
                border: 1px solid #4CAF50;
                border-radius: 10px;
                padding: 1rem;
                margin: 2rem 0;
            }
            
            .api-endpoints {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 1rem;
                margin: 2rem 0;
            }
            
            .endpoint-card {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                padding: 1.5rem;
                border: 1px solid rgba(255, 255, 255, 0.2);
                transition: transform 0.3s ease;
            }
            
            .endpoint-card:hover {
                transform: translateY(-5px);
                background: rgba(255, 255, 255, 0.15);
            }
            
            .endpoint-title {
                font-size: 1.1rem;
                font-weight: bold;
                margin-bottom: 0.5rem;
                color: #FFD700;
            }
            
            .endpoint-desc {
                font-size: 0.9rem;
                opacity: 0.8;
                margin-bottom: 1rem;
            }
            
            .endpoint-link {
                display: inline-block;
                background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
                color: white;
                text-decoration: none;
                padding: 0.5rem 1rem;
                border-radius: 5px;
                font-size: 0.8rem;
                transition: opacity 0.3s ease;
            }
            
            .endpoint-link:hover {
                opacity: 0.8;
            }
            
            .demo-section {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                padding: 2rem;
                margin: 2rem 0;
                text-align: left;
            }
            
            .demo-title {
                font-size: 1.5rem;
                margin-bottom: 1rem;
                text-align: center;
                color: #FFD700;
            }
            
            .question-input {
                width: 100%;
                padding: 1rem;
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 5px;
                background: rgba(255, 255, 255, 0.1);
                color: white;
                font-size: 1rem;
                margin-bottom: 1rem;
            }
            
            .question-input::placeholder {
                color: rgba(255, 255, 255, 0.7);
            }
            
            .ask-button {
                background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
                color: white;
                border: none;
                padding: 1rem 2rem;
                border-radius: 5px;
                cursor: pointer;
                font-size: 1rem;
                transition: opacity 0.3s ease;
            }
            
            .ask-button:hover {
                opacity: 0.8;
            }
            
            .answer-box {
                margin-top: 1rem;
                padding: 1rem;
                background: rgba(0, 0, 0, 0.2);
                border-radius: 5px;
                border: 1px solid rgba(255, 255, 255, 0.2);
                display: none;
            }
            
            .loading {
                display: none;
                text-align: center;
                margin: 1rem 0;
            }
            
            .spinner {
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 50%;
                border-top: 2px solid white;
                width: 20px;
                height: 20px;
                animation: spin 1s linear infinite;
                margin: 0 auto;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            .footer {
                margin-top: 2rem;
                opacity: 0.7;
                font-size: 0.9rem;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 TDS Virtual TA</h1>
            <p class="subtitle">Your AI-Powered Teaching Assistant for Tools in Data Science</p>
            
            <div class="status">
                <h3>✅ Status: Online & Ready!</h3>
                <p>Deployed successfully on Railway • Last updated: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC") + """</p>
            </div>
            
            <div class="demo-section">
                <h3 class="demo-title">💬 Try It Out!</h3>
                <input type="text" class="question-input" id="questionInput" 
                       placeholder="Ask me anything about TDS... (e.g., 'Should I use gpt-4o-mini or gpt-3.5-turbo?')">
                <button class="ask-button" onclick="askQuestion()">Ask Question</button>
                
                <div class="loading" id="loading">
                    <div class="spinner"></div>
                    <p>Thinking...</p>
                </div>
                
                <div class="answer-box" id="answerBox">
                    <h4>Answer:</h4>
                    <p id="answerText"></p>
                    <div id="linksSection"></div>
                </div>
            </div>
            
            <div class="api-endpoints">
                <div class="endpoint-card">
                    <div class="endpoint-title">📊 API Documentation</div>
                    <div class="endpoint-desc">Interactive API docs with all endpoints</div>
                    <a href="/docs" class="endpoint-link">View Docs</a>
                </div>
                
                <div class="endpoint-card">
                    <div class="endpoint-title">🔍 Health Check</div>
                    <div class="endpoint-desc">Check system status and components</div>
                    <a href="/health" class="endpoint-link">Check Health</a>
                </div>
                
                <div class="endpoint-card">
                    <div class="endpoint-title">🧮 Token Calculator</div>
                    <div class="endpoint-desc">Calculate GPT API costs</div>
                    <a href="/api/solve-sample-problem" class="endpoint-link">Solve Sample</a>
                </div>
                
                <div class="endpoint-card">
                    <div class="endpoint-title">💰 Cost Calculator</div>
                    <div class="endpoint-desc">Calculate token costs for different models</div>
                    <a href="#" onclick="showTokenCalculator()" class="endpoint-link">Calculate</a>
                </div>
            </div>
            
            <div class="footer">
                <p>Built with FastAPI • Deployed on Railway • Optimized for 4GB containers</p>
                <p>🚀 Ready to help with your TDS assignments and questions!</p>
            </div>
        </div>
        
        <script>
            async function askQuestion() {
                const input = document.getElementById('questionInput');
                const loading = document.getElementById('loading');
                const answerBox = document.getElementById('answerBox');
                const answerText = document.getElementById('answerText');
                const linksSection = document.getElementById('linksSection');
                
                if (!input.value.trim()) {
                    alert('Please enter a question!');
                    return;
                }
                
                loading.style.display = 'block';
                answerBox.style.display = 'none';
                
                try {
                    console.log('Making request to /api/');
                    const response = await fetch('/api/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            question: input.value,
                            image: null
                        })
                    });
                    
                    console.log('Response status:', response.status);
                    
                    if (response.ok) {
                        const data = await response.json();
                        console.log('Response data:', data);
                        answerText.textContent = data.answer;
                        
                        // Display links if available
                        if (data.links && data.links.length > 0) {
                            linksSection.innerHTML = '<h4>📚 Helpful Links:</h4>' + 
                                data.links.map(link => 
                                    `<a href="${link.url}" target="_blank" style="color: #FFD700; text-decoration: none; display: block; margin: 0.5rem 0;">🔗 ${link.text}</a>`
                                ).join('');
                        } else {
                            linksSection.innerHTML = '';
                        }
                        
                        answerBox.style.display = 'block';
                    } else {
                        const errorText = await response.text();
                        console.error('API Error:', response.status, errorText);
                        throw new Error(`API Error: ${response.status} - ${errorText}`);
                    }
                } catch (error) {
                    console.error('Fetch error:', error);
                    answerText.textContent = `Error: ${error.message}. Please check the browser console for details.`;
                    answerBox.style.display = 'block';
                }
                
                loading.style.display = 'none';
            }
            
            // Allow Enter key to submit
            document.getElementById('questionInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    askQuestion();
                }
            });
            
            function showTokenCalculator() {
                const text = prompt('Enter text to calculate tokens:');
                if (text) {
                    fetch('/api/calculate-tokens', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            text: text,
                            model: 'gpt-3.5-turbo-0125',
                            token_type: 'input'
                        })
                    })
                    .then(response => {
                        if (!response.ok) {
                            throw new Error(`HTTP ${response.status}`);
                        }
                        return response.json();
                    })
                    .then(data => {
                        alert(`Tokens: ${data.token_count}\\nCost: $${data.cost_dollars.toFixed(6)} (${data.cost_cents.toFixed(4)} cents)`);
                    })
                    .catch(error => {
                        console.error('Token calculator error:', error);
                        alert(`Error calculating tokens: ${error.message}`);
                    });
                }
            }
        </script>
    </body>
    </html>
    """
    return html_content

@app.post("/api/", response_model=QuestionResponse)
async def answer_question(request: QuestionRequest):
    """
    Main API endpoint to answer student questions
    """
    # Check if components are initialized
    if not all([data_scraper, question_answerer, image_processor]):
        raise HTTPException(status_code=503, detail="Service not ready. Please try again in a moment.")
    
    try:
        start_time = datetime.now()
        logger.info(f"Received question: {request.question[:100]}...")
        
        # Process image if provided
        image_context = None
        if request.image:
            try:
                if image_processor.validate_image(request.image):
                    image_context = await image_processor.process_image(request.image)
                    if image_context:
                        logger.info("Image processed successfully")
                    else:
                        logger.warning("Image processing returned no context")
                else:
                    logger.warning("Invalid image format provided")
            except Exception as e:
                logger.warning(f"Failed to process image: {str(e)}")
        
        # Get answer from question answerer
        answer_data = await question_answerer.answer_question(
            question=request.question,
            image_context=image_context
        )
        
        # Prepare response
        response = QuestionResponse(
            answer=answer_data["answer"],
            links=[Link(url=link["url"], text=link["text"]) for link in answer_data["links"]]
        )
        
        # Log response time
        elapsed_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"Question answered in {elapsed_time:.2f} seconds")
        
        if elapsed_time > 30:
            logger.warning(f"Response took {elapsed_time:.2f} seconds (>30s limit)")
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/api/calculate-tokens", response_model=TokenCalculationResponse)
async def calculate_token_cost(request: TokenCalculationRequest):
    """Calculate token costs for GPT models"""
    if not token_calculator:
        raise HTTPException(status_code=503, detail="Token calculator not ready")
    
    try:
        result = token_calculator.calculate_cost(
            text=request.text,
            model=request.model,
            token_type=request.token_type
        )
        
        return TokenCalculationResponse(**result)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error calculating tokens: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/solve-sample-problem")
async def solve_sample_problem():
    """Solve the specific token cost problem from the image"""
    if not token_calculator:
        raise HTTPException(status_code=503, detail="Token calculator not ready")
    
    try:
        solution = token_calculator.solve_sample_problem()
        return {"solution": solution}
    except Exception as e:
        logger.error(f"Error solving sample problem: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/health")
async def health_check():
    """Detailed health check endpoint"""
    components_status = {
        "data_scraper": data_scraper is not None,
        "question_answerer": question_answerer is not None,
        "image_processor": image_processor is not None,
        "token_calculator": token_calculator is not None
    }
    
    data_loaded = data_scraper is not None and data_scraper.is_data_loaded()
    
    return {
        "status": "healthy" if all(components_status.values()) else "degraded",
        "timestamp": datetime.now().isoformat(),
        "data_loaded": data_loaded,
        "components": components_status
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port) 