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
    id = id.strip(" 0D").upper()
    return "D"+id

#print(normalize_taisho_id("123"))
#print(normalize_taisho_id("T123"))
#print(normalize_taisho_id("T123-45"))
#print(normalize_taisho_id("T123(45)"))
#print(normalize_taisho_id("T123a"))

T_TO_GROUP = {}
D_TO_T = {}
T_TO_D = {}
D_TO_RKTS = {}
RKTS_SAMEABSTRACT = {}
D_TO_ABSTRACT = {}
T_TO_ABSTRACT = {}

with open('input/rkts-sameabstract.csv', newline='') as csvfile:
    tkreader = csv.reader(csvfile)
    for row in tkreader:
        RKTS_SAMEABSTRACT[row[0]] = row[1]
        RKTS_SAMEABSTRACT[row[1]] = row[0]

with open('input/Taisho-groups.csv', newline='') as csvfile:
    tkreader = csv.reader(csvfile)
    next(tkreader, None) # skip first line
    for row in tkreader:
        if (len(row) > 1 and len(row[1]) > 0) or not row[0]:
            continue
        idxlist = row[0].split(',')
        groupname = taisho_to_group_id(idxlist[0])
        for id in idxlist:
            if '?' in id or not id:
                continue
            idnorm = normalize_taisho_id(id)
            if idnorm in T_TO_GROUP:
                print("error: %s is in multiple groups" % idnorm)
            T_TO_GROUP[idnorm] = groupname

with open('input/Derge-Taisho.csv', newline='') as csvfile:
    tkreader = csv.reader(csvfile)
    next(tkreader, None) # skip first line
    for row in tkreader:
        if len(row) < 2 or (len(row) > 2 and len(row[2]) > 0) or not row[0] or not row[1]:
            continue
        D = normalize_D_id(row[0])
        tlist = row[1].split(',')
        tlistnorm = []
        for t in tlist:
            if not t:
                continue
            tnorm = normalize_taisho_id(t)
            tlistnorm.append(tnorm)
            if tnorm in T_TO_D:
                print("warning: %s appears several times in T_TO_D" % tnorm)
            T_TO_D[tnorm] = D
        D_TO_T[D] = tlistnorm
