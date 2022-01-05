import csv
from xml.etree.ElementTree import ElementTree
import xml.etree.ElementTree as ET
import re

namespaces = {'': 'http://www.tei-c.org/ns/1.0', 'tei': 'http://www.tei-c.org/ns/1.0', 'xml': 'http://www.w3.org/XML/1998/namespace'}

PERSONS = {}
NAMESHBGR = {}

filename='input/hobotei.xml'
doc = ElementTree()
doc.parse(filename)
TEI = doc.getroot()
listPerson = TEI.find('tei:text/tei:body/tei:div/tei:p/tei:listPerson', namespaces)
for person in listPerson.findall('tei:person', namespaces):
    res = {"texts": []}
    idstr = person.attrib.get("{http://www.w3.org/XML/1998/namespace}id")
    res["id"] = idstr
    names = []
    res["names"] = names
    for name in person.findall("tei:name", namespaces):
        for n in name.iter():
            lang = n.attrib.get("{http://www.w3.org/XML/1998/namespace}lang")
            if n.text is not None and lang in ["zh", "sa-Latn"]:
                value = n.text.strip()
                names.append(value)
                if value not in NAMESHBGR:
                    NAMESHBGR[value] = []
                NAMESHBGR[value].append(res)
    noteElt = person.find("tei:note", namespaces)
    if noteElt is not None:
        res["note"] = noteElt.text.strip()
    PERSONS[idstr] = res
listBibl = TEI.find('tei:text/tei:back/tei:listBibl', namespaces)
for bibl in listBibl.findall('tei:bibl', namespaces):
    idstr = bibl.attrib.get("{http://www.w3.org/XML/1998/namespace}id")
    for name in bibl.findall("tei:name", namespaces):
        pid = name.attrib.get("corresp")[1:]
        role = name.attrib.get("type")
        if pid not in PERSONS:
            print("in bibl %s, %s is not in listPerson" % (idst, pid))
            continue
        person = PERSONS[pid]
        if role not in person:
            person[role] = []
        person["texts"].append(idstr)

filename='input/Buddhist_Studies_Person_Authority.xml'
doc = ElementTree()
doc.parse(filename)
TEI = doc.getroot()

NAMESDILA = {}

listPerson = TEI.find('tei:text/tei:body/tei:listPerson', namespaces)
for person in listPerson.findall('tei:person', namespaces):
    res = { "names" : [] }
    res["id"] = person.attrib.get("{http://www.w3.org/XML/1998/namespace}id")
    for name in person.findall("tei:persName", namespaces):
        namestr = name.text.strip()
        res["names"].append(namestr)
        if namestr not in NAMESDILA:
            NAMESDILA[namestr] = []
        NAMESDILA[namestr].append(res)


TEXTPERSONSDILA = {}
with open('input/jl_editors.csv', newline='') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        if not row[1].startswith('T'):
            continue
        if row[1] not in TEXTPERSONSDILA:
            TEXTPERSONSDILA[row[1]] = []
        TEXTPERSONSDILA[row[1]].append(row[2])

# HBGR id, matches on name, matches on text, best guess, names in HBGR, created by (in HBGR), note(in HBGR)

with open('input/hbgr-dila.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
    totalpersons = 0
    totalmatched = 0
    for _, p in PERSONS.items():
        totalpersons += 1
        line = [p["id"], "", "", "", ", ".join(p["names"]), ", ".join(p["texts"]), p["note"]]
        dilanamematches = set()
        for n in p["names"]:
            if n in NAMESDILA:
                for dilap in NAMESDILA[n]:
                    dilanamematches.add(dilap["id"])
        line[1] = ",".join(dilanamematches)
        dilauniontextmatches = set()
        dilaintersectiontextmatches = set()
        first = True

        for t in p["texts"]:
            if t in TEXTPERSONSDILA:
                for dilap in TEXTPERSONSDILA[t]:
                    dilauniontextmatches.add(dilap)
                if first:
                    dilaintersectiontextmatches = set(TEXTPERSONSDILA[t])
                else:
                    dilaintersectiontextmatches &= set(TEXTPERSONSDILA[t])
                first = False
        if len(dilaintersectiontextmatches) == 1:
            line[2] = ",".join(dilaintersectiontextmatches)
        elif len(dilaintersectiontextmatches) > 1:
            line[2] = ",".join(dilaintersectiontextmatches) + "?"
        else:
            line[2] = ",".join(dilauniontextmatches) + "?"
        bestguess = dilaintersectiontextmatches & dilanamematches
        writefurtherlines = False
        if len(bestguess) == 1:
            line[3] = ",".join(bestguess)
        elif len(dilanamematches) == 0 and len(dilaintersectiontextmatches) == 1:
            line[3] = ",".join(dilaintersectiontextmatches)
        elif len(dilanamematches) == 1 and len(dilaintersectiontextmatches) == 0:
            line[3] = ",".join(dilanamematches)
        else:
            line[3] = "?"
            writefurtherlines = True
        writer.writerow(line)
        if writefurtherlines:
            allmatches = dilaintersectiontextmatches & dilanamematches
            if len(allmatches) == 0:
                allmatches = dilauniontextmatches & dilanamematches
            if len(allmatches) == 0:
                if len(dilaintersectiontextmatches) > 0:
                    allmatches = dilaintersectiontextmatches.union(dilanamematches)
                else:
                    allmatches = dilauniontextmatches.union(dilanamematches)
            for pid in allmatches:
                writer.writerow([p["id"], "", "", pid+"?", "", "", ""])
        else:
            totalmatched += 1
    print("%d/%d found" % (totalmatched, totalpersons))