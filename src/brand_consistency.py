import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

class BrandConsistencyChecker:
    def check_consistency(self, generated_ad, brand_guidelines):
        """
        Check if the generated ad is consistent with brand guidelines.
        Returns a consistency score between 0 and 1.
        """
        prompt = f"""
        Analyze the consistency between this generated ad and the brand guidelines:
        
        Generated Ad:
        {generated_ad['text']}
        
        Brand Guidelines:
        - Brand Name: {brand_guidelines['name']}
        - Brand Voice: {brand_guidelines['voice']}
        - Target Audience: {brand_guidelines['target_audience']}
        - Brand Colors: {', '.join(brand_guidelines['colors'])}
        - Brand Fonts: {', '.join(brand_guidelines['fonts'])}
        
        Please evaluate the following aspects and provide a score between 0 and 1 for each:
        1. Brand Voice Consistency
        2. Target Audience Alignment
        3. Message Clarity
        4. Visual Style (if applicable)
        5. Overall Brand Alignment
        
        Return the scores in JSON format.
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert brand consistency analyst."},
                {"role": "user", "content": prompt}
            ]
        )
        
        # Parse the response to get scores
        try:
            scores = eval(response.choices[0].message['content'])
            # Calculate average score
            consistency_score = sum(scores.values()) / len(scores)
            return consistency_score
        except:
            # If parsing fails, return a default score
            return 0.5

    def get_improvement_suggestions(self, generated_ad, brand_guidelines):
        """
        Get suggestions for improving brand consistency.
        """
        prompt = f"""
        Provide specific suggestions to improve the brand consistency of this ad:
        
        Generated Ad:
        {generated_ad['text']}
        
        Brand Guidelines:
        - Brand Name: {brand_guidelines['name']}
        - Brand Voice: {brand_guidelines['voice']}
        - Target Audience: {brand_guidelines['target_audience']}
        - Brand Colors: {', '.join(brand_guidelines['colors'])}
        - Brand Fonts: {', '.join(brand_guidelines['fonts'])}
        
        Please provide:
        1. Specific changes to align with brand voice
        2. Suggestions for better target audience alignment
        3. Ways to strengthen brand message
        4. Visual improvements (if applicable)
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert brand consultant."},
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.choices[0].message['content'] 