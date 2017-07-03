import argparse
import pprint as pp

import requests
from bs4 import BeautifulSoup


class BookGetter(object):
    """Scrape books from BiblioCommons"""

    def __init__(self, library, shelf, userid):
        """Build URL for scraping happiness."""
        self.library = library
        self.shelf = shelf
        self.userid = userid
        # TODO: Add support for more than 100 books.
        self.site_root = f'https://{self.library}.bibliocommons.com/collection/show/{self.userid}/library/{self.shelf}?page=1&view=small&display_quantity=100'

    def get_books(self):
        """Grab books from provided URL."""
        books = []
        response = requests.get(self.site_root)
        soup = BeautifulSoup(response.text, 'lxml')
        book_divs = soup.find('div', {'id': 'bibList'})
        for book_div in book_divs.findAll('div', {'class': 'info'}):
            book = {}
            try:
                book['title'] = book_div.find('span', {'class': 'title'}).text
            except AttributeError:
                book['title'] = 'N/A'
            try:
                book['author'] = book_div.find('span', {'class': 'author'}).a.text
            except AttributeError:
                book['author'] = 'N/A'
            books.append(book)
        return books


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--library', help='Library abbreviation.')
    parser.add_argument('-s', '--shelf', help='Shelf to scrape.',
                        default='for_later')
    parser.add_argument('-u', '--user', help='User to scrape.')
    args = parser.parse_args()
    bg = BookGetter(args.library, args.shelf, args.user)
    books = bg.get_books()
    pp.pprint(books)