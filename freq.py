#stupid hacky stuff
logging = 0
exec(open("./wordle-evaluator.py").read())


hardMode = False

def load_freq():
    with open('unigram_freq.csv') as f:
        freq = {}
        f.readline()
        for line in f:
            freq[line.split(',')[0].strip().upper()] = int(line.split(',')[1])
        return freq

def add_freq():
    with open('unigram_freq.csv') as f:
        freq = {}
        f.readline()
        for line in f:
            freq[line.split(',')[0].strip().upper()] = int(line.split(',')[1])

    file = open('wordle-guesses.txt', 'r')
    wfile = open('wordle-g-freq.csv', 'w')
    for l in file:
        if l.strip() in freq.keys():
            wfile.write(l.strip() + "," + str(freq[l.strip()]) + '\n')
        else:
            wfile.write(l.strip() + ",0\n")

def transform(s):
    s = s.replace(":black_large_square:", "X")
    s = s.replace(":white_large_square:", "X")
    s = s.replace(":large_green_square:", "G")
    s = s.replace(":large_yellow_square:", "Y")
    s = s.replace("⬛", "X")
    s = s.replace("⬜", "X")
    s = s.replace("🟨", "Y")
    s = s.replace("🟩", "X")
    return s

def loadGuesses(answer):
    logging.info("Loading answer tables")
    freq = load_freq()
    results = {}
    last_pos = 0;
    with open("gamut.csv", "r") as g:
        for l in g:
            ls = l.split(",")
            gAnswer = ls[0]
            if gAnswer == answer:
                gGuess = ls[1]
                gResult = ls[2]
                t = results.setdefault(gResult, [])
                t.append((gGuess,freq.setdefault(gGuess, 0)))
    return (results)

def loadSequence(filename, answer):
    gamut = loadGuesses(answer)
    with open(filename) as f:
        l = f.readline()
        if not l.startswith("Wordle"):
            logging.info("This is not a Wordle share file.")
            quit()
        if l.count('X/6') > 0:
            logging.info("Cannot process non-winning sequences.")
            quit()
        if l.count('*') > 0:
            hardMode = True
        for a in f:
            h = transform(a).strip().upper()
            print(gamut[h])




loadSequence("share.txt","QUERY")