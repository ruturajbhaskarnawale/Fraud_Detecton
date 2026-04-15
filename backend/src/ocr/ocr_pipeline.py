import logging
import cv2
import os
import sys

# Ensure backend root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.ocr.engine import OCREngine
from src.ocr.preprocessor import OCRPreprocessor
from src.ocr.post_processor import OCRPostProcessor

logger = logging.getLogger('HybridOCRPipeline')

class HybridOCRPipeline:
    def __init__(self):
        self.engine = OCREngine(languages=['en', 'hi']) # Added Hindi support
        self.preprocessor = OCRPreprocessor()
        self.post_processor = OCRPostProcessor()
        self.threshold = 0.65 # Confidence threshold for failover

    def process(self, image_path, doc_type, debug_mode=False):
        """
        Execute Hybrid OCR workflow with failover and debug support.
        """
        logger.info(f"Processing {image_path} with Hybrid Pipeline...")
        
        # 0. Setup Debugging
        debug_dir = r"c:\Users\rutur\OneDrive\Desktop\jotex\data\processed\ocr\debug"
        if debug_mode:
            os.makedirs(os.path.join(debug_dir, "original"), exist_ok=True)
            os.makedirs(os.path.join(debug_dir, "pipeline_a"), exist_ok=True)
            os.makedirs(os.path.join(debug_dir, "pipeline_b"), exist_ok=True)
            os.makedirs(os.path.join(debug_dir, "roi"), exist_ok=True)
            
            base_name = os.path.basename(image_path)
            raw_img = cv2.imread(image_path)
            if raw_img is not None:
                cv2.imwrite(os.path.join(debug_dir, "original", base_name), raw_img)

        # Track 1: Pipeline A (CLAHE + Bilateral)
        img_a = self.preprocessor.pipeline_a(image_path)
        if debug_mode and img_a is not None:
            cv2.imwrite(os.path.join(debug_dir, "pipeline_a", os.path.basename(image_path)), img_a)
            
        data_a = self.engine.extract_text(img_a)
        conf_a = sum([d['confidence'] for d in data_a]) / len(data_a) if data_a else 0
        text_a = self.engine.get_full_text(data_a)
        
        # Safety: Ensure post_processor gets a string
        parsed_a = self.post_processor.format_results(str(text_a), doc_type)
        
        # Dynamic Early Exit: Skip fixed threshold if regex validation passes for both ID and Name
        has_id = bool(parsed_a.get("id_number"))
        has_name = bool(parsed_a.get("name") and len(parsed_a.get("name")) >= 3)
        
        if (has_id and has_name) or (conf_a >= 0.70 and has_id):
            logger.info("Track A successful (Early Exit triggered).")
            return {
                "method": "pipeline_a",
                "confidence": conf_a,
                "data": parsed_a
            }
            
        # Track 2: Failover to Pipeline B (Adaptive Threshold)
        img_b = self.preprocessor.pipeline_b(image_path)
        if debug_mode and img_b is not None:
            cv2.imwrite(os.path.join(debug_dir, "pipeline_b", os.path.basename(image_path)), img_b)

        data_b = self.engine.extract_text(img_b)
        conf_b = sum([d['confidence'] for d in data_b]) / len(data_b) if data_b else 0
        text_b = self.engine.get_full_text(data_b)
        
        parsed_b = self.post_processor.format_results(str(text_b), doc_type)
        
        if conf_b > conf_a and parsed_b.get("id_number"):
            logger.info("Track B improved results.")
            return {
                "method": "pipeline_b",
                "confidence": conf_b,
                "data": parsed_b
            }
            
        # Track 3: Final fallback to Region-based OCR
        logger.info("Attempting ROI-based extraction...")
        raw_rois = self.preprocessor.pipeline_c(image_path, doc_type)
        
        # Defensive Check: ensure rois is a list
        rois = raw_rois if isinstance(raw_rois, list) else []
        
        roi_results = {}
        roi_confidences = []
        
        for i, roi in enumerate(rois):
            roi_data = self.engine.extract_text(roi.get("crop"))
            if debug_mode and roi.get("crop") is not None:
                roi_fn = f"{os.path.basename(image_path)}_{roi.get('label')}_{i}.jpg"
                cv2.imwrite(os.path.join(debug_dir, "roi", roi_fn), roi.get("crop"))
                
            roi_text = self.engine.get_full_text(roi_data)
            roi_results[roi.get("label", f"region_{i}")] = roi_text
            if roi_data:
                roi_confidences.append(sum([d['confidence'] for d in roi_data]) / len(roi_data))
                
        final_roi_text = "\n".join([str(v) for v in roi_results.values()])
        parsed_roi = self.post_processor.format_results(final_roi_text, doc_type)
        
        return {
            "method": "roi_pipeline" if rois else "failed",
            "confidence": sum(roi_confidences)/len(roi_confidences) if roi_confidences else 0,
            "data": parsed_roi if rois else {"full_text": "", "id_number": None, "dob": None}
        }

if __name__ == "__main__":
    # Integration test
    pipeline = HybridOCRPipeline()
    # test_img = "data/final/test/ocr/..."
    # print(pipeline.process(test_img, "aadhaar"))
    pass
