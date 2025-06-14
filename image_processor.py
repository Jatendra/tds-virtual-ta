import base64
import logging
from typing import Optional
from PIL import Image
import io
import asyncio

logger = logging.getLogger(__name__)

class ImageProcessor:
    """Handles processing of base64 encoded images"""
    
    def __init__(self):
        self.supported_formats = ['JPEG', 'PNG', 'GIF', 'BMP', 'WEBP']
    
    async def process_image(self, base64_image: str) -> Optional[str]:
        """
        Process a base64 encoded image and extract context
        
        Args:
            base64_image: Base64 encoded image string
            
        Returns:
            String description of the image content or None if processing fails
        """
        try:
            # Decode base64 image
            image_data = base64.b64decode(base64_image)
            
            # Open image with PIL
            image = Image.open(io.BytesIO(image_data))
            
            # Get basic image info
            width, height = image.size
            format_name = image.format
            mode = image.mode
            
            logger.info(f"Processing image: {width}x{height}, format: {format_name}, mode: {mode}")
            
            # For now, return basic image information
            # In a real implementation, you might use OCR or image recognition
            context = f"Image attachment detected: {width}x{height} {format_name} image"
            
            # Try to detect if it's a screenshot (common for TDS questions)
            if self._is_likely_screenshot(image):
                context += ". This appears to be a screenshot, possibly showing code, error messages, or assignment questions."
            
            # Try to detect text-heavy images (might contain code or questions)
            if self._is_text_heavy(image):
                context += ". This image appears to contain text content, possibly code or assignment questions."
            
            return context
            
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            return None
    
    def _is_likely_screenshot(self, image: Image.Image) -> bool:
        """
        Heuristic to determine if an image is likely a screenshot
        """
        width, height = image.size
        
        # Screenshots often have specific aspect ratios
        aspect_ratio = width / height
        
        # Common screenshot characteristics
        if (width > 800 and height > 600) or (aspect_ratio > 1.3 and aspect_ratio < 2.0):
            return True
        
        return False
    
    def _is_text_heavy(self, image: Image.Image) -> bool:
        """
        Heuristic to determine if an image contains a lot of text
        """
        # Convert to grayscale for analysis
        gray_image = image.convert('L')
        
        # Get image statistics
        width, height = gray_image.size
        
        # For now, use simple heuristics
        # In a real implementation, you might use OCR or edge detection
        
        # Assume larger images with certain aspect ratios might contain text
        if width > 400 and height > 300:
            return True
        
        return False
    
    async def extract_text_from_image(self, base64_image: str) -> Optional[str]:
        """
        Extract text from image using OCR (placeholder implementation)
        
        In a real implementation, you would use libraries like:
        - pytesseract for OCR
        - easyocr for better accuracy
        - Google Vision API for cloud-based OCR
        """
        try:
            # This is a placeholder - in reality you'd implement OCR here
            logger.info("OCR text extraction not implemented - returning placeholder")
            return "Text extraction from images is not yet implemented. Please describe the image content in your question."
            
        except Exception as e:
            logger.error(f"Error extracting text from image: {str(e)}")
            return None
    
    def validate_image(self, base64_image: str) -> bool:
        """
        Validate that the base64 string represents a valid image
        """
        try:
            image_data = base64.b64decode(base64_image)
            image = Image.open(io.BytesIO(image_data))
            
            # Check if format is supported
            if image.format not in self.supported_formats:
                logger.warning(f"Unsupported image format: {image.format}")
                return False
            
            # Check image size (prevent extremely large images)
            width, height = image.size
            max_size = 4096  # 4K max
            
            if width > max_size or height > max_size:
                logger.warning(f"Image too large: {width}x{height}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Image validation failed: {str(e)}")
            return False 