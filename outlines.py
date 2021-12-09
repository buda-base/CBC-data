import csv
import json
import rdflib
import sys
from rdflib import URIRef, Literal, BNode
from rdflib.namespace import RDF, SKOS, RDFS, OWL, Namespace, NamespaceManager, XSD

BF = Namespace("http://id.loc.gov/ontologies/bibframe/")
BDR = Namespace("http://purl.bdrc.io/resource/")
BDO = Namespace("http://purl.bdrc.io/ontology/core/")
TMP = Namespace("http://purl.bdrc.io/ontology/tmp/")
BDG = Namespace("http://purl.bdrc.io/graph/")
BDA = Namespace("http://purl.bdrc.io/admindata/")
ADM = Namespace("http://purl.bdrc.io/ontology/admin/")
MBBT = Namespace("http://mbingenheimer.net/tools/bibls/")
CBCT_URI = "https://dazangthings.nz/cbc/text/"
CBCT = Namespace(CBCT_URI)

NSM = NamespaceManager(rdflib.Graph())
NSM.bind("bdr", BDR)
NSM.bind("", BDO)
NSM.bind("bdg", BDG)
NSM.bind("bda", BDA)
NSM.bind("adm", ADM)
NSM.bind("skos", SKOS)
NSM.bind("rdf", RDF)
NSM.bind("cbct", CBCT)
NSM.bind("mbbt", MBBT)
NSM.bind("bf", BF)

def normalize_taisho_id(id):
    id = id.strip().replace(' ', '')
    if '(' in id:
        id = id.replace('(', '-').replace(')', '')
    dashidx = id.find('-')
    numpart = id
    suffix = ""
    if dashidx != -1:
        numpart = id[:dashidx]
        suffix = id[dashidx:]
    if numpart.startswith('T'):
        numpart = numpart[1:]
    if numpart[-1].isalpha():
        suffix = numpart[-1].upper()+suffix
        numpart = numpart[:-1]
    numpartint = int(numpart)
    return "T%04d%s" % (int(numpart),suffix)

def normalize_k_id(id):
    id = id.strip().replace(' ', '')
    if '(' in id:
        id = id.replace('(', '-').replace(')', '')
    dashidx = id.find('-')
    numpart = id
    suffix = ""
    prefix = "K"
    if dashidx != -1:
        numpart = id[:dashidx]
        suffix = id[dashidx:]
    if numpart.startswith('KS'):
        numpart = numpart[2:]
        prefix = "KS"
    if numpart.startswith('K'):
        numpart = numpart[1:]
    if numpart[-1].isalpha():
        suffix = numpart[-1].upper()+suffix
        numpart = numpart[:-1]
    numpartint = int(numpart)
    return "%s%04d%s" % (prefix, int(numpart),suffix)

# bdr:CBCSiglaK

reg = rdflib.Graph()
reg.namespace_manager = NSM
with open('input/W3CN27014.csv', newline='') as csvfile:
    tkreader = csv.reader(csvfile)
    next(tkreader)
    mainparti = 0
    rootw = BDR["W3CN27014"]
    rootmw = BDR["MW3CN27014"]
    for row in tkreader:
        mainparti += 1
        if row[0] == "" or row[3] == "":
            continue
        k = normalize_k_id(row[0])
        mw = BDR["MW3CN27014_"+k]
        reg.add((mw, RDF.type, BDO.Instance))
        reg.add((mw, BDO.inRootInstance, rootmw))
        reg.add((mw, BDO.partType, BDR.PartTypeText))
        reg.add((mw, BDO.partOf, rootmw))
        reg.add((mw, BDO.partIndex, Literal(mainparti, datatype=XSD.integer)))
        reg.add((mw, BDO.partIndex, Literal(mainparti, datatype=XSD.integer)))
        if row[6] != "":
            t = normalize_taisho_id(row[6])
            reg.add((mw, BDO.instanceOf, BDR["WA0TTE"+t]))
        if row[9] != "":
            reg.add((mw, SKOS.prefLabel, Literal(row[9], lang="zh-hant")))
            reg.add((mw, SKOS.hiddenLabel, Literal(row[1], lang="zh-hant")))
        elif row[1] != "":
            reg.add((mw, SKOS.prefLabel, Literal(row[1], lang="zh-hant")))
        if row[7] != "":
            reg.add((mw, SKOS.altLabel, Literal(row[7], lang="ko")))
        idr = BDR["IDMW3CN27014_"+k]
        reg.add((mw, BF.identifiedBy, idr))
        reg.add((idr, RDF.type, BDR.CBCSiglaK))
        reg.add((idr, RDF.value, Literal(k)))
        clr = BDR["CLMW3CN27014_"+k]
        reg.add((mw, BDO.contentLocation, clr))
        reg.add((clr, RDF.type, BDO.ContentLocation))
        reg.add((clr, BDO.contentLocationPage, Literal(row[3], datatype=XSD.integer)))
        reg.add((clr, BDO.contentLocationVolume, Literal(row[2], datatype=XSD.integer)))
        reg.add((clr, BDO.contentLocationEndPage, Literal(row[4], datatype=XSD.integer)))
        reg.add((clr, BDO.contentLocationEndVolume, Literal(row[5], datatype=XSD.integer)))
        reg.add((clr, BDO.contentLocationInstance, rootw))

print(reg.serialize(format='ttl').decode("utf-8") )