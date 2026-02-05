#!/bin/env python

import os
import re
import sys

index_map = {}

IGNORE = []
with open("/home/httpd/django/nosher/scripts/ignore.dat") as ignore:
    IGNORE = ignore.read().splitlines()

SPECIALS = []
with open("/home/httpd/django/nosher/scripts/specials.dat") as specials:
    SPECIALS = specials.read().splitlines()

MAGS = ["POCW", "PRAC", "PCN", "POPCW", "PCW", "YC"]


def isIndexable(word, intermediate = False):
     return (word[0:1].isupper()  
            and not word in IGNORE \
            and not word in MAGS \
            and len(word) > 1 \
            and word.find("-based") < 0 \
            and word.find("-born") < 0 \
            and word.find("-made") < 0 \
            ) \
        or intermediate and (word.isupper() or word == "&" or (word.isnumeric() and len(word) > 1))

files = os.listdir('/home/httpd/nosher.net/docs/archives/computers/')
for f in files:
        previous = []
        #if f[0:22] == "comp_today_1981-09_042":
        #if f[0:24] == "pet_brochure_1977_11_003":
        #if f == "pcw_1983-07_010_icl.txt":
        if f[-4:] == ".txt" and not f == "intro.txt" and not f == "title.txt" and not f == "map.txt":
            with open(os.path.join("/home/httpd/nosher.net/docs/archives/computers", f)) as fh: 
                filename = f.replace(".txt", "")
                print(filename)
                lines = fh.readlines()
                text = " ".join(lines) 
                text = text.replace("\n", " . ")
                uniques = []

                # strip out [@Commodore]-style tags and replace with their text content only
                for k in ["@", "#", "!", "=", "picture: "]:
                    groups = re.findall(r"\[" + k + r"(.*?)]", text)
                    for match in groups:
                        parts = match.split("|")
                        lookup = parts[1] if len(parts) > 1 else parts[0]
                        text = text.replace("[{}{}]".format(k, match), lookup)

                # strip out other "wiki" tags
                text = re.sub(r"\[\[.*?\]\]", " ", text)
                text = re.sub(r"\[.*?\]", " ", text)
                text = re.sub(r"^-([a-z]*?) ", " . ", text)


                for special in SPECIALS:
                     if special in text:
                          uniques.append(special)

                text = text.replace("\\\"(.*?)\"", "") \
                        .replace("\"", " . ") \
                        .replace("(", " ( ") \
                        .replace(")", " ) ") \
                        .replace("~", "") \
                        .replace(",", " . ") \
                        .replace(":", " . ") \
                        .replace("CP/M", "CP|M") \
                        .replace("I/O", "I|O") \
                        .replace("/", " / ") \
                        .replace("?", " . ") \
                        .replace("!", " . ") \
                        .replace(" - ", " . ") \
                        .replace(";", " . ") \
                        .replace("’", "'") \
                        .replace("'s", " . ") \
                        .replace("n't", "nYYYt") \
                        .replace("O'", "OYYY") \
                        .replace("'ve", "YYYve") \
                        .replace("'re", "YYYre") \
                        .replace("’s", " . ") \
                        .replace("s'", "s . ") \
                        .replace("'", "") 

                # treat some hyphenated phrases as word breaks
                for hyph in [
                    "focused", "style", "days", "generated", "endorsed", 
                    "approved", "specific", "branded", "specific", "like",
                    "format", "standard", "derived",
                    ]:
                    text = text.replace("-{}".format(hyph), " . ") 

                # remove or replace HTML tags 
                text = re.sub(r"<h[1-4]>(.*?)</h[1-4]>", r"\1", text)
                text = re.sub("<.*?>", " ", text)

                # swap initial and period so they're not treated as separate words
                text = re.sub(r"([A-Z])\. ([A-Z])\. ", r"\1ZZZ \2ZZZ ", text) # e.g. H. L. Audio
                text = re.sub(r" ([A-Z])\. ", r" \1ZZZ ", text) # e.g. George C. Coakley
                text = re.sub(r" ([A-Z])\.([0-9][0-9]) ", r" \1ZZZ\2 ", text) # e.g. X.25

                text = text.replace("  ", " ").replace(".", " . ")
                words = text.split(" ")
                end = len(words)
                i = 0

                while i < end:
                    word = words[i]
                    if isIndexable(word):
                            phrase = word
                            i += 1
                            while isIndexable(words[i], intermediate=True):
                                phrase += " " + words[i]
                                i += 1
                            if not phrase in uniques:
                                notMeta = True
                                for u in uniques:
                                     if phrase in u:
                                          notMeta = False
                                if notMeta:
                                    uniques.append(phrase.replace("|", "/").replace("ZZZ", ".").replace("YYY", "'"))
                    else :
                        i += 1
                          
                for u in uniques:
                    if u in index_map:
                        lst = index_map[u]
                        if not filename in lst:
                            lst.append(filename)
                            index_map[u] = lst
                    else:
                        index_map[u] = [filename]


keys = list(index_map.keys())
keys = sorted(keys, key=lambda s: s.lower())

for az in list("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
        found = {}
        for k in keys:
            if k[0:1] == az:
                found[k] = index_map[k] 
        if found:
            with open("/home/httpd/nosher.net/docs/archives/computers/catalogue_{}.dat".format(az), "w") as out:
                for k in found:
                    out.write("{0}\t{1}\n".format(k, ",".join(found[k])))
            out.close()
