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
        <title>TDS Virtual TA - AI-Powered Teaching Assistant</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 25%, #0f3460 50%, #533483 100%);
                min-height: 100vh;
                color: #ffffff;
                cursor: default;
                overflow-x: hidden;
            }
            
            /* Custom cursor */
            * {
                cursor: inherit;
            }
            
            a, button, input, .clickable {
                cursor: pointer !important;
            }
            
            /* Navigation */
            .navbar {
                position: fixed;
                top: 0;
                width: 100%;
                padding: 1rem 2rem;
                backdrop-filter: blur(20px);
                background: rgba(26, 26, 46, 0.8);
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                z-index: 1000;
                transition: all 0.3s ease;
            }
            
            .nav-container {
                display: flex;
                justify-content: space-between;
                align-items: center;
                max-width: 1200px;
                margin: 0 auto;
            }
            
            .logo {
                font-size: 1.5rem;
                font-weight: bold;
                background: linear-gradient(45deg, #00d4ff, #5a67d8);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .nav-links {
                display: flex;
                gap: 2rem;
                list-style: none;
            }
            
            .nav-links a {
                color: rgba(255, 255, 255, 0.8);
                text-decoration: none;
                font-weight: 500;
                transition: color 0.3s ease;
                text-transform: uppercase;
                font-size: 0.9rem;
                letter-spacing: 0.5px;
            }
            
            .nav-links a:hover {
                color: #00d4ff;
            }
            
            .cta-button {
                background: linear-gradient(45deg, #00d4ff, #5a67d8);
                color: white;
                padding: 0.8rem 1.5rem;
                border: none;
                border-radius: 30px;
                font-weight: 600;
                text-decoration: none;
                transition: all 0.3s ease;
                text-transform: uppercase;
                font-size: 0.8rem;
                letter-spacing: 0.5px;
            }
            
            .cta-button:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 30px rgba(0, 212, 255, 0.3);
            }
            
            /* Main content */
            .main-content {
                margin-top: 100px;
                padding: 4rem 2rem 2rem;
                max-width: 1200px;
                margin-left: auto;
                margin-right: auto;
            }
            
            .hero-section {
                text-align: center;
                margin-bottom: 4rem;
            }
            
            .hero-title {
                font-size: clamp(2.5rem, 6vw, 4.5rem);
                font-weight: 700;
                line-height: 1.1;
                margin-bottom: 1.5rem;
                background: linear-gradient(45deg, #ffffff, #00d4ff, #5a67d8);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                animation: fadeInUp 1s ease;
            }
            
            .hero-subtitle {
                font-size: 1.3rem;
                color: rgba(255, 255, 255, 0.8);
                margin-bottom: 2rem;
                max-width: 600px;
                margin-left: auto;
                margin-right: auto;
                line-height: 1.6;
                animation: fadeInUp 1s ease 0.2s both;
            }
            
            .status-badge {
                display: inline-block;
                background: rgba(0, 212, 255, 0.1);
                border: 1px solid rgba(0, 212, 255, 0.3);
                padding: 0.5rem 1rem;
                border-radius: 20px;
                font-size: 0.9rem;
                margin-bottom: 3rem;
                animation: fadeInUp 1s ease 0.4s both;
            }
            
            .status-indicator {
                display: inline-block;
                width: 8px;
                height: 8px;
                background: #00ff88;
                border-radius: 50%;
                margin-right: 0.5rem;
                animation: pulse 2s infinite;
            }
            
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }
            
            /* Demo section */
            .demo-container {
                background: rgba(255, 255, 255, 0.05);
                backdrop-filter: blur(20px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 20px;
                padding: 3rem;
                margin: 3rem 0;
                animation: fadeInUp 1s ease 0.6s both;
            }
            
            .demo-title {
                font-size: 2rem;
                font-weight: 600;
                margin-bottom: 2rem;
                text-align: center;
                color: #00d4ff;
            }
            
            .input-container {
                position: relative;
                margin-bottom: 1.5rem;
            }
            
            .question-input {
                width: 100%;
                padding: 1.2rem 1.5rem;
                border: 2px solid rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                background: rgba(255, 255, 255, 0.05);
                color: white;
                font-size: 1rem;
                transition: all 0.3s ease;
                font-family: inherit;
            }
            
            .question-input:focus {
                outline: none;
                border-color: #00d4ff;
                box-shadow: 0 0 20px rgba(0, 212, 255, 0.2);
                background: rgba(255, 255, 255, 0.08);
            }
            
            .question-input::placeholder {
                color: rgba(255, 255, 255, 0.5);
            }
            
            .ask-button {
                background: linear-gradient(45deg, #00d4ff, #5a67d8);
                color: white;
                border: none;
                padding: 1.2rem 3rem;
                border-radius: 15px;
                font-size: 1rem;
                font-weight: 600;
                transition: all 0.3s ease;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                width: 100%;
                margin-bottom: 1rem;
            }
            
            .ask-button:hover {
                transform: translateY(-2px);
                box-shadow: 0 15px 40px rgba(0, 212, 255, 0.3);
            }
            
            .ask-button:active {
                transform: translateY(0);
            }
            
            /* Loading animation */
            .loading {
                display: none;
                text-align: center;
                margin: 2rem 0;
            }
            
            .spinner {
                width: 40px;
                height: 40px;
                border: 3px solid rgba(255, 255, 255, 0.1);
                border-top: 3px solid #00d4ff;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin: 0 auto 1rem;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            .answer-box {
                display: none;
                background: rgba(0, 0, 0, 0.3);
                border-radius: 15px;
                padding: 2rem;
                margin-top: 2rem;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            
            .answer-box h4 {
                color: #00d4ff;
                margin-bottom: 1rem;
                font-size: 1.1rem;
            }
            
            .answer-box a {
                color: #00d4ff;
                text-decoration: none;
                margin: 0.5rem 0;
                display: block;
                transition: color 0.3s ease;
            }
            
            .answer-box a:hover {
                color: #ffffff;
            }
            
            /* Feature cards */
            .features-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 2rem;
                margin: 4rem 0;
            }
            
            .feature-card {
                background: rgba(255, 255, 255, 0.05);
                backdrop-filter: blur(20px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 20px;
                padding: 2rem;
                text-align: center;
                transition: all 0.3s ease;
                animation: fadeInUp 1s ease 0.8s both;
            }
            
            .feature-card:hover {
                transform: translateY(-10px);
                box-shadow: 0 20px 60px rgba(0, 212, 255, 0.1);
                border-color: rgba(0, 212, 255, 0.3);
            }
            
            .feature-icon {
                font-size: 2.5rem;
                margin-bottom: 1rem;
                display: block;
            }
            
            .feature-title {
                font-size: 1.2rem;
                font-weight: 600;
                margin-bottom: 1rem;
                color: #00d4ff;
            }
            
            .feature-desc {
                color: rgba(255, 255, 255, 0.7);
                line-height: 1.6;
                margin-bottom: 1.5rem;
            }
            
            .feature-link {
                background: rgba(0, 212, 255, 0.1);
                color: #00d4ff;
                padding: 0.8rem 1.5rem;
                border-radius: 10px;
                text-decoration: none;
                font-weight: 500;
                transition: all 0.3s ease;
                display: inline-block;
            }
            
            .feature-link:hover {
                background: rgba(0, 212, 255, 0.2);
                transform: translateY(-2px);
            }
            
            /* Footer */
            .footer {
                text-align: center;
                margin-top: 4rem;
                padding: 2rem;
                border-top: 1px solid rgba(255, 255, 255, 0.1);
                color: rgba(255, 255, 255, 0.6);
            }
            
            /* Animations */
            @keyframes fadeInUp {
                from {
                    opacity: 0;
                    transform: translateY(30px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            /* Responsive */
            @media (max-width: 768px) {
                .nav-links {
                    display: none;
                }
                
                .main-content {
                    padding: 2rem 1rem;
                }
                
                .demo-container {
                    padding: 2rem 1.5rem;
                }
                
                .features-grid {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>
    <body>
        <!-- Navigation -->
        <nav class="navbar">
            <div class="nav-container">
                <div class="logo">🤖 TDS Virtual TA</div>
                <ul class="nav-links">
                    <li><a href="/docs">API Docs</a></li>
                    <li><a href="/health">Health</a></li>
                    <li><a href="/api/solve-sample-problem">Calculator</a></li>
                </ul>
                <a href="#demo" class="cta-button">Try Now</a>
            </div>
        </nav>

        <!-- Main Content -->
        <div class="main-content">
            <!-- Hero Section -->
            <section class="hero-section">
                <h1 class="hero-title">Streamline Learning,<br>Skyrocket Performance,<br>and Delight Students</h1>
                <p class="hero-subtitle">
                    Your AI-Powered Teaching Assistant for Tools in Data Science course. 
                    Get instant help with assignments, model selection, token calculations, and more.
                </p>
                <div class="status-badge">
                    <span class="status-indicator"></span>
                    Online & Ready • Last updated: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC") + """
                </div>
            </section>

            <!-- Demo Section -->
            <section id="demo" class="demo-container">
                <h2 class="demo-title">💬 Ask Me Anything About TDS</h2>
                <div class="input-container">
                    <input type="text" class="question-input" id="questionInput" 
                           placeholder="Ask me anything about TDS... (e.g., 'Should I use gpt-4o-mini or gpt-3.5-turbo?')">
                </div>
                <button class="ask-button clickable" onclick="askQuestion()">Ask Question</button>
                
                <div class="loading" id="loading">
                    <div class="spinner"></div>
                    <p>AI is thinking...</p>
                </div>
                
                <div class="answer-box" id="answerBox">
                    <h4>📝 Answer:</h4>
                    <p id="answerText"></p>
                    <div id="linksSection"></div>
                </div>
            </section>

            <!-- Features Grid -->
            <section class="features-grid">
                <div class="feature-card">
                    <span class="feature-icon">📊</span>
                    <h3 class="feature-title">API Documentation</h3>
                    <p class="feature-desc">Interactive Swagger docs with all endpoints, request/response examples, and testing interface.</p>
                    <a href="/docs" class="feature-link clickable">Explore API</a>
                </div>
                
                <div class="feature-card">
                    <span class="feature-icon">🔍</span>
                    <h3 class="feature-title">Health Monitoring</h3>
                    <p class="feature-desc">Real-time system status, component health checks, and performance monitoring.</p>
                    <a href="/health" class="feature-link clickable">Check Status</a>
                </div>
                
                <div class="feature-card">
                    <span class="feature-icon">🧮</span>
                    <h3 class="feature-title">Token Calculator</h3>
                    <p class="feature-desc">Calculate GPT API costs, token counts, and solve sample problems with precision.</p>
                    <a href="/api/solve-sample-problem" class="feature-link clickable">Try Calculator</a>
                </div>
                
                <div class="feature-card">
                    <span class="feature-icon">💰</span>
                    <h3 class="feature-title">Cost Analysis</h3>
                    <p class="feature-desc">Analyze token costs for different models and optimize your AI spending.</p>
                    <a href="#" onclick="showTokenCalculator()" class="feature-link clickable">Calculate Costs</a>
                </div>
            </section>
        </div>

        <!-- Footer -->
        <footer class="footer">
            <p>Built with FastAPI • Deployed on Railway • Optimized for 4GB containers</p>
            <p>🚀 Ready to help with your TDS assignments and questions!</p>
        </footer>
        
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
                    const response = await fetch(window.location.origin + '/api/', {
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
                    fetch(window.location.origin + '/api/calculate-tokens', {
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