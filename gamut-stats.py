import csv
import statistics
from math import sqrt,cos,sin,radians

def writeGamutStats():
    with open('gamut.csv', newline='\n') as c:
        sr = csv.reader(c, delimiter=',')
        output = open("gamut-avg.csv", "w")
        prevWord = ""
        total = 0
        pl = []
        distinctResponses = set()
        allDistinctResponses = set()
        go = False

        for l in sr:
            word = l[0]
            if (word == prevWord):
                total += int(l[3])
                pl.append(int(l[3]))
                distinctResponses.add(l[2])
                allDistinctResponses.add(l[2])
            else:            
                if go:
                    print(word)
                    st = str(total)
                    output.write(word + "," + st + "," + str(len(distinctResponses)) + "," + str(int(statistics.mean(pl))) + "," + str(int(statistics.median(pl))) + "\n")
                    total = 1
                    pl = []
                    distinctResponses = set()
                else:
                    go = True
            prevWord = word

        print(str(len(allDistinctResponses)))

# this generates a PPM image for convenience. you can convert it to
# any other format with this command from ImageMagick. it also has
# various hardcodes because I don't feel like exploring all the variations
# $ convert gamut-image.ppm gamut-image.png
def generateGamutImage(strategy="DEFAULT"):

    w, h = 2315, 2315
    with open('gamut.csv', newline='\n') as c:
        file = open('gamut-image.ppm', 'w')
        file.write('P3\n' + str(w) + '  ' + str(h) + '\n255\n')
        sr = csv.reader(c, delimiter=',')

        x = 0
        for l in sr:        
            (r,g,b) = getPixelColor(l, strategy)            
            file.write(str(r) + " " + str(g) + " " + str(b) + "\t")
            
            x += 1
            if x >= (w-1): 
                file.write('\n')
                x = 0

def getPixelColor(line, strategy="DEFAULT"):

    r, g, b = 0, 0, 0
    if strategy == "DEFAULT":
        for rl in line[2]:
            (lr, lg, lb) = getColor(rl)
            r = r + lr; g = g + lg; b = b + lb
        return (r//5, g//5, b//5)

    if strategy == "REMAINING":
        for rl in line[3]:
            sat = 255-(int(line[3])//4)
            (lr, lg, lb) = (sat, sat, sat)
        return (lr, lg, lb)

    if strategy == "LETTERS":
        letord = (ord(line[0][0])-64)
        aord = (ord(line[1][0])-64)
        for rl in line[2]:
            (lr, lg, lb) = getColor(rl)
            r = r + lr; g = g + lg; b = b + lb
        hue = RGBRotate()
        hue.set_hue_rotation(((letord+aord)*41)%360)
        return hue.apply(r//5, g//5, b//5)

            

    return (0,0,0)

def getColor(r, strategy="DEFAULT"):
    
    if strategy == "DEFAULT":
        if r == "Y": return (255,255,0)
        if r == "G": return (0, 255, 0)
        return (0,0,0)


def clamp(v):
    if v < 0:
        return 0
    if v > 255:
        return 255
    return int(v + 0.5)

class RGBRotate(object):
    def __init__(self):
        self.matrix = [[1,0,0],[0,1,0],[0,0,1]]

    def set_hue_rotation(self, degrees):
        cosA = cos(radians(degrees))
        sinA = sin(radians(degrees))
        self.matrix[0][0] = cosA + (1.0 - cosA) / 3.0
        self.matrix[0][1] = 1./3. * (1.0 - cosA) - sqrt(1./3.) * sinA
        self.matrix[0][2] = 1./3. * (1.0 - cosA) + sqrt(1./3.) * sinA
        self.matrix[1][0] = 1./3. * (1.0 - cosA) + sqrt(1./3.) * sinA
        self.matrix[1][1] = cosA + 1./3.*(1.0 - cosA)
        self.matrix[1][2] = 1./3. * (1.0 - cosA) - sqrt(1./3.) * sinA
        self.matrix[2][0] = 1./3. * (1.0 - cosA) - sqrt(1./3.) * sinA
        self.matrix[2][1] = 1./3. * (1.0 - cosA) + sqrt(1./3.) * sinA
        self.matrix[2][2] = cosA + 1./3. * (1.0 - cosA)

    def apply(self, r, g, b):
        rx = r * self.matrix[0][0] + g * self.matrix[0][1] + b * self.matrix[0][2]
        gx = r * self.matrix[1][0] + g * self.matrix[1][1] + b * self.matrix[1][2]
        bx = r * self.matrix[2][0] + g * self.matrix[2][1] + b * self.matrix[2][2]
        return clamp(rx), clamp(gx), clamp(bx)
                

# writeGamutStats()

generateGamutImage("LETTERS")