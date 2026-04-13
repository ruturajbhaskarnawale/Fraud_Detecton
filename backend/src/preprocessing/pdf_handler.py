from pdf2image import convert_from_path
import os

class PDFHandler:
    @staticmethod
    def convert_to_images(pdf_path, output_folder=None):
        """
        Convert a PDF file to a list of PIL Images.
        """
        try:
            images = convert_from_path(pdf_path, dpi=300)
            return images
        except Exception as e:
            print(f"Error converting PDF: {e}")
            return []

    @staticmethod
    def save_images(images, output_folder, prefix="page"):
        """Save list of PIL images to a folder."""
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        saved_paths = []
        for i, image in enumerate(images):
            path = os.path.join(output_folder, f"{prefix}_{i}.png")
            image.save(path, "PNG")
            saved_paths.append(path)
        return saved_paths
