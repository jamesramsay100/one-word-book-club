"""Generate summary from PDF"""
from book import Book

if __name__ == '__main__':
    bk = Book(
        "Winnie the Pooh",
        "AA Milne",
        "pdf/Winnie-The-Pooh-1-78.pdf"
    )

    bk.generate_summary()

    print("Done loading book")
