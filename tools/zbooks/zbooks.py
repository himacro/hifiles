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


class MyCompleter(Completer):

    def get_completions(self, document, complete_event):

        self.document = document

        def cmd_completions(cmd):
            yield from (Completion(cmd, -len(document.text) + 1) for cmd in CMDS)


        def book_completions():
            def match_book(words, book):
                strings = ' '.join([book['title']] + book['tags']).lower()
                for word in words:
                    if word not in strings:
                        return False

                return True

            ordered_books = sorted(zip(books.keys(), books.values()), key=lambda v: v[1]['title'])
            for id_, book in ordered_books:
                if match_book(args, book): 
                    yield Completion('{} ({})({})'.format(book['title'], ' '.join(book['tags']), id_), -len(document.text))
            

        def library_completions(word):
            LIBS = ('v2r2', 'v2r1', 'v1r13')
            offset = -len(word) if word else 0
            candidates = (lib for lib in LIBS if lib.startswith(word))

            if not candidates:
                candidates = LIBS

            yield from (Completion(lib, offset) for lib in candidates)

        userinput = document.text.lower()
        ends_with_space = True if userinput[-1] == ' ' else False
        args = userinput.split()
        CMDS = ('update', 'exit')

        if userinput.startswith('!'):
            words = userinput[1:].split()
            if words:
                cmd, *args = words
            else:
                cmd, args = '', []
            
            if cmd not in CMDS:
                yield from cmd_completions(cmd)
            else:
                if not userinput.endswith(' ') and not args:
                    return

                if userinput.endswith(' '):
                    last_word = ''
                else:
                    last_word = args[-1]

                if cmd == 'update':
                    yield from library_completions(last_word)
        else:
            yield from book_completions()


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

    root = 'http://www-03.ibm.com/systems/z/os/zos/library/bkserv'
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
    
    for lib in libs:

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
   
        if text.startswith('!'):
            cmd, *parms = text[1:].split(maxsplit=1)
        
            if cmd == 'exit':
                sys.exit(0)

            elif cmd == 'update':
                update_index(parms)

            else:
                print('Uknown command!')
        else:
            bookid = text[-9:-1]
            if bookid in books:
                open_book(bookid)
            else:
                print('Unknown book')




if __name__ == '__main__':

    index = 'index.json'

    try:
        with open(index) as f:
            books = json.load(f)
    except FileNotFoundError:
        books = {}

    run()
