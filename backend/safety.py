from backend.config import Config

class SafetyChecker:
    # Check if input exceeds maximum length
    @staticmethod
    def check_input_length(text: str) -> tuple[bool, str]:
        if len(text) > 500000:
            return False, f"Input too long. Maximum {500000} characters allowed."
        if len(text) < 50:
            return False, "Input too short. Please provide substantial text to analyze."
        return True, ""
    
    # Detect prompt injection attempts
    @staticmethod
    def detect_injection(text: str) -> tuple[bool, str]:

        text_lower = text.lower()
        for pattern in Config.INJECTION_PATTERNS:
            if pattern in text_lower:
                return True, f"Security violation detected. This request cannot be processed."
        return False, ""
    
    # Run all safety checks    
    @staticmethod
    def validate_input(text: str) -> tuple[bool, str]:
        valid, msg = SafetyChecker.check_input_length(text)
        if not valid:
            return False, msg
        
        is_injection, msg = SafetyChecker.detect_injection(text)
        if is_injection:
            return False, msg
        
        return True, ""

safety_checker = SafetyChecker()