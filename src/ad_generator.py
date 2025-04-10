import os
import google.generativeai as genai
from dotenv import load_dotenv
import json
from PIL import Image
import io
import base64
import time
from typing import Dict, List, Optional, Union

# Load environment variables
load_dotenv()

# Configure the Gemini API
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables")
genai.configure(api_key=api_key)

class AdGenerator:
    def __init__(self):
        # Use Gemini 1.5 Pro for text generation (latest stable version)
        self.text_model = genai.GenerativeModel('models/gemini-1.5-pro')
        # Use Gemini 1.5 Pro for vision tasks (since it supports multimodal)
        self.image_model = genai.GenerativeModel('models/gemini-1.5-pro')
        
        # Define supported ad formats and their specifications
        self.ad_formats = {
            "Social Media Post": {
                "text_length": "Short and punchy, max 280 characters",
                "image_size": "1200x630 pixels",
                "components": ["headline", "main_text", "cta"]
            },
            "Banner Ad": {
                "text_length": "Very concise, max 50 characters",
                "image_size": "728x90 pixels",
                "components": ["headline", "cta"]
            },
            "Email Marketing": {
                "text_length": "Detailed but scannable, max 500 characters",
                "image_size": "600x300 pixels",
                "components": ["subject_line", "headline", "main_text", "cta"]
            },
            "Print Ad": {
                "text_length": "Balanced copy, max 200 characters",
                "image_size": "8.5x11 inches",
                "components": ["headline", "subheadline", "main_text", "cta"]
            }
        }

    def generate_ads(self, reference_analysis: Dict, brand_guidelines: Dict, 
                    ad_format: str, num_variations: int, style_adjustments: Optional[Dict] = None) -> List[Dict]:
        """
        Generate new ads based on reference analysis and brand guidelines.
        
        Args:
            reference_analysis (Dict): Analysis of the reference ad
            brand_guidelines (Dict): Brand specifications and guidelines
            ad_format (str): Desired ad format
            num_variations (int): Number of variations to generate
            style_adjustments (Dict, optional): Specific style adjustments requested
            
        Returns:
            List[Dict]: List of generated advertisements
        """
        generated_ads = []
        format_specs = self.ad_formats.get(ad_format, {})
        
        for i in range(num_variations):
            try:
                # Generate text content with components
                text_content = self._generate_text_content(
                    reference_analysis,
                    brand_guidelines,
                    ad_format,
                    format_specs,
                    style_adjustments
                )
                
                # Generate image if format requires it
                image_content = None
                if "image_size" in format_specs:
                    image_content = self._generate_image_content(
                        reference_analysis,
                        brand_guidelines,
                        text_content,
                        ad_format,
                        format_specs,
                        style_adjustments
                    )
                
                generated_ads.append({
                    "text": text_content,
                    "image": image_content,
                    "format": ad_format,
                    "specs": format_specs
                })
                
            except Exception as e:
                print(f"Error generating ad variation {i+1}: {str(e)}")
                continue
        
        return generated_ads

    def _generate_text_content(self, reference_analysis: Dict, brand_guidelines: Dict,
                             ad_format: str, format_specs: Dict, 
                             style_adjustments: Optional[Dict] = None) -> Dict:
        """
        Generate ad copy using the Gemini API with specific components
        """
        # Prepare brand voice and style guidance
        brand_voice = self._prepare_brand_voice(brand_guidelines, style_adjustments)
        
        prompt = f"""
        Create compelling ad copy following these specifications:
        
        Reference Analysis:
        {json.dumps(reference_analysis, indent=2)}
        
        Brand Guidelines:
        {json.dumps(brand_guidelines, indent=2)}
        
        Format Requirements:
        - Type: {ad_format}
        - Text Length: {format_specs.get('text_length', 'Standard length')}
        - Required Components: {', '.join(format_specs.get('components', []))}
        
        Brand Voice:
        {brand_voice}
        
        Style Adjustments:
        {json.dumps(style_adjustments, indent=2) if style_adjustments else 'None'}
        
        Please generate ad copy in JSON format with the following components:
        {json.dumps(format_specs.get('components', []), indent=2)}
        
        Each component should reflect the brand voice and style while maintaining the specified length constraints.
        """
        
        try:
            response = self.text_model.generate_content(prompt)
            
            # Extract JSON from the response
            response_text = response.text
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                try:
                    content = json.loads(json_str)
                    return content
                except json.JSONDecodeError:
                    # If JSON parsing fails, structure the response manually
                    return {
                        "raw_text": response_text,
                        "error": "Failed to parse JSON response"
                    }
            else:
                # If no JSON found, structure the entire response
                return {
                    "raw_text": response_text,
                    "error": "No JSON found in response"
                }
                
        except Exception as e:
            return {
                "error": f"Error generating text: {str(e)}",
                "raw_text": ""
            }

    def _generate_image_content(self, reference_analysis: Dict, brand_guidelines: Dict,
                              text_content: Dict, ad_format: str, format_specs: Dict,
                              style_adjustments: Optional[Dict] = None) -> Optional[str]:
        """
        Generate image using Stable Diffusion API with brand consistency
        """
        import requests

        # Get Stable Diffusion API key
        api_key = os.getenv('STABILITY_API_KEY')
        if not api_key:
            print("Warning: STABILITY_API_KEY not found. Using placeholder image.")
            return self._generate_placeholder_image(ad_format)

        # Extract brand colors and visual elements
        colors = brand_guidelines.get('colors', [])
        fonts = brand_guidelines.get('fonts', [])
        style = brand_guidelines.get('style', 'Professional')

        # Parse format size
        size_str = format_specs.get('image_size', '1024x1024')
        try:
            if 'x' in size_str:
                # Extract numbers from the size string, ignoring units
                import re
                numbers = re.findall(r'\d+', size_str)
                if len(numbers) >= 2:
                    target_width, target_height = int(numbers[0]), int(numbers[1])
                else:
                    target_width, target_height = 1024, 1024
            else:
                target_width, target_height = 1024, 1024
        except Exception as e:
            print(f"Error parsing image size: {str(e)}")
            target_width, target_height = 1024, 1024

        # Map to the closest allowed dimensions for Stable Diffusion XL
        allowed_dimensions = [
            (1024, 1024), (1152, 896), (1216, 832), (1344, 768), (1536, 640),
            (640, 1536), (768, 1344), (832, 1216), (896, 1152)
        ]
        
        # Find the closest allowed dimensions
        closest_dimensions = min(
            allowed_dimensions,
            key=lambda dim: abs(dim[0] - target_width) + abs(dim[1] - target_height)
        )
        
        width, height = closest_dimensions
        print(f"Using dimensions {width}x{height} (closest to requested {target_width}x{target_height})")

        # Create prompt for image generation
        prompt = f"""Create a professional advertisement image with:
        Style: {style}
        Colors: {', '.join(colors)}
        Format: {ad_format}
        Brand Elements: Professional, modern, clean design
        Text Elements: {json.dumps(text_content)}
        """

        try:
            response = requests.post(
                "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Authorization": f"Bearer {api_key}"
                },
                json={
                    "text_prompts": [{"text": prompt}],
                    "cfg_scale": 7,
                    "height": height,
                    "width": width,
                    "samples": 1,
                    "steps": 30,
                },
            )

            if response.status_code != 200:
                print(f"Error generating image: {response.text}")
                return self._generate_placeholder_image(ad_format)

            # Create directory if it doesn't exist
            os.makedirs("generated_images", exist_ok=True)

            # Save the generated image
            timestamp = int(time.time())
            image_path = f"generated_images/ad_{ad_format.lower().replace(' ', '_')}_{timestamp}.png"

            # Get the image data from the response
            data = response.json()
            if data and "artifacts" in data and len(data["artifacts"]) > 0:
                image_data = base64.b64decode(data["artifacts"][0]["base64"])
                with open(image_path, "wb") as f:
                    f.write(image_data)
                return image_path

        except Exception as e:
            print(f"Error generating image: {str(e)}")
            return self._generate_placeholder_image(ad_format)

        return self._generate_placeholder_image(ad_format)

    def _generate_placeholder_image(self, ad_format: str) -> str:
        """
        Generate a placeholder image with text when image generation fails
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs("generated_images", exist_ok=True)
            
            # Generate unique filename with format info
            timestamp = int(time.time())
            image_path = f"generated_images/ad_{ad_format.lower().replace(' ', '_')}_{timestamp}.png"
            
            # Create a placeholder image with text
            width, height = 800, 600
            img = Image.new('RGB', (width, height), color='white')
            
            # Add text to the image
            from PIL import ImageDraw, ImageFont
            draw = ImageDraw.Draw(img)
            
            # Try to load a font, fall back to default if not available
            try:
                font = ImageFont.truetype("Arial", 40)
            except:
                font = ImageFont.load_default()
            
            text = f"Placeholder Image\n{ad_format}\n{width}x{height}"
            
            # Calculate text position to center it
            bbox = draw.multiline_textbbox((0, 0), text, font=font, align='center')
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (width - text_width) / 2
            y = (height - text_height) / 2
            
            # Draw text with a light gray color
            draw.multiline_text((x, y), text, fill='#666666', font=font, align='center')
            
            img.save(image_path)
            return image_path
            
        except Exception as e:
            print(f"Error generating placeholder image: {str(e)}")
            return None

    def _prepare_brand_voice(self, brand_guidelines: Dict, 
                           style_adjustments: Optional[Dict] = None) -> str:
        """
        Prepare detailed brand voice guidance
        """
        voice = brand_guidelines.get('voice', '')
        target_audience = brand_guidelines.get('target_audience', '')
        
        voice_guidance = f"""
        Brand Voice Characteristics:
        - Primary Voice: {voice}
        - Target Audience: {target_audience}
        """
        
        if style_adjustments:
            voice_guidance += f"\nStyle Adjustments:\n"
            for key, value in style_adjustments.items():
                voice_guidance += f"- {key}: {value}\n"
        
        return voice_guidance

    def _download_image(self, url: str) -> str:
        """
        Download image from URL and convert to base64.
        """
        import requests
        
        response = requests.get(url)
        image = Image.open(io.BytesIO(response.content))
        
        # Convert to base64
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode() 