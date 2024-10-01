#!/usr/bin/python3

# COPIED FROM /archives/computers/graph/

from xml.dom.minidom import parse, parseString
import math

with open("computers.gfz") as fh:

    companies = []
    for line in fh.readlines():
        if (line.find("COMPANY") > -1 or line.find("HUB") > -1) and line.find("label=") > -1:
            l = line.rstrip().replace("\\\"", "").replace("\\n", " ").split("\"")
            companies.append(l[1])
    companies.sort()

    tree = parse("computers.svg")
    xels = {}
    svg = tree.getElementsByTagName("g")
    transforms = svg[0].getAttribute("transform").replace(" rotate(0) ", "|").split("|")
    scale = tx = None
    for t in transforms:
        if t.find("scale") > -1:
            scale = float(t.replace("scale(", "").replace(")", "").split(" ")[0])
        elif t.find("translate") > -1:
            txs = t.replace("translate(", "").replace(")", "").split(" ")
            txs = list(map(lambda x: float(x), txs))

    for el in tree.getElementsByTagName("g"):
        eid = el.getAttribute("id")
        if eid.find("node") > -1:
            ch = el.getElementsByTagName("text")[0]
            com = ch.firstChild.nodeValue.replace("\n", " ").replace("\"", "")
            print (com, ": ", ch.getAttribute("x"), ", ", ch.getAttribute("y"), " scale:", scale)
            xels[com] = {"x": (float(ch.getAttribute("x")) + txs[0]) * scale, "y": (float(ch.getAttribute("y")) + txs[1]) * scale, "id": eid}
            print (com, xels[com])
       
    with open("index.html", "w") as out:
        out.write("""<p class="svgindex">GOTO: """)
        for i in range(0, len(companies)):
            c = companies[i]
            xy = xels[c]
            out.write("""<a onclick='gosvg("{}", {:.2f},{:.2f});'>{}</a>""".format(xy["id"], xy["x"], xy["y"], c))
            if i < len(companies) -1:
                out.write(", ")
            out.write("\n")
        out.write("</p>")
            
