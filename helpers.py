import re
import os
import string
import util
import itertools


def removePunctuation(inFile):
    with open(inFile) as fileIn:
        stringText = fileIn.read()
        return stringText.translate(None, string.punctuation)

def alphaLowerNoSpace(inFile):
    with open(inFile) as fileIn:
        stringText = fileIn.read()
        return re.sub(r'[^a-zA-Z]','', stringText).lower()

def stripText(inFile):
    with open(inFile) as fileIn:
        stringText = fileIn.read()
        return re.sub('[^A-Za-z ]+', '', stringText).lower()

# this is really just finding the joint probability
# of all two-letter combos, but I don't think that it is actually
# the conditional probability table.
def bigramDist(inFile):
    stringText = stripText(inFile)
    biDist = util.Counter()
    for i in range(len(stringText)-1):
        biDist[stringText[i] + stringText[i+1]] += 1
    biDist.normalize()
    return biDist

def bigramDistCond(inFile):
    # Make a string from the file, stripped of all punctuation, etc.
    stringText = stripText(inFile)
    biDist = {}
    for letter in ' abcdefghijklmnopqrstuvwxyz':
        biDist[letter] = util.Counter()
        for i in range(len(stringText)-1):
            if stringText[i] == letter:
                biDist[letter][letter+stringText[i+1]]+=1
        biDist[letter].normalize()
    return biDist

# # See if this does the same thing. It saves on run time (don't need to loop over the stringText 27 times, only once.)
# def bigramDistCond(inFile):
#     # Make a string from the file, stripped of all punctuation, etc.
#     stringText = stripText(inFile)
#     biDist = {}
#     for letter in ' abcdefghijklmnopqrstuvwxyz':
#         biDist[letter] = util.Counter()

#     for i in range(len(stringText)-1):
#         biDist[stringText[i]][stringText[i]+stringText[i+1]]+=1

#     for letter in ' abcdefghijklmnopqrstuvwxyz':
#         biDist[letter].normalize()

#     return biDist


def trigramDist(inFile):
    stringText = stripText(inFile)
    triDist = util.Counter()
    for i in range(len(stringText)-2):
        triDist[stringText[i] + stringText[i+1] + stringText[i+2]] += 1
    triDist.normalize()
    return triDist

def trigramDistCond(inFile):
    chars = ' abcdefghijklmnopqrstuvwxyz'
    bigrams = []
    for char in chars:
        for char1 in chars:
            bigrams.append(char+char1)
    stringText = stripText(inFile)
    triDist = {}
    for bi in bigrams:
        triDist[bi] = util.Counter()
        for i in range(len(stringText)-2):
            if stringText[i]+stringText[i+1] == bi:
                triDist[bi][bi + stringText[i+2]] += 1
        triDist[bi].normalize()
    return triDist

# # See if this does the same thing:
# def trigramDistCond(inFile):
#     chars = ' abcdefghijklmnopqrstuvwxyz'
#     bigrams = [(char+char1) for char in chars for char1 in chars]
#     stringText = stripText(inFile)
#     triDist = {bi:util.Counter() for bi in bigrams}

#     for i in range(len(stringText)-2):
#         triDist[stringText[i]+stringText[i+1]][stringText[i]+stringText[i+1] + stringText[i+2]] += 1

#     for bi in bigrams:
#         triDist[bi].normalize()

#     return triDist

def fourgramDist(inFile):
    stringText = stripText(inFile)
    foDist = util.Counter()
    for i in range(len(stringText)-3):
        foDist[stringText[i] + stringText[i+1] + stringText[i+2] + stringText[i+3]] += 1
    foDist.normalize()
    return foDist


def bigramSegment(sentence, biDist):
    pi = []
    newSentence = sentence[0]
    pi.append(1)
    for i in range(len(sentence)-1):
        pSpace = biDist[sentence[i]+' '] + biDist[' '+sentence[i+1]] # * pi[i]
        pLetter = 2*biDist[sentence[i]+sentence[i+1]] # * pi[i]
        pi.append(max(pSpace,pLetter))
        if pSpace > pLetter:
            newSentence += ' ' + sentence[i+1]
        else:
            newSentence += sentence[i+1]

    return newSentence

