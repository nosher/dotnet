#!/usr/bin/python3

import os
import re
import pymysql.cursors
import sys

sys.path.append("..")

from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, ID, DATETIME, IDLIST 
from constants import *
from datetime import *
 
def createIndex(root, host, user, passwd):   
 
    '''
    Schema definition: title(name of file), path(as ID), content(indexed
    but not stored),textdata (stored text content)
    '''
    connection_local = pymysql.connect(
        host = host,
        user = user,                    
        password = passwd,               
        db='website',                      
        charset='utf8mb4',                 
        cursorclass=pymysql.cursors.DictCursor
    )

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
                img = "{}/archives/computers/images/{}-s.webp".format("https://static.nosher.net", f.split("/")[-1].replace(".txt", ""))
                url = "/archives/computers/{}".format(f.split("/")[-1].replace(".txt", ""))
                writer.add_document(
                    path = url, 
                    content = text, 
                    image = img
                )
                fh.close()

    # process photo albums
    root = "/home/httpd/nosher.net/docs/"
    with connection_local.cursor() as cursor:  
                sql = "SELECT * FROM `images_photoalbum`"
                cursor.execute(sql)
                rows = cursor.fetchall()

    for r in rows:

        ipath = "/images/{}".format(r["path"])
        full = "{}/{}/{}".format(root, ipath, "details.txt")

        try:
            timestamp = datetime.strptime(ipath.split("/")[-1][0:10], "%Y-%m-%d")
        except ValueError:
            print ("Warning: failed to parse timestamp in ", full)
            timestamp = datetime.strptime("1989-10-01", "%Y-%m-%d")

        with open(full, "r", encoding="utf-8") as fh:
            print ("Processing: ", full, timestamp)
            try:
                first = 0 
                text = fh.readlines()
                if len(text) > 3: 
                    for i in range(0, len(text)):
                        try:
                            parts  = text[i].split("\t")
                            if len(parts) > 1:
                                # this is an album description match
                                if parts[0] == "title" or parts[0] == "intro":
                                    images = []
                                    if len(text) > 7:
                                        for j in range(3, 7):
                                            bits = text[j].split("\t")
                                            images.append(bits[0])
                                    img = "{}{}/".format(WEBROOT, ipath)
                                    writer.add_document(
                                        path = ipath, 
                                        imgs = ",".join(images), 
                                        content = parts[1], 
                                        image = img, 
                                        date = timestamp
                                    )
                                elif parts[0] == "locn":
                                    pass    
                                else:
                                    # this is a match to an individual photo
                                    if first == 0: first = i
                                    img = "{}{}/{}-s.webp".format(WEBROOT, ipath, parts[0])
                                    writer.add_document(
                                        path = "{}/{}".format(ipath, i - first), 
                                        content = parts[1], 
                                        image = img, 
                                        date = timestamp
                                    )
                        except ValueError:
                            print ("Exception procesing ", ipath)
            except UnicodeDecodeError:
                print ("Failed processing (Unicode error)", full)

    writer.commit()

if __name__ == "__main__":

    if not "DB_PWD" in os.environ:
        sys.exit("No db passwd set. Is DB_PWD empty?")                       
    if not "DB_USER" in os.environ:
        sys.exit("No db user set. Is DB_USER empty?") 
    if not "DB_HOST" in os.environ:
        sys.exit("No db host set. Is DB_HOST empty?") 
    root = "corpus"
    
    createIndex(
        root,
        os.environ['DB_HOST'], 
        os.environ['DB_USER'], 
        os.environ['DB_PWD']
    )