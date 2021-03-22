import pdfplumber
import hashlib
from os import walk
import string
import os
from epub_conversion.utils import open_book, convert_epub_to_lines
import numpy as np
from pandas import read_csv

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

# ".epub", ".pdf", ".djvu"
_, filenames = run_fast_scandir("C:/Users/tesse/Desktop/Files/Dropbox/BIB", [".epub", ".pdf", ".djvu"])

paths = read_csv("best/result.csv").values[:, 1]



# filenames = ["C:/Users/tesse/Desktop/Files/Dropbox/BIB/Non-Fiction/Statistics/2004 Statistics and Probability for Engineering Applications With Microsoft Excel - W.J. DeCoursey.pdf"]

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
  if fn in paths:
    continue
  if fn.lower().endswith(".pdf"):
    text = "".encode('utf-8')
    pdf = pdfplumber.open(fn)
    n = len(pdf.pages)
    ctr = 0
    best_text = "".encode('utf-8')
    notext = "True"
    while ctr < n:
      try:
        text = pdf.pages[ctr].extract_text()
        if text != None:
          if len(text) > 200:
            best_text = text.encode('utf-8')
            notext = ""
            break
          elif len(text) > len(best_text):
            best_text = text.encode('utf-8')
            notext = ""
      except:
        print(f"error parsing page {ctr} of {fn}")
      ctr += 1
    # print(text)
    h = hashlib.md5(best_text)
    bt = int(h.hexdigest(), 16)
    hsh = get_hash(bt, digs)
    csvline = f'{hsh},"{fn}",{notext}'


  elif fn.lower().endswith(".epub"):
    notext = "True"
    try:
      book = open_book(fn)
    except:
      lines = [""]
    try:
      lines = convert_epub_to_lines(book)
      notext = ""
    except:
      lines = [""]

    h = hashlib.md5("\n".join(lines).encode('utf-8'))
    bt = int(h.hexdigest(), 16)
    hsh = get_hash(bt, digs)
    csvline = f'{hsh},"{fn}",{notext}'

  elif fn.lower().endswith(".djvu"):
    print("djvu")
    BLOCK_SIZE = 65536 # The size of each read from the file
    h = hashlib.md5() # Create the hash object, can use something other than `.sha256()` if you wish
    with open(fn, 'rb') as f: # Open the file to read it's bytes
      fb = f.read(BLOCK_SIZE) # Read from the file. Take in the amount declared above
      while len(fb) > 0: # While there is still data being read from the file
        h.update(fb) # Update the hash
        fb = f.read(BLOCK_SIZE) # Read the next block from the file
    bt = int(h.hexdigest(), 16)
    hsh = get_hash(bt, digs)
    csvline = f'{hsh},"{fn}"'

  file = open("result.csv", "a", encoding="utf-8")
  file.write(csvline + "\n") 
  file.close() 
  print(csvline)

