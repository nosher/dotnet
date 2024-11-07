#!/bin/env python

import os
import re

index_map = {}

IGNORE = []
with open("/home/httpd/nosher.net/docs/archives/computers/ignore.dat") as ignore:
    IGNORE = ignore.read().splitlines()

SPECIALS = []
with open("/home/httpd/nosher.net/docs/archives/computers/specials.dat") as specials:
    SPECIALS = specials.read().splitlines()

files = os.listdir('/home/httpd/nosher.net/docs/archives/computers/')
for f in files:
        print (f)
        previous = []
        if f[-4:] == ".txt":
            with open(os.path.join("/home/httpd/nosher.net/docs/archives/computers", f)) as fh: 
                lines = fh.readlines()
                del lines[0] # remove title line
                rawtext = " ".join(lines)
                text = " ".join(lines) \
                        .replace("\n", "") \
                        .replace("\"", "") \
                        .replace("(", " ( ") \
                        .replace(")", " ) ") \
                        .replace("~", "") \
                        .replace(",", " , ") \
                        .replace(":", " : ") \
                        .replace("CP/M", "CP|M") \
                        .replace("/", " / ") \
                        .replace("?", " . ") \
                        .replace("!", " ! ") \
                        .replace("'s", " . ") \
                        .replace("s'", "s . ") \
                        .replace(";", " ; ")
    
                # remove some tags 
                text = re.sub("<h[1-3]>.*?</h[1-3]>", " ", text)
                text = re.sub("<.*?>", " ", text)
                # remove source and picture tags, etc
                text = re.sub("\[\[.*?\]\]", " ", text)
                text = re.sub("\[.*?\]", " ", text)
                text = re.sub("-([a-z]*?) ", " . ", text)
                # temporarily swap out middle initials, e.g. George C. Coakley
                # so that the full stop isn't treated as a sentence separator.
                text = re.sub(" ([A-Z])\. ", r" \1XXX ", text)

                text = text.replace(".", " . ")
                words = text.split(" ")
                i = 0
                phrase = ""
                for word in words:
                    if (re.match("^[A-Z]", word) and not word in IGNORE) \
                        or (re.match("^[0-9]", word) and phrase != "") \
                        or (re.match("&", word) and phrase != "") \
                        :
                        phrase = phrase + word.replace("XXX", ".").replace("|", "/") + " "                        
                    else:
                        ref = f.replace(".txt", "")
                        phrase = phrase.strip()
                        if not phrase == "" and len(phrase) > 1:
                            do = True
                            for p in previous:
                                if p.find(phrase) > -1:
                                    do = False 
                            if do:
                                refs = []
                                if phrase in index_map:
                                    refs = index_map[phrase]
                                if not ref in refs:
                                    refs.append(ref)
                                    index_map[phrase] = refs
                                previous.append(phrase)
                        phrase = ""
                    i += 1 
                for sp in SPECIALS:
                    if rawtext.find(sp) > -1:
                            ref = f.replace(".txt", "")
                            refs = []
                            if sp in index_map:
                                refs = index_map[sp]
                            if not ref in refs:
                                refs.append(ref)
                                index_map[sp] = refs
               
keys = list(index_map.keys())
keys = sorted(keys, key=lambda s: s.lower())
with open("/home/httpd/nosher.net/docs/archives/computers/catalogue.dat", "w") as out:
    for k in keys:
        out.write("{0}\t{1}\n".format(k, ",".join(index_map[k])))
    out.close()


