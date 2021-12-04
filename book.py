"""Defines the Book class."""
import re
import os
import pdfplumber
import openai
from tqdm import tqdm

class Book():
    """
    Class stores text and provides methods to manipulate it and generate summaries
    """

    def __init__(self, title, author, pdf_file):
        self.title = title
        self.author = author
        self.pdf_file = pdf_file
        self.raw_text = self.load_text()
        self.text = self.clean_text()

    def load_text(self):
        """Load text from pdf file"""

        print("Opening PDF file...")
        with pdfplumber.open(self.pdf_file) as pdf:

            pdf_text = ""

            print("Converting pdf to text...")
            for _page in tqdm(pdf.pages):
                page_text = _page.extract_text()
                if page_text:
                    pdf_text += page_text

            return pdf_text

    def clean_text(self) -> str:
        """
        Clean up text
        """

        print("Cleaining text...")

        if self.raw_text is None:
            return ""

        else:
            # remove unicode
            clean_text = self.raw_text.encode('ascii', 'ignore').decode('ascii')

            # remove repeated whitespace
            clean_text = re.sub(' +', ' ', clean_text)

            # remove numbers from string
            clean_text = re.sub('[0-9]+', '', clean_text)

            # remove multiple returns from string
            clean_text = re.sub('\n+', '\n', clean_text)

            return clean_text

    def get_word_count(self):
        """
        Count words in string
        """
        return len(self.text.split())

    @staticmethod
    def split_text_into_n_word_chunks(text, n_words):
        """
        Split text into chunks of n words
        """
        words = text.split()
        chunks = []
        for i in range(0, len(words), n_words):
            chunks.append(' '.join(words[i:i+n_words]))
        return chunks

    @staticmethod
    def tldr_summary(
        input_text:str,
        engine:str="curie",
        summary_prompt:str="\n\ntl;dr:",
        max_tokens:int=64,
        temperature:float=0.1
    ):
        """
        Makes a summarisation text prediction
        """
        openai.api_key = os.getenv("OPENAI_API_KEY")
        response = openai.Completion.create(
            engine=engine,
            prompt=input_text+summary_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            # stop=["\n"]
        )
        return response.choices[0].text
    