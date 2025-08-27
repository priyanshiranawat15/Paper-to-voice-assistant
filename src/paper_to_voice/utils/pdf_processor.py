"""
Utility functions for PDF processing and image encoding
"""

import os
import base64
import streamlit as st
import pypdfium2 as pdfium


def encode_image_to_base64(file_path: str) -> str:
    """
    Encode an image file to base64 string
    
    Args:
        file_path: Path to the image file
        
    Returns:
        Base64 encoded image string with data URI prefix
    """
    with open(file_path, "rb") as img_file:
        return f"data:image/jpeg;base64,{base64.b64encode(img_file.read()).decode()}"


def process_pdf(pdf_path: str) -> list[str]:
    """
    Convert PDF pages to individual image files
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        List of image filenames created
    """
    image_filenames = []
    try:
        pdf = pdfium.PdfDocument(pdf_path)
        num_pages = len(pdf)

        output_dir = os.path.dirname(pdf_path)
        os.makedirs(output_dir, exist_ok=True)

        for i in range(num_pages):
            page = pdf[i]
            image = page.render(scale=4).to_pil()

            filename = f"Photo_{i:03d}.jpg"
            image_path = os.path.join(output_dir, filename)
            image.save(image_path)
            image_filenames.append(filename)

    except Exception as e:
        st.error(f"Error processing PDF: {e}")

    return image_filenames
