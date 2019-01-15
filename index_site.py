import os
import re
from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, ID, DATETIME, IDLIST
from archives.constants import *
from datetime import *
import sys
 
def createIndex(root):   
 
    '''
    Schema definition: title(name of file), path(as ID), content(indexed
    but not stored),textdata (stored text content)
    '''
    schema = Schema(path = ID(stored = True), imgs = IDLIST(stored = True), image = TEXT(stored = True), content = TEXT, date = DATETIME(sortable = True))
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
                    try:
                        timestamp = datetime.strptime(path.split("/")[-1][0:10], "%Y-%m-%d")
                    except ValueError:
                        timestamp = datetime.strptime("1989-10-01", "%Y-%m-%d")
                    with open(full, "r") as fh:
                        try:
                            first = 0 
                            text = fh.readlines()
                            if len(text) > 3: 
                                for i in range(0, len(text)):
                                    try:
                                        parts  = text[i].split("\t")
                                        if len(parts) > 1:
                                            # convert to URL path
                                            webpath = path.replace("/home/httpd/nosher.net/docs/", "")
                                            # this is an album description match
                                            if parts[0] == "title" or parts[0] == "intro":
                                                images = []
                                                if len(text) > 7:
                                                    for j in range(3, 7):
                                                        bits = text[j].split("\t")
                                                        images.append(bits[0])
                                                img = "{}/{}/{}-s.jpg".format(WEBROOT, webpath, text[3].split("\t")[0])
                                                writer.add_document(path = webpath, imgs = ",".join(images), content = parts[1], image = img, date = timestamp)
                                            elif parts[0] == "locn":
                                                pass    
                                            # this is a match to an individual photo
                                            else:
                                                if first == 0: first = i
                                                img = "{}/{}/{}-s.jpg".format(WEBROOT, webpath, parts[0])
                                                writer.add_document(path = "{}/{}".format(webpath, i - first), content = parts[1], image = img, date = timestamp)
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
