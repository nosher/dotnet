#!/bin/env python

import os
import re


SPECIALS = ["1541", "1570", "1571", "400", "800", "6128", "8256", "6502", "8080", "8086", "80186", "80286", "80386", "4004", "8008", "6800", "6809", "68000", "68020", "modem", "mouse" "lap-held", "screen", "floppy", "sound", "graphics", "telesoftware", "teletext", "adapter", "radio", "transmitted", "program", "broadcast", "microcomputers", "microcomputer", "viewdata", "network", "acoustic-coupler", "radio-telephone", "satellite", "baud", "video", "videotext", "interface", "graphical", "portable", "high-technology", "luggable", "Aim-65", "OS/2", "PS/2", "Year of Unix", "Year of the Linux desktop", "4-Tel", "Fantasic Adventures of 4-T", "Vince the Valve", "virus"]

index_map = {}
IGNORE = []
with open("/home/httpd/nosher.net/docs/archives/computers/ignore.dat") as ignore:
    IGNORE = ignore.read().splitlines()

files = os.listdir('/home/httpd/nosher.net/docs/archives/computers/')
for f in files:
        print (f)
        previous = []
        if f[-4:] == ".txt":
            with open(os.path.join("/home/httpd/nosher.net/docs/archives/computers", f)) as fh: 
                lines = fh.readlines()
                rawtext = " ".join(lines)
                text = " ".join(lines) \
                        .replace("\n", "") \
                        .replace("\"", "") \
                        .replace("(", " ( ") \
                        .replace(")", " ) ") \
                        .replace("~", "") \
                        .replace(".", " . ") \
                        .replace(",", " , ") \
                        .replace(":", " : ") \
                        .replace("?", " . ") \
                        .replace("!", " ! ") \
                        .replace("'s", " . ") \
                        .replace("s'", "s . ") \
                        .replace(";", " ; ")
    
                # removesome tags 
                text = re.sub("<h[1-3]>.*?</h[1-3]>", " ", text)
                text = re.sub("<.*?>", " ", text)
                # remove source and picture tags, etc
                text = re.sub("\[\[.*?\]\]", " ", text)
                text = re.sub("\[.*?\]", " ", text)
                text = re.sub("-([a-z]*?) ", " . ", text)
                words = text.split(" ")
                i = 0
                phrase = ""
                for word in words:
                    if (re.match("^[A-Z]", word) and not word in IGNORE) \
                        or (re.match("^[0-9]", word) and phrase != ""):
                        phrase = phrase + word + " "                        
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


