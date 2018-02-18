import sys
from context2vec import train
import numpy as np
import pandas as pd
import re
import traceback
from context2vec.common.context_models import Toks
from context2vec.common.model_reader import ModelReader
import time
import six

# set the tolerace of levenshtein distance
LEVEN_DIST = 2

# set the number of candidates
N_RESULT = 5

STATE = sys.argv[4]
if STATE != 'manual' and STATE != 'auto':
    raise Exception("STATE error!")

OUTPUT = sys.argv[5]

model_param_file = sys.argv[2]

model_reader = ModelReader(model_param_file)
w = model_reader.w
word2index = model_reader.word2index
index2word = model_reader.index2word
model = model_reader.model
target_exp = re.compile('\<.*\>')
#context_v = model.context2vec(sent, target_pos) 
xp = np

# Read the dictionary
dic_path = sys.argv[3]
with open(dic_path, "r") as f:
    WORDS = f.readlines()
for i in range(len(WORDS)):
    WORDS[i] = re.sub(r"\n", "", WORDS[i].lower())
    WORDS[i] = re.sub(r"\r", "", WORDS[i].lower())

def levenshtein(s1, s2):
    if len(s1) < len(s2):
        return levenshtein(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[
                             j + 1] + 1  # j+1 instead of j since previous_row and current_row are one character longer
            deletions = current_row[j] + 1  # than s2
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def candidates(word):
    "Generate possible spelling corrections for word."
    return set(known([word]) or known(edits1(word))) #or known(edits2(word))) or [word])

def known(words):
    "The subset of `words` that appear in the dictionary of WORDS."
    return set(w for w in words if w in WORDS)

def exist(word):
    "The subset of `words` that appear in the dictionary of WORDS."
    return (word in WORDS)

def edits1(word):
    "All edits that are one edit away from `word`."
    letters    = 'abcdefghijklmnopqrstuvwxyz'
    splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
    deletes    = [L + R[1:]               for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
    replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
    inserts    = [L + c + R               for L, R in splits for c in letters]
    return set(deletes + transposes + replaces + inserts)

def edits2(word):
    "All edits that are two edits away from `word`."
    return (e2 for e1 in edits1(word) for e2 in edits1(e1))

def parse_input(line):
    # strip a sentence into a list of words
    sent = line.strip().split()
    target_pos = []
    for i, word in enumerate(sent):
        #print word, exist(word)
        if i != 0 and target_exp.match(word) == None and word.isalpha() and exist(word)==False:
            target_pos.append(i)
            sent[i] = word
    return sent, target_pos

def mult_sim(w, target_v, context_v):
    target_similarity = w.dot(target_v)
    target_similarity[target_similarity<0] = 0.0
    context_similarity = w.dot(context_v)
    context_similarity[context_similarity<0] = 0.0
    return (target_similarity * context_similarity)



def main(input_path):
    print "\n--> Start reading the preprocessed file ... ..."
    with open (input_path, "r") as myfile:
        lines = myfile.readlines()

    # Normalize the lines one by one
    if OUTPUT != '-1':
        thefile = open('result/'+OUTPUT+'.txt', 'w')  
    for i,line in enumerate(lines):
        print "\n-------Sentence %d:------\n"%(i+1), line
        print ">> Extracting the words to be corrected ... ..."
        sent, target_pos = parse_input(line)
        print ">> The following positions are not correct:"
        print target_pos
        if len(target_pos) == 0:
            l = line
        else:
            corr_line = auto_corr(sent, target_pos)
            l = " ".join(corr_line)
        if OUTPUT == '-1':
            print "\n=====The corrected sentences:====="
            print l, '\n'
        else:
            thefile.write("%s\n" % l.encode('utf-8'))
            
def auto_corr(sent, target_pos):
    """
    given the sentence and the target words indexes,
    return the corrected sentence
    """
    for pos in target_pos:
        target_v = None
        t0 = time.time()
        if len(sent) > 1:
            context_v = model.context2vec(sent, pos) 
            context_v = context_v / xp.sqrt((context_v * context_v).sum())
        else:
            context_v = None

        if target_v is not None and context_v is not None:
            similarity = mult_sim(w, target_v, context_v)
        else:
            if target_v is not None:
                v = target_v
            elif context_v is not None:
                v = context_v                
            else:
                raise Exception("Can't find a target nor context.")   
            similarity = (w.dot(v)+1.0)/2 # Cosine similarity can be negative, mapping similarity to [0,1]

        old_word = sent[pos]
        if STATE == 'manual':
            print "\n>> For the correction of word: ", old_word
            print ">>>> Calculating the candidates ... ..."
        candidats = candidates(old_word)

        l = []
        count = 0

        if len(candidats)!=0:
            for i in (-similarity).argsort():
                if index2word[i] not in candidats:
                    continue
                else:
                    count += 1
                    if STATE == 'manual':
                        print "candidate %d:\t"%count, index2word[i], ", similarity:\t", similarity[i]
                    l.append(i)
                if count == N_RESULT:
                    break 
        else:
            for i in (-similarity).argsort():
                if np.isnan(similarity[i]):
                    continue
                #print sent[pos], index2word[i]
                dist = levenshtein(index2word[i], sent[pos])
                if dist <= LEVEN_DIST:
                    count += 1
                    if STATE == 'manual':
                        print "candidate %d:\t"%count, index2word[i],", similarity:\t", similarity[i], ", levenshtein distance:\t", dist
                    l.append(i)
                if count == N_RESULT:
                    break 
        if len(l) == 0:
            continue
            
        if STATE == 'manual':
            print "Time: %.2fs"%(time.time()-t0)
            print "Please choose the replacement, enter the number of the candidate: (Enter 0 for no replacement)"
            choice = six.moves.input('>> ')
            c = int(choice)
            if c == 0:
                continue # no change made
            elif c > 0:
                idx = l[c - 1]
            else:
                raise Exception("Invalid input!")   
        elif STATE == 'auto':
            idx = l[0]
        corr_word = index2word[idx]

        
        print ">>>> \t", old_word, "\t--->\t", corr_word
        sent[pos] = corr_word
    return sent


main(sys.argv[1])