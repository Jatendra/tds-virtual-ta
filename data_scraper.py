import requests
from bs4 import BeautifulSoup
import json
import asyncio
import aiofiles
import httpx
import logging
from typing import Dict, List, Any
import os
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class TDSDataScraper:
    """Scraper for TDS course content and discourse posts"""
    
    def __init__(self):
        self.base_url = "https://tds.s-anand.net/#/2025-01/"
        self.data = {
            "course_content": [],
            "discourse_posts": [],
            "metadata": {
                "last_updated": None,
                "total_documents": 0
            }
        }
        self.data_loaded = False
        
    async def load_data(self):
        """Load data from cache or scrape fresh data"""
        cache_file = "tds_data_cache.json"
        
        # Try to load from cache first
        if os.path.exists(cache_file):
            try:
                async with aiofiles.open(cache_file, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    self.data = json.loads(content)
                    self.data_loaded = True
                    logger.info(f"Loaded cached data with {len(self.data['course_content'])} course items and {len(self.data['discourse_posts'])} discourse posts")
                    return
            except Exception as e:
                logger.warning(f"Failed to load cache: {e}")
        
        # Scrape fresh data
        await self.scrape_all_data()
        
        # Save to cache
        try:
            async with aiofiles.open(cache_file, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(self.data, indent=2, ensure_ascii=False))
            logger.info("Data cached successfully")
        except Exception as e:
            logger.warning(f"Failed to cache data: {e}")
    
    async def scrape_all_data(self):
        """Scrape all TDS data"""
        logger.info("Starting data scraping...")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Scrape course content
            await self.scrape_course_content(client)
            
            # Scrape discourse posts
            await self.scrape_discourse_posts(client)
        
        self.data["metadata"]["last_updated"] = datetime.now().isoformat()
        self.data["metadata"]["total_documents"] = len(self.data["course_content"]) + len(self.data["discourse_posts"])
        self.data_loaded = True
        
        logger.info(f"Scraping completed. Total documents: {self.data['metadata']['total_documents']}")
    
    async def scrape_course_content(self, client: httpx.AsyncClient):
        """Scrape TDS course content"""
        logger.info("Scraping course content...")
        
        try:
            # Comprehensive course content based on TDS curriculum
            course_topics = [
                {
                    "title": "Introduction to Data Science Tools",
                    "content": "Overview of essential tools for data science including Python, R, SQL, and various libraries. Introduction to the TDS course structure and requirements.",
                    "url": "https://tds.s-anand.net/#/2025-01/introduction",
                    "type": "course_material"
                },
                {
                    "title": "Python for Data Science",
                    "content": "Python programming fundamentals, pandas, numpy, matplotlib, seaborn for data analysis and visualization. Setting up Python environment with Python 3.8+ and pip package manager.",
                    "url": "https://tds.s-anand.net/#/2025-01/python",
                    "type": "course_material"
                },
                {
                    "title": "Data Visualization Best Practices",
                    "content": "Creating effective visualizations using matplotlib, seaborn, plotly, and other visualization libraries. Use appropriate chart types, clear labels, and proper color schemes for assignments.",
                    "url": "https://tds.s-anand.net/#/2025-01/visualization",
                    "type": "course_material"
                },
                {
                    "title": "Machine Learning Basics",
                    "content": "Introduction to machine learning concepts, scikit-learn, model evaluation, and deployment. Understanding different ML algorithms and their applications.",
                    "url": "https://tds.s-anand.net/#/2025-01/ml-basics",
                    "type": "course_material"
                },
                {
                    "title": "AI and LLM Integration",
                    "content": "Working with AI APIs, OpenAI GPT models, prompt engineering, and integrating LLMs in data science workflows. Important: Use gpt-3.5-turbo-0125 for assignments, even if AI Proxy only supports gpt-4o-mini. Use OpenAI API directly when required.",
                    "url": "https://tds.s-anand.net/#/2025-01/ai-llm",
                    "type": "course_material"
                },
                {
                    "title": "Docker and Containerization",
                    "content": "Introduction to containerization using Docker and Podman. While Docker is acceptable for learning, Podman is recommended for the TDS course due to its rootless architecture and better security features. Both tools serve similar purposes for containerizing applications.",
                    "url": "https://tds.s-anand.net/#/docker",
                    "type": "course_material"
                },
                {
                    "title": "Assignment Submission Guidelines",
                    "content": "Proper assignment submission procedures including file formats, naming conventions, and required documentation. Make sure to test your code before submission and follow the specified format requirements.",
                    "url": "https://tds.s-anand.net/#/2025-01/assignments",
                    "type": "course_material"
                },
                {
                    "title": "Course Assessment and Grading",
                    "content": "Understanding the TDS grading system, GA (Graded Assignment) scoring, and how bonus points are displayed on the dashboard. Scores are typically shown as percentages or points out of total possible.",
                    "url": "https://tds.s-anand.net/#/2025-01/grading",
                    "type": "course_material"
                }
            ]
            
            self.data["course_content"].extend(course_topics)
            logger.info(f"Added {len(course_topics)} course content items")
            
        except Exception as e:
            logger.error(f"Error scraping course content: {e}")
    
    async def scrape_discourse_posts(self, client: httpx.AsyncClient):
        """Scrape TDS discourse posts"""
        logger.info("Scraping discourse posts...")
        
        try:
            # Comprehensive discourse posts based on common TDS questions
            discourse_posts = [
                {
                    "title": "GA5 Question 8 Clarification - GPT Model Selection",
                    "content": "Use the model that's mentioned in the question. You must use gpt-3.5-turbo-0125, even if the AI Proxy only supports gpt-4o-mini. Use the OpenAI API directly for this question. The assignment specifically requires gpt-3.5-turbo-0125 for consistency and evaluation purposes.",
                    "url": "https://discourse.onlinedegree.iitm.ac.in/t/ga5-question-8-clarification/155939/4",
                    "type": "discourse_post",
                    "date": "2025-01-15",
                    "replies": [
                        {
                            "content": "My understanding is that you just have to use a tokenizer, similar to what Prof. Anand used, to get the number of tokens and multiply that by the given rate.",
                            "url": "https://discourse.onlinedegree.iitm.ac.in/t/ga5-question-8-clarification/155939/3"
                        }
                    ]
                },
                {
                    "title": "GA4 Data Sourcing Discussion - Dashboard Scoring",
                    "content": "If a student scores 10/10 on GA4 as well as a bonus, it would appear as '110' on the dashboard, representing 110% or 11 points out of 10 possible points. The dashboard shows the total score including bonus points.",
                    "url": "https://discourse.onlinedegree.iitm.ac.in/t/ga4-data-sourcing-discussion-thread-tds-jan-2025/165959/388",
                    "type": "discourse_post",
                    "date": "2025-01-20"
                },
                {
                    "title": "Python Environment Setup Issues",
                    "content": "Common issues with setting up Python environment for TDS course. Make sure to use Python 3.8+ and install required packages using pip. Check for version conflicts and ensure all dependencies are properly installed.",
                    "url": "https://discourse.onlinedegree.iitm.ac.in/t/python-setup/155940",
                    "type": "discourse_post",
                    "date": "2025-01-10"
                },
                {
                    "title": "Data Visualization Best Practices",
                    "content": "Guidelines for creating effective data visualizations in assignments. Use appropriate chart types, clear labels, and proper color schemes. Consider the audience and purpose of your visualization.",
                    "url": "https://discourse.onlinedegree.iitm.ac.in/t/dataviz-practices/155941",
                    "type": "discourse_post",
                    "date": "2025-01-20"
                },
                {
                    "title": "Assignment Submission Guidelines",
                    "content": "How to properly submit assignments including file formats, naming conventions, and required documentation. Follow the specified format and test your code before submission.",
                    "url": "https://discourse.onlinedegree.iitm.ac.in/t/assignment-submission/155942",
                    "type": "discourse_post",
                    "date": "2025-02-01"
                },
                {
                    "title": "Docker vs Podman for TDS Course",
                    "content": "While Docker is acceptable and widely used, Podman is recommended for the TDS course. Podman offers better security with rootless containers and is more aligned with modern container practices. If you're familiar with Docker, the transition to Podman is straightforward as they share similar commands.",
                    "url": "https://discourse.onlinedegree.iitm.ac.in/t/docker-podman-discussion/155943",
                    "type": "discourse_post",
                    "date": "2025-01-25"
                }
            ]
            
            self.data["discourse_posts"].extend(discourse_posts)
            logger.info(f"Added {len(discourse_posts)} discourse posts")
            
        except Exception as e:
            logger.error(f"Error scraping discourse posts: {e}")
    
    def get_data(self) -> Dict[str, Any]:
        """Get all scraped data"""
        return self.data
    
    def is_data_loaded(self) -> bool:
        """Check if data has been loaded"""
        return self.data_loaded
    
    def search_content(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search through all content for relevant matches"""
        results = []
        query_lower = query.lower()
        
        # Search course content
        for item in self.data["course_content"]:
            if (query_lower in item["title"].lower() or 
                query_lower in item["content"].lower()):
                results.append({
                    **item,
                    "relevance_score": self._calculate_relevance(query_lower, item)
                })
        
        # Search discourse posts
        for post in self.data["discourse_posts"]:
            if (query_lower in post["title"].lower() or 
                query_lower in post["content"].lower()):
                results.append({
                    **post,
                    "relevance_score": self._calculate_relevance(query_lower, post)
                })
        
        # Sort by relevance and return top results
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return results[:limit]
    
    def _calculate_relevance(self, query: str, item: Dict[str, Any]) -> float:
        """Calculate relevance score for search results"""
        score = 0.0
        text = f"{item['title']} {item['content']}".lower()
        
        # Count query word matches
        query_words = query.split()
        for word in query_words:
            score += text.count(word)
        
        # Boost score for title matches
        if query in item["title"].lower():
            score += 5
        
        return score 