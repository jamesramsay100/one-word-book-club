import pdfplumber
import re
from tqdm import tqdm

class Book():
    def __init__(self, title, author, pdf_file):
        self.title = title
        self.author = author
        self.pdf_file = pdf_file
        self.raw_text = self.load_text()
        self.text = self.clean_text()

    def load_text(self):
        print("Opening PDF file...")
        with pdfplumber.open(self.pdf_file) as pdf:

            pdf_text = ""
            
            print("Converting pdf to text...")
            for p in tqdm(pdf.pages):
                page_text = p.extract_text()
                if page_text:
                    pdf_text += page_text

            return pdf_text

    def clean_text(self) -> str:
        """
        Clearn up text
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
        return len(self.text.split())

    