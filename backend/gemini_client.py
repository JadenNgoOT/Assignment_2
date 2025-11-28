import google.generativeai as genai
from typing import List, Dict, Tuple
import re
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
    
    # Analyze a legal document using Gemini
    # Returns: (summary, terms_looked_up, usage_metadata)
    def analyze_document(self, text: str) -> Tuple[str, List[str], Dict]:
        self.terms_looked_up = []
        
        # Create the prompt
        prompt = f"""
            Analyze this legal document and provide a clear, structured summary.

            Document:
            {text}

            Provide:
            1. Document type (e.g., NDA, Employment Agreement, etc.)
            2. Key parties involved
            3. Important dates and terms
            4. Main obligations and rights
            5. Notable clauses or risks
            6. **List any specialized legal terms or jargon that appear in the document** (e.g., indemnification, force majeure, arbitration, etc.)

            Format your response EXACTLY like this:

            **Document Type:** [type]
            
            **Summary:**
            [Your detailed summary here]
            
            **Legal Terms Found:**
            - term1: definition1
            - term2: definition2
            - term3: definition3
        """

        # Configure generation settings
        generation_config = {
            'temperature': 0.7,
            'top_p': 0.95,
            'top_k': 40,
            'max_output_tokens': 2048,
        }
        
        # Safety settings - set to BLOCK_NONE for legal documents
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
        
        try:
            # Generate response
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            
            # Check if response was blocked - use fallback
            if not response.parts:
                return self._get_fallback_response(text)
            
            summary = response.text
            
            # Extract legal terms that Gemini identified
            ai_identified_terms = self._extract_terms_from_summary(summary)
            
            # Enhance with definitions for the terms Gemini found
            summary_with_definitions = self._enhance_with_definitions(summary, ai_identified_terms)
            
            # Get usage metadata
            usage_metadata = {
                'prompt_tokens': response.usage_metadata.prompt_token_count,
                'completion_tokens': response.usage_metadata.candidates_token_count,
                'total_tokens': response.usage_metadata.total_token_count,
            }
            
            return summary_with_definitions, self.terms_looked_up, usage_metadata
            
        except Exception:
            # Handle any API errors with fallback
            return self._get_fallback_response(text)
    
    # Return fallback response when API fails or blocks content
    def _get_fallback_response(self, text: str) -> Tuple[str, List[str], Dict]:
        summary = f"""
            **Document Analysis (Fallback)**

            This appears to be a legal document containing approximately {len(text.split())} words.

            Due to API content filtering, a detailed analysis could not be completed automatically. The document contains standard legal terminology and provisions.

            **Manual Review Recommended:** Please review the document for specific terms, obligations, and conditions.
        """
        usage_metadata = {'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0}
        return summary, [], usage_metadata
    
    # Extract legal terms that Gemini identified from the summary
    def _extract_terms_from_summary(self, summary: str) -> List[str]:
        terms = []
        
        # Check if Gemini included a legal terms section
        if "**Legal Terms Found:**" in summary:
            terms_section = summary.split("**Legal Terms Found:**")[1]
        elif "Legal Terms Found:" in summary:
            terms_section = summary.split("Legal Terms Found:")[1]
        else:
            return terms
        
        # Extract terms from bullet points
        term_patterns = re.findall(r'[-*•]\s*([a-zA-Z\s]+)', terms_section)
        
        # Clean up the terms
        for term in term_patterns:
            cleaned_term = term.strip().lower()
            if cleaned_term and not cleaned_term.startswith('**'):
                terms.append(cleaned_term)
        
        # Limit to 10 terms
        return terms[:10]

    # Look up definitions for the legal terms that Gemini identified
    def _enhance_with_definitions(self, summary: str, ai_identified_terms: List[str]) -> str:
        if not ai_identified_terms:
            return summary
        
        # Look up definitions for the terms (limit to 3 to avoid too many API calls)
        definitions_section = "\n**Legal Terms Explained:**\n"
        
        terms_defined = 0
        for term in ai_identified_terms:
            if terms_defined >= 3:
                break
                
            result = legal_term_lookup.lookup(term)
            if result:
                self.terms_looked_up.append(term)
                definitions_section += f"• {legal_term_lookup.format_definition(result)}\n\n"
                terms_defined += 1
        
        # Only add section if definitions found
        if terms_defined > 0:
            return summary + definitions_section
        
        return summary

gemini_client = GeminiClient()