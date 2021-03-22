import pdfplumber
import hashlib
from os import walk
import string
import os
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup


def epub2thtml(epub_path):
    book = epub.read_epub(epub_path)
    chapters = []
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            chapters.append(item.get_content())
    return chapters

blacklist = [
	'[document]',
	'noscript',
	'header',
	'html',
	'meta',
	'head', 
	'input',
	'script',
	# there may be more elements you don't want, such as "style", etc.
]
def chap2text(chap):
    output = ''
    soup = BeautifulSoup(chap, 'html.parser')
    text = soup.find_all(text=True)
    for t in text:
        if t.parent.name not in blacklist:
            output += '{} '.format(t)
    return output

def thtml2ttext(thtml):
  Output = "[]"
  for html in thtml:
    text = chap2text(html)
    Output += (text)
    if len(Output) > 200:
      break
  return Output

def epub2text(epub_path):
  chapters = epub2thtml(epub_path)
  ttext = thtml2ttext(chapters)
  return ttext

# _, _, filenames = next(walk("C:/Users/tesse/Desktop/Files/Dropbox/BIB"))

def run_fast_scandir(dir, ext):    # dir: str, ext: list
    subfolders, files = [], []

    for f in os.scandir(dir):
        if f.is_dir():
            subfolders.append(f.path)
        if f.is_file():
            if os.path.splitext(f.name)[1].lower() in ext:
                files.append(f.path)


    for dir in list(subfolders):
        sf, f = run_fast_scandir(dir, ext)
        subfolders.extend(sf)
        files.extend(f)
    return subfolders, files

digs = [i for i in string.digits] + [i for i in string.ascii_letters]

# print(digs)
# exit()

def get_hash(x, digs):
    if x == 0:
        return digs[0]

    digits = []

    while x:
        digits.append(digs[int(x % len(digs))])
        x = int(x / len(digs))

    digits.reverse()
    return ''.join(digits)

# , ".pdf", ".djvu"
_, filenames = run_fast_scandir("C:/Users/tesse/Desktop/Files/Dropbox/BIB", [".epub"]) 

# filenames = ["C:/Users/tesse/Desktop/Files/Dropbox/BIB/0 New BOOKS/2007 Trig or treat an encyclopedia of trigonometric identity proofs (TIPs), intellectually challenging games - Yeo.pdf"]

file = open("filenames.csv","w", encoding="utf-8")
file.write('\ufeff')
file.write("\n".join([f'"{i}"' for i in filenames]))
file.close() 

# exit()


# csv = "key,path,notext\n"
file = open("result.csv", "w", encoding="utf-8")
file.write('\ufeff')
file.write("key,path,notext\n")
file.close() 

for fn in filenames:
  if fn.lower().endswith(".pdf"):
    text = "".encode('utf-8')
    pdf = pdfplumber.open(fn)
    n = len(pdf.pages)
    ctr = 0
    best_text = "".encode('utf-8')
    notext = "True"
    while ctr < n:
      text = pdf.pages[ctr].extract_text()
      if text != None:
        if len(text) > 200:
          best_text = text.encode('utf-8')
          notext = ""
          break
        elif len(text) > len(best_text):
          best_text = text.encode('utf-8')
          notext = ""
      ctr += 1
    # print(text)
    h = hashlib.md5(best_text)
    bt = int(h.hexdigest(), 16)
    hsh = get_hash(bt, digs)
    csvline = f'{hsh},"{fn}",{notext}'


  elif fn.lower().endswith(".epub"):

    text = epub2text(fn)
    h = hashlib.md5(text.encode('utf-8'))
    bt = int(h.hexdigest(), 16)
    hsh = get_hash(bt, digs)
    csvline = f'{hsh},"{fn}"'

  elif fn.lower().endswith(".djvu"):
    print("djvu")

  file = open("result.csv", "a", encoding="utf-8")
  file.write(csvline + "\n") 
  file.close() 
  print(csvline)

