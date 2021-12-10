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

K_TO_T = {}
K_TO_SKT = {}
T_TO_SKT = {}

with open('input/Taisho-K.csv', newline='') as csvfile:
    tkreader = csv.reader(csvfile)
    for row in tkreader:
        t = row[0]
        for i in range(1,len(row)):
            k = row[i]
            if k not in K_TO_T:
                K_TO_T[k] = set()
            K_TO_T[k].add(t)

with open('input/Sanskrit-K.csv', newline='') as csvfile:
    tkreader = csv.reader(csvfile)
    for row in tkreader:
        skt = row[0]
        for i in range(1,len(row)):
            k = row[i]
            if k not in K_TO_SKT:
                K_TO_SKT[k] = set()
            K_TO_SKT[k].add(skt)

for k, tlist in K_TO_T.items():
    if k in K_TO_SKT:
        skt = K_TO_SKT[k]
        for t in tlist:
            if t not in T_TO_SKT:
                T_TO_SKT[t] = set()
            T_TO_SKT[t].update(skt)

# transforming sets into lists...
for t,s in T_TO_SKT.items():
    T_TO_SKT[t] = list(s)

with open('derived/t_to_skt.json', 'w', encoding='utf-8') as f:
    json.dump(T_TO_SKT, f, ensure_ascii=False, indent=4)


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

T_TO_PART = {}

with open('input/W3CN27014.csv', newline='') as csvfile:
    tkreader = csv.reader(csvfile)
    next(tkreader)
    for row in tkreader:
        if row[0] == "":
            continue
        k = normalize_k_id(row[0])
        t = None
        if row[6] != "":
            t = normalize_taisho_id(row[6])
            if t not in T_TO_PART:
                T_TO_PART[t] = []
            T_TO_PART[t].append("MW3CN27014_"+k)

reg = rdflib.Graph()
reg.namespace_manager = NSM
with open('input/W3CN27014.csv', newline='') as csvfile:
    tkreader = csv.reader(csvfile)
    next(tkreader)
    mainparti = 0
    subparti = 0
    rootw = BDR["W3CN27014"]
    rootmw = BDR["MW3CN27014"]
    previousText = None
    for row in tkreader:
        if row[0] == "" or row[3] == "":
            continue
        k = normalize_k_id(row[0])
        mw = BDR["MW3CN27014_"+k]
        if '-' in k:
            subparti += 1
            reg.add((mw, BDO.partOf, previousText))
            reg.add((mw, BDO.partIndex, Literal(subparti, datatype=XSD.integer)))
            reg.add((previousText, BDO.hasPart, mw))
        else:
            previousText = mw
            mainparti += 1
            subparti = 0
            reg.add((mw, BDO.partOf, rootmw))
            reg.add((rootmw, BDO.hasPart, mw))
            reg.add((mw, BDO.partIndex, Literal(mainparti, datatype=XSD.integer)))
        reg.add((mw, RDF.type, BDO.Instance))
        reg.add((mw, BDO.inRootInstance, rootmw))
        reg.add((mw, BDO.partType, BDR.PartTypeText))
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
        if row[5] != row[2]:
            reg.add((clr, BDO.contentLocationEndVolume, Literal(row[5], datatype=XSD.integer)))
        reg.add((clr, BDO.contentLocationInstance, rootw))

reg.serialize("derived/MW3CN27014.ttl", format="turtle")


with open('derived/t_to_part.json', 'w', encoding='utf-8') as f:
    json.dump(T_TO_PART, f, ensure_ascii=False, indent=4)

def taisho_to_group_id(id):
    id = normalize_taisho_id(id)
    return "TG"+id[1:]

def normalize_D_id(id):
    id = id.lstrip(" 0D").strip().upper()
    return "D"+id

#print(normalize_taisho_id("123"))
#print(normalize_taisho_id("T123"))
#print(normalize_taisho_id("T123-45"))
#print(normalize_taisho_id("T123(45)"))
#print(normalize_taisho_id("T123a"))

T_TO_GROUP = {}
GROUP_TO_T = {}
D_TO_RKTS = {}
D_TO_T = {}
T_TO_D = {}
RKTS_SAMEABSTRACT = {}
RKTS_TO_ABSTRACT = {}
T_TO_ABSTRACT = {}
T_TO_PARR = {}
T_TO_CHTITLE = {}
GROUP_TO_ABSTRACT = {}

with open('input/rkts-sameabstract.csv', newline='') as csvfile:
    tkreader = csv.reader(csvfile)
    for row in tkreader:
        RKTS_SAMEABSTRACT[row[1]] = row[0]

