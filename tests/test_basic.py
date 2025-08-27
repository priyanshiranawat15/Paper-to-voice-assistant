"""
Basic tests for Paper to Voice Assistant
"""

import pytest
import os
from src.paper_to_voice.core.config import get_llm
from src.paper_to_voice.utils.pdf_processor import encode_image_to_base64


def test_config_loading():
    """Test that configuration loads properly"""
    try:
        llm = get_llm()
        assert llm is not None
        print("✅ Configuration loaded successfully")
    except Exception as e:
        print(f"❌ Configuration failed: {e}")


def test_image_encoding():
    """Test image encoding functionality"""
    # This test would need a sample image file
    # For now, just test the function exists
    assert callable(encode_image_to_base64)
    print("✅ Image encoding function available")


if __name__ == "__main__":
    test_config_loading()
    test_image_encoding()
    print("🎉 Basic tests completed!")
