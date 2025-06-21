import os
import requests
from bs4 import BeautifulSoup
import io
from PIL import Image, ImageDraw
from config import SAVE_DIRECTORY, DIALOGUE_FILENAME, IMAGE_FILENAME

def get_headers():
    """Return headers for web requests to avoid being blocked"""
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }

def save_dialogue_to_file(dialogue):
    """Save generated dialogue to a file"""
    try:
        # Create a directory for saved files if it doesn't exist
        if not os.path.exists(SAVE_DIRECTORY):
            os.makedirs(SAVE_DIRECTORY)
        filename = os.path.join(SAVE_DIRECTORY, DIALOGUE_FILENAME)
        with open(filename, "w", encoding="utf-8") as file:
            file.write(dialogue)
        print(f"Dialogue saved to {filename}")
        return True
    except Exception as e:
        print(f"Failed to save dialogue: {e}")
        return False

def save_image_to_file(image_bytes):
    """Save generated image to a file"""
    try:
        if not os.path.exists(SAVE_DIRECTORY):
            os.makedirs(SAVE_DIRECTORY)

        filename = os.path.join(SAVE_DIRECTORY, IMAGE_FILENAME)
        with open(filename, "wb") as file:
            file.write(image_bytes)
        print(f"Image saved to {filename}")
        return True
    except Exception as e:
        print(f"Failed to save image: {e}")
        return False

def create_error_image(error_message):
    """Create an error image with the given message"""
    try:
        img = Image.new('RGB', (600, 400), color=(200, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.text((10, 10), "Error Generating Image", fill=(255, 255, 255))
        draw.text((10, 50), f"Error: {str(error_message)[:150]}", fill=(255, 255, 255))

        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        return img_byte_arr.getvalue()
    except Exception:
        return None

def create_fallback_image():
    """Create a fallback image when generation fails"""
    try:
        img = Image.new('RGB', (600, 400), color=(73, 109, 137))
        draw = ImageDraw.Draw(img)
        draw.text((10, 10), "Image Generation Failed", fill=(255, 255, 255))
        draw.text((10, 50), "Please check your API settings", fill=(255, 255, 255))

        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        return img_byte_arr.getvalue()
    except Exception:
        return None
