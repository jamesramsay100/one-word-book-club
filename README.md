# one-word-book-club
Generates short summaries of books. Also attempts a 'one word summary' with variable success.

## Setup
Create virtual environment
`python -m venv venv`

Install dependencies
`venv/bin/pip install -r requirements.txt`

Create a API KEY for accessing OpenAI GPT-3 models. Export key to environment variable `OPENAI_API_KEY`

## Generating a summary
Example is included in `main.py`


```
bk = Book(
    title="Winnie the Pooh",
    author="AA Milne",
)
bk.load_pdf("pdf/Winnie-The-Pooh.pdf")
bk.generate_summary(
    engine="curie",
    save=True
)
```
