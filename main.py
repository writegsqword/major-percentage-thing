import json
import os
import matplotlib.pyplot as plt
from difflib import SequenceMatcher as SM

known_majors = [
    ["Mathehatics", "Math"],
    ["Biochemistry", "BioChem"],
    ["Anthropology", "Anth"],
    ["Linguistics", "ling"],
    'Music',
    "Business",
    ["Aerospace Engineering", "Aerospace"],
    "Physics",
    "Archeology",
    "English",
    ["Political Science", "PolSci"],
    ["Cognitive Science","CogSci"],
    ["Literature", "Lit"],
    ["Computer Science", "CS", "CSE", "CompSci"],
    ["Electrical Engineering", "EE"],
    ["Computer engineering", "CE"],
    ["Data Science", "DS"],
    "Data analysis",
    ["Statistics", "Stats"],
    ["Psychology","Psych"],
    ["Communications", "Comm"],
    ["Biology","Bio"],
    ["Chemistry", "Chem"],
    ["Economics", "Econ"],
    ["Environmental Systems", "ES"],
    "Art",
    ["Math-Computer Science", "Math-CS", "Math-CompSci"],
    "Neuroscience",
    "Sociology",
    "Undeclared",
    "Studio",
    ["ICAM"]
]
blacklist = [
    "at",
    "college",
]
known_flat = []
for m in known_majors:
    if type(m) == list:
        for m2 in m:
            known_flat.append(m2)
        continue
    known_flat.append(m)

def remap_flattened(major):
    for m in known_majors:
        if type(m) != list:
            if major == m:
                return m
            continue
        for m2 in m:
            if major == m2:
                return m[0]
    return "Unknown"

def extract_major(tokens : list, prev_major = "Unknown", max_score = 0):
    global known_flat
    global blacklist

    for i, t in enumerate(tokens):
        if not "major" in t.lower():
            continue
        toks = []
        try:
            toks.append(tokens[i - 1])
            toks.append(tokens[i - 2])
            toks.append(tokens[i - 3])
            toks.append(f"{tokens[i - 2]} {tokens[i - 1]}")
            toks.append(f"{tokens[i - 3]} {tokens[i - 2]}")
        except:
            pass
        try:

            toks.append(tokens[i + 1])
            toks.append(tokens[i + 2])
            toks.append(tokens[i + 3])
            toks.append(tokens[i + 4])
            toks.append(f"{tokens[i + 1]} {tokens[i + 2]}")
            toks.append(f"{tokens[i + 2]} {tokens[i + 3]}")
            toks.append(f"{tokens[i + 1]} {tokens[i + 2]} {tokens[i + 3]}")
            toks.append(f"{tokens[i + 3]} {tokens[i + 4]}")
            toks.append(f"{tokens[i + 2]} {tokens[i + 3]} {tokens[i + 4]}")
        except:
            pass
        major = prev_major
        found_flag = False
        for tok in toks:
            for m in known_flat:
                #if exact match found
                if m.lower() == tok.lower():
                    return (m, 99999)

        
        for tok in toks:
            tok = tok.lower()
            if tok in blacklist:
                continue
            for m in known_flat:
                
                #dont check lev dist if its one of those meme abbreviations
                if len(tok) < 5 and len(tok) == len(m):
                    continue
                score = SM(None, m.lower(), tok).ratio()
                toklen = len(tok)
                #score *= 1 / (toklen * 2)
                if score < max_score:
                    continue
                max_score = score
                #print(f"{major} ----------> {m} ||||| {tok}")
                major = m

        if major == "Unknown":
            #print(toks)
            return (major, max_score)
        #print(f"Result: {major}")
        return (major, max_score)



def process_data(msgs_list : list):
    majors_mapping = {}
    majors_res_mapping = {}
    author_name_id_mapping = {}
    for entry in msgs_list:
        content : str = entry["content"]
        if not "major" in content.lower():
            continue
        author : dict = entry["author"]
        author_name = author["name"]
        author_id = author["id"]
        tokens = content.split()
        author_name_id_mapping[author_id] = author_name
        
        if author_id in majors_res_mapping.keys():
            prev_res = majors_res_mapping[author_id]
            majors_res_mapping[author_id] = extract_major(tokens, prev_res[0], prev_res[1])
            continue
        majors_res_mapping[author_id] = extract_major(tokens, max_score=0.8)
        #print(majors_res_mapping[author_id])
 
    for k, v in majors_res_mapping.items():
        majors_mapping[k] = v[0]
        
    return majors_mapping


def import_data(fname) -> list:
    with open(fname, "r") as f:
        res = json.loads(f.read())
    return res["messages"]
def main():
    msgs = []
    for root, dirs, files in os.walk("data"):
        for f in files:
            msgs += import_data(f"{root}/{f}")
    majors_map = process_data(msgs)
    majors_count_map = {}
    for k, v in majors_map.items():
        if v == "Unknown":
             continue
        v = remap_flattened(v)
        if not v in majors_count_map.keys():
            majors_count_map[v] = 1
            continue
        majors_count_map[v] += 1
    nl_tup = []
    for k, v in majors_count_map.items():
        nl_tup.append((k,v))
    nl_tup.sort(key = lambda x : x[1])

    labels, nums = zip(*nl_tup)
    print(nums)
    tot=sum(nums)
    plt.rcParams['font.size'] = 8
    plt.pie(nums, labels=labels, autopct=lambda x : (('{:.4f}%\n({:.0f})'.format(x, tot*x/100)) if x > 3 else ''))
    
    print(tot)
    # plt.xticks(rotation=45)
    # plt.bar(labels, nums)
    plt.show()


main()
