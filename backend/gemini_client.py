import google.generativeai as genai
from typing import List, Dict, Tuple
import time
from .config import config
from .tools import legal_term_lookup

# Configure Gemini
genai.configure(api_key=config.GEMINI_API_KEY)

# Handles interaction with Gemini API including tool calling
class GeminiClient:
    
    def __init__(self):
        self.model = genai.GenerativeModel(
            config.GEMINI_MODEL, 
            system_instruction=config.SYSTEM_PROMPT
        )
        self.terms_looked_up = []
    
    #Analyze a legal document using Gemini
    #Returns: (summary, terms_looked_up, usage_metadata)
    def analyze_document(self, text: str) -> Tuple[str, List[str], Dict]:
        
        
        self.terms_looked_up = []
        
        # Create the prompt
        prompt = f"""
            Analyze this legal document and provide a clear, structured summary.

            Document:
            {text}

            Provide:
            1. Document type (e.g. NDA, Employment Agreement, etc.)
            2. Key parties involved
            3. Important dates and terms
            4. Main obligations and rights
            5. Notable clauses or risks

            When you encounter legal jargon (like "indemnification", "force majeure", "arbitration", etc.), 
            I will help you look up definitions. Just mention the terms you'd like defined.

            Summary:
            """

        try:
            # Start timing
            start_time = time.time()
            
            # Generate response
            response = self.model.generate_content(prompt)
            
            # Extract the summary
            summary = response.text
            
            # Check if response mentions legal terms that need lookup
            summary_with_definitions = self._enhance_with_definitions(summary, text)
            
            # Get usage metadata
            usage_metadata = {
                'prompt_tokens': getattr(response.usage_metadata, 'prompt_token_count', 0),
                'completion_tokens': getattr(response.usage_metadata, 'candidates_token_count', 0),
                'total_tokens': getattr(response.usage_metadata, 'total_token_count', 0),
            }
            
            return summary_with_definitions, self.terms_looked_up, usage_metadata
            
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")
        

    #Look for legal terms in the document and add definitions   
    def _enhance_with_definitions(self, summary: str, original_text: str) -> str:
        # Common legal terms to check for
        legal_terms = [
            'indemnification', 'indemnify', 'force majeure', 'arbitration',
            'jurisdiction', 'breach', 'whereas', 'hereby', 'notwithstanding',
            'pursuant', 'covenant', 'liability', 'confidential', 'termination',
            'non-disclosure', 'non-compete', 'severability', 'waiver'
        ]
        
        # Check which terms appear in the original document
        text_lower = original_text.lower()
        found_terms = []
        
        for term in legal_terms:
            if term in text_lower and term not in found_terms:
                found_terms.append(term)
        
        # Look up definitions for found terms (limit to 3 to avoid too many API calls)
        definitions_section = ""
        if found_terms:
            definitions_section = "\n\n---\n**Legal Terms Explained:**\n\n"
            
            for term in found_terms[:3]:  # Limit to 3 terms
                result = legal_term_lookup.lookup(term)
                if result:
                    self.terms_looked_up.append(term)
                    definitions_section += f"• {legal_term_lookup.format_definition(result)}\n\n"
        
        return summary + definitions_section

gemini_client = GeminiClient()