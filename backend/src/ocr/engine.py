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
        Extract text from image using EasyOCR with tuned parameters.
        """
        if image is None:
            logger.warning("Received None image for OCR. Skipping.")
            return []
            
        logger.info("Starting tuned OCR extraction...")
        
        # Tuned parameters for high performance
        try:
            results = self.reader.readtext(
                image,
                paragraph=True,
                slope_ths=0.2,
                height_ths=0.5
            )
        except Exception as e:
            logger.warning(f"EasyOCR tuned inference failed ({e}). Retrying with safe defaults...")
            try:
                # Provide a basic non-dict readtext method
                results = self.reader.readtext(image)
            except Exception as e2:
                logger.error(f"EasyOCR safe fallback also failed: {e2}")
                return []
                
        if results is None or isinstance(results, bool):
            logger.warning(f"EasyOCR returned invalid type: {type(results)}. Forcing list.")
            results = []
            
        elif not isinstance(results, (list, tuple)):
            logger.warning(f"EasyOCR returned unexpected type: {type(results)}. Forcing list.")
            results = list(results) if hasattr(results, "__iter__") else []

        extracted_data = []
        for result in results:
            # results might have diff structure with paragraph=True
            if len(result) == 3:
                bbox, text, prob = result
            else:
                bbox, text = result
                prob = 0.9 # Default for paragraph grouping if missing
                
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
