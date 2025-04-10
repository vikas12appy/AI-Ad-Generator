# AI Ad Generator

An AI-powered advertisement generator that produces new, on-brand ads from reference ads. This project helps brands and advertisers generate fresh, cohesive ad creatives that align with their brand identity and style guidelines.

## Features

- Reference Ad Analysis: Extract key elements from provided ads
- Creative Generation: Generate new ads using AI models
- Brand Consistency: Ensure generated ads adhere to brand rules
- Flexible Output: Support for multiple ad formats
- User-friendly Interface: Simple Streamlit interface for ad generation

## Prerequisites

- Python 3.8 or higher
- OpenAI API key
- Internet connection for API calls

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-ad-generator.git
cd ai-ad-generator
```

2. Create and activate a virtual environment:
```bash
# On macOS/Linux
python -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
.\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Add your OpenAI API key to the `.env` file:
   ```
   OPENAI_API_KEY=your_openai_api_key
   ```

## Usage

1. Start the application:
```bash
streamlit run app.py
```

2. Access the web interface:
   - Open your browser and go to `http://localhost:8501`
   - The interface will guide you through the ad generation process

3. Generate Ads:
   - Upload reference ads in the supported formats (JPG, PNG)
   - Provide brand guidelines and preferences
   - Click "Generate" to create new ad variations
   - Download or modify the generated ads

## Project Structure

```
ai-ad-generator/
├── app.py              # Main Streamlit application
├── src/               # Source code directory
│   ├── ad_analyzer.py    # Reference ad analysis
│   ├── ad_generator.py   # Ad generation logic
│   ├── brand_consistency.py  # Brand rules checker
│   └── utils.py          # Utility functions
├── assets/            # Sample assets and resources
├── generated_images/  # Output directory for generated ads
├── output/           # Additional output files
├── requirements.txt  # Python dependencies
└── .env.example     # Environment variables template
```

## Configuration

The application can be configured through the `.env` file:
- `OPENAI_API_KEY`: Your OpenAI API key
- Additional configuration options can be added as needed

## Contributing

1. Fork the repository
2. Create a new branch: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Commit your changes: `git commit -m 'Add some feature'`
5. Push to the branch: `git push origin feature/your-feature-name`
6. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- OpenAI for providing the API
- Streamlit for the web interface framework
- Contributors and users of this project 