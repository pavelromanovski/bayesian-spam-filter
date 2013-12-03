import sys,os
import argparse
import re
from collections import OrderedDict
import readline

def FileExists(path):
    if os.path.exists(path) != True:
        raise Exception('Invalid file path: {0}'.format(path))

def TokenProbability(filePath, tokenRegex, intermediateFilePath=None, verbose=False):
    if intermediateFilePath == None:
        intermediateFilePath = filePath

    tokens = {}
    # Generate frequencies
    for line in open(filePath, encoding="Latin-1"):
        for token in re.split(tokenRegex, line):
            if re.search(tokenRegex, token):
                tokens[token] = tokens.get(token,0)+1

    # Remove words that appear less than 3 times
    deleteTokens = []
    for word, count in tokens.items():
        if count < 3:
            deleteTokens.append(word)
    for token in deleteTokens:
        del(tokens[token])

    # Generate probabilities
    sum=0
    for word, count in tokens.items():
        sum += count

    # Compute probability
    fileName = "{0}.intermediate".format(intermediateFilePath)
    with open(fileName, "wt") as out_file:
        for word,count in tokens.items():
            tokens[word] = round(count/sum,7)
            if verbose:
                out_file.write("%s %d %e\n" % (word, count, tokens[word]))

    return tokens

# Compute probability that a message is spam
# P(S|W1,W2,W3,...) =                     P(W1|S)*P(W2|S)*P(W3|S)*...
#                     ---------------------------------------------------------------------
#                     P(W1|S)*P(W2|S)*P(W3|S)*... + (1-P(W1|S))*(1-P(W2|S))*(1-P(W3|S))*...
def IsMessageSpam(tokenProbabilities, tokens):
    #P(W1|S)*P(W2|S)*P(W3|S)*...
    priorProduct = 1
    #P(W1|S)*P(W2|S)*P(W3|S)*... + (1-P(W1|S))*(1-P(W2|S))*(1-P(W3|S))*...
    complementaryProduct = 1

    if len(tokens) >= 15:
        relevantTokens = {}
        for token in tokens:
            distinction = abs(0.5 - round(tokenProbabilities.get(token, 0.4),7))
            if distinction in relevantTokens:
                relevantTokens[distinction].append(token)
            else:
                relevantTokens[distinction] = [token]

        relevantTokens = OrderedDict(sorted(relevantTokens.items(), reverse=True))
        tokens = []
        wordCount = 0
        for prob,words in relevantTokens.items():
            for word in words:
                if wordCount < 15 and prob > .1:
                    wordCount += 1
                    tokens.append(word)

    #Compute prior(evidence) product
    for token in tokens:
        priorProduct *= tokenProbabilities.get(token, 0.4)

    #Compute complementary product
    for token in tokens:
        complementaryProduct *= 1-tokenProbabilities.get(token, 0.4)

    return round(priorProduct / (priorProduct + complementaryProduct),2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--non-interactive", nargs=2, help="pass in spam path followed by ham path")
    args = parser.parse_args()
    paths = {}
    if args.non_interactive:
        #run manual mode
        paths['spamPath'] = args.non_interactive[0]
        paths['hamPath'] = args.non_interactive[1]
    else:
        #run interactive mode
        paths['spamPath'] = input('Enter spam file path: ')
        paths['hamPath'] = input('Enter ham file path: ')

    try:
        FileExists(paths['spamPath'])
        FileExists(paths['hamPath'])
    except Exception as e:
        print(e)


    # valid characters: a-zA-z for tokens
    tokenRegex = re.compile(r"([a-zA-Z]{3,})")
    try:
        # Generate frequency tables with tokenizer and quantifier
        print('Generating spam probabilities...', end='')
        sys.stdout.flush()
        spamTokenProbabilities = TokenProbability(paths['spamPath'], tokenRegex)
        print(' Added {0} tokens.'.format(len(spamTokenProbabilities)))
        sys.stdout.flush()
        print('Generating ham probabilities...', end='')
        sys.stdout.flush()
        hamTokenProbabilities = TokenProbability(paths['hamPath'], tokenRegex)
        print(' Added {0} tokens.'.format(len(hamTokenProbabilities)))
        sys.stdout.flush()

        # Generate Spamicity table
        # P(S|W) =      P(W|S)
        #          -------------------
        #           P(W|S) + P(W|H)
        # P(S|W) = PSW, P(W|S) = PWS
        tokenSpamicity = {}
        print('Generating spamicity table...', end='')
        sys.stdout.flush()
        for token,PWS in spamTokenProbabilities.items():
            PWH = hamTokenProbabilities.get(token,0)
            tokenSpamicity[token] = PWS / ( PWS + PWH )
        print(' Done.')
        sys.stdout.flush()

        while True:
            msg = input('\nEnter an email message: ')
            tokens = []
            for token in re.split(tokenRegex, msg):
                if re.search(tokenRegex, token):
                    if token not in tokens:
                        tokens.append(token)
            probability = IsMessageSpam(tokenSpamicity, tokens)
            print('Is this spam? {0}%'.format(probability*100.00))
    except Exception as e:
        print(e)

    sys.exit(0)

