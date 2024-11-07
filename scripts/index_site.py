import os
import re
from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, ID, DATETIME, IDLIST 
from constants import *
from datetime import *
import sys
 
def createIndex(root):   
 
    '''
    Schema definition: title(name of file), path(as ID), content(indexed
    but not stored),textdata (stored text content)
    '''
    index_file = "/home/httpd/django/nosher/index"

    schema = Schema(path = ID(stored = True), \
                    imgs = IDLIST(stored = True), \
                    image = TEXT(stored = True), \
                    content = TEXT(stored = True), \
                    date = DATETIME(sortable = True) )
    
    if not os.path.exists(index_file):
        os.mkdir(index_file)
    ix = create_in(index_file, schema)
    writer = ix.writer()

    # process computer adverts pages
    root = "/home/httpd/nosher.net/docs/archives/computers"
    files = [os.path.join(root, i) for i in os.listdir(root)]
    for f in files:
        if f[-4:] == ".txt":
            with open(f, "r", encoding="utf-8") as fh:
                print (f)
                lines = [s.rstrip() for s in fh.readlines()]
                text = re.sub("<.*?>|\[.*?\]", "", " ".join(lines))
                img = "{}/archives/computers/images/{}-s.jpg".format("https://nosher.net", f.split("/")[-1].replace(".txt", ""))
                url = "archives/computers/{}".format(f.split("/")[-1].replace(".txt", ""))
                writer.add_document(path = url, content = text, image = img)
                fh.close()

    # process photo albums
    root = "/home/httpd/nosher.net/docs/images/"
    for path, folder, files in os.walk(root):
        for f in files:
                if f == "details.txt":
                    full = os.path.join(path, f)
                    try:
                        timestamp = datetime.strptime(path.split("/")[-1][0:10], "%Y-%m-%d")
                    except ValueError:
                        print ("Warning: failed to parse timestamp")
                        timestamp = datetime.strptime("1989-10-01", "%Y-%m-%d")
                    print (full, timestamp)
                    with open(full, "r", encoding="utf-8") as fh:
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
                                            else:
                                                # this is a match to an individual photo
                                                if first == 0: first = i
                                                img = "{}/{}/{}-s.jpg".format(WEBROOT, webpath, parts[0])
                                                writer.add_document(path = "{}/{}".format(webpath, i - first), content = parts[1], image = img, date = timestamp)
                                    except ValueError:
                                        print (path, l)
                        except UnicodeDecodeError:
                            print (full + " failed")
    writer.commit()

if __name__ == "__main__":
    root = "corpus"
    createIndex(root)