def bigramSegmentNew(sentence, biDist):
    newSentence = sentence[0]
    for i in range(len(sentence)-1):
        pSpace = biDist[sentence[i]][sentence[i]+' ']
        pLetter = biDist[sentence[i]][sentence[i]+sentence[i+1]]
        # renormalize the previous branch in the probability tree
        pSpace /= (pSpace + pLetter)
        # account for the probability of adding the next letter after the space
        pSpace *= biDist[' '][' '+sentence[i+1]]
        if pSpace > pLetter:
            newSentence += ' ' + sentence[i+1]
        else:
            newSentence += sentence[i+1]

    return newSentence


def fourgramSegment(sentence, fourDist):
    pi = []
    newSentence = sentence[0]
    pi.append(1)
    for i in range(len(sentence)-3):
        pSpace = fourDist[sentence[i-2]+sentence[i-1] + sentence[i] + ' '] \
                + fourDist[sentence[i-1]+sentence[i] + ' ' +sentence[i+1]]\
                + fourDist[sentence[i]+ ' ' + sentence[i+1] + sentence[i+2]]\
                + fourDist[' ' + sentence[i+1] + sentence[i+2] + sentence[i+3]]
        pLetter = (4.0/3)*(fourDist[sentence[i-2]+sentence[i-1] + sentence[i] + sentence[i+1]]
                           + fourDist[sentence[i-1]+sentence[i] + sentence[i+1] + sentence[i+2]]
                           + fourDist[sentence[i]+sentence[i+1] + sentence[i+2] + sentence[i+3]])
        pi.append(max(pSpace,pLetter))
        if pSpace > pLetter:
            newSentence += ' ' + sentence[i+1]
        else:
            newSentence += sentence[i+1]

    return newSentence

