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

GRAPHNAME = "http://purl.bdrc.io/graph/CBC-data"

DIRECTSCANS = False
SATIMAGES = True
if "-c" in sys.argv:
    DIRECTSCANS = True
    SATIMAGES = False
    print("ric mode on")

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
T_TO_TRANS = {}

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

with open('derived/t_to_trans.json', encoding='utf-8') as f:
    T_TO_TRANS = json.load(f)

with open('derived/t_to_abstract.json', encoding='utf-8') as f:
    T_TO_ABSTRACT = json.load(f)

with open('derived/t_to_skt.json', encoding='utf-8') as f:
    T_TO_SKT = json.load(f)

with open('derived/t_to_vol.json', encoding='utf-8') as f:
    T_TO_VOLNUM = json.load(f)

with open('derived/abstract-to-mbbt.json', encoding='utf-8') as f:
    ABSTRACT_TO_MBBT = json.load(f)

with open('derived/totoparr.json', encoding='utf-8') as f:
    TOTOPARR = json.load(f)

for l in TOTOPARR.values():
    for e in l:
        for e2 in l:
            if e2 != e:
                LOD_G.add((BDR[e], BDO.workHasParallelsIn, BDR[e2]))

BDRCSTARTPAGE = {}
with open('input/bdrcstartpage.csv', newline='') as csvfile:
    tkreader = csv.reader(csvfile)
    for row in tkreader:
        BDRCSTARTPAGE[int(row[0])] = int(row[1])

BDRCLOCS = {}
with open('input/pageranges.csv', newline='') as csvfile:
    tkreader = csv.reader(csvfile)
    for row in tkreader:
        BDRCLOCS['T'+row[0]] = {
            "bvol": int(row[1]),
            "evol": int(row[2]),
            "bpage": int(row[3])+BDRCSTARTPAGE[int(row[1])]-1,
            "epage": int(row[4])+BDRCSTARTPAGE[int(row[1])]-1,
            }

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
MAIN_TAISHO_RID_W = "W0TT0000"

ROOT_RIDS = [MAIN_TAISHO_RID]

#
# Generate some data
#


if SATIMAGES:
    LOD_G.add((BDR[MAIN_TAISHO_RID_W], RDF.type, BDO.Instance))
    LOD_G.add((BDR[MAIN_TAISHO_RID_W], RDF.type, BDO.ImageInstance))
    LOD_G.add((BDR[MAIN_TAISHO_RID_W], BDO.instanceReproductionOf, BDR[MAIN_TAISHO_RID]))
    LOD_G.add((BDR[MAIN_TAISHO_RID], BDO.instanceHasReproduction, BDR[MAIN_TAISHO_RID_W]))
    LOD_G.add((BDR[MAIN_TAISHO_RID_W], BDO.instanceOf, BDR[MAIN_TAISHO_RID_A]))
    LOD_G.add((BDR[MAIN_TAISHO_RID_A], BDO.workHasInstance, BDR[MAIN_TAISHO_RID_W]))
    LOD_G.add((BDR[MAIN_TAISHO_RID_W], BDO.scanInfo, Literal("These images from SAT are only accessible through the outline of the version.", lang="en")))
    LOD_G.add((BDR[MAIN_TAISHO_RID_W], TMP.thumbnailIIIFService, URIRef("https://candra.dhii.jp/iipsrv/iipsrv.fcgi?IIIF=/taisho/01/01_0001.tif")))
    LOD_G.add((BDR[MAIN_TAISHO_RID], TMP.thumbnailIIIFService, URIRef("https://candra.dhii.jp/iipsrv/iipsrv.fcgi?IIIF=/taisho/01/01_0001.tif")))

    LOD_G.add((BDA[MAIN_TAISHO_RID_W], RDF.type, ADM.AdminData))
    LOD_G.add((BDA[MAIN_TAISHO_RID_W], BDO.isRoot, Literal(True)))
    LOD_G.add((BDA[MAIN_TAISHO_RID_W], ADM.access, BDA.AccessOpen))
    LOD_G.add((BDA[MAIN_TAISHO_RID_W], ADM.adminAbout, BDR[MAIN_TAISHO_RID_W]))
    LOD_G.add((BDA[MAIN_TAISHO_RID_W], ADM.graphId, URIRef("http://purl.bdrc.io/graph/CBC-data")))
    LOD_G.add((BDA[MAIN_TAISHO_RID_W], ADM.restrictedInChina, Literal(False)))
    LOD_G.add((BDA[MAIN_TAISHO_RID_W], ADM.status, BDA.StatusReleased))
    LOD_G.add((BDA[MAIN_TAISHO_RID_W], ADM.access, BDA.AccessOpen))
    LOD_G.add((BDA[MAIN_TAISHO_RID_W], ADM.metadataLegal, BDA.LD_BDRC_CC0))
    LOD_G.add((BDA[MAIN_TAISHO_RID_W], ADM.contentLegal, BDA.LD_SAT_images))
    for i in range(1,101):
        vol = BDR["I0TT00%d" % i]
        LOD_G.add((BDA[MAIN_TAISHO_RID_W], ADM.adminAbout, vol))
        LOD_G.add((vol, RDF.type, BDO.ImageGroup))
        LOD_G.add((vol, BDO.volumeOf, BDR[MAIN_TAISHO_RID_W]))
        LOD_G.add((BDR[MAIN_TAISHO_RID_W], BDO.instanceHasVolume, vol))
        LOD_G.add((vol, BDO.volumeNumber, Literal(i, datatype=XSD.integer)))
        LOD_G.add((vol, RDFS.comment, Literal("These images from SAT are only accessible through the outline of the version.", lang="en")))
