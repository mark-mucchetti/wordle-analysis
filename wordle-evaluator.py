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

def runStrategy(frequencyTable, exactMatches, currentList, strat="FIRST", firstWord="RAISE"):

    if (len(currentList) == 0):
        raise ValidationError("No words left to suggest.")

    if strat == "FIRST":
        return currentList[0].strip()

    if strat == "LAST":
        return currentList[-1].strip()

    if strat == "MID":
        return currentList[len(currentList)//2].strip()
    
    if strat == "RAISE":
        if frequencyTable == {}:
            return "RAISE"
        return currentList[0].strip()

    if strat == "EX-MID":
        if frequencyTable == {}:
            return firstWord
        return currentList[len(currentList)//2].strip()

def loadFile(name="DICT-5"):
    file = "dict-5.txt"
    if name=="W-ANS": file = "wordle-answers.txt"
    if name=="W-GUESS": file = "wordle-guesses.txt"
    if name=="ALL": file = "dictionary.txt"
    f = open(file, "r")
    return f.readlines()

def getEmoji(c):
    c = c.replace("G", "🟩")
    c = c.replace("Y", "🟨")   
    c = c.replace("X", "⬜")
    return c

def runGamut(wordList):
    file = open("gamut.csv", "w")

    for guess in wordList:
        logging.info(guess.rstrip())
        for answer in wordList:

            frequencyTable = {}
            exactMatches = emptyExactMatches(5)
            currentList = wordList

            guess = guess.rstrip()
            answer = answer.rstrip()            
            result = processGuess(guess, answer)

            (frequencyTable, exactMatches) = updateFrequencyTable(frequencyTable, exactMatches, guess, result)
            currentList = filterWords(frequencyTable, exactMatches, currentList)

            file.write(guess + "," + answer + "," + result + "," + str(len(currentList)) + "\n")

def guessAll(wordList, strat="FIRST", firstWord="RAISE"):
    file = open("results.csv", "w")
    for w in wordList:
        w = w.strip()
        guessCount = guessSequence(w, strat, firstWord)
        file.write(w + "," + str(guessCount) + "\n")
        logging.info("Guessed word %s in %d guesses.", w, guessCount)


def guessSequence(answer, strat="FIRST", firstWord="RAISE"):

    frequencyTable = {}
    exactMatches = emptyExactMatches(len(answer))
    currentList = wordList
    maxGuesses = 20
    guessCount = 0
    guess = ""
    
    while guessCount < maxGuesses and guess != answer:
        guess = runStrategy(frequencyTable, exactMatches, currentList, strat, firstWord)
        result = processGuess(guess, answer)
        guessCount += 1

        (frequencyTable, exactMatches) = updateFrequencyTable(frequencyTable, exactMatches, guess, result)
        currentList = filterWords(frequencyTable, exactMatches, currentList)

        logging.debug( answer + " | " + guess + " -> " + str(getEmoji(result)) + " : " + str(len(currentList)) + " words remain")

    
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
    guessFreq = {}
    answerFreq = {}

    # really should just cache the frequency tables
    for a in answer:
        answerFreq[a] = answerFreq.setdefault(a, 0) + 1
    for g in guess:
        guessFreq[g] = guessFreq.setdefault(g, 0) + 1
    #print("guess table  " + str(guessFreq))
    #print("answer table " + str(answerFreq))

    s = set(answerFreq).intersection(set(guessFreq))
    #print ("intersection " + str(s))

    for m in s:
        #print(m + " ", end=" ")
        # each M is a letter that will be Y or G
        gloc = [i for i in range(len(guess)) if guess.startswith(m, i)]
        aloc = [i for i in range(len(answer)) if answer.startswith(m, i)]
        green = set(gloc).intersection(aloc)
        #print ("gloc :" + str(gloc))
        for j in green:
            resultList[j] = "G"
            gloc.remove(j)
        answerFreq[m] = answerFreq[m] - len(green)
        #print (str(resultList))
        #print (str(answerFreq[m]) + " left to place")
        #print(str(gloc) + " possibilities")
        for i in range(0, answerFreq[m]):
            if i < len(gloc):
                k = gloc[i]
                #print("placing Y at " + str(k))
                resultList[k] = "Y"

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
wordList = loadFile("W-ANS")
logging.info('Loaded %d words', len(wordList))

guessList = loadFile("W-GUESS")
logging.info('Loaded %d guesses', len(guessList))

# uncomment to play directly
interactiveGame(wordList)

# uncomment to run the entire wordlist into a file
#guessAll(wordList, "EX-MID", "GAFFE")

# uncomment to look at a single word
#logging.getLogger().setLevel(logging.DEBUG)
#answer = "NYMPH"
#firstWord = "MAJOR"
#guessCount = guessSequence(answer, "EX-MID", firstWord)
#logging.info("Guessed word %s in %d guesses.", answer, guessCount)

#guess = "EQCEE"
#answer = "ZILLS"
#print(guess)
#print(answer)
#print(getEmoji(processGuess(guess, answer)))

#runGamut(wordList)