with open('input/abstract-rkts.csv', newline='') as csvfile:
    tkreader = csv.reader(csvfile)
    for row in tkreader:
        if len(row) > 1 and row[1] and '?' not in row[1]:
            RKTS_TO_ABSTRACT[row[1]] = row[0]

def normalizerkts(id):
    id = id.strip()
    dashidx = id.find('-')
    numpart = id
    suffix = ""
    if dashidx != -1:
        numpart = id[:dashidx]
        suffix = id[dashidx:]
    if numpart[-1].isalpha():
        suffix = numpart[-1].upper()+suffix
        numpart = numpart[:-1]
    numpartint = int(numpart)
    return "%04d%s" % (int(numpart),suffix)

def rktsid_to_abstract(rkts):
    global RKTS_SAMEABSTRACT, RKTS_TO_ABSTRACT
    if rkts in RKTS_SAMEABSTRACT:
        rkts = RKTS_SAMEABSTRACT[rkts]
    if rkts in RKTS_TO_ABSTRACT:
        return RKTS_TO_ABSTRACT[rkts]
    return "WA0R%sI%s" % (rkts[0],normalizerkts(rkts[1:]))

def rktsid_to_all_tib_w(rkts):
    global RKTS_SAMEABSTRACT
    res = ["WA0R%s%s" % (rkts[0],normalizerkts(rkts[1:]))]
    if rkts in RKTS_SAMEABSTRACT:
        rkts = RKTS_SAMEABSTRACT[rkts]
        res.append("WA0R%s%s" % (rkts[0],normalizerkts(rkts[1:])))
    return res

def tid_to_expr(tid):
    return "WA0TTE%s" % tid

with open('input/Taisho-groups.csv', newline='') as csvfile:
    tkreader = csv.reader(csvfile)
    next(tkreader, None) # skip first line
    for row in tkreader:
        if (len(row) > 1 and len(row[1]) > 0) or not row[0]:
            continue
        idxlist = row[0].split(',')
        groupname = taisho_to_group_id(idxlist[0])
        tlist = []
        GROUP_TO_T[groupname] = tlist
        for id in idxlist:
            if '?' in id or not id:
                continue
            idnorm = normalize_taisho_id(id)
            if idnorm in T_TO_GROUP:
                print("error: %s is in multiple groups" % idnorm)
            T_TO_GROUP[idnorm] = groupname
            tlist.append(idnorm)

with open('input/Taisho-K-translations.csv', newline='') as csvfile:
    tkreader = csv.reader(csvfile)
    res = {}
    next(tkreader, None) # skip first line
    for row in tkreader:
        if '?' in row[1]:
            continue
        taisho = normalize_taisho_id(row[0])
        rkts = rktsid_to_all_tib_w(row[1])
        res[taisho] = rkts
    with open('derived/t_to_trans.json', 'w', encoding='utf-8') as f:
        json.dump(res, f, ensure_ascii=False, indent=4)

with open('input/Derge-Taisho.csv', newline='') as csvfile:
    tkreader = csv.reader(csvfile)
    next(tkreader, None) # skip first line
    for row in tkreader:
        if len(row) < 2 or (len(row) > 2 and len(row[2]) > 0) or not row[0] or not row[1]:
            continue
        D = normalize_D_id(row[0])
        tlist = row[1].split(',')
        tlistnorm = []
        group = None
        for t in tlist:
            if not t:
                continue
            tnorm = normalize_taisho_id(t)
            tlistnorm.append(tnorm)
            if tnorm in T_TO_D:
                print("warning: %s appears several times in T_TO_D" % tnorm)
            T_TO_D[tnorm] = D
            if tnorm in T_TO_GROUP:
                if group is not None and T_TO_GROUP[tnorm] != group:
                    print("warning: %s appears in incoherent groups (different groups for the same D)" % tnorm)
                group = T_TO_GROUP[tnorm]
            elif group is not None:
                print("warning: %s appears in incoherent groups (some T not in the main group)" % tnorm)
        if group and set(GROUP_TO_T[group]) != set(tlistnorm):
            print("warning: %s appears in incoherent groups (missing Ts)" % tnorm)
        D_TO_T[D] = tlistnorm

with open('input/derge-rkts.csv', newline='') as csvfile:
    tkreader = csv.reader(csvfile)
    for row in tkreader:
        D = normalize_D_id(row[1])
        rkts = row[0]
        D_TO_RKTS[D] = rkts