else:
    LOD_G.add((BDR[MAIN_TAISHO_RID], BDO.instanceHasReproduction, BDR["W0TT0"]))

## TODO: abstract work for the Chinese Canon

## main entry for the Taisho:
LOD_G.add((BDR[MAIN_TAISHO_RID], RDF.type, BDO.Instance))
LOD_G.add((BDR[MAIN_TAISHO_RID], SKOS.prefLabel, Literal("Taishō Tripitaka", lang="en")))
LOD_G.add((BDR[MAIN_TAISHO_RID], SKOS.prefLabel, Literal("大正新脩大藏經", lang="zh-Hant")))
LOD_G.add((BDR[MAIN_TAISHO_RID], BDO.isRoot, Literal(True)))

LOD_G.add((BDR[MAIN_TAISHO_RID_A], RDF.type, BDO.Work))
LOD_G.add((BDR[MAIN_TAISHO_RID_A], SKOS.prefLabel, Literal("Taishō Tripitaka", lang="en")))
LOD_G.add((BDR[MAIN_TAISHO_RID_A], SKOS.prefLabel, Literal("大正新脩大藏經", lang="zh-Hant")))
LOD_G.add((BDR[MAIN_TAISHO_RID_A], BDO.isRoot, Literal(True)))
LOD_G.add((BDR[MAIN_TAISHO_RID], BDO.instanceOf, BDR[MAIN_TAISHO_RID_A]))
LOD_G.add((BDR[MAIN_TAISHO_RID_A], BDO.workHasInstance, BDR[MAIN_TAISHO_RID]))


LOD_G.add((BDA[MAIN_TAISHO_RID], RDF.type, ADM.AdminData))
LOD_G.add((BDA[MAIN_TAISHO_RID], BDO.isRoot, Literal(True)))
LOD_G.add((BDA[MAIN_TAISHO_RID], ADM.access, BDA.AccessOpen))
LOD_G.add((BDA[MAIN_TAISHO_RID], ADM.adminAbout, BDR[MAIN_TAISHO_RID]))
LOD_G.add((BDA[MAIN_TAISHO_RID], ADM.graphId, URIRef("http://purl.bdrc.io/graph/CBC-data")))
LOD_G.add((BDA[MAIN_TAISHO_RID], ADM.restrictedInChina, Literal(False)))
LOD_G.add((BDA[MAIN_TAISHO_RID], ADM.status, BDA.StatusReleased))
LOD_G.add((BDA[MAIN_TAISHO_RID], ADM.metadataLegal, BDA.LD_BDRC_CC0))

LOD_G.add((BDR[MAIN_TAISHO_RID_A], TMP.entityScore, Literal(1000)))
LOD_G.add((BDR[MAIN_TAISHO_RID], TMP.entityScore, Literal(1000)))

# direct scans outline graph, W0TT0
DSOG = rdflib.Graph()
DSOG.namespace_manager = NSM
DSOG.add((BDA.O0TT0, RDF.type, BDA.AdminData))
DSOG.add((BDA.O0TT0, ADM.adminAbout, BDR.O0TT0))
DSOG.add((BDA.O0TT0, ADM.graphId, BDG.O0TT0))
DSOG.add((BDA.O0TT0, ADM.status, BDA.StatusWithdrawn))
DSOG.add((BDR.O0TT0, RDF.type, BDO.Outline))
DSOG.add((BDR.O0TT0, BDO.authorshipStatement, Literal("BDRC, based on data provided by DILA", lang="en")))
DSOG.add((BDR.O0TT0, BDO.outlineOf, BDR.MW0TT0))
DSOG.add((BDR.O0TT0, BDO.paginationType, BDR.PaginationRelative))

