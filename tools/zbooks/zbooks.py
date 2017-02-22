import os
import sys
import subprocess
import logging
import re
import json

from bs4 import BeautifulSoup
import requests

from prompt_toolkit import prompt
from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit.completion import Completer, Completion


CMD_PREFIX = '!'
CMDS = ('update', 'exit')
books = {}

class MyCompleter(Completer):

    def _parse(self, user_input):

        self.user_input = user_input.lower()

        self.in_cmd = False
        self.cmd = ''
        self.args = []

        if self.user_input.startswith(CMD_PREFIX):
            self.in_cmd = True
            tokens = self.user_input[1:].split()
            if tokens:
                self.cmd, *self.args = tokens

        if self.user_input:
            self.char_before_cursor = self.user_input[-1]

    def _word_completions(self, part, words):
        candidates = [word for word in words if word.startswith(part)]

        if not candidates:
            candidates = words

        yield from (Completion(word, -len(word) + 1) for word in candidates)


    def _cmd_completions(self, word):
        yield from self._word_completions(word, CMDS)


    def _lib_completions(self, word):
        LIBS = ('v2r2', 'v2r1', 'v1r13')
        yield from self._word_completions(word, LIBS)



    def _book_completions(self, text):
        def match_book(words, book):
            strings = ' '.join([book['title']] + book['tags']).lower()
            for word in words:
                if word not in strings:
                    return False

            return True

        words = text.split()
        ordered_books = sorted(zip(books.keys(), books.values()), key=lambda v: v[1]['title'])
        for id_, book in ordered_books:
            if match_book(words, book): 
                yield Completion('{} ({})({})'.format(book['title'], ' '.join(book['tags']), id_), -len(text))
        

    def get_completions(self, document, _):
        self._parse(document.text)

        if self.in_cmd:
            if self.cmd in CMDS:
                if self.cmd == 'update':
                    if self.char_before_cursor == ' ':
                        yield from self._lib_completions('')
                    elif self.args:
                        yield from self._lib_completions(self.args[-1])
                    else:
                        return
            else:
                yield from self._cmd_completions(self.cmd)

        else:
            yield from self._book_completions(self.user_input)


def download_book(bookid, bookpath):
    print("Downloading ...")
    url = books[bookid]['url']
    r = requests.get(url)
    with open(bookpath, 'wb') as f:
        f.write(r.content)
    

def open_book(bookid):
    bookpath = os.path.join('books', bookid + '.pdf')
    if not os.path.exists(bookpath):
        download_book(bookid, bookpath)
    print("Opening ...")
    subprocess.Popen(('xdg-open', bookpath))


def update_elements_and_features(zosver):

    root = r'http://www-03.ibm.com/systems/z/os/zos/library/bkserv'
    if zosver.startswith('v1r'):
        zver = zosver[2:]
    else:
        zver = zosver

    url = os.path.join(root, zver+'pdf')

    resp = requests.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'lxml')
    
    BOOK_BASE = r'http://publibz.boulder.ibm.com/epubs/pdf' 
    books = {}
    pdf_nodes = soup.find_all('a', href=re.compile(BOOK_BASE + r'.*\.pdf$'))
    for node in pdf_nodes:
        id_ = node['href'].split('/')[-1].split('.')[0]
        if zosver.startswith('v2'):
            title = node.text
        else:
            title_node = node.parent.previous_sibling.previous_sibling
            if title_node:
                title = title_node.text
            else:
                continue

        pdf_url = node['href']
        books[id_] = {'url': pdf_url, 'title': title, 'tags': [zosver, ]}

    return books


def update_redbooks():
    print("Not Implemented")
    return {}


def update_share():
    print("Not Implemented")
    return {}

def update_index(libs):
    from functools import partial
    
    updates = {
        'v1r13': partial(update_elements_and_features, 'v1r13'),
        'v2r1': partial(update_elements_and_features, 'v2r1'),
        'v2r2': partial(update_elements_and_features, 'v2r2'),
        'redbooks': update_redbooks,
        'share': update_share,
        }
    
    for lib in set(libs.split()):

        print('Updating... ' + lib)

        new = updates[lib]()
        books.update(new)

        with open(index, 'w') as f:
            json.dump(books, f, indent=True)
    


def run():
    print('Tip: `ctrl+u` to clear the input')
    while True:
        if not books:
            print('Index is empty, please `!update` it.')

        text = prompt('> ', completer=MyCompleter())
        if not text:
            continue
   
        if text.startswith(CMD_PREFIX):
            cmd, *parms = text[1:].split(maxsplit=1)
        
            if cmd == 'exit':
                sys.exit(0)

            elif cmd == 'update':
                update_index(parms[0])

            else:
                print('Uknown command!')
        else:
            bookid = text[-9:-1]
            if bookid in books:
                open_book(bookid)
            else:
                print('Unknown book')



def main():
    global books

    index = 'index.json'
    try:
        with open(index) as f:
            books = json.load(f)
    except FileNotFoundError:
        books = {}

    run()


if __name__ == '__main__':
    main()
