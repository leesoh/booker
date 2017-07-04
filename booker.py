import argparse
import pprint as pp

import requests
from bs4 import BeautifulSoup


class BookGetter(object):
    """Scrape books from BiblioCommons"""

    def __init__(self, library):
        """Build URL for scraping happiness."""
        self.library = library
        self.site_root = f'https://{self.library}.bibliocommons.com/collection/show/'

    def __get_book_divs(self, page_number):
        """Grab all book divs from the specified page."""
        print('[*] Now on page: ', page_number)
        params = {'page': page_number,
                  'display_quantity': self.display_quantity}
        response = requests.get(self.site_root, params=params)
        soup = BeautifulSoup(response.text, 'lxml')
        book_divs = soup.find('div', {'id': 'bibList'})
        return book_divs

    def __parse_divs(self, book_divs):
        """Parse author and title from book div."""
        books = []
        for book_div in book_divs.findAll('div', {'class': 'info'}):
            book = {}
            try:
                book['title'] = book_div.find('span', {'class': 'title'}).text
            except AttributeError:
                book['title'] = 'N/A'
            try:
                book['author'] = book_div.find('span', {'class': 'author'}).a.text
                # Remove the year, if present
                if len(book['author'].split(',')) >= 3:
                    book_author = book['author'].split(',')
                    book_author = book_author[:2]
                    #del book_author[-1]
                    book['author'] = ','.join(book_author)
            except AttributeError:
                book['author'] = 'N/A'
            books.append(book)
        return books

    def get_books(self, shelf, userid):
        """Grab books from provided URL."""
        books = []
        self.site_root += f'{userid}/library/{shelf}'
        # How many to grab at a time. 100 appears to be the max.
        self.display_quantity = 100
        # Use a simple request first so we can get number of items
        response = requests.get(self.site_root)
        soup = BeautifulSoup(response.text, 'lxml')
        # Grab total number of books in shelf
        total_books = int(soup.find('p', {'class': 'total'}).strong.text)
        # Total pages to scrape
        num_pages = -(-total_books // self.display_quantity)
        for i in range(1, num_pages + 1):
            book_divs = self.__get_book_divs(i)
            books += self.__parse_divs(book_divs)
        return books


if __name__ == '__main__':
    """Parse arguments from command-line invocation."""
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--library', help='Library abbreviation.',
                        required=True)
    parser.add_argument('-s', '--shelf', help='Shelf to scrape.',
                        default='for_later')
    parser.add_argument('-u', '--user', help='User to scrape.', required=True)
    args = parser.parse_args()
    bg = BookGetter(args.library)
    books = bg.get_books(args.shelf, args.user)
    books.sort(key=lambda x: x['author'])
    pp.pprint(books)
