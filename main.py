"""Generate summary from PDF"""
from book import Book

if __name__ == '__main__':
    bk = Book(
        title="Winnie the Pooh",
        author="AA Milne",
    )
    bk.load_pdf("pdf/Winnie-The-Pooh.pdf")
    bk.generate_summary(
        engine="curie",
        save=True
    )