# sat iiif outline graph, W0TT0000
SIOF = rdflib.Graph()
SIOF.namespace_manager = NSM
SIOF.add((BDA.O0TT0000, RDF.type, BDA.AdminData))
SIOF.add((BDA.O0TT0000, ADM.adminAbout, BDR.O0TT0000))
SIOF.add((BDA.O0TT0000, ADM.graphId, BDG.O0TT0000))
SIOF.add((BDA.O0TT0000, ADM.status, BDA.StatusReleased))
SIOF.add((BDR.O0TT0000, RDF.type, BDO.Outline))
SIOF.add((BDR.O0TT0000, BDO.authorshipStatement, Literal("BDRC, based on data provided by DILA", lang="en")))
SIOF.add((BDR.O0TT0000, BDO.outlineOf, BDR.MW0TT0000))
SIOF.add((BDR.O0TT0000, BDO.paginationType, BDR.PaginationRelative))

pi = 1
for cat in CATS:
    res = BDR[cat[1]]
    DSOG.add((BDR["MW0TT0"], BDO.hasPart, res))
    DSOG.add((res, RDF.type, BDO.Instance))
    DSOG.add((res, BDO.partOf, BDR[MAIN_TAISHO_RID]))
    DSOG.add((res, BDO.partType, BDR.PartTypeSection))
    DSOG.add((res, BDO.inRootInstance, BDR[MAIN_TAISHO_RID]))
    SIOF.add((BDR["MW0TT0000"], BDO.hasPart, res))
    SIOF.add((res, RDF.type, BDO.Instance))
    SIOF.add((res, BDO.partOf, BDR[MAIN_TAISHO_RID]))
    SIOF.add((res, BDO.partType, BDR.PartTypeSection))
    SIOF.add((res, BDO.inRootInstance, BDR[MAIN_TAISHO_RID]))
    cl = BDR["CL"+cat[1]]
    DSOG.add((res, BDO.contentLocation, cl))
    DSOG.add((cl, RDF.type, BDO.ContentLocation))
    SIOF.add((res, BDO.contentLocation, cl))
    SIOF.add((cl, RDF.type, BDO.ContentLocation))
    DSOG.add((cl, BDO.contentLocationInstance, BDR["W0TT0"]))
    SIOF.add((cl, BDO.contentLocationInstance, BDR["W0TT0000"]))
    DSOG.add((cl, BDO.contentLocationVolume, Literal(cat[6], datatype=XSD.integer)))
    DSOG.add((cl, BDO.contentLocationEndVolume, Literal(cat[7], datatype=XSD.integer)))
    DSOG.add((res, BDO.partIndex, Literal(pi, datatype=XSD.integer)))
    SIOF.add((cl, BDO.contentLocationVolume, Literal(cat[6], datatype=XSD.integer)))
    SIOF.add((cl, BDO.contentLocationEndVolume, Literal(cat[7], datatype=XSD.integer)))
    SIOF.add((res, BDO.partIndex, Literal(pi, datatype=XSD.integer)))
    if row[2]:
        DSOG.add((res, SKOS.altLabel, Literal(cat[2], lang="en")))
        SIOF.add((res, SKOS.altLabel, Literal(cat[2], lang="en")))
    if row[3]:
        DSOG.add((res, SKOS.altLabel, Literal(cat[3], lang="sa-x-iast")))
        SIOF.add((res, SKOS.altLabel, Literal(cat[3], lang="sa-x-iast")))
    if row[4]:
        DSOG.add((res, SKOS.prefLabel, Literal(cat[4], lang="zh-hant")))
        SIOF.add((res, SKOS.prefLabel, Literal(cat[4], lang="zh-hant")))
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
    res_dsog = BDR["MW0TT%s" % T]
    res_siof = BDR["MW0TT%s" % T]
    DSOG.add((BDR[parent], BDO.hasPart, res_dsog))
    SIOF.add((BDR[parent], BDO.hasPart, res_siof))
    DSOG.add((res_dsog, RDF.type, BDO.Instance))
    SIOF.add((res_siof, RDF.type, BDO.Instance))
    DSOG.add((res_dsog, BDO.partOf, BDR[parent]))
    SIOF.add((res_siof, BDO.partOf, BDR[parent]))
    DSOG.add((res_dsog, BDO.inRootInstance, BDR.MW0TT0))
    SIOF.add((res_siof, BDO.inRootInstance, BDR.MW0TT0000))
    DSOG.add((res_dsog, BDO.partType, BDR.PartTypeText))
    SIOF.add((res_siof, BDO.partType, BDR.PartTypeText))
    DSOG.add((res_dsog, BDO.partIndex, Literal(parentsLastPart[parent], datatype=XSD.integer)))
    SIOF.add((res_siof, BDO.partIndex, Literal(parentsLastPart[parent], datatype=XSD.integer)))
    DSOG.add((res_dsog,BF.identifiedBy,BDR["IDO0TT0"+T]))
    SIOF.add((res_siof,BF.identifiedBy,BDR["IDO0TT0000"+T]))
    DSOG.add((BDR["IDO0TT0"+T],RDF.type,BDR.CBCSiglaT))
    SIOF.add((BDR["IDO0TT0000"+T],RDF.type,BDR.CBCSiglaT))
    DSOG.add((BDR["IDO0TT0"+T],RDF.value,Literal(T)))
    SIOF.add((BDR["IDO0TT0000"+T],RDF.value,Literal(T)))
    hasIndic = (taisho_id_to_int(T) < 1693)
    exprln = tid_to_expr(T)
    expr = BDR[exprln]
    abst = None
    if T in T_TO_ABSTRACT:
        abst = BDR[T_TO_ABSTRACT[T]]
    if abst:
        LOD_G.add((abst, RDF.type, BDO.Work))
        LOD_G.add((BDA[MAIN_TAISHO_RID], ADM.adminAbout, abst))
    DSOG.add((res_dsog, BDO.instanceOf, expr))
    SIOF.add((res_siof, BDO.instanceOf, expr))
    LOD_G.add((BDA[MAIN_TAISHO_RID], ADM.adminAbout, expr))
    DSOG.add((expr, BDO.workHasInstance, res_dsog))
    SIOF.add((expr, BDO.workHasInstance, res_siof))
    LOD_G.add((expr, BDO.language, BDR.LangZh))
    LOD_G.add((expr, RDF.type, BDO.Work))
    if hasIndic and abst:
        LOD_G.add((expr, BDO.workHasParallelsIn, abst))
        LOD_G.add((abst, BDO.workHasParallelsIn, expr))
        LOD_G.add((abst, BDO.language, BDR.LangInc))
    if exprln in ABSTRACT_TO_MBBT:
        LOD_G.add((expr, ADM.sameAsMBBT, MBBT[ABSTRACT_TO_MBBT[exprln]]))
        LOD_G.add((expr, OWL.sameAs, MBBT[ABSTRACT_TO_MBBT[exprln]]))
        LOD_G.add((MBBT[ABSTRACT_TO_MBBT[exprln]], OWL.sameAs, expr))
    if T in T_TO_CBCA:
        LOD_G.add((expr, ADM.sameAsCBCAt, URIRef(CBCT_URI+T_TO_CBCA[T]+"/")))
        LOD_G.add((expr, OWL.sameAs, URIRef(CBCT_URI+T_TO_CBCA[T]+"/")))
    TforSAT = T
    if T[-1].isalpha():
        TforSAT = T[:-1]
    if not hastextparent:
        #LOD_G.add((expr, ADM.seeOtherSAT, Literal("http://21dzk.l.u-tokyo.ac.jp/SAT2018/%s.html" % TforSAT, datatype=XSD.anyURI)))
        #LOD_G.add((expr, ADM.seeOtherCBETA, Literal("http://cbetaonline.dila.edu.tw/%s" % T, datatype=XSD.anyURI)))
        LOD_G.add((expr, RDFS.seeAlso, Literal("http://21dzk.l.u-tokyo.ac.jp/SAT2018/%s.html" % TforSAT, datatype=XSD.anyURI)))
        LOD_G.add((expr, RDFS.seeAlso, Literal("http://cbetaonline.dila.edu.tw/%s" % T, datatype=XSD.anyURI)))
        DSOG.add((res_dsog, RDFS.seeAlso, Literal("http://21dzk.l.u-tokyo.ac.jp/SAT2018/%s.html" % TforSAT, datatype=XSD.anyURI)))
        SIOF.add((res_siof, RDFS.seeAlso, Literal("http://cbetaonline.dila.edu.tw/%s" % T, datatype=XSD.anyURI)))
        DSOG.add((res_dsog, RDFS.seeAlso, Literal("http://21dzk.l.u-tokyo.ac.jp/SAT2018/%s.html" % TforSAT, datatype=XSD.anyURI)))
        SIOF.add((res_siof, RDFS.seeAlso, Literal("http://cbetaonline.dila.edu.tw/%s" % T, datatype=XSD.anyURI)))
    if T in T_TO_CN:
        # TODO: maybe incipit title?
        title = Literal(T_TO_CN[T], lang="zh-hant")
        DSOG.add((res_dsog, SKOS.prefLabel, title))
        SIOF.add((res_siof, SKOS.prefLabel, title))
        LOD_G.add((expr, SKOS.prefLabel, title))
        DSOG.add((res_dsog, BDO.hasTitle, BDR["TTO0TT0"+T]))
        SIOF.add((res_siof, BDO.hasTitle, BDR["TTO0TT0000"+T]))
        DSOG.add((BDR["TTO0TT0"+T], RDF.type, BDO.IncipitTitle))
        SIOF.add((BDR["TTO0TT0000"+T], RDF.type, BDO.IncipitTitle))
        DSOG.add((BDR["TTO0TT0"+T], RDFS.label, title))
        SIOF.add((BDR["TTO0TT0000"+T], RDFS.label, title))
        #LOD_G.add((abst, SKOS.prefLabel, title))
    if T in T_TO_TRANS:
        # TODO: maybe incipit title?
        for lname in T_TO_TRANS[T]:
            LOD_G.add((expr, BDO.workHasTranslation, BDR[lname]))
            LOD_G.add((BDR[lname], BDO.workTranslationOf, expr))
    if T in T_TO_SKT:
        for skt in T_TO_SKT[T]:
            if abst:
                LOD_G.add((abst, SKOS.altLabel, Literal(skt, lang="sa-x-iast")))
    if not hastextparent:
        # SAT doesn't have manifests for subparts
        volnum = T_TO_VOLNUM[T]
        item = BDR[tid_to_item_sat(T)]
        SIOF.add((item, RDF.type, BDO.ImageInstance))
        SIOF.add((item, TMP.thumbnailIIIFService, URIRef("https://candra.dhii.jp/iipsrv/iipsrv.fcgi?IIIF=/taisho/01/01_0001.tif")))
        SIOF.add((item, BDO.instanceOf, expr))
        SIOF.add((item, BDO.instanceReproductionOf, res_siof))
        SIOF.add((res_siof, BDO.instanceHasReproduction, item))
        SIOF.add((itemA, ADM.adminAbout, item))
        vol = BDR[tid_to_volume_sat(T, volnum)]
        SIOF.add((vol, RDF.type, BDO.ImageGroup))
        SIOF.add((vol, RDF.type, BDO.Volume))
        SIOF.add((item, BDO.instanceHasVolume, vol))
        SIOF.add((vol, BDO.volumeOf, item))
        SIOF.add((vol, BDO.volumeNumber, Literal(volnum, datatype=XSD.integer)))
        manifest = tid_to_manifest_sat(TforSAT, volnum)
        SIOF.add((vol, BDO.hasIIIFManifest, manifest))
        cl = BDR["CLW0TT0000"+T]
        SIOF.add((res_siof, BDO.contentLocation, cl))
        SIOF.add((cl, RDF.type, BDO.ContentLocation))
        SIOF.add((cl, BDO.contentLocationInstance, BDR["W0TT0000"]))
        SIOF.add((cl, BDO.contentLocationVolume, Literal(volnum, datatype=XSD.integer)))
    if T in BDRCLOCS:
        loc = BDRCLOCS[T]
        cl = BDR["CLW0TT0"+T]
        DSOG.add((res_dsog, BDO.contentLocation, cl))
        DSOG.add((cl, RDF.type, BDO.ContentLocation))
        DSOG.add((cl, BDO.contentLocationInstance, BDR["W0TT0"]))
        DSOG.add((cl, BDO.contentLocationVolume, Literal(loc["bvol"], datatype=XSD.integer)))
        if loc["bvol"] != loc["evol"]:
            DSOG.add((cl, BDO.contentLocationEndVolume, Literal(loc["evol"], datatype=XSD.integer)))
        DSOG.add((cl, BDO.contentLocationPage, Literal(loc["bpage"], datatype=XSD.integer)))
        DSOG.add((cl, BDO.contentLocationEndPage, Literal(loc["epage"], datatype=XSD.integer)))

LOD_G.serialize("CBC.ttl", format="turtle")
DSOG.serialize("O0TT0.ttl", format="turtle")
SIOF.serialize("O0TT0000.ttl", format="turtle")