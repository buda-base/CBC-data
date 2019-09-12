import csv
import json
import rdflib
from rdflib import URIRef, Literal, BNode
from rdflib.namespace import RDF, SKOS, Namespace, NamespaceManager, XSD

BDR = Namespace("http://purl.bdrc.io/resource/")
BDO = Namespace("http://purl.bdrc.io/ontology/core/")
BDG = Namespace("http://purl.bdrc.io/graph/")
BDA = Namespace("http://purl.bdrc.io/admindata/")
ADM = Namespace("http://purl.bdrc.io/ontology/admin/")

NSM = NamespaceManager(rdflib.Graph())
NSM.bind("bdr", BDR)
NSM.bind("", BDO)
NSM.bind("bdg", BDG)
NSM.bind("bda", BDA)
NSM.bind("adm", ADM)
NSM.bind("skos", SKOS)
NSM.bind("rdf", RDF)

GRAPHNAME = "http://purl.bdrc.io/graph/CBC-data"

LOD_DS = rdflib.Dataset()
LOD_G = LOD_DS.graph(BDG[GRAPHNAME])
LOD_G.namespace_manager = NSM

T_TO_ABSTRACT = {}
T_TO_SKT = {}
T_TO_CN = {}
ALL_T = []

def normalize_taisho_id(id):
    id = id.strip()
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

with open('derived/t_to_abstract.json', 'w', encoding='utf-8') as f:
    T_TO_ABSTRACT = json.load(f)

with open('derived/t_to_skt.json', 'w', encoding='utf-8') as f:
    T_TO_SKT = json.load(f)

with open('input/index-chtitles.csv', newline='') as csvfile:
    tkreader = csv.reader(csvfile)
    for row in tkreader:
        T = normalize_taisho_id(row[0])
        ALL_T.append(T)
        T_TO_CN[T]=row[1]

T_TO_CAT = {}
CATS = []
with open('input/categories.csv', newline='') as csvfile:
    tkreader = csv.reader(csvfile)
    next(tkreader, None) # skip first line
    firsttocats = []
    for row in tkreader:
        firsttocats.append((int(row[1]),int(row[0])))
        CATS.append(row)
    for T in T_TO_CN:
        Tint = taisho_id_to_int(T)
        previouscat = None
        for firsttocat in firsttocats:
            if firsttocat[0] > Tint:
                T_TO_CAT[T] = previouscat
                break
            previouscat = firsttocat[1]
        T_TO_CAT[T] = previouscat

MAIN_TAISHO_RID = "W0TT0000"

ROOT_RIDS = [MAIN_TAISHO_RID]

#
# Generate some data
#

## main entry for the Taisho:
LOG_G.add((BDR[MAIN_TAISHO_RID], RDF.type, BDO.Work))
LOG_G.add((BDR[MAIN_TAISHO_RID], SKOS.prefLabel, Literal("Taisho Revised Tripitaka", lang="en")))
LOG_G.add((BDR[MAIN_TAISHO_RID], SKOS.prefLabel, Literal("大正新脩大藏經", lang="zh-Hant")))

pi = 1
for cat in CATS:
    res = BDR[cat[1]]
    LOG_G.add((BDR[MAIN_TAISHO_RID], BDO.workHasPart, res))
    LOG_G.add((res, BDO.workPartOf, BDR[MAIN_TAISHO_RID]))
    LOG_G.add((res, BDO.partIndex, Literal(pi, datatype=XSD.integer)))
    if row[2]:
        LOG_G.add((res, SKOS.prefLabel, Literal(row[2], lang="en")))
    if row[3]:
        LOG_G.add((res, SKOS.prefLabel, Literal(row[3], lang="sa-x-iast")))
    if row[4]:
        LOG_G.add((res, SKOS.prefLabel, Literal(row[4], lang="zh-Hant")))
    pi += 1

def hasParent(id):
    # returns the parent or None according to the Taisho id
    dashidx = id.find('-')
    if dashidx != -1:
        return id[:dashidx]
    return None

def tid_to_taishopart(tid):
    return "W0TTT%s" % tid

def tid_to_expr(tid):
    return "W0TET%s" % tid

parentsLastPart = {}
seenAbstracts = []
for T in ALL_T:
    parent = hasParent(id)
    if not parent:
        parent = T_TO_CAT[T]
    if parent not in parentsLastPart:
        parentsLastPart[parent] = 1
    else:
        parentsLastPart[parent] += 1
    res = BDR[tid_to_taishopart(T)]
    LOG_G.add((BDR[parent], BDO.workHasPart, res))
    LOG_G.add((res, BDO.workPartOf, BDR[MAIN_TAISHO_RID]))
    LOG_G.add((res, BDO.partIndex, Literal(parentsLastPart[parent], datatype=XSD.integer)))
    LOG_G.add((res, BDO.workCBCSiglaT, Literal(T)))
    expr = tid_to_expr(T)
    LOG_G.add((res, BDO.workExpressionOf, expr))
    LOG_G.add((expr, BDO.workHasExpression, res))
    LOG_G.add((expr, RDF.type, BDRO.AbstractWork))
    LOG_G.add((expr, RDF.type, BDRO.Work))
    abst = T_TO_ABSTRACT[T]
    LOG_G.add((expr, BDO.workExpressionOf, abst))
    LOG_G.add((abst, BDO.workHasExpression, expr))
    LOG_G.add((abst, RDF.type, BDRO.AbstractWork))
    LOG_G.add((abst, RDF.type, BDRO.Work))
    if T in T_TO_CN:
        LOG_G.add((res, SKOS.prefLabel, Literal(T_TO_CN[T], lang="zh-Hant")))
        LOG_G.add((expr, SKOS.prefLabel, Literal(T_TO_CN[T], lang="zh-Hant")))
        LOG_G.add((abst, SKOS.prefLabel, Literal(T_TO_CN[T], lang="zh-Hant")))
    if T in T_TO_SKT:
        LOG_G.add((abst, SKOS.prefLabel, Literal(T_TO_CN[T], lang="sa-x-iast")))

print(LOD_DS.serialize(format='ttl').decode("utf-8") )