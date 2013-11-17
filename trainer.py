import argparse
import re

# Trainer: Tokenizer -> Quantifier -> Generate Word, Probability pairs

parser = argparse.ArgumentParser()

# training arguments
parser.add_argument("-t", "--train-file", help="train from specified file", default="untrained.data")

args = parser.parse_args()

# tokenizer & quantifier
# valid characters: a-zA-z0-9_
tokenRegex = re.compile(r"([a-zA-Z]{3,})")
wordFreq = {}
try:
    for line in open(args.train_file, encoding="Latin-1"):
        for token in re.split(tokenRegex, line):
            if re.search(tokenRegex, token):
                wordFreq[token] = wordFreq.get(token,0)+1
except Exception as e:
    print(e)

# count up total number of valid tokens
sum=0
for word, count in wordFreq.items():
    sum += count

# compute probability
with open("intermediate.data", "wt") as out_file:
    for word,count in wordFreq.items():
        wordFreq[word] = count/sum
        #print("%s %d %e" % (word, count, count/sum))
        out_file.write("%s %d %e\n" % (word, count, count/sum))

while True:
    input('Enter your message: ')
    #compute
    print("%s probability: %d%%" % ("HAM", 5))
