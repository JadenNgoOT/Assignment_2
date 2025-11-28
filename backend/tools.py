# Only one tool for now may expand
import requests
from typing import Optional, Dict

class LegalTermLookup:
    # API tool to look up defenitions of complex legal terms
    @staticmethod
    def lookup(term: str) -> Optional[Dict]:
        try:
            # Clean the term
            term = term.strip().lower()
            
            # Try dictionary API
            url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{term}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    meanings = data[0].get('meanings', [])
                    if meanings:
                        # Get the first definition
                        definition = meanings[0].get('definitions', [{}])[0].get('definition', '')
                        part_of_speech = meanings[0].get('partOfSpeech', '')
                        
                        return {
                            'term': term,
                            'definition': definition,
                            'part_of_speech': part_of_speech,
                            'source': 'dictionary_api'
                        }
            
            # Fallback: common legal terms
            legal_terms = {
                'indemnification': 'A contractual obligation where one party agrees to compensate another for harm, loss, or damage.',
                'force majeure': 'Unforeseeable circumstances that prevent someone from fulfilling a contract.',
                'arbitration': 'Resolution of a dispute by an impartial third party instead of going to court.',
                'jurisdiction': 'The official power to make legal decisions and judgments.',
                'breach': 'Violation or infringement of a law, obligation, or agreement.',
                'whereas': 'A legal term used in contracts to introduce recitals or background statements.',
                'hereby': 'By this means; as a result of this document or statement.',
                'notwithstanding': 'In spite of; without being affected by.',
                'pursuant': 'In accordance with or following.',
                'covenant': 'A formal agreement or promise in a contract.'
            }
            
            if term in legal_terms:
                return {
                    'term': term,
                    'definition': legal_terms[term],
                    'part_of_speech': 'legal term',
                    'source': 'builtin'
                }
            
            return None
            
        except Exception as e:
            print(f"Error looking up term '{term}': {e}")
            return None
        
    # Format a definition result for display
    @staticmethod
    def format_definition(result: Dict) -> str:
        if not result:
            return ""
        
        return f"**{result['term'].title()}** ({result['part_of_speech']}): {result['definition']}"

legal_term_lookup = LegalTermLookup()