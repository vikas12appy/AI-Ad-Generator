import os
import base64
from PIL import Image
import io

def save_uploaded_file(uploaded_file):
    """
    Save an uploaded file to the assets directory.
    """
    # Create assets directory if it doesn't exist
    if not os.path.exists("assets"):
        os.makedirs("assets")
    
    # Save the file
    file_path = os.path.join("assets", uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return file_path

def create_output_directory():
    """
    Create the output directory if it doesn't exist.
    """
    if not os.path.exists("output"):
        os.makedirs("output")

def save_generated_ad(ad_content, format_name, variation_number):
    """
    Save a generated ad to the output directory.
    """
    # Create output directory if it doesn't exist
    create_output_directory()
    
    # Save text content
    text_path = os.path.join("output", f"{format_name}_variation_{variation_number}_text.txt")
    with open(text_path, "w") as f:
        f.write(ad_content["text"])
    
    # Save image content if present
    if "image" in ad_content and ad_content["image"]:
        image_path = os.path.join("output", f"{format_name}_variation_{variation_number}_image.png")
        image_data = base64.b64decode(ad_content["image"])
        image = Image.open(io.BytesIO(image_data))
        image.save(image_path)
    
    return {
        "text_path": text_path,
        "image_path": image_path if "image" in ad_content and ad_content["image"] else None
    }

def load_brand_guidelines(file_path):
    """
    Load brand guidelines from a JSON file.
    """
    import json
    
    with open(file_path, "r") as f:
        return json.load(f)

def save_brand_guidelines(guidelines, file_path):
    """
    Save brand guidelines to a JSON file.
    """
    import json
    
    with open(file_path, "w") as f:
        json.dump(guidelines, f, indent=4) 