# AI Ad Generator

An AI-powered advertisement generator that produces new, on-brand ads from reference ads. This project helps brands and advertisers generate fresh, cohesive ad creatives that align with their brand identity and style guidelines.

## Features

- Reference Ad Analysis: Extract key elements from provided ads
- Creative Generation: Generate new ads using AI models
- Brand Consistency: Ensure generated ads adhere to brand rules
- Flexible Output: Support for multiple ad formats
- User-friendly Interface: Simple CLI/GUI for ad generation

## Setup

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Create a `.env` file with your API keys:
```
OPENAI_API_KEY=your_openai_api_key
```

## Usage

1. Run the application:
```bash
streamlit run app.py
```

2. Upload reference ads and provide brand guidelines
3. Generate new ad creatives
4. Customize and iterate on the generated ads

## Project Structure

- `app.py`: Main application file
- `src/`: Source code directory
  - `ad_analyzer.py`: Reference ad analysis module
  - `ad_generator.py`: Ad generation module
  - `brand_consistency.py`: Brand consistency checker
  - `utils.py`: Utility functions
- `assets/`: Directory for storing assets
- `output/`: Directory for generated ads

## Requirements

- Python 3.8+
- OpenAI API key
- Internet connection for API calls

## License

MIT License 