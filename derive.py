import csv
import json

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

def rktsid_to_abstract(rkts):
    global RKTS_SAMEABSTRACT, RKTS_TO_ABSTRACT
    if rkts in RKTS_SAMEABSTRACT:
        rkts = RKTS_SAMEABSTRACT[rkts]
    if rkts in RKTS_TO_ABSTRACT:
        return RKTS_TO_ABSTRACT[rkts]
    return "W0R%sA%s" % (rkts[0],rkts[1:])

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

# we consider that this contains all the identifiers
with open('input/index-chtitles.csv', newline='') as csvfile:
    tkreader = csv.reader(csvfile)
    for row in tkreader:
        T = normalize_taisho_id(row[0])
        T_TO_CHTITLE[T]=row[1]

def group_to_abstract(group):
    return "W0TGA%s" % group

def tid_to_abstract(tid):
    return "W0TA%s" % tid

def tid_to_taishopart(tid):
    return "W0TT%s" % tid

def tid_to_expr(tid):
    return "W0TE%s" % tid

for T in T_TO_CHTITLE:
    if T in T_TO_ABSTRACT:
        continue
    elif T in T_TO_GROUP:
        T_TO_ABSTRACT[T] = group_to_abstract(T_TO_GROUP[T])
    else:
        T_TO_ABSTRACT[T] = tid_to_abstract(T)

with open('derived/t_to_abstract.json', 'w', encoding='utf-8') as f:
    json.dump(T_TO_ABSTRACT, f, ensure_ascii=False, indent=4)

T_TO_EXPR = {}
T_TO_TAISHOPART = {}
for T in T_TO_CHTITLE:
    T_TO_EXPR[T] = tid_to_expr(T)
    T_TO_TAISHOPART[T] = tid_to_taishopart(T)

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
        if T not in T_TO_ABSTRACT:
            print("warning: "+T+" in mbbt but not in abstract")
            #print(T_TO_ABSTRACT)
            continue
        MBBT_TO_ABSTRACT[row[0]]=T_TO_ABSTRACT[T]
        ABSTRACT_TO_MBBT[T_TO_ABSTRACT[T]]=row[0]

with open('derived/mbbt-to-abstract.json', 'w', encoding='utf-8') as f:
    json.dump(MBBT_TO_ABSTRACT, f, ensure_ascii=False, indent=4)

with open('derived/abstract-to-mbbt.json', 'w', encoding='utf-8') as f:
    json.dump(ABSTRACT_TO_MBBT, f, ensure_ascii=False, indent=4)