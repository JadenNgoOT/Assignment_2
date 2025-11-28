import requests
from typing import Optional, Dict

class LegalTermLookup:
    # API tool to look up defenitions of complex legal terms
    @staticmethod
    def lookup(term: str) -> Optional[Dict]:
        # Clean the term
        term = term.strip().lower()

        # Try dictionary API
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{term}"
        response = requests.get(url, timeout=5)

        if response.status_code != 200:
            return None

        data = response.json()
        if not data:
            return None

        meanings = data[0].get('meanings', [])
        if not meanings:
            return None

        definition = meanings[0].get('definitions', [{}])[0].get('definition', '')
        part_of_speech = meanings[0].get('partOfSpeech', '')

        return {
            'term': term,
            'definition': definition,
            'part_of_speech': part_of_speech,
            'source': 'dictionary_api'
        }

    # Format a definition result for display
    @staticmethod
    def format_definition(result: Dict) -> str:
        if not result:
            return ""
        return f"**{result['term'].title()}** ({result['part_of_speech']}): {result['definition']}"

legal_term_lookup = LegalTermLookup()
