# encoding=utf-8
import sys
sys.path.append("../perceptronTrain")
from SentenceReader import SentenceReader
from collections import defaultdict
from sCharType import sCharType
import argparse
import codecs
import math
import os

parser = argparse.ArgumentParser()
parser.add_argument("-path",dest="filepath",default="../data/zhuxian_all.seg")
parser.add_argument("-mode",dest="mode")
parser.add_argument("-maxSize",dest="maxSize",default="3",type=int)
parser.add_argument("-dict",dest="fileDict",default=None)
args = parser.parse_args()
print args

class SingleWord(object):
    """docstring for SingleWord"""
    def __init__(self):
        super(SingleWord, self).__init__()
        self.leftdict = defaultdict(int)
        self.rightdict = defaultdict(int)
        self.count = 0
        self.mutualInf = 0.0
    def leftEntropy(self):
        leftTotal = float(sum(self.leftdict.values()))
        leftE = 0.0
        for key,value in self.leftdict.iteritems():
            leftE -= (value / leftTotal) * math.log(value / leftTotal)
        return leftE
    def rightEntropy(self):
        rightTotal = float(sum(self.rightdict.values()))
        rightE = 0.0
        for key,value in self.rightdict.iteritems():
            rightE -= (value / rightTotal) * math.log(value / rightTotal)
        return rightE

class Corpus(object):
    """docstring for Corpus"""
    def __init__(self, filterFile, maxSize, mode):
        super(Corpus, self).__init__()
        self.mode = mode
        self.characters = defaultdict(int)
        self.words = defaultdict(SingleWord)
        self.count = 0
        self.maxSize = maxSize
        self.sCharT = sCharType()
        self.quiet = False
        self.filterSet = set()
        if filterFile is not None:
            with codecs.open(args.fileDict,'r','utf-8') as fd:
                self.filterSet = set([line.split()[0] for line in fd.readlines()])
            print "filterSet size is %d" % len(self.filterSet)
    def process(self,filename):
        if self.mode == "test":
            testSet = SentenceReader(filename,True)
        elif self.mode == "train":
            testSet = SentenceReader(filename,False)
        for candiateLength in xrange(1,self.maxSize + 1):
            if not self.quiet:
                print candiateLength,
            while testSet.hasNext():
                sent = testSet.next()
                WordTemp = ''
                for index in xrange(sent.size() - candiateLength):
                    if candiateLength == 1:
                        self.characters[sent.getChar(index)] += 1
                        self.count += 1
                        continue
                    if sent.getAction(index) is None:
                        pseudoWord = ''
                        for i in xrange(candiateLength):
                            pseudoWord += sent.getChar(index + i)
                    else:
                        label = sent.getAction(index)
                        if label == "S":
                            continue
                        elif label == "I" or label == "B":
                            WordTemp += sent.getChar(index)
                            continue
                        pseudoWord = WordTemp + sent.getChar(index)
                        WordTemp = ''
                        if len(pseudoWord) != candiateLength:
                            continue
                        index -= candiateLength - 1

                    if self.sCharT.containsEnChar(pseudoWord) or self.sCharT.containsNum(pseudoWord) \
                        or self.sCharT.containsPunc(pseudoWord):
                            continue

                    leftChar = rightChar = '#'
                    if index > 0:
                        C = sent.getChar(index - 1)
                        if self.sCharT.isEnChar(C) or self.sCharT.isNum(C) or self.sCharT.isPunc(C):
                            pass
                        else:
                            leftChar = C
                    if index + candiateLength < sent.size():
                        C = sent.getChar(index + candiateLength)
                        if self.sCharT.isEnChar(C) or self.sCharT.isNum(C) or self.sCharT.isPunc(C):
                            pass
                        else:
                            rightChar = C
                    self.words[pseudoWord].count += 1
                    self.words[pseudoWord].leftdict[leftChar] += 1
                    self.words[pseudoWord].rightdict[rightChar] += 1
                    self.calcMutualInf(pseudoWord,candiateLength)
            testSet.reset()

    def calcMutualInf(self, key, length):
        value = self.words[key]
        mutualInf = math.log(value.count / float(self.count - len(key) + 1))
        if length == 2:
            for Ch in key:
                mutualInf -= math.log(self.characters[Ch] / float(self.count))
            value.mutualInf = mutualInf
        if length == 3:
            minusList = []
            if key[:2] in self.words:
                minus = 0.0
                minus += math.log(self.words[key[:2]].count / float(self.count - 2))
                minus += math.log(self.characters[key[-1]] / float(self.count))
                minusList.append(minus)
            if key[-2:] in self.words:
                minus = 0.0
                minus += math.log(self.characters[key[0]] / float(self.count))
                minus += math.log(self.words[key[-2:]].count / float(self.count - 2))
                minusList.append(minus)
            if minusList:
                value.mutualInf = mutualInf - max(minusList)

    def saveWords(self, filename):
        with open(filename,'w+') as outfile:
            for key,value in self.words.iteritems():
                mutualInf = value.mutualInf
                leftE = value.leftEntropy()
                rightE = value.rightEntropy()
                # if value.count < 2\
                if value.count < 2 or leftE <= 0.0 or rightE <= 0.0 or mutualInf <= 0.0\
                or (key in self.filterSet):
                    continue
                print >>outfile,"%s,%d,%f,%f,%f" % (
                    key.encode("utf-8"),value.count,leftE,rightE,mutualInf)

def main():
    cp = Corpus(args.fileDict, args.maxSize, args.mode)
    cp.process(args.filepath)
    print "%s Done!" % args.filepath
    if args.mode == "train":
        cp.saveWords("pseudoWords_ctb.txt")
    else:
        cp.saveWords("pseudoWords.txt")

if __name__ == '__main__':
    main()
