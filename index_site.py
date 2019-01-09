import os
import re
from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, ID
from archives.constants import *
import sys
 
def createIndex(root):   
 
    '''
    Schema definition: title(name of file), path(as ID), content(indexed
    but not stored),textdata (stored text content)
    '''
    schema = Schema(path = ID(stored = True), image = TEXT(stored = True), content = TEXT)
    if not os.path.exists("index"):
        os.mkdir("index")
    ix = create_in("index", schema)
    writer = ix.writer()

    root = "/home/httpd/nosher.net/docs/archives/computers"
    files = [os.path.join(root, i) for i in os.listdir(root)]
    for f in files:
        continue
        if f[-4:] == ".txt":
            with open(f, "r") as fh:
                print (f)
                text = fh.readlines()
                if len(text) > 1:
                    title = _strip(text[0])
                    body = _strip("".join(text[1:]))
                else:
                    title = ""
                    body = _strip(text[0])
                img = "{}/archives/computers/images/{}-s.jpg".format(WEBROOT, f.split("/")[-1].replace(".txt", ""))
                writer.add_document(path = f, content = body, image = img)
                fh.close()

    root = "/home/httpd/nosher.net/docs/images/"
    for path, folder, files in os.walk(root):
        for f in files:
                if f == "details.txt":
                    full = os.path.join(path, f)
                    print (full)
                    with open(full, "r") as fh:
                        try:
                            text = fh.readlines()
                            if len(text) > 3: 
                                for i in range(0, len(text)):
                                    try:
                                        parts  = text[i].split("\t")
                                        if len(parts) > 1:
                                            webpath = path.replace("/home/httpd/nosher.net/docs/", "")
                                            if parts[0] == "title" or parts[0] == "intro":
                                                img = "{}/{}/{}-s.jpg".format(WEBROOT, webpath, text[3])
                                                writer.add_document(path = webpath, content = parts[1], image = img)
                                            elif parts[0] == "locn":
                                                pass
                                            else:
                                                img = "{}/{}/{}-s.jpg".format(WEBROOT, webpath, parts[0])
                                                writer.add_document(path = "{}/{}".format(webpath, i), content = parts[1], image = img)
                                    except ValueError:
                                        print (path, l)
                        except UnicodeDecodeError:
                            print (full + " failed")

            
    writer.commit()

def _strip(txt):
    txt = re.sub("\[.*?\]", "", txt)
    txt = re.sub("<.*?>", "", txt)
    return txt

if __name__ == "__main__":
    root = "corpus"
    createIndex(root)
