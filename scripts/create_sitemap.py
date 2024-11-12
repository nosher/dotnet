#!/usr/bin/python3

import pymysql.cursors
import sys
import os  

from xml.dom import minidom 
from datetime import datetime
from datetime import date
from pytz import timezone
from stat import *

class Sitemap():

    '''
    Generate a sitemap for nosher.net, as per the protocol defined
    at https://www.sitemaps.org/protocol.html, with Google extensions for images:
    https://developers.google.com/search/docs/crawling-indexing/sitemaps/image-sitemaps
    '''

    ROOT_URL = "https://nosher.net/"
    STATIC_ROOT_URL = "https://static.nosher.net/"
    FILE_ROOT = "/home/httpd/nosher.net/docs/"

    def __init__(self, dbhost, dbuser, dbpwd):
        '''
        Initialise the class, creating a MariadDB connection
        '''
        self.connection_local = pymysql.connect(host=dbhost,
                            user=dbuser,                    
                            password=dbpwd,               
                            db='website',                      
                            charset='utf8mb4',                 
                            cursorclass=pymysql.cursors.DictCursor)
        self.root = minidom.Document() 
        self._createUrlset()


    def createUrlNode(self, uri, last_mod = None, images = None):  
        '''
        Create a url node with loc, lastmod and optional 
        image child/children for each page
        '''  
        url = self.root.createElement('url') 
        loc = self.root.createElement("loc")
        loc.appendChild(self.root.createTextNode(uri))
        url.appendChild(loc)

        # add Last Modified element if required
        if last_mod:
            lastmod = self.root.createElement("lastmod")
            lastmod.appendChild(self.root.createTextNode(last_mod))
            url.appendChild(lastmod)

        # add image elements if required
        if images:
            for img in images:
                image = self.root.createElement("image:image")
                imageloc = self.root.createElement("image:loc")
                imageloc.appendChild(self.root.createTextNode(img))
                image.appendChild(imageloc)
                url.appendChild(image)  

        return url


    def process(self):
        '''
        Process the various sections of the website, building a set of url nodes
        '''
        # photo albums
        for page in self._get_image_pages():
            print ("Processing {}".format(page))
            # create a node and add it
            self.urlset.appendChild(self.createUrlNode(
                uri = self.ROOT_URL + "images/" + page, 
                last_mod = self._get_lastmod("images/" + page + "/details.txt"),
                images = self._get_images_for_page(page)
            )) 

        # Computer adverts
        for page in self._get_adverts():
            # create a node and add it
            self.urlset.appendChild(self.createUrlNode(
                uri = self.ROOT_URL + "archives/computers/" + page,
                last_mod = self._get_lastmod("archives/computers/" + page + ".txt"),
                images = [self.STATIC_ROOT_URL + "archives/computers/images/" + page + "-m.webp"]
            )) 

        # AJO, Saxon Horse, Brandon Flint
        self._get_content_files("ajo")

        # Saxon Horse
        self._get_content_files("saxonhorse")

        # Brandon Flint
        self._get_content_files("brandonflint")

        # RAF Halton archive
        self._get_content_files("raf69th")
               
        # RAF Halton archive
        self._get_content_files("recipes")

        # write out XML
        self._write()


    def _createUrlset(self):   
        '''
        Create the URL set node
        ''' 
        self.urlset = self.root.createElement('urlset')  
        self.urlset.setAttribute("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")
        self.urlset.setAttribute("xmlns:image", "http://www.google.com/schemas/sitemap-image/1.1")


    def _get_content_files(self, section):
        '''
        Create a list of XML elements for each page in the specified content section.

        Requires that the file files.dat exists in the content directory listing the
        available files.
        '''
        files = []
        with open(self.FILE_ROOT + "content/{}/files.dat".format(section)) as fh:
            for f in [s.rstrip() for s in fh.readlines()]:
                files.append(f)
        for page in files:
            self.urlset.appendChild(self.createUrlNode(
                uri = self.ROOT_URL + "content/{}/{}".format(section, page.replace("index.html", "")), \
                last_mod = self._get_lastmod("content/{}/{}".format(section, page))
            )) 


    def _get_lastmod(self, page):
        ''' 
        Return the file's last modified date as YYYY-MM-DD 
        '''
        f = self.FILE_ROOT + page
        if not os.path.isfile(f):
            f = f + "index.html"
        print ("Checking " + f)
        stats = os.stat(f)
        fmt_date = datetime.fromtimestamp(stats[ST_MTIME]).replace(tzinfo=timezone('UTC')).strftime("%Y-%m-%d")
        return fmt_date


    def _get_images_for_page(self, page):
        '''
        Get a list of the images in each photo album
        '''
        images = []
        base = self.ROOT_URL + "images/"
        with open(self.FILE_ROOT + "images/" + page + "/details.txt") as fh:
            lines = fh.readlines()
            for l in lines:
                l = l.strip()
                if l[1] != "#" and l[:5] != "intro" and l[:5] != "title" and l[:4] != "locn":
                    try:
                        (img, _) = l.split("\t")
                    except ValueError:
                        img = l
                    images.append(self.STATIC_ROOT_URL + "images/" + page + "/" + img + "-m.webp")
        return images


    def _get_image_pages(self):
            '''
            Get a list of all photo albums from the database
            '''
            rows = []
            paths = []
            with self.connection_local.cursor() as cursor:  
                    sql = "SELECT * FROM `images_photoalbum`"
                    cursor.execute(sql)
                    rows = cursor.fetchall()
            for r in rows:
                paths.append(r["path"])
            return paths


    def _get_adverts(self):
        '''
        Get a list of all computer adverts from the database
        '''
        rows = []
        paths = []
        with self.connection_local.cursor() as cursor:  
                sql = "SELECT * FROM `archives_archiveitems`"
                cursor.execute(sql)
                rows = cursor.fetchall()
        for r in rows:
            adid = r["adid"].split(",")[0]
            paths.append(adid)
        return paths


    def _write(self):
        '''
        Write the XML out to a file
        '''
        self.root.appendChild(self.urlset) 
        xml_str = self.root.toprettyxml(encoding="utf-8", indent ="  ")  
        with open(self.FILE_ROOT + "sitemap.xml", "wb") as f: 
            f.write(xml_str)  


if __name__ == "__main__":
    
    if not "DB_PWD" in os.environ:
        sys.exit("No db passwd set. Is DB_PWD empty?")                       
    if not "DB_USER" in os.environ:
        sys.exit("No db user set. Is DB_USER empty?") 
    if not "DB_HOST" in os.environ:
        sys.exit("No db host set. Is DB_HOST empty?") 

    sitemap = Sitemap( 
            os.environ['DB_HOST'], \
            os.environ['DB_USER'], \
            os.environ['DB_PWD'] \
        ).process()