with open('input/derge-rkts.csv', newline='') as csvfile:
    tkreader = csv.reader(csvfile)
    for row in tkreader:
        D = normalize_D_id(row[1])
        abstract = rktsid_to_abstract(row[0])
        if D not in D_TO_T:
            continue
        for T in D_TO_T[D]:
            T_TO_ABSTRACT[T] = abstract
            newrids = rktsid_to_all_tib_w(row[0])
            if newrids:
                if T not in T_TO_PARR:
                    T_TO_PARR[T] = [tid_to_expr(T)]
                T_TO_PARR[T].extend(newrids)

# we consider that this contains all the identifiers
with open('input/index-chtitles.csv', newline='') as csvfile:
    tkreader = csv.reader(csvfile)
    for row in tkreader:
        T = normalize_taisho_id(row[0])
        T_TO_CHTITLE[T]=row[1]

def group_to_abstract(group):
    return "WA0TTGA%s" % group

def tid_to_abstract(tid):
    return "WA0TTA%s" % tid

def tid_to_taishopart(tid):
    return "MW0TTP%s" % tid

for T in T_TO_CHTITLE:
    if T in T_TO_ABSTRACT:
        continue
    elif T in T_TO_GROUP:
        T_TO_ABSTRACT[T] = group_to_abstract(T_TO_GROUP[T])
    #else:
    #    T_TO_ABSTRACT[T] = tid_to_abstract(T)

with open('derived/t_to_abstract.json', 'w', encoding='utf-8') as f:
    json.dump(T_TO_ABSTRACT, f, ensure_ascii=False, indent=4)

T_TO_EXPR = {}
T_TO_TAISHOPART = {}
for T in T_TO_CHTITLE:
    T_TO_EXPR[T] = tid_to_expr(T)
    T_TO_TAISHOPART[T] = tid_to_taishopart(T)

# fill T_TO_PARR with Chinese parallels:
for tlist in GROUP_TO_T.values():
    for t in tlist:
        if t not in T_TO_PARR:
            T_TO_PARR[t] = [tid_to_expr(T)]
        for t2 in tlist:
            if t2 == t:
                continue
            if t2 not in T_TO_EXPR:
                print("oops: ", t2)
                continue
            T_TO_PARR[t].append(T_TO_EXPR[t2])

with open('derived/t_to_expr.json', 'w', encoding='utf-8') as f:
    json.dump(T_TO_EXPR, f, ensure_ascii=False, indent=4)

with open('derived/t_to_taishopart.json', 'w', encoding='utf-8') as f:
    json.dump(T_TO_TAISHOPART, f, ensure_ascii=False, indent=4)

def taisho_id_to_int(id):
    id = normalize_taisho_id(id)
    id = id[1:]
    dashidx = id.find('-')
    if dashidx != -1:
        id = id[:dashidx]
    if id[-1].isalpha():
        id = id[:-1]
    return int(id)

T_TO_VOL = {}
with open('input/volume-firstindex.csv', newline='') as csvfile:
    tkreader = csv.reader(csvfile)
    lastid = 0
    firsttovols = []
    for row in tkreader:
        firsttovols.append((int(row[1]),int(row[0])))
    for T in T_TO_CHTITLE:
        Tint = taisho_id_to_int(T)
        previousvol = 1
        for firsttovol in firsttovols:
            if firsttovol[0] > Tint:
                T_TO_VOL[T] = previousvol
                break
            previousvol = firsttovol[1]
        T_TO_VOL[T] = previousvol

with open('derived/t_to_vol.json', 'w', encoding='utf-8') as f:
    json.dump(T_TO_VOL, f, ensure_ascii=False, indent=4)

MBBT_TO_ABSTRACT = {}
ABSTRACT_TO_MBBT = {}

with open('input/Mbbt-Taisho.csv', newline='') as csvfile:
    tkreader = csv.reader(csvfile)
    for row in tkreader:
        T = normalize_taisho_id(row[1])
        if T not in T_TO_EXPR:
            print("warning: "+T+" in mbbt but not in expr")
            #print(T_TO_ABSTRACT)
            continue
        MBBT_TO_ABSTRACT[row[0]]=T_TO_EXPR[T]
        ABSTRACT_TO_MBBT[T_TO_EXPR[T]]=row[0]

with open('derived/mbbt-to-abstract.json', 'w', encoding='utf-8') as f:
    json.dump(MBBT_TO_ABSTRACT, f, ensure_ascii=False, indent=4)

with open('derived/abstract-to-mbbt.json', 'w', encoding='utf-8') as f:
    json.dump(ABSTRACT_TO_MBBT, f, ensure_ascii=False, indent=4)

with open('derived/totoparr.json', 'w', encoding='utf-8') as f:
    json.dump(T_TO_PARR, f, ensure_ascii=False, indent=4)
