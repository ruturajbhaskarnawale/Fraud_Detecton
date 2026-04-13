import easyocr
import logging
import os
import cv2

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('OCREngine')

class OCREngine:
    def __init__(self, languages=['en']):
        """
        Initialize EasyOCR reader.
        Default is English.
        """
        logger.info(f"Initializing EasyOCR with languages: {languages}")
        self.reader = easyocr.Reader(languages)

    def extract_text(self, image, min_confidence=0.4):
        """
        Extract text from image using EasyOCR.
        Returns a list of dicts with text, bounding box, and confidence.
        """
        logger.info("Starting OCR extraction...")
        
        # EasyOCR can take image path, cv2 image, or PIL image
        results = self.reader.readtext(image)
        
        extracted_data = []
        for (bbox, text, prob) in results:
            if prob >= min_confidence:
                extracted_data.append({
                    "text": text,
                    "bbox": [list(map(int, pt)) for pt in bbox],
                    "confidence": float(prob)
                })
        
        logger.info(f"Extracted {len(extracted_data)} text blocks above confidence {min_confidence}")
        return extracted_data

    def get_full_text(self, extracted_data):
        """Convert extracted data list to a single string."""
        return "\n".join([item["text"] for item in extracted_data])

    def log_results(self, extracted_data, output_path=None):
        """Log OCR results to a file for debugging."""
        log_content = "\n".join([f"[{item['confidence']:.2f}] {item['text']}" for item in extracted_data])
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(log_content)
        return log_content
