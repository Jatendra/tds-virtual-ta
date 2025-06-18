from fastapi import FastAPI, HTTPException
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

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "TDS Virtual TA is running!", "timestamp": datetime.now().isoformat()}

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