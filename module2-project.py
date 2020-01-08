import os
import random
from typing import List
from sklearn.feature_extraction.text import TfidfVectorizer
from os.path import join
from jpype import JClass, JString, getDefaultJVMPath, shutdownJVM, startJVM, java

ZEMBEREK_PATH: str = join('..', '..', 'bin', '/Users/metehanertan/Desktop/zemberek-full.jar')

path = "/Users/metehanertan/Desktop/1150haber/"
fileNames = []
libWord = []
wordList = []
sentence = []

s = 0
wordLimit = 100000

noun = {}
obj = {}
verb = {}

nCounter = 0
oCounter = 0
vCounter = 0
deleted = 0

# Dictionary for letter values
letterValue = {'a': 1, 'b': 2, 'c': 3, 'ç': 4, 'd': 5, 'e': 6, 'f': 7, 'g': 8, 'ğ': 9, 'h': 10, 'ı': 11,
               'i': 12, 'j': 13, 'k': 14, 'l': 15, 'm': 16, 'n': 17, 'o': 18, 'ö': 19, 'p': 20, 'r': 21,
               's': 22, 'ş': 23, 't': 24, 'u': 25, 'ü': 26, 'v': 27, 'y': 28, 'z': 29, 'â': 1}


# Calculating total letter values of given word
def calcWordLen(word):
    sum = 0
    for letter in word:
        if letter in letterValue.keys():
            sum += letterValue[letter]
        else:
            pass
    return sum


# Finding the object with minimum value
def findMinObjLen():
    return min(obj.items(), key=lambda x: x[1][1])[1]


# Finding the object with maximum value
def findMaxObjLen():
    return max(obj.items(), key=lambda x: x[1][1])[1]


# Finding the verb with minimum value
def findMinVerbLen():
    return min(verb.items(), key=lambda x: x[1][1])[1]


# Finding the verb with maximum value
def findMaxVerbLen():
    return max(verb.items(), key=lambda x: x[1][1])[1]


# Finding the noun with minimum value
def findMinNounLen():
    return min(noun.items(), key=lambda x: x[1][1])[1]


# Finding the noun with maximum value
def findMaxNounLen():
    return max(noun.items(), key=lambda x: x[1][1])[1]


# Finding a random verb that can fit in the sentence
def randomVerb():
    global vCounter, sentence, verb
    loop = 1
    while loop == 1:
        m = random.randint(1, vCounter - 1)
        if remaining > verb[m][1]:
            sentence.append(verb[m])
            verb_len = verb[m][1]
            loop = 0
    return verb_len


# Finding a random noun that can fit in the sentence
def randomNoun():
    global nCounter, sentence, noun
    loop = 1
    while loop == 1:
        n = random.randint(1, nCounter - 1)
        if remaining > noun[n][1]:
            sentence.append(noun[n])
            noun_len = noun[n][1]
            loop = 0
    return noun_len


# Finding a random object
def randomObj():
    global oCounter, sentence, obj
    n = random.randint(1, oCounter - 1)
    sentence.append(obj[n])
    obj_len = obj[n][1]
    return obj_len


# Printing the sentence
def printSentence():
    global sentence, sentenceLength, deleted
    length = len(sentence)
    problemValue = sentenceLength - deleted

    if deleted != 0:
        print("\n   --- There was a problem accured. The best one created with " , problemValue , " is:")

    if length == 2:
        print("\n   --- The generated sentence is: " + sentence[0][0] + " " + sentence[1][0] + ".\n")
    elif length == 3:
        print("\n   --- The generated sentence is: " + sentence[0][0] + " " + sentence[2][0] + " " + sentence[1][0] + ".\n")



print("         ---  GENERATING SENTENCE PROGRAM  ---")
print("Generating the dictionary with given input using Zemberek.")

fileNames = [subdir + os.path.sep + file for subdir, dirs, files in os.walk(path) for file in files]
# fileNames = [fileName.replace('\\','/') for fileName in fileNames ] # you may add this line for windows os

