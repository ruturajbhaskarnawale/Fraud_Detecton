import torch
from transformers import LayoutLMv3ForTokenClassification, LayoutLMv3Processor
from PIL import Image
import numpy as np

try:
    model_name = "microsoft/layoutlmv3-base"
    processor = LayoutLMv3Processor.from_pretrained(model_name, apply_ocr=False)
    model = LayoutLMv3ForTokenClassification.from_pretrained(model_name, num_labels=21)
    
    # Dummy input
    image = Image.new("RGB", (224, 224))
    words = ["hello", "world"]
    boxes = [[0, 0, 100, 100], [101, 101, 200, 200]]
    
    encoding = processor(image, words, boxes=boxes, return_tensors="pt")
    outputs = model(**encoding)
    print("Success! Logits shape:", outputs.logits.shape)
except Exception as e:
    print("Failed:", e)
