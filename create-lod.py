import csv
import json
import rdflib
from rdflib import URIRef, Literal, BNode
from rdflib.namespace import RDF, SKOS, RDFS, OWL, Namespace, NamespaceManager, XSD

BF = Namespace("http://id.loc.gov/ontologies/bibframe/")
BDR = Namespace("http://purl.bdrc.io/resource/")
BDO = Namespace("http://purl.bdrc.io/ontology/core/")
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

GRAPHNAME = "http://purl.bdrc.io/graph/CBC-data"

LOD_DS = rdflib.Dataset()
LOD_G = LOD_DS.graph(BDG[GRAPHNAME])
LOD_G.namespace_manager = NSM

T_TO_ABSTRACT = {}
T_TO_SKT = {}
T_TO_CN = {}
T_TO_VOLNUM = {}
ALL_T = []
T_TO_CBCA = {}
ABSTRACT_TO_MBBT = {}

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

with open('derived/t_to_abstract.json', encoding='utf-8') as f:
    T_TO_ABSTRACT = json.load(f)

with open('derived/t_to_skt.json', encoding='utf-8') as f:
    T_TO_SKT = json.load(f)

with open('derived/t_to_vol.json', encoding='utf-8') as f:
    T_TO_VOLNUM = json.load(f)

with open('derived/abstract-to-mbbt.json', encoding='utf-8') as f:
    ABSTRACT_TO_MBBT = json.load(f)

with open('input/index-chtitles.csv', newline='') as csvfile:
    tkreader = csv.reader(csvfile)
    for row in tkreader:
        T = normalize_taisho_id(row[0])
        ALL_T.append(T)
        T_TO_CN[T]=row[1]

with open('input/CBCAt-T.csv', newline='') as csvfile:
    tkreader = csv.reader(csvfile)
    for row in tkreader:
        T = normalize_taisho_id(row[1])
        T_TO_CBCA[T]=row[0]

def taisho_id_to_int(id):
    id = normalize_taisho_id(id)
    id = id[1:]
    dashidx = id.find('-')
    if dashidx != -1:
        id = id[:dashidx]
    if id[-1].isalpha():
        id = id[:-1]
    return int(id)

T_TO_CAT = {}
CATS = []
with open('input/categories.csv', newline='') as csvfile:
    tkreader = csv.reader(csvfile)
    next(tkreader, None) # skip first line
    firsttocats = []
    for row in tkreader:
        firsttocats.append((int(row[5]),row[1]))
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

MAIN_TAISHO_RID_A = "WA0TT0000"
MAIN_TAISHO_RID = "MW0TT0000"

ROOT_RIDS = [MAIN_TAISHO_RID]

#
# Generate some data
#

## TODO: abstract work for the Chinese Canon

## main entry for the Taisho:
LOD_G.add((BDR[MAIN_TAISHO_RID], RDF.type, BDO.Instance))
LOD_G.add((BDR[MAIN_TAISHO_RID], SKOS.prefLabel, Literal("Taisho Revised Tripitaka", lang="en")))
LOD_G.add((BDR[MAIN_TAISHO_RID], SKOS.prefLabel, Literal("大正新脩大藏經", lang="zh-Hant")))
LOD_G.add((BDR[MAIN_TAISHO_RID], BDO.isRoot, Literal(True)))

LOD_G.add((BDR[MAIN_TAISHO_RID_A], RDF.type, BDO.Work))
LOD_G.add((BDR[MAIN_TAISHO_RID_A], SKOS.prefLabel, Literal("Taisho Revised Tripitaka", lang="en")))
LOD_G.add((BDR[MAIN_TAISHO_RID_A], SKOS.prefLabel, Literal("大正新脩大藏經", lang="zh-Hant")))
LOD_G.add((BDR[MAIN_TAISHO_RID_A], BDO.isRoot, Literal(True)))
LOD_G.add((BDR[MAIN_TAISHO_RID], BDO.instanceOf, BDR[MAIN_TAISHO_RID_A]))
LOD_G.add((BDR[MAIN_TAISHO_RID_A], BDO.workHasInstance, BDR[MAIN_TAISHO_RID]))


