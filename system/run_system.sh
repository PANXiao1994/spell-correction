#!/bin/sh

CONTEXT2VECDIR="MODEL_DIR/MODEL.params"
DICTDIR="dictionary/words_alpha.txt"
PREPROCESSED="result/preprocess1.txt"

echo "Preprocessing ... ..."
python3 ./commands/preprocess.py $1 $2 $3 $PREPROCESSED

python ./commands/system.py $PREPROCESSED $CONTEXT2VECDIR $DICTDIR $4 $5

rm $PREPROCESSED
