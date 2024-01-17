from typing import Optional, Dict, List, Any


class APIResponseProcessor:
    def __init__(self, api_response: dict = None):
        self.api_response = api_response
        self.validate_response()

    def validate_response(self):
        """Validates the structure and content of the incoming JSON."""
        if not isinstance(self.api_response, dict):
            raise ValueError("API response must be a dictionary.")

        # Check for required keys
        required_keys = ["query", "conversation_id"]

        for key in required_keys:
            if key not in self.api_response:
                raise ValueError(f"Missing key in API response: {key}")

    def extract_query(self) -> str:
        """Extracts the main query from the API response."""
        return self.api_response.get("query", "")

    def extract_conversation_id(self) -> Optional[str]:
        """Extract the current conversation id"""
        return self.api_response.get("conversation_id", None)

    def extract_filters(self) -> Optional[Dict[str, List[Any]]]:
        return self.api_response.get("filters", None)

    def extract_knowledge_bank_id(self) -> Optional[str]:
        """Extracts the knowledge bank id from the API response."""
        return self.api_response.get("knowledge_bank_id", None)


class APIConvTitleRequestProcesor:
    def __init__(self, api_response: dict = None):
        self.api_response = api_response
        self.validate_response()

    def validate_response(self):
        if not isinstance(self.api_response, dict):
            raise ValueError("API response must be a dictionary.")
        required_keys = ["query", "answer"]
        for key in required_keys:
            if key not in self.api_response:
                raise ValueError(f"Missing key in API response: {key}")

    def extract_query(self) -> str:
        """Extracts the main query from the API response."""
        return self.api_response.get("query", "")

    def extract_answer(self) -> str:
        return self.api_response.get("answer", "")
