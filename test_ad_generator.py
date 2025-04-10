from src.ad_generator import AdGenerator

def main():
    # Sample data
    reference_analysis = {
        "style": "Modern and professional",
        "tone": "Confident and authoritative",
        "key_elements": ["Clean design", "Professional imagery", "Clear messaging"]
    }
    
    image_analysis = "Professional office setting with modern technology and clean design"
    
    brand_guidelines = {
        "name": "TechPro Solutions",
        "voice": "Professional and innovative",
        "target_audience": "Business professionals and tech-savvy decision makers",
        "colors": ["#2C3E50", "#3498DB", "#ECF0F1"],
        "fonts": ["Helvetica", "Arial"]
    }
    
    ad_format = "Social Media Post"
    num_variations = 2
    
    # Initialize the generator
    generator = AdGenerator()
    
    # Generate ads
    print("Generating ads...")
    ads = generator.generate_ads(
        reference_analysis,
        image_analysis,
        brand_guidelines,
        ad_format,
        num_variations
    )
    
    # Print results
    print("\nGenerated Ads:")
    for i, ad in enumerate(ads, 1):
        print(f"\nAd Variation {i}:")
        print("Text Content:")
        print(ad["text"])
        print("\nImage Status:")
        print(ad["image"])
        print("-" * 50)

if __name__ == "__main__":
    main() 