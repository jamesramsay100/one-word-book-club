"""Defines the Book class."""
import re
import os
from typing import OrderedDict
import pdfplumber
import openai
from tqdm import tqdm
from collections import OrderedDict

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
        self.summaries = {}

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
        engine:str="ada",
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
            frequency_penalty=0.8,
            presence_penalty=0.5,
            # stop=["\n"]
        )
        return response.choices[0].text

    def generate_summary(
        self,
        compression_ratio:float = 0.25,
        min_summary_length:int = 10,
        chunk_length:int = 1000,
        engine:str="ada",
    ):
        """
        Generate a summary for the book
        """
        print("Generating summary...")

        # get word count and et full text as first 'summary'
        word_count = self.get_word_count()
        print(f"Word count: {word_count}...")
        self.summaries[word_count] = self.text

        # check total cost with user
        summary_cost = self.calculate_summary_cost(
            word_count,
            compression_ratio,
            engine=engine
        )
        cntnue = self.ask_yesno(
            f"\n\nSummary cost using engine {engine}: $US {summary_cost}. Continue? [y/n]"
        )
        if cntnue==False:
            print("\n\nExiting...")
            exit(0)

        # generate shorter and shorter summaries
        while word_count > min_summary_length:

            # get text chunks
            input_text = self.summaries.get(
                min(self.summaries)
            )
            text_chunks = self.split_text_into_n_word_chunks(input_text, chunk_length)

            # append summary of each chunk
            _all_summaries = ""
            for chunk in tqdm(text_chunks):
                _chunk_summary = self.tldr_summary(
                    input_text=chunk,
                    engine=engine,
                    summary_prompt="\n\nIn summary:",
                    max_tokens=int(min(chunk_length, word_count)*compression_ratio),
                    temperature=0.1
                )
                _all_summaries += _chunk_summary

            word_count = len(_all_summaries.split())
            self.summaries[word_count] = _all_summaries
            print(f"Generated summary of length {word_count}...")

        print("Done...!")

        self.saveDictAsMarkdown(
            self.summaries,
            "delme.mD"
        )

    @staticmethod
    def get_min_dict_key(dictionary):
        """
        Get minimum key in dictionary
        """
        return min(dictionary, key=dictionary.get)

    @staticmethod
    def calculate_summary_cost(total_word_count, compression_ratio, engine):
        """Calculate OPENAI cost"""
        cost_per_1k_token = {
            "ada": 0.0008,
            "curie": 0.0060,
            "babbage": 0.0012,
            "davinci": 0.0600,
        }

        initial_token_count = total_word_count * (1+compression_ratio)
        total_token_count = initial_token_count / (1-compression_ratio)  # infinite geometric series
        total_cost = total_token_count * cost_per_1k_token[engine] / 1000

        return total_cost

    @staticmethod
    def ask_yesno(question):
        """
        Helper to get yes / no answer from user.
        """
        yes = ['yes', 'y']
        no = ['no', 'n'] # pylint: disable=invalid-name

        done = False
        print(question)
        while not done:
            choice = input().lower()
            if choice in yes:
                return True
            elif choice in no:
                return False
            else:
                print("Please respond by yes or no.")

    @staticmethod
    def saveDictAsMarkdown(dictionary, filename):
        """
        Save dictionary as markdown file
        """
        # sort dictionary by key ascending
        sorted_dict = OrderedDict(sorted(dictionary.items()))

        with open(filename, 'w') as file:
            for key, value in sorted_dict.items():
                file.write(f"#{key} word summary\n {value}\n\n")