LOD_G.add((BDA[MAIN_TAISHO_RID], RDF.type, ADM.AdminData))
LOD_G.add((BDA[MAIN_TAISHO_RID], BDO.isRoot, Literal(True)))
LOD_G.add((BDA[MAIN_TAISHO_RID], ADM.access, BDA.AccessOpen))
LOD_G.add((BDA[MAIN_TAISHO_RID], ADM.adminAbout, BDR[MAIN_TAISHO_RID]))
LOD_G.add((BDA[MAIN_TAISHO_RID], ADM.restrictedInChina, Literal(False)))
LOD_G.add((BDA[MAIN_TAISHO_RID], ADM.status, BDA.StatusReleased))
LOD_G.add((BDA[MAIN_TAISHO_RID], ADM.metadataLegal, BDA.LD_BDRC_CC0))

pi = 1
for cat in CATS:
    res = BDR[cat[1]]
    LOD_G.add((BDR[MAIN_TAISHO_RID], BDO.hasPart, res))
    LOD_G.add((res, RDF.type, BDO.Work))
    LOD_G.add((res, BDO.partOf, BDR[MAIN_TAISHO_RID]))
    LOD_G.add((res, BDO.partType, BDR.PartTypeSection))
    LOD_G.add((res, BDO.inRootInstance, BDR[MAIN_TAISHO_RID]))
    LOD_G.add((res, BDO.partIndex, Literal(pi, datatype=XSD.integer)))
    if row[2]:
        LOD_G.add((res, SKOS.altLabel, Literal(cat[2], lang="en")))
    if row[3]:
        LOD_G.add((res, SKOS.altLabel, Literal(cat[3], lang="sa-x-iast")))
    if row[4]:
        LOD_G.add((res, SKOS.prefLabel, Literal(cat[4], lang="zh-hant")))
    pi += 1



def hasParent(id):
    # returns the parent or None according to the Taisho id
    dashidx = id.find('-')
    if dashidx != -1:
        return tid_to_taishopart(id[:dashidx])
    return None

def tid_to_taishopart(tid):
    return "MW0TT%s" % tid

def tid_to_expr(tid):
    return "WA0TTE%s" % tid

def tid_to_item_sat(tid):
    return "W0SAT%s" % tid

def tid_to_volume_sat(tid, volnum):
    return "I0SAT%s_%d" % (tid,volnum)

def tid_to_manifest_sat(tid, volnum):
    tidstr = "%04d" % taisho_id_to_int(tid)
    volstr = "%02d" % volnum
    return URIRef("https://dzkimgs.l.u-tokyo.ac.jp/iiif/taisho/manifests/%s_%s_manifest.json" % (tidstr,volstr))

parentsLastPart = {}
seenAbstracts = []

itemA = BDA["I0SAT00"]
LOD_G.add((itemA, RDF.type, ADM.AdminData))
LOD_G.add((itemA, BDO.isRoot, Literal(True)))
LOD_G.add((itemA, ADM.access, BDA.AccessOpen))
LOD_G.add((itemA, ADM.restrictedInChina, Literal(False)))
LOD_G.add((itemA, ADM.status, BDA.StatusReleased))
LOD_G.add((itemA, ADM.contentLegal, BDA.LD_SAT_images))

