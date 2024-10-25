import json
import os
import matplotlib.pyplot as plt
#Credits: https://stackoverflow.com/questions/2460177/edit-distance-in-python
def levenshtein_distance(s1, s2):
    s1 = s1.lower()
    s2 = s2.lower()
    if len(s1) > len(s2):
        s1, s2 = s2, s1

    distances = range(len(s1) + 1)
    for i2, c2 in enumerate(s2):
        distances_ = [i2+1]
        for i1, c1 in enumerate(s1):
            if c1 == c2:
                distances_.append(distances[i1])
            else:
                distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
        distances = distances_
    return distances[-1]

known_majors = [
    "Math",
    "Business",
    ["Aerospace Engineering", "Aerospace"],
    "Physics",
    "Archeology",
    "English",
    ["Political Science", "PolSci"],
    ["Cognitive Science","CogSci"],
    ["Literature", "Lit"],
    ["Computer Science", "CS", "CSE", "CompSci"],
    ["Computer engineering", "CE"],
    ["Data Science", "DS"],
    "Data analysis",
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
    "Undeclared"
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

def extract_major(tokens : list):
    global known_majors
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
            toks.append(f"{tokens[i + 1]} {tokens[i + 2]}")
            toks.append(f"{tokens[i + 2]} {tokens[i + 3]}")
        except:
            pass
        min_lev = 0.5
        major = "Unknown"
        found_flag = False
        for tok in toks:
            for m in known_flat:
                #if exact match found
                if m.lower() == tok.lower():
                    return major

        
        for tok in toks:
            for m in known_flat:
                #dont check lev dist if its one of those meme abbreviations
                if len(tok) < 5 and len(tok) == len(m):
                    continue
                dist = levenshtein_distance(tok, m)
                toklen = len(tok)
                dist *= 1 / (toklen * 2)
                if dist >= min_lev:
                    continue
                min_lev = dist
                #print(f"{major} ----------> {m} ||||| {tok}")
                major = m

        if major == "Unknown":
            #print(toks)
            return major
        #print(f"Result: {major}")
        return major



def process_data(msgs_list : list):
    majors_mapping = {}
    author_name_id_mapping = {}
    for entry in msgs_list:
        content : str = entry["content"]
        if not "major" in content.lower():
            continue
        author : dict = entry["author"]
        author_name = author["name"]
        author_id = author["id"]
        if author_id in majors_mapping.keys():
            continue
        tokens = content.split()
 
        majors_mapping[author_id] = extract_major(tokens)
        author_name_id_mapping[author_id] = author_name
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
    print(sum(nums))
    #plt.pie(nums, labels=labels)
    #plt.rcParams['font.size'] = 6
    plt.xticks(rotation=45)
    plt.bar(labels, nums)
    plt.show()


main()
