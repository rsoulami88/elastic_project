import spacy
from lists import *
from spellchecker import SpellChecker

nlp_fr = spacy.load('en')
spell = SpellChecker(language='fr')

def intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return list(set(lst3))

def get_exp(text):
    experience = []
    if text.lower().find("experience") != -1:
        Exp = text.lower().split("experience")[1]
        Mois = ["janvier", "fevrier", "mars", "avril", "mai", "juin", "juillet", "aout", "septembre", "octobre", "novembre", "decembre"]
        for i in range(len(Exp.split("20")) - 1):
            annee = Exp.split("20")[i+1][0:2]
            txt = Exp.split("20")[i+1].replace("–", " ").replace("-", " ")
            mois = intersection(Exp.split("20")[i].replace("–", " ").replace("-", " ").split(),Mois)
            index1 = intersection(Exp.split("20")[i+1].replace("–", " ").replace("-", " ").split(),Mois)
            texte = ' '.join(txt.split()[2:len(txt.split()) - len(index1)])
            document = {
                "annee": "20" + annee,
                "duree": ' - '.join(mois),
                "experience": texte
            }
            experience.append(document)
        return experience
    else:
        return []

def get_languages(text):
    doc = nlp_fr(text)
    L = [tok.text.lower() for tok in doc]
    #L = [spell.correction(L[i]) for i in range(int((2*len(L))/3), len(L)-1)]
    languages = intersection(L, langue)
    return languages

def get_technologies(text):
    doc = nlp_fr(text)
    L = [tok.text.lower() for tok in doc]
    #L = [spell.correction(L[i]) for i in range(int((2*len(L))/3), len(L)-1)]
    Technologies = {"bigdata": intersection(L, BigDataTools),
                    "program": intersection(L, Program),
                    "front": intersection(L, Front),
                    "back": intersection(L, Back),
                    "mobile": intersection(L, Mobile),
                    "design": intersection(L, Design),
                    "scrum": intersection(L, Scrum),
                    "devops": intersection(L, DevOps),
                    "bi": intersection(L, BI),
                    "bd": intersection(L, BD)}
    return Technologies

# def get_name(text, email):
#     if email != "":
#         name = []
#         email = email.split("@")[0]
#         doc = nlp_fr(text)
#         L = [tok.text.lower() for tok in doc]
#         for word in L:
#             if email.find(word) != -1 and len(word) > 2:
#                 name.append(word)
#         return ' '.join(name)
#     else:
#         return ""

def get_name(text, email):
    doc = nlp_fr(text)
    L = [tok.text.lower() for tok in doc]
    List = [l for l in L if len(l)>2]
    if type(email) == str:
        name = []
        email = email.split("@")[0]
        for word in L:
            if email.count(word) > 0 and len(word) > 2:
                name.append(word)
                if len(L[L.index(word)+1]) > 2:
                    name.append(L[L.index(word)+1])
                else:
                    name.append(L[L.index(word)-1])
        return ' '.join(name[0:2])
    elif text.find("@") != -1:
        name = []
        M = text.split(" ")
        M = [l for l in M if l.find("@") != -1]
        email = M[0]
        for word in L:
            if email.count(word) > 0 and len(word) > 2:
                name.append(word)
                if len(L[L.index(word)+1]) > 2:
                    name.append(L[L.index(word)+1])
                else:
                    name.append(L[L.index(word)-1])
        return ' '.join(name[0:2])
    else:
        return ' '.join(List[0:2])

def entity_reco(text):
    doc = nlp_fr(text)
    for ent in doc.ents:
        print(ent.text, ent.label_)

def get_email(text):
    doc = nlp_fr(text)
    for tok in doc:
        if tok.like_email == True:
            return tok.text

def get_num(text):
    docfr = nlp_fr(text)
    Phone = []
    for ent in docfr:
        if ent.like_num == True:
            num = []
            num.append(ent.text)
            i = 1
            while i < 5 and (list(docfr).index(ent) + i) < len(list(docfr)) and docfr[list(docfr).index(ent) + i].like_num == True:
                num.append(docfr[list(docfr).index(ent) + i].text)
                i = i + 1
            if len(''.join(num)) > 9:
                Phone.append(''.join(num))
                break
    return Phone[0] if len(Phone) > 0 else []