tfidfVectorizer = TfidfVectorizer(decode_error='ignore')
docTermMatrix = tfidfVectorizer.fit_transform((open(f, encoding="utf8", errors='ignore').read() for f in fileNames))

wordList = [libWord[0] for i, libWord in zip(range(0, wordLimit), tfidfVectorizer.vocabulary_.items())]

startJVM(
    getDefaultJVMPath(),
    '-ea',
    f'-Djava.class.path={ZEMBEREK_PATH}',
    convertStrings=False
)

TurkishMorphology: JClass = JClass('zemberek.morphology.TurkishMorphology')

morphology: TurkishMorphology = TurkishMorphology.createWithDefaults()

for word in wordList:
    analysis: java.util.ArrayList = (
        morphology.analyzeAndDisambiguate(JString(word)).bestAnalysis()
    )

    pos: List[str] = []

    for i, analysis in enumerate(analysis, start=1):

        if str(analysis.getPos()) == "Noun":
            noun[nCounter] = [word, calcWordLen(word)]
            nCounter += 1
        elif str(analysis.getPos()) == "Adjective":
            obj[oCounter] = [word, calcWordLen(word)]
            oCounter += 1
        elif str(analysis.getPos()) == "Verb":
            verb[vCounter] = [word, calcWordLen(word)]
            vCounter += 1

shutdownJVM()

print("Generating dictionary part ended.")

while 1:

    # Taking sentence length part
    acceptable = 0
    while acceptable == 0:

        minLength = findMinNounLen()[1] + findMinVerbLen()[1]
        maxLength = findMaxNounLen()[1] + findMaxObjLen()[1] + findMaxVerbLen()[1]
        print("(If you want to exit the program, you should enter -1)\n"
              "(min: ", minLength, " max:", maxLength, ")\nEnter a sum of sentence value: ")
        sentenceLength = int(input())

        if sentenceLength == -1:  # If exit
            print("Program ended...")
            exit(1)
        elif sentenceLength == minLength:  # If entered is min length
            sentence.append(findMinNounLen()[0])
            sentence.append(findMinVerbLen()[0])
            printSentence()
        elif sentenceLength == maxLength:  # If entered is max length
            sentence.append(findMaxNounLen()[0])
            sentence.append(findMaxVerbLen()[0])
            sentence.append(findMaxObjLen()[0])
            printSentence()
        elif minLength < sentenceLength < maxLength:
            acceptable = 1
        else:
            print("         --- Enter a valid input !!! ---")
            continue

    remaining = sentenceLength

    turn = 0
    while turn == 0:
        print("Selecting noun and verb")
        sentence.clear()
        remaining = sentenceLength

        # Noun Part
        nounLen = randomNoun()
        remaining -= nounLen

        # Verb Part
        verb_flag = 0
        for v in verb.keys():
            if verb[v][1] == remaining:  # Completing Verb
                sentence.append(verb[v])
                verbLen = verb[v][1]
                remaining -= verbLen
                verb_flag = 1

        if verb_flag == 1:
            break

        if remaining < findMinVerbLen()[1]:
            continue

        randVerbLen = randomVerb()
        remaining -= randVerbLen

        # Object Part
        if remaining < findMinObjLen()[1]:
            continue
        if remaining > findMaxObjLen()[1]:

            print("Adding object")
            loop = 0
            deleted = 0
            while loop < 2000:

                if deleted == 100:
                    deleted == 0
                    break

                obj_flag = 0
                for o in obj.keys():
                    if obj[o][1] == remaining:
                        sentence.append(obj[o])
                        remaining -= obj[o][1]
                        obj_flag = 1

                if obj_flag == 1:
                    turn = 1
                    break

                loop += 1
                if remaining == 0:
                    print("Remaining is 0.")
                    continue
                elif loop == 200:
                    deleted += 1
                    loop = 0
                    remaining -= 1

    printSentence()
