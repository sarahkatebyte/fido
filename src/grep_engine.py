"""
this is a grep engine for my beloved fido bot! 

This module handles pattern matching on email context to determine if the nature of the content is spammy
It utilizes regex to identify these specific emails
"""
import re
from typing import Dict, List, Optional

class GrepEngine:
    """
    Pattern mathcing engine for email content 
    uses regex patterns to filter emails based on rules
    """
    def __init__(self):
        """
        Initialize the grep engine.
        placeholder for now
        """
        pass

    def match_pattern(self, pattern: str, text: str, case_sensitive: bool = False) -> bool:
        """
        Check if a pattern matches the given text using regex

        Args:
            pattern: regular exp pattern to match
            text: Text to search in
            case_sensitive: should matching be case sensitive (default: false)

        Returns:
            True if pattern matches, False otherwise

        Example:
            match_pattern:("amazon", "noreply@amazon.com") -> True
            match_pattern:("^urgent", "Urgent: Please read") -> True
        """
        if not text:
            return False

        try:
            if case_sensitive:
                regex = re.compile(pattern)
            else:
                regex = re.compile(pattern, re.IGNORECASE)
            
            # Search for a pattern in the text 
            match = regex.search(text)
            # Return True if we found a match, False otherwise
            return match is not None
            
        except re.error as e:
            # If the regex pattern is invalid, print error and return False
            print(f"Invalid regex pattern '{pattern}': {e}")
            return False
