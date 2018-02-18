# text-normalization

* A system that allows automatical text normalization

## Requirements
For running successfully this system, you need both python 2.7 and python 3.6 on your machine.

For running "preprocess.py", you need install [[ekphrasis]](https://github.com/cbaziotis/ekphrasis) in the python 3.6 envoronment.

For running "system.py", you need install [[context2vec]](https://github.com/orenmel/context2vec) in the python 2.7 environment.

* You can also ignore the preprocess part, which means you need to skip the preprocess.py part in the run_system.sh.

	* Your input file should be named result/preprocess1.txt. And all lines in your input file will be normalized.

## Quick-start
First, enter the subfolder named "system", then open the terminal, run the command below:

```
sh run_system.sh [input-file] [num_sentences] [mode] [state] [output_file_name]
```

* [input-file]: The input file path
* [num_sentences]: The number of sentences in the input-file you want to normalize
* [mode]: The way to select sentences from the input file:
if mode = 'random': choose randomly
	- if mode = '-1': choose all sentences in the file
	- if mode = [other int type]: choose the range of [int(mode):int(mode)+num_sentences]
* [state]: The state of selecting the corrected words
	- if state = 'manual': you will choose the corrected words manually from the candidates
	- if state = 'auto': the candidate with the largest similarity will be selected automatically
* [output_file_name]: The file name of the output of result. The file will be stored directly in the ./output/ repository

### Example
```
sh run_system.sh ./corpus/CorpusBataclan_en.1M.raw.txt 3 51 auto output
```
This will normalize the line 51 to 53(included) in the file "./corpus/CorpusBataclan_en.1M.raw.txt", the corrected words are selected automatically, the result will be stored in "./result/output.txt"

## run_system.sh

```
#!/bin/sh

CONTEXT2VECDIR="MODEL_DIR/MODEL.params"
DICTDIR="dictionary/words_alpha.txt"
PREPROCESSED="result/preprocess1.txt"

echo "Preprocessing ... ..."
python3 ./commands/preprocess.py $1 $2 $3 $PREPROCESSED

python2 ./commands/system.py $PREPROCESSED $CONTEXT2VECDIR $DICTDIR $4 $5

rm $PREPROCESSED
```
* The variable $CONTEXT2VECDIR is the trained context2vec model. 

* Attention! The model provided in the repository is a tiny demo one, so the performance is poor. For better performance, download pre-trained context2vec models from [[here]](http://u.cs.biu.ac.il/~nlp/resources/downloads/context2vec/) and unzip the model under the system folder.

* The variable $DICTDIR is the dictionay file. You can use other dictionary

* The variable $PREPROCESSED is a temporary file to store the preprecessed sentences, and will be deleted in the end.

## Known issues

* All words are converted to lowercase.


## References
https://github.com/orenmel/context2vec

https://github.com/cbaziotis/ekphrasis
