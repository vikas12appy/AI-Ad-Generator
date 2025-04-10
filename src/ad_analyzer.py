import google.generativeai as genai
from PIL import Image
import io
import os
from dotenv import load_dotenv
import base64
import json

# Load environment variables
load_dotenv()

# Configure Gemini
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables")
genai.configure(api_key=api_key)

class AdAnalyzer:
    def __init__(self):
        # Use Gemini 1.5 Pro for analysis (latest stable version)
        self.model = genai.GenerativeModel('models/gemini-1.5-pro')

    def analyze_text(self, text):
        """
        Analyze text-based reference ad to extract key elements.
        """
        prompt = f"""
        Analyze this advertisement text and extract key elements:
        {text}
        
        Please provide:
        1. Main message/theme
        2. Tone of voice
        3. Target audience
        4. Key selling points
        5. Call to action
        6. Writing style
        
        Format the response as valid JSON.
        """
        
        response = self.model.generate_content(prompt)
        
        # Extract JSON from the response
        response_text = response.text
        # Find the JSON part (between first { and last })
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            json_str = response_text[json_start:json_end]
            return json.loads(json_str)
        else:
            # If no JSON found, structure the entire response as JSON
            return {
                "analysis": response_text,
                "error": "Response was not in JSON format"
            }

    def analyze_image(self, image_file):
        """
        Analyze image-based reference ad to extract visual elements.
        """
        try:
            # Load and prepare the image
            image = Image.open(image_file)
            
            prompt = """
            Analyze this advertisement image and provide insights about:
            1. Visual composition
            2. Color scheme
            3. Brand elements
            4. Message clarity
            5. Target audience appeal
            6. Areas for improvement
            
            Format the response as valid JSON.
            """
            
            response = self.model.generate_content([prompt, image])
            
            # Extract JSON from the response
            response_text = response.text
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                return json.loads(json_str)
            else:
                return {
                    "analysis": response_text,
                    "error": "Response was not in JSON format"
                }
                
        except Exception as e:
            return {
                "error": f"Error analyzing image: {str(e)}"
            }

    def extract_brand_elements(self, text_analysis, image_analysis):
        """
        Combine text and image analysis to extract comprehensive brand elements.
        """
        prompt = f"""
        Based on the following analyses, extract comprehensive brand elements:
        
        Text Analysis:
        {json.dumps(text_analysis, indent=2)}
        
        Image Analysis:
        {json.dumps(image_analysis, indent=2)}
        
        Please provide a JSON response with:
        1. Overall brand personality
        2. Key visual elements
        3. Communication style
        4. Target audience profile
        5. Brand voice characteristics
        """
        
        response = self.model.generate_content(prompt)
        
        # Extract JSON from the response
        response_text = response.text
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            json_str = response_text[json_start:json_end]
            return json.loads(json_str)
        else:
            return {
                "analysis": response_text,
                "error": "Response was not in JSON format"
            }

# Create an instance for easy import
ad_analyzer = AdAnalyzer() 