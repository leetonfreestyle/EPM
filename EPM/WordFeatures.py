#!/usr/bin/python
# encoding=utf-8
from sCharType import sCharType

class WordFeatures(object):
    """docstring for WordFeatures"""
    def __init__(self, filename):
        super(WordFeatures, self).__init__()
        self.filename = filename
        self.features = list()
        self.weights = dict()
        self.lengthOfLine = 0
        self.lengthOfWord = 0
        self.line = None
        self.sCharT = sCharType()
        try:
            with open(self.filename,'r') as pfile:
                self.allLines = [line.strip().decode("utf-8").split(',') for line in pfile.xreadlines()]
        except IOError as e:
            print e

    def getTrainFeatures(self):
        result = []
        for line in self.allLines:
            self.features = []
            self.weights = {}
            self.lengthOfLine = len(line)
            self.lengthOfWord = len(line[0])
            weights = [int(line[1]),float(line[2]),float(line[3]),float(line[4])]
            self.line = line
            self.parseLine()
            result.append((weights,self.features))
        return result

    def getFeatures(self):
        for line in self.allLines:
            self.lengthOfLine = len(line)
            self.lengthOfWord = len(line[0])
            self.line = line
            self.parseLine()
        return self.features,self.weights
    
    def parseLine(self):
        if self.lengthOfLine != 5 or self.lengthOfWord > 3:
            return False
        self.firstChar()
        self.lastChar()

    def firstChar(self):
        C = self.line[0][0]
        C1 = self.line[0][1]
        e = "C,C1:%s,%s:B" % (C, C1)
        self.features.append(e)
        self.weights[e] = (int(self.line[1]),float(self.line[2]),
            float(self.line[3]),float(self.line[4]))
        if self.lengthOfWord == 3:
            e = "C,C2:%s,%s:B" % (C,self.line[0][-1])
            self.features.append(e)
            self.weights[e] = (int(self.line[1]),float(self.line[2]),
                float(self.line[3]),float(self.line[4]))
    def lastChar(self):
        C_1 = self.line[0][-2]
        C = self.line[0][-1]
        e = "C_1,C:%s,%s:E"%(C_1, C)
        self.features.append(e)
        self.weights[e] = (int(self.line[1]),float(self.line[2]),
            float(self.line[3]),float(self.line[4]))
        if self.lengthOfWord == 3:
            e = "C_2,C:%s,%s:E" % (self.line[0][0],C)
            self.features.append(e)
            self.weights[e] = (int(self.line[1]),float(self.line[2]),
                float(self.line[3]),float(self.line[4]))

def main():
    wf = WordFeatures("pseudoWords_ctb.txt")
    result = wf.getTrainFeatures()
    print len(result)
    print result[:5]
    print result[-5:]
    wf = WordFeatures("pseudoWords.txt")
    features,weights = wf.getFeatures()
    print len(features),len(weights)
    print features[:5]
    print features[-5:]

if __name__ == '__main__':
    main()
