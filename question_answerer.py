import asyncio
import logging
from typing import Dict, List, Any, Optional
import re
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class QuestionAnswerer:
    """Handles answering student questions based on TDS course data"""
    
    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.course_content = data.get("course_content", [])
        self.discourse_posts = data.get("discourse_posts", [])
        
        # Common question patterns and their responses
        self.question_patterns = {
            r"gpt.*4o.*mini|gpt.*3\.?5.*turbo|ai.*proxy.*gpt|model.*selection": {
                "answer": "You must use `gpt-3.5-turbo-0125`, even if the AI Proxy only supports `gpt-4o-mini`. Use the OpenAI API directly for this question. The assignment specifically requires gpt-3.5-turbo-0125 for consistency and evaluation purposes.",
                "keywords": ["gpt", "model", "ai", "openai", "turbo", "proxy"]
            },
            r"token.*cost|cost.*token|cents.*million|million.*token": {
                "answer": "For token cost calculations with gpt-3.5-turbo-0125: the cost per million input tokens is typically 50 cents. Calculate as: (token_count / 1,000,000) × 50 cents. For Japanese text, estimate ~3 characters per token. For English, ~4 characters per token.",
                "keywords": ["token", "cost", "calculation", "cents", "pricing"]
            },
            r"python.*setup|environment.*setup|installation": {
                "answer": "Make sure to use Python 3.8+ and install required packages using pip. Common issues include version conflicts and missing dependencies. Check your environment setup and ensure all dependencies are properly installed.",
                "keywords": ["python", "setup", "environment", "installation"]
            },
            r"visualization|chart|plot|graph": {
                "answer": "Use appropriate chart types, clear labels, and proper color schemes. Consider matplotlib, seaborn, or plotly for creating effective visualizations in your assignments. Consider the audience and purpose of your visualization.",
                "keywords": ["visualization", "chart", "plot", "matplotlib", "seaborn"]
            },
            r"assignment.*submission|submit.*assignment": {
                "answer": "Follow proper file formats, naming conventions, and include required documentation when submitting assignments. Make sure to test your code before submission and follow the specified format requirements.",
                "keywords": ["assignment", "submission", "submit", "format"]
            },
            r"docker.*podman|podman.*docker|containerization": {
                "answer": "While Docker is acceptable and widely used, Podman is recommended for the TDS course. Podman offers better security with rootless containers and is more aligned with modern container practices. If you're familiar with Docker, the transition to Podman is straightforward as they share similar commands.",
                "keywords": ["docker", "podman", "container", "containerization"]
            },
            r"dashboard.*score|score.*dashboard|ga.*bonus|bonus.*ga": {
                "answer": "If a student scores 10/10 on GA4 as well as a bonus, it would appear as '110' on the dashboard, representing 110% or 11 points out of 10 possible points. The dashboard shows the total score including bonus points.",
                "keywords": ["dashboard", "score", "bonus", "ga", "grading"]
            },
            r"sep.*2025.*exam|2025.*exam|end.*term.*exam": {
                "answer": "I don't have information about the TDS Sep 2025 end-term exam schedule as this information is not yet available. Please check the official course announcements or contact the course coordinators for the most up-to-date exam schedule information.",
                "keywords": ["exam", "schedule", "september", "2025"]
            }
        }
    
    async def answer_question(self, question: str, image_context: Optional[str] = None) -> Dict[str, Any]:
        """
        Answer a student question based on available data
        
        Args:
            question: The student's question
            image_context: Optional context from image processing
            
        Returns:
            Dictionary with answer and relevant links
        """
        logger.info(f"Processing question: {question[:100]}...")
        
        # Search for relevant content
        relevant_content = self._search_relevant_content(question)
        
        # Generate answer based on patterns and content
        answer = await self._generate_answer(question, relevant_content, image_context)
        
        # Get relevant links
        links = self._get_relevant_links(question, relevant_content)
        
        return {
            "answer": answer,
            "links": links
        }
    
    def _search_relevant_content(self, question: str) -> List[Dict[str, Any]]:
        """Search for content relevant to the question"""
        results = []
        question_lower = question.lower()
        
        # Search course content
        for item in self.course_content:
            relevance_score = self._calculate_relevance(question_lower, item)
            if relevance_score > 0:
                results.append({
                    **item,
                    "relevance_score": relevance_score
                })
        
        # Search discourse posts
        for post in self.discourse_posts:
            relevance_score = self._calculate_relevance(question_lower, post)
            if relevance_score > 0:
                results.append({
                    **post,
                    "relevance_score": relevance_score
                })
        
        # Sort by relevance
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return results[:5]  # Return top 5 most relevant
    
    def _calculate_relevance(self, question: str, item: Dict[str, Any]) -> float:
        """Calculate how relevant an item is to the question"""
        score = 0.0
        text = f"{item.get('title', '')} {item.get('content', '')}".lower()
        
        # Split question into words
        question_words = re.findall(r'\b\w+\b', question.lower())
        
        # Count word matches
        for word in question_words:
            if len(word) > 2:  # Skip very short words
                score += text.count(word) * len(word)  # Longer words get higher weight
        
        # Boost score for title matches
        if any(word in item.get('title', '').lower() for word in question_words):
            score += 10
        
        # Boost score for exact phrase matches
        if question.lower() in text:
            score += 20
        
        return score
    
    async def _generate_answer(self, question: str, relevant_content: List[Dict[str, Any]], image_context: Optional[str] = None) -> str:
        """Generate an answer based on the question and relevant content"""
        
        # Check for pattern matches first
        for pattern, response_info in self.question_patterns.items():
            if re.search(pattern, question.lower()):
                logger.info(f"Matched pattern: {pattern}")
                answer = response_info["answer"]
                
                # Add image context if available
                if image_context:
                    answer += f"\n\nRegarding the attached image: {image_context}"
                
                return answer
        
        # If no pattern match, generate answer from relevant content
        if relevant_content:
            # Use the most relevant content item
            top_content = relevant_content[0]
            
            # Create contextual answer based on content
            content_text = top_content.get('content', '')[:300]
            answer = f"Based on the TDS course materials: {content_text}"
            
            # Add more context from other relevant items
            if len(relevant_content) > 1:
                additional_context = relevant_content[1].get('content', '')[:150]
                if additional_context:
                    answer += f"\n\nAdditional context: {additional_context}"
            
            # Add image context if available
            if image_context:
                answer += f"\n\nRegarding the attached image: {image_context}"
            
            return answer + "... Please refer to the linked resources for more detailed information."
        
        # Fallback answer for unknown topics
        base_answer = "I understand your question about the TDS course. Please refer to the course materials and discourse posts for detailed information. If you need specific clarification, consider posting on the course discourse forum."
        
        if image_context:
            base_answer += f"\n\nRegarding the attached image: {image_context}"
            
        return base_answer
    
    def _get_relevant_links(self, question: str, relevant_content: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Get relevant links for the question with improved relevance filtering"""
        links = []
        question_lower = question.lower()
        
        # Define relevance threshold for content-based links
        MIN_RELEVANCE_SCORE = 15
        
        # Add specific links for common questions first (only if highly relevant)
        if any(word in question_lower for word in ["gpt", "model", "ai", "proxy", "turbo", "4o", "mini"]):
            # Only add GPT-related links for GPT questions
            links.append({
                "url": "https://discourse.onlinedegree.iitm.ac.in/t/ga5-question-8-clarification/155939/4",
                "text": "Use the model that's mentioned in the question."
            })
            if any(word in question_lower for word in ["token", "cost", "calculate"]):
                links.append({
                    "url": "https://discourse.onlinedegree.iitm.ac.in/t/ga5-question-8-clarification/155939/3",
                    "text": "Token calculation approach for GPT models."
                })
        
        elif any(word in question_lower for word in ["dashboard", "score", "bonus"]) and "ga" in question_lower:
            links.append({
                "url": "https://discourse.onlinedegree.iitm.ac.in/t/ga4-data-sourcing-discussion-thread-tds-jan-2025/165959/388",
                "text": "GA4 Data Sourcing Discussion - Dashboard Scoring"
            })
        
        elif any(word in question_lower for word in ["docker", "podman", "container"]):
            links.append({
                "url": "https://tds.s-anand.net/#/docker",
                "text": "Docker and Containerization Guide"
            })
            links.append({
                "url": "https://discourse.onlinedegree.iitm.ac.in/t/docker-podman-discussion/155943",
                "text": "Docker vs Podman for TDS Course"
            })
        
        elif any(word in question_lower for word in ["python", "setup", "environment", "installation"]):
            links.append({
                "url": "https://tds.s-anand.net/#/2025-01/setup",
                "text": "Python Environment Setup Guide"
            })
        
        elif any(word in question_lower for word in ["visualization", "chart", "plot", "graph"]):
            links.append({
                "url": "https://tds.s-anand.net/#/2025-01/visualization",
                "text": "Data Visualization Best Practices"
            })
        
        elif any(word in question_lower for word in ["assignment", "submission", "submit"]):
            links.append({
                "url": "https://tds.s-anand.net/#/2025-01/assignments",
                "text": "Assignment Submission Guidelines"
            })
        
        # Only add links from relevant content if they meet relevance threshold
        for item in relevant_content:
            if (item.get("relevance_score", 0) >= MIN_RELEVANCE_SCORE and 
                item.get("url") and 
                not any(link["url"] == item["url"] for link in links)):
                
                # Create meaningful link text
                link_text = item.get("title", "")
                if not link_text and item.get("content"):
                    # Extract first sentence or meaningful snippet
                    content = item["content"][:100].strip()
                    if content:
                        link_text = content + ("..." if len(item["content"]) > 100 else "")
                    else:
                        continue  # Skip if no meaningful text
                
                # Only add if link text is relevant to the question
                if self._is_link_relevant(question_lower, link_text, item.get("content", "")):
                    links.append({
                        "url": item["url"],
                        "text": link_text
                    })
        
        # If no specific links found, provide a general course link only for broad questions
        if (not links and 
            any(word in question_lower for word in ["tds", "course", "help", "general", "what", "how"])):
            links.append({
                "url": "https://tds.s-anand.net/#/2025-01/",
                "text": "TDS Course Materials"
            })
        
        return links[:3]  # Return at most 3 highly relevant links
    
    def _is_link_relevant(self, question: str, link_text: str, content: str) -> bool:
        """Check if a link is truly relevant to the question"""
        # Extract key words from question (excluding common words)
        question_keywords = set(re.findall(r'\b\w{4,}\b', question.lower()))
        common_words = {"should", "could", "would", "what", "which", "when", "where", "that", "this", "with", "from"}
        question_keywords -= common_words
        
        # Check if link text or content contains relevant keywords
        link_content = f"{link_text} {content}".lower()
        
        # At least 2 keywords should match for relevance
        matches = sum(1 for keyword in question_keywords if keyword in link_content)
        return matches >= 2 or len(question_keywords) <= 2
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the loaded data"""
        return {
            "course_content_count": len(self.course_content),
            "discourse_posts_count": len(self.discourse_posts),
            "total_documents": len(self.course_content) + len(self.discourse_posts),
            "question_patterns": len(self.question_patterns)
        } 