def trigramSegment(sentence, biDist, triDist, prevLetter = None, prevProb = 1):
    if prevLetter == None:
        newSentence = sentence[0]
        pSpace = biDist[sentence[0]][sentence[0]+' ']
        pLetter = biDist[sentence[0]][sentence[0]+sentence[1]]
        pSpace /= (pSpace + pLetter)  # renormalize the previous branch in the probability tree
        pSpace *= triDist[sentence[0]+' '][sentence[0]+' '+sentence[1]]  # account for the probability of adding the next letter after the space
        if pSpace > pLetter:
            pSpace /= (pSpace+pLetter)  # renormalize again
            newSentence += ' ' + sentence[1] + trigramSegment(sentence[1:],biDist,triDist,prevLetter= ' ',prevProb = pSpace)
        else:
            pLetter /= (pSpace+pLetter)
            newSentence += sentence[1] + trigramSegment(sentence[1:],biDist,triDist,prevLetter=sentence[0],prevProb = pLetter)
    else:
        if len(sentence) == 0:
            return '.'
        if len(sentence) == 1:
            return sentence + '.'
        if len(sentence) == 2:
            pS = triDist[prevLetter+sentence[0]][prevLetter+sentence[0]+' '] * prevProb
            pL = triDist[prevLetter+sentence[0]][prevLetter+sentence[0]+sentence[1]] * prevProb
            pS /= (pS + pL)  # renormalize the previous branch in the probability tree
            pL /= (pS + pL)
            pSL = pS * triDist[sentence[0]+' '][sentence[0]+' '+sentence[1]]
            if pSL > pL:
                return ' '+sentence[1]
            else:
                return sentence[1]
        else:
            #print prevLetter+sentence[0]+' '
            #print triDist[prevLetter+sentence[0]][prevLetter+sentence[0]+' ']
            #print prevLetter+sentence[0]+sentence[1]
            #print triDist[prevLetter+sentence[0]][prevLetter+sentence[0]+sentence[1]]
            pS = triDist[prevLetter+sentence[0]][prevLetter+sentence[0]+' '] * prevProb
            pL = triDist[prevLetter+sentence[0]][prevLetter+sentence[0]+sentence[1]] * prevProb
            pS /= (pS + pL)  # renormalize the previous branch in the probability tree
            pL /= (pS + pL)
            # move to next level in the tree
            pLSL = pS * triDist[sentence[0]+' '][sentence[0]+' '+sentence[1]]  # account for the probability of adding the next letter after the space
            pLLS = triDist[sentence[0]+sentence[1]][sentence[0]+sentence[1]+' '] * pL
            pLLL = triDist[sentence[0]+sentence[1]][sentence[0]+sentence[1]+sentence[2]] * pL
            # normalize all probabilities at the same level in the tree.
            pLSL /= (pLSL+pLLS+pLLL)
            pLLS /= (pLSL+pLLS+pLLL)
            pLLL /= (pLSL+pLLS+pLLL)
            # move to next level in the tree
            pLSLS = pLSL * triDist[' '+sentence[1]][' '+sentence[1]+' ']
            pLSLL = pLSL * triDist[' '+sentence[1]][' '+sentence[1]+sentence[2]]
            pLLSL = pLLS * triDist[sentence[1]+' '][sentence[1]+' '+sentence[2]]
            pLLL_ = pLLL
            # normalize all probabilities at the same level in the tree.
            pLSLS /= (pLSLS+pLSLL+pLLSL+pLLL)
            pLSLL /= (pLSLS+pLSLL+pLLSL+pLLL)
            pLLSL /= (pLSLS+pLSLL+pLLSL+pLLL)
            pLLL_ /= (pLSLS+pLSLL+pLLSL+pLLL)
            # move to last level in the tree
            pLSLSL = pLSLS * triDist[sentence[1]+' '][sentence[1]+' '+sentence[2]]
            # pick best sequence and probability of that sequence
            if pLSLSL >= pLSLL and pLSLSL >= pLLSL and pLSLSL >= pLLL_:
                segment = ' '+sentence[1]+' '+sentence[2]
                pLast = pLSLSL/(pLSLSL+pLSLL+pLLSL+pLLL_)
                lLast = ' '
                #print 'best: '
            #print ' '+sentence[1]+' '+sentence[2]
            #print pLSLSL/(pLSLSL+pLSLL+pLLSL+pLLL_)
            if pLSLL >= pLSLSL and pLSLL >= pLLSL and pLSLL >= pLLL_:
                segment = ' '+sentence[1]+sentence[2]
                pLast = pLSLL/(pLSLSL+pLSLL+pLLSL+pLLL_)
                lLast = sentence[1]
                #print 'best: '
            #print ' '+sentence[1]+sentence[2]
            #print pLSLL/(pLSLSL+pLSLL+pLLSL+pLLL_)
            if pLLSL >= pLSLSL and pLLSL >= pLSLL and pLLSL >= pLLL_:
                segment = sentence[1]+' '+sentence[2]
                pLast = pLLSL/(pLSLSL+pLSLL+pLLSL+pLLL_)
                lLast = ' '
                #print 'best: '
            #print sentence[1]+' '+sentence[2]
            #print pLLSL/(pLSLSL+pLSLL+pLLSL+pLLL_)
            if pLLL_ >= pLSLSL and pLLL_ >= pLSLL and pLLL_ >= pLLSL:
                segment = sentence[1]+sentence[2]
                pLast = pLLL_/(pLSLSL+pLSLL+pLLSL+pLLL_)
                lLast = sentence[1]
                #print 'best: '
            #print sentence[1]+sentence[2]
            #print pLLL_/(pLSLSL+pLSLL+pLLSL+pLLL_)
            newSentence = segment + trigramSegment(sentence[2:],biDist,triDist,prevLetter=lLast,prevProb = pLast)
    return newSentence

def product(lst):
    prod = 1.00
    for el in lst:
        prod *= el
    return prod