for T in ALL_T:
    hastextparent = True
    parent = hasParent(T)
    if not parent:
        hastextparent = False
        parent = T_TO_CAT[T]
    if parent not in parentsLastPart:
        parentsLastPart[parent] = 1
    else:
        parentsLastPart[parent] += 1
    res = BDR[tid_to_taishopart(T)]
    LOD_G.add((BDR[parent], BDO.hasPart, res))
    LOD_G.add((res, RDF.type, BDO.Instance))
    LOD_G.add((res, BDO.partOf, BDR[parent]))
    LOD_G.add((res, BDO.inRootInstance, BDR[MAIN_TAISHO_RID]))
    LOD_G.add((res, BDO.partType, BDR.PartTypeText))
    LOD_G.add((res, BDO.partIndex, Literal(parentsLastPart[parent], datatype=XSD.integer)))
    anode = rdflib.BNode()
    LOD_G.add((res,BF.identifiedBy,anode))
    LOD_G.add((anode,RDF.type,BDR.CBCSiglaT))
    LOD_G.add((anode,RDF.value,Literal(T)))
    hasIndic = (taisho_id_to_int(T) < 1693)
    expr = BDR[tid_to_expr(T)]
    abstln = T_TO_ABSTRACT[T]
    abst = BDR[abstln]
    LOD_G.add((abst, RDF.type, BDO.Work))
    if abstln in ABSTRACT_TO_MBBT:
        LOD_G.add((abst, ADM.sameAsMBBT, MBBT[ABSTRACT_TO_MBBT[abstln]]))
        LOD_G.add((abst, OWL.sameAs, MBBT[ABSTRACT_TO_MBBT[abstln]]))
        LOD_G.add((MBBT[ABSTRACT_TO_MBBT[abstln]], OWL.sameAs, abst))
    if hasIndic:
        LOD_G.add((res, BDO.instanceOf, expr))
        LOD_G.add((expr, BDO.workHasInstance, res))
        LOD_G.add((expr, BDO.language, BDR.LangZh))
        LOD_G.add((expr, RDF.type, BDO.Work))
        LOD_G.add((expr, BDO.workTranslationOf, abst))
        LOD_G.add((abst, BDO.workHasTranslation, expr))
        LOD_G.add((abst, BDO.language, BDR.LangInc))
        LOD_G.add((BDA[MAIN_TAISHO_RID], ADM.adminAbout, expr))
    else:
        expr = abst
        LOD_G.add((res, BDO.instanceOf, abst))
        LOD_G.add((expr, BDO.language, BDR.LangZh))
        LOD_G.add((abst, BDO.workHasInstance, res))
    if T in T_TO_CBCA:
        LOD_G.add((expr, ADM.sameAsCBCAt, URIRef(CBCT_URI+T_TO_CBCA[T]+"/")))
        LOD_G.add((expr, OWL.sameAs, URIRef(CBCT_URI+T_TO_CBCA[T]+"/")))
    TforSAT = T
    if T[-1].isalpha():
        TforSAT = T[:-1]
    if not hastextparent:
        LOD_G.add((expr, ADM.seeOtherSAT, Literal("http://21dzk.l.u-tokyo.ac.jp/SAT2018/%s.html" % TforSAT, datatype=XSD.AnyURI)))
        LOD_G.add((expr, ADM.seeOtherCBETA, Literal("http://cbetaonline.dila.edu.tw/%s" % T, datatype=XSD.AnyURI)))
        LOD_G.add((expr, RDFS.seeAlso, Literal("http://21dzk.l.u-tokyo.ac.jp/SAT2018/%s.html" % TforSAT, datatype=XSD.AnyURI)))
        LOD_G.add((expr, RDFS.seeAlso, Literal("http://cbetaonline.dila.edu.tw/%s" % T, datatype=XSD.AnyURI)))
    if T in T_TO_CN:
        # TODO: maybe incipit title?
        LOD_G.add((res, SKOS.prefLabel, Literal(T_TO_CN[T], lang="zh-hant")))
        LOD_G.add((expr, SKOS.prefLabel, Literal(T_TO_CN[T], lang="zh-hant")))
        LOD_G.add((abst, SKOS.prefLabel, Literal(T_TO_CN[T], lang="zh-hant")))
    if T in T_TO_SKT:
        for skt in T_TO_SKT[T]:
            LOD_G.add((abst, SKOS.prefLabel, Literal(skt, lang="sa-x-iast")))
    if hastextparent:
        # SAT doesn't have manifests for subparts
        continue
    volnum = T_TO_VOLNUM[T]
    item = BDR[tid_to_item_sat(T)]
    LOD_G.add((item, RDF.type, BDO.ImageInstance))
    LOD_G.add((item, BDO.instanceOf, abst))
    LOD_G.add((item, BDO.instanceReproductionOf, res))
    LOD_G.add((res, BDO.instanceHasReproduction, item))
    LOD_G.add((itemA, ADM.adminAbout, item))
    vol = BDR[tid_to_volume_sat(T, volnum)]
    LOD_G.add((vol, RDF.type, BDO.ImageGroup))
    LOD_G.add((vol, RDF.type, BDO.Volume))
    LOD_G.add((item, BDO.instanceHasVolume, vol))
    LOD_G.add((vol, BDO.volumeOf, item))
    LOD_G.add((vol, BDO.volumeNumber, Literal(1, datatype=XSD.integer)))
    manifest = tid_to_manifest_sat(TforSAT, volnum)
    LOD_G.add((vol, BDO.hasIIIFManifest, manifest))

print(LOD_G.serialize(format='ttl').decode("utf-8") )