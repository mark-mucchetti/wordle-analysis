# Wordle Evaluator
# Copyright (c) 2022 Mark Mucchetti
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import logging, sys
import re
import string
wordList = []

# logging configuration
logging.basicConfig(stream=sys.stderr, level=logging.INFO)

def runStrategy(frequencyTable, exactMatches, currentList, strat="FIRST"):

    if (len(currentList) == 0):
        raise ValidationError("No words left to suggest.")

    if strat == "FIRST":
        return currentList[0].strip()

    if strat == "LAST":
        return currentList[-1].strip()

    if strat == "MID":
        return currentList[len(currentList)//2].strip()

def loadFile():
    #file = open("dictionary.txt", "r")
    file = open("dict-5.txt", "r")
    return file.readlines()

def getEmoji(c):
    c = c.replace("G", "🟩")
    c = c.replace("Y", "🟨")   
    c = c.replace("X", "⬜")
    return c

def guessAll(wordList, strat="FIRST"):
    file = open("results.csv", "w")
    for w in wordList:
        w = w.strip()
        guessCount = guessSequence(w, strat)
        file.write(w + "," + str(guessCount) + "\n")
        logging.info("Guessed word %s in %d guesses.", w, guessCount)


def guessSequence(answer, strat="FIRST"):

    frequencyTable = {}
    exactMatches = exactMatches = emptyExactMatches(len(answer))
    currentList = wordList
    maxGuesses = 20
    guessCount = 0
    guess = ""
    
    while guessCount < maxGuesses and guess != answer:
        guess = runStrategy(frequencyTable, exactMatches, currentList, strat)
        result = processGuess(guess, answer)
        logging.debug( answer + " | " + guess + " -> " + str(getEmoji(result)))
        guessCount += 1

        (frequencyTable, exactMatches) = updateFrequencyTable(frequencyTable, exactMatches, guess, result)
        currentList = filterWords(frequencyTable, exactMatches, currentList)
    
    return guessCount

def runSequence(history):
    pass

def filterWords(frequencyTable, exactMatches, currentList):

    # filter by exact matches
    exactList = list(filter(buildExactMatchesRegex(exactMatches).match, currentList))

    # test the remainder for inexact matches and out-of-positions
    currentList = []

    for word in exactList:
        success = True
        for k in frequencyTable.keys():
            if (word.count(k) < frequencyTable[k][0] or
                (frequencyTable[k][1] == 1 and (word.count(k) != frequencyTable[k][0]))):
                success = False
                break
        if success:
            currentList.append(word.strip())

    return currentList

def updateFrequencyTable(frequencyTable, exactMatches, guess, result):

    curFrequency = {}
    for j in range(0, len(guess)):
    # add this letter to the table if we've never seen it before
        frequencyTable[guess[j]] = frequencyTable.setdefault(guess[j], (0, False))

        if result[j] == "G":
            curFrequency[guess[j]] = curFrequency.setdefault(guess[j],0)+1
            exactMatches[j] = guess[j]
        elif result[j] == "Y":
            curFrequency[guess[j]] = curFrequency.setdefault(guess[j],0)+1
            exactMatches[j] = exactMatches[j].replace(guess[j],"")
        else:
            # we've found all of this letter, lock to exact count
            exactMatches[j] = exactMatches[j].replace(guess[j],"")
            frequencyTable[guess[j]] = (frequencyTable[guess[j]][0], True)
    
    # process current frequencies into stateful frequency table and update minima
    for k in curFrequency.keys():
        if (frequencyTable[k][0] < curFrequency[k]):
            frequencyTable[k] = (curFrequency[k], frequencyTable[k][1])

    return (frequencyTable, exactMatches)

def processGuess(guess, answer):

    resultList = []
    for j in range(0, len(answer)): resultList.append("X")

    for j in range(0, len(answer)):
        #logging.debug(answer[j] + " -> " + guess[j])
        #logging.debug(guess.count(answer[j]))
        if answer[j] == guess[j]:
            resultList[j] = "G"
        elif guess.count(answer[j]) > 0:
            res = [i for i in range(len(guess)) if guess.startswith(answer[j], i)]
            # r is all indexes of the guess that match this letter in any position
            # we only want to update positions that are not "G", but we always want to go
            # until we find any to make them "Y"
            max = answer.count(answer[j])
            for r in res:
                i = guess[r]
                if resultList[r] != "G": 
                    resultList[r] = "Y"
                max -= 1
                if max == 0: break
                        
        #logging.debug("".join(resultList))

    return "".join(resultList)

class ValidationError(Exception):
    pass

def validateInput(guess, result, length):
    if length != 0:
        if len(result) != length:
            raise ValidationError("Result is of wrong length.")
        if len(guess) != length:
            raise ValidationError("Guess is of wrong length.")

    if (len(guess) != len(result)):
        raise ValidationError("Guess and result do not have matching length.")
    pass

    if (re.match('[^A-Z]', guess + result)):
        raise ValidationError("Please use only letters A-Z.")

def emptyExactMatches(length):
    matches = []
    for j in range(0,length):
        matches.append(string.ascii_uppercase)
    pass
    return matches

def buildExactMatchesRegex(exactMatches):
    regex = "^"
    for t in exactMatches:
        regex = regex + str.format('[{}]', t)
    regex = regex + "$"
    return re.compile(regex)
    pass

def interactiveGame(wordList):

    wordLength = 0
    historyList = {}
    frequencyTable = {}
    exactMatches = []
    init = False

    currentList = wordList

    while True:
        guess =  input("Guess : " ).upper()
        result = input("Result: ").upper()

        # collect input
        try:
            validateInput(guess, result, wordLength)
            wordLength = len(guess)
        except ValidationError as exception:
            logging.error(exception)
            break

        historyList[guess] = result
        if not init:
            exactMatches = emptyExactMatches(wordLength)
            logging.debug("Loaded exact matches set of length %d", wordLength)
            init = True

        (frequencyTable, exactMatches) = updateFrequencyTable(frequencyTable, exactMatches, guess, result)

        # get current state
        logging.debug(frequencyTable)
        logging.debug(exactMatches)

        # filter the wordlist with this state
        curLength = len(currentList)
        currentList = filterWords(frequencyTable, exactMatches, currentList)

        logging.info("Wordlist filtered from %d to %d word(s).",curLength,len(currentList))

        if (len(currentList) == 0):
            logging.error("No words remaining.")
            break
        
        if (len(currentList) == 1):
            logging.info("The answer is %s", currentList[0])
            break

        if (len(currentList) < 100):
            logging.info(currentList)

        solverGuess = runStrategy(frequencyTable, exactMatches, currentList)
        logging.info("Try %s", solverGuess)

# load whatever wordlist
wordList = loadFile()
logging.info('Loaded %d words', len(wordList))

# uncomment to play directly
#interactiveGame(wordList)

# uncomment to run the entire wordlist into a file
# guessAll(wordList, "MID")

# uncomment to look at a single word
logging.getLogger().setLevel(logging.DEBUG)
w = "BANAL"
guessCount = guessSequence(w, "FIRST")
logging.info("Guessed word %s in %d guesses.", w, guessCount)


