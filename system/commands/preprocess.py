#/Users/panxiao/anaconda3/bin/python
import sys
import numpy as np
import pandas as pd
import re
from ekphrasis.classes.segmenter import Segmenter
from ekphrasis.classes.preprocessor import TextPreProcessor
from ekphrasis.classes.tokenizer import SocialTokenizer
from ekphrasis.dicts.emoticons import emoticons

text_processor = TextPreProcessor(
    # terms that will be normalized
    normalize=['url', 'email', 'percent', 'money', 'phone', 'user',
        'time', 'url', 'date', 'number'],
    # terms that will be annotated
    annotate={"hashtag", "allcaps", "elongated", "repeated",
        'emphasis', 'censored'},
    fix_html=False,  # fix HTML tokens
    segmenter="twitter", 
    corrector="twitter", 
    
    unpack_hashtags=True,  # perform word segmentation on hashtags
    unpack_contractions=True,  # Unpack contractions (can't -> can not)
    spell_correct_elong=True,  # spell correction for elongated words
    
    tokenizer=SocialTokenizer(lowercase=True).tokenize,
    
    dicts=[emoticons]
)
def main(corpus_path, num_lines, mode, preprocessed):
    # Read the corpus to correct
    
    with open(corpus_path, "r") as myfile:
        doc = myfile.readlines()
    for i in range(len(doc)):
        result = re.sub(r"http\S+", "", doc[i])
        doc[i] = re.sub(r"\n", "", result.lower())
    n = len(doc)
    if int(num_lines):
        num_lines = int(num_lines)
    else:
        raise Exception("num_lines input error!")
    # subsample the lines to be normalized
    if mode == 'random':
        idx = np.random.choice(np.arange(n),num_lines)
        lines = doc[idx]
    elif int(mode):
        if int(mode) >= 0:
            lines = doc[int(mode): int(mode)+num_lines]
        elif int(mode) == -1:
            lines = doc
        else:
            raise Exception("Mode number error!")
    else:
        raise Exception("Mode input type error!")

    # write the preprocessed sentences into the intermediate file
    thefile = open(preprocessed, 'w')
    for l in lines:
        line = " ".join(text_processor.pre_process_doc(l))
        thefile.write("%s\n" % line.encode('utf-8'))
    thefile.close()

main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])