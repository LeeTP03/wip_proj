
import pathlib
import textwrap
import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

class GenAI:
    def __init__(self) -> None:
        self.model = self.initialize_AI()
    
    def initialize_AI(self):
        load_dotenv()
        api_key = os.getenv('GENAI_API_KEY')
        genai.configure(api_key=api_key)
        return genai.GenerativeModel('gemini-1.5-flash')
    
    def generate_text(self, prompt: str):
        response = self.model.generate_content(prompt)
        return response.text