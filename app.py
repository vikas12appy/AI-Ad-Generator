import streamlit as st
from src.ad_generator import AdGenerator
from src.ad_analyzer import ad_analyzer
import os
import time
import json
from typing import Dict, List, Optional
import tempfile
from PIL import Image
import io
import re

# Set page configuration
st.set_page_config(
    page_title="AI Ad Generator Pro",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a more classy look
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1a237e;
        text-align: center;
        margin-bottom: 1.5rem;
        font-family: 'Playfair Display', serif;
    }
    .sub-header {
        font-size: 1.8rem;
        color: #283593;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        font-family: 'Playfair Display', serif;
    }
    .section-header {
        font-size: 1.4rem;
        color: #3949ab;
        margin-top: 1.2rem;
        margin-bottom: 0.8rem;
        font-family: 'Playfair Display', serif;
    }
    .info-text {
        font-size: 1.1rem;
        color: #455a64;
        font-family: 'Roboto', sans-serif;
    }
    .success-text {
        color: #2e7d32;
        font-weight: 500;
    }
    .error-text {
        color: #c62828;
        font-weight: 500;
    }
    .warning-text {
        color: #f57c00;
        font-weight: 500;
    }
    .stButton>button {
        width: 100%;
        background-color: #3949ab;
        color: white;
        border-radius: 8px;
        padding: 0.8rem 1.2rem;
        font-weight: 500;
        font-size: 1.1rem;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #283593;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .ad-container {
        background-color: #f5f5f5;
        border-radius: 12px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .brand-section {
        background-color: #e8eaf6;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border: 1px solid #c5cae9;
    }
    .style-section {
        background-color: #e3f2fd;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border: 1px solid #bbdefb;
    }
    .reference-section {
        background-color: #f3e5f5;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border: 1px solid #e1bee7;
    }
    .output-section {
        background-color: #fafafa;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border: 1px solid #eeeeee;
    }
    .color-preview {
        width: 30px;
        height: 30px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 10px;
        border: 2px solid #fff;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .font-preview {
        padding: 5px 10px;
        border-radius: 4px;
        background-color: #fff;
        margin-right: 10px;
        border: 1px solid #e0e0e0;
    }
    .stTextInput>div>div>input {
        border-radius: 8px;
        padding: 0.8rem;
    }
    .stTextArea>div>div>textarea {
        border-radius: 8px;
        padding: 0.8rem;
    }
    .stSelectbox>div>div>select {
        border-radius: 8px;
        padding: 0.8rem;
    }
    .stSlider>div>div>div {
     
    }
</style>
""", unsafe_allow_html=True)

def validate_inputs(brand_name: str, brand_colors: str, brand_fonts: str, 
                   reference_text: str, reference_type: str) -> tuple[bool, str]:
    """Validate user inputs"""
    if not brand_name.strip():
        return False, "Brand name is required"
    if not brand_colors.strip():
        return False, "At least one brand color is required"
    if not brand_fonts.strip():
        return False, "At least one brand font is required"
    if reference_type == "Text Only" and not reference_text.strip():
        return False, "Reference advertisement text is required"
    return True, ""

def display_color_preview(color: str) -> str:
    """Generate HTML for color preview"""
    return f'<div class="color-preview" style="background-color: {color};"></div>'

def display_font_preview(font: str) -> str:
    """Generate HTML for font preview"""
    return f'<div class="font-preview" style="font-family: {font};">{font}</div>'

def handle_gemini_error(error_message: str) -> tuple[bool, str]:
    """Handle Gemini API errors and provide user-friendly messages"""
    # Check for API key expiration error
    if "API key expired" in error_message or "API_KEY_INVALID" in error_message:
        return False, f"""
        <div class="error-text">
            <h3>Gemini API Key Error</h3>
            <p>Your Gemini API key has expired or is invalid. Please renew your API key.</p>
            <p>To fix this issue:</p>
            <ol>
                <li>Go to the <a href="https://ai.google.dev/" target="_blank">Google AI Studio</a></li>
                <li>Navigate to your API keys section</li>
                <li>Create a new API key or renew your existing one</li>
                <li>Update your .env file with the new API key</li>
            </ol>
            <p>After updating your API key, restart the application.</p>
        </div>
        """
    
    # Check for quota error
    if "429" in error_message and "quota" in error_message.lower():
        # Extract retry delay if available
        retry_delay = 60  # Default to 60 seconds
        retry_match = re.search(r'retry_delay\s*{\s*seconds\s*:\s*(\d+)\s*}', error_message)
        if retry_match:
            retry_delay = int(retry_match.group(1))
        
        return False, f"""
        <div class="error-text">
            <h3>Gemini API Quota Exceeded</h3>
            <p>You've reached your current quota limit for the Gemini API. Please try again in {retry_delay} seconds.</p>
            <p>For more information, visit: <a href="https://ai.google.dev/gemini-api/docs/rate-limits" target="_blank">Gemini API Rate Limits</a></p>
        </div>
        """
    
    # Handle other Gemini API errors
    return False, f"""
    <div class="error-text">
        <h3>Gemini API Error</h3>
        <p>An error occurred with the Gemini API: {error_message}</p>
        <p>Please try again later or contact support if the issue persists.</p>
    </div>
    """

def main():
    # Header
    st.markdown('<h1 class="main-header">AI Advertisement Generator Pro</h1>', unsafe_allow_html=True)
    st.markdown('<p class="info-text" style="text-align: center;">Create professional, brand-aligned advertisements with advanced AI technology</p>', unsafe_allow_html=True)
    
    # Create two columns for the main content
    col1, col2 = st.columns([1, 2])
    
    # Left column - Input Parameters
    with col1:
        st.markdown('<h2 class="sub-header">Input Parameters</h2>', unsafe_allow_html=True)
        
        # Reference Content Section
        # st.markdown('<div class="reference-section">', unsafe_allow_html=True)
        st.markdown('<h3 class="section-header">Reference Content</h3>', unsafe_allow_html=True)
        
        reference_type = st.radio(
            "Reference Type",
            ["Text Only", "Text + Image", "Image Only"],
            help="Choose the type of reference content to analyze"
        )
        
        reference_text = None
        if reference_type in ["Text Only", "Text + Image"]:
            reference_text = st.text_area(
                "Reference Advertisement Text",
                placeholder="Enter a sample advertisement text that represents your desired style...",
                height=150,
                help="This text will be analyzed for tone, style, and messaging"
            )
        
        reference_image = None
        if reference_type in ["Text + Image", "Image Only"]:
            uploaded_file = st.file_uploader(
                "Upload Reference Image",
                type=["png", "jpg", "jpeg"],
                help="Upload an image that represents your brand's visual style. This image will be used for analysis to understand your visual style."
            )
            if uploaded_file:
                # Read the uploaded file
                image_data = uploaded_file.getvalue()
                
                # Open the image with PIL
                img = Image.open(io.BytesIO(image_data))
                
                # Calculate new dimensions while maintaining aspect ratio
                max_dimension = 800  # Maximum width or height
                width, height = img.size
                
                if width > height:
                    new_width = min(width, max_dimension)
                    new_height = int(height * (new_width / width))
                else:
                    new_height = min(height, max_dimension)
                    new_width = int(width * (new_height / height))
                
                # Resize the image
                resized_img = img.resize((new_width, new_height), Image.LANCZOS)
                
                # Save the resized image temporarily
                temp_dir = tempfile.gettempdir()
                temp_file_path = os.path.join(temp_dir, f"reference_image_{int(time.time())}.png")
                resized_img.save(temp_file_path, format='PNG')
                reference_image = temp_file_path
                
                # Display image preview
                st.image(resized_img, caption=f"Reference Image Preview ({new_width}x{new_height})", width=300)
                
                # Show original vs resized dimensions
                st.markdown(f"<p class='info-text'>Image resized from {width}x{height} to {new_width}x{new_height}</p>", unsafe_allow_html=True)
                
                # Add option to use uploaded image directly
                use_uploaded_image = st.checkbox(
                    "Use this image directly in the output (instead of generating a new one)",
                    help="If checked, your uploaded image will be used directly in the output. If unchecked, a new image will be generated based on your reference image's style."
                )
                
                if use_uploaded_image:
                    st.info("Your uploaded image will be used directly in the output. No new image will be generated.")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Brand Guidelines Section
        # st.markdown('<div class="brand-section">', unsafe_allow_html=True)
        st.markdown('<h3 class="section-header">Brand Guidelines</h3>', unsafe_allow_html=True)
        
        brand_name = st.text_input(
            "Brand Name", 
            placeholder="Enter your brand name...",
            help="The name of your brand or company"
        )
        brand_voice = st.selectbox(
            "Brand Voice",
            ["Professional and innovative", "Casual and friendly", "Luxury and premium", 
             "Bold and edgy", "Warm and approachable", "Technical and precise"],
            help="Select the primary voice for your brand communications"
        )
        
        # Target audience with dropdown and custom input
        st.markdown('<h4 class="section-header">Target Audience</h4>', unsafe_allow_html=True)
        
        # Dropdown for common target audiences
        common_audiences = [
            "Select or enter custom...",
            "Business professionals",
            "Young adults (18-24)",
            "Parents with young children",
            "Tech enthusiasts",
            "Health-conscious individuals",
            "Luxury consumers",
            "Budget-conscious shoppers",
            "Senior citizens",
            "Students",
            "Fitness enthusiasts",
            "Travelers",
            "Homeowners",
            "Pet owners",
            "Foodies",
            "Environmentalists"
        ]
        
        selected_audience = st.selectbox(
            "Common Target Audiences",
            common_audiences,
            help="Select a common target audience or enter a custom one below"
        )
        
        # Custom target audience input
        if selected_audience == "Select or enter custom...":
            target_audience = st.text_input(
                "Custom Target Audience",
                placeholder="Describe your target audience in detail...",
                help="Describe your target audience in detail (e.g., 'Urban millennials interested in sustainable fashion')"
            )
        else:
            target_audience = selected_audience
        
        st.markdown('<h4 class="section-header">Visual Identity</h4>', unsafe_allow_html=True)
        
        # Brand Colors with color pickers
        st.markdown("**Brand Colors**")
        color_col1, color_col2, color_col3 = st.columns(3)
        
        with color_col1:
            primary_color = st.color_picker("Primary Color", "#1a237e", help="Select your primary brand color")
        
        with color_col2:
            secondary_color = st.color_picker("Secondary Color", "#3949ab", help="Select your secondary brand color")
        
        with color_col3:
            accent_color = st.color_picker("Accent Color", "#7986cb", help="Select your accent color")
        
        # Combine colors for the generator
        brand_colors = f"{primary_color},{secondary_color},{accent_color}"
        
        # Display color previews
        colors_html = "".join([display_color_preview(color.strip()) for color in brand_colors.split(",")])
        st.markdown(f'<div style="display: flex; align-items: center; margin: 10px 0;">{colors_html}</div>', unsafe_allow_html=True)
        
        # Brand Fonts with dropdown
        st.markdown("**Brand Fonts**")
        font_col1, font_col2 = st.columns(2)
        
        with font_col1:
            primary_font = st.selectbox(
                "Primary Font",
                ["Playfair Display", "Roboto", "Montserrat", "Open Sans", "Lato", "Poppins", 
                 "Raleway", "Oswald", "Source Sans Pro", "Merriweather", "PT Sans", "Nunito",
                 "Ubuntu", "Dancing Script", "Pacifico", "Comfortaa", "Quicksand", "Josefin Sans"],
                index=0,
                help="Select your primary brand font"
            )
        
        with font_col2:
            secondary_font = st.selectbox(
                "Secondary Font",
                ["Playfair Display", "Roboto", "Montserrat", "Open Sans", "Lato", "Poppins", 
                 "Raleway", "Oswald", "Source Sans Pro", "Merriweather", "PT Sans", "Nunito",
                 "Ubuntu", "Dancing Script", "Pacifico", "Comfortaa", "Quicksand", "Josefin Sans"],
                index=1,
                help="Select your secondary brand font"
            )
        
        # Combine fonts for the generator
        brand_fonts = f"{primary_font},{secondary_font}"
        
        # Display font previews
        fonts_html = "".join([display_font_preview(font.strip()) for font in brand_fonts.split(",")])
        st.markdown(f'<div style="display: flex; align-items: center; margin: 10px 0;">{fonts_html}</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Style Adjustments Section
        # st.markdown('<div class="style-section">', unsafe_allow_html=True)
        st.markdown('<h3 class="section-header">Style Adjustments</h3>', unsafe_allow_html=True)
        
        tone_adjustment = st.slider(
            "Tone Adjustment",
            min_value=1,
            max_value=5,
            value=3,
            help="1: More formal, 5: More casual"
        )
        
        creativity_level = st.slider(
            "Creativity Level",
            min_value=1,
            max_value=5,
            value=3,
            help="1: Conservative, 5: Highly creative"
        )
        
        emotion_level = st.slider(
            "Emotional Appeal",
            min_value=1,
            max_value=5,
            value=3,
            help="1: Rational, 5: Emotional"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Ad Settings Section
        st.markdown('<h3 class="section-header">Ad Settings</h3>', unsafe_allow_html=True)
        ad_format = st.selectbox(
            "Advertisement Format",
            ["Social Media Post", "Banner Ad", "Email Marketing", "Print Ad"],
            help="Select the format for your advertisement"
        )
        num_variations = st.slider("Number of Variations", 1, 5, 2)
        
        # Generate button
        generate_button = st.button("Generate Advertisements")
    
    # Right column - Results
    with col2:
        st.markdown('<div class="results-section">', unsafe_allow_html=True)
        st.markdown('<h2 class="sub-header results-header">Results</h2>', unsafe_allow_html=True)
        
        # Create a container for results
        results_container = st.empty()
        
        # Generate button logic
        if generate_button:
            # Validate inputs
            is_valid, error_message = validate_inputs(brand_name, brand_colors, brand_fonts, 
                                                    reference_text or "", reference_type)
            
            if not is_valid:
                st.markdown(f'<p class="error-text">{error_message}</p>', unsafe_allow_html=True)
                return
            
            try:
                with st.spinner("Analyzing reference content..."):
                    # Analyze reference content
                    reference_analysis = {}
                    
                    if reference_text:
                        try:
                            text_analysis = ad_analyzer.analyze_text(reference_text)
                            reference_analysis["text_analysis"] = text_analysis
                        except Exception as e:
                            error_handled, error_msg = handle_gemini_error(str(e))
                            if error_handled:
                                st.markdown(error_msg, unsafe_allow_html=True)
                                return
                            else:
                                raise e
                    
                    if reference_image:
                        try:
                            # Check if the file exists before trying to analyze it
                            if os.path.exists(reference_image):
                                image_analysis = ad_analyzer.analyze_image(reference_image)
                                reference_analysis["image_analysis"] = image_analysis
                            else:
                                st.error(f"Reference image file not found at: {reference_image}")
                                return
                        except Exception as e:
                            error_handled, error_msg = handle_gemini_error(str(e))
                            if error_handled:
                                st.markdown(error_msg, unsafe_allow_html=True)
                                return
                            else:
                                raise e
                    
                    # Display analysis in an expander
                    with results_container.expander("Reference Analysis", expanded=True):
                        st.json(reference_analysis)
                
                with st.spinner("Generating new advertisements..."):
                    # Prepare brand guidelines
                    brand_guidelines = {
                        "name": brand_name,
                        "voice": brand_voice,
                        "target_audience": target_audience,
                        "colors": [c.strip() for c in brand_colors.split(",")],
                        "fonts": [f.strip() for f in brand_fonts.split(",")],
                        "style": "Professional"
                    }
                    
                    # Prepare style adjustments
                    style_adjustments = {
                        "tone": {
                            "level": tone_adjustment,
                            "description": "formal" if tone_adjustment < 3 else "casual"
                        },
                        "creativity": {
                            "level": creativity_level,
                            "description": "conservative" if creativity_level < 3 else "creative"
                        },
                        "emotion": {
                            "level": emotion_level,
                            "description": "rational" if emotion_level < 3 else "emotional"
                        }
                    }
                    
                    # Generate ads with error handling
                    try:
                        generator = AdGenerator()
                        ads = generator.generate_ads(
                            reference_analysis,
                            brand_guidelines,
                            ad_format,
                            num_variations,
                            style_adjustments
                        )
                    except Exception as e:
                        error_handled, error_msg = handle_gemini_error(str(e))
                        if error_handled:
                            st.markdown(error_msg, unsafe_allow_html=True)
                            return
                        else:
                            raise e
                    
                    if not ads:
                        st.markdown('<p class="error-text">Failed to generate advertisements. Please try again.</p>', unsafe_allow_html=True)
                        return
                    
                    # Display results
                    st.markdown('<div class="output-section">', unsafe_allow_html=True)
                    st.markdown('<h3 class="section-header">Generated Advertisements</h3>', unsafe_allow_html=True)
                    
                    for i, ad in enumerate(ads, 1):
                        st.markdown(f'<div class="ad-container">', unsafe_allow_html=True)
                        st.markdown(f'<h3 style="color: #3949ab;">Advertisement {i}</h3>', unsafe_allow_html=True)
                        
                        # Format information
                        st.markdown('<h4 class="section-header">Format Details</h4>', unsafe_allow_html=True)
                        st.json(ad["specs"])
                        
                        # Text content
                        st.markdown('<h4 class="section-header">Text Content</h4>', unsafe_allow_html=True)
                        if isinstance(ad["text"], dict):
                            for component, content in ad["text"].items():
                                st.markdown(f"**{component.replace('_', ' ').title()}:**")
                                st.markdown(content)
                        else:
                            st.markdown(ad["text"])
                        
                        # Image content
                        if ad["image"]:
                            st.markdown('<h4 class="section-header">Image</h4>', unsafe_allow_html=True)
                            
                            # Check if we should use the uploaded image directly
                            if 'use_uploaded_image' in locals() and use_uploaded_image and reference_image:
                                # Check if the file exists before trying to use it
                                if os.path.exists(reference_image):
                                    # Use the uploaded image directly
                                    img = Image.open(reference_image)
                                    
                                    # Calculate new dimensions while maintaining aspect ratio
                                    max_width = 300  # Increased from 200 to 300 for better quality
                                    width_percent = (max_width / float(img.size[0]))
                                    new_height = int((float(img.size[1]) * float(width_percent)))
                                    
                                    # Resize the image with high-quality settings
                                    resized_img = img.resize((max_width, new_height), Image.LANCZOS)
                                    
                                    # Display the resized image with better quality
                                    st.image(resized_img, caption=f"Your Uploaded Image - {img.size[0]}x{img.size[1]}", width=300)
                                    
                                    # Add a download button for the original image
                                    with open(reference_image, "rb") as file:
                                        btn = st.download_button(
                                            label="Download Image",
                                            data=file,
                                            file_name=f"ad_{ad_format.lower().replace(' ', '_')}.png",
                                            mime="image/png",
                                            key=f"download_uploaded_{i}"  # Add unique key
                                        )
                                else:
                                    st.error(f"Reference image file not found at: {reference_image}")
                            else:
                                # Use the generated image
                                if os.path.exists(ad["image"]):
                                    # Load the image with PIL
                                    img = Image.open(ad["image"])
                                    
                                    # Calculate new dimensions while maintaining aspect ratio
                                    max_width = 300  # Increased from 200 to 300 for better quality
                                    width_percent = (max_width / float(img.size[0]))
                                    new_height = int((float(img.size[1]) * float(width_percent)))
                                    
                                    # Resize the image with high-quality settings
                                    resized_img = img.resize((max_width, new_height), Image.LANCZOS)
                                    
                                    # Display the resized image with better quality
                                    st.image(resized_img, caption=f"{ad_format} - {img.size[0]}x{img.size[1]}", width=300)
                                    
                                    # Add a download button for the original image
                                    with open(ad["image"], "rb") as file:
                                        btn = st.download_button(
                                            label="Download Generated Image",
                                            data=file,
                                            file_name=f"ad_{ad_format.lower().replace(' ', '_')}.png",
                                            mime="image/png",
                                            key=f"download_generated_{i}"  # Add unique key
                                        )
                                else:
                                    st.warning("Image file not found. Please try generating again.")
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Success message
                    st.markdown('<p class="success-text" style="text-align: center;">Advertisements generated successfully!</p>', unsafe_allow_html=True)
                    
            except Exception as e:
                # Check if it's a Gemini API error
                error_handled, error_msg = handle_gemini_error(str(e))
                if error_handled:
                    st.markdown(error_msg, unsafe_allow_html=True)
                else:
                    st.markdown(f'<p class="error-text">An error occurred: {str(e)}</p>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main() 