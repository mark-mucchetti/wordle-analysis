rfile = open("dictionary.txt", "r")
wfile = open("dict-5.txt","w")

for line in rfile:
    if len(line) == 6:
        wfile.write(line)