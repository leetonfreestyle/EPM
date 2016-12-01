# -*- coding: utf-8 -*-
from FeatureVector import FeatureVector
from sCharType import sCharType

class SegState(object):

    sCharT = sCharType()

    def __init__(self,sentence):
        self.sentence = sentence
        self.score = 0
        self.step = 0
        self.isGold = True
        self.prevState = None
        self.action = None
        self.localFV = None
        self.fillPrimitiveUnits()

    def fillPrimitiveUnits(self):
        self.C = self.C_1 = self.C_2 = self.C1 = self.C2 = '#'
        self.tagprev = self.tagprevprev = "#"
        if self.step - 1 >= 0 and self.step - 1 < self.sentence.size():
            self.C_1 = self.sentence.getChar(self.step-1)
            self.tagprev = self.getAction()
            if self.step-2 >= 0 and self.step-2 < self.sentence.size():
                self.C_2 = self.sentence.getChar(self.step-2)
                self.tagprevprev = self.prevState.getAction()
        if self.step < self.sentence.size():
            self.C = self.sentence.getChar(self.step)
        if self.sentence.size() > self.step + 1:
            self.C1 = self.sentence.getChar(self.step+1)
            if self.sentence.size() > self.step +2:
                self.C2 = self.sentence.getChar(self.step+2)


    def compareTo(self,s):
        if self.score > s.getScore():
            return 1
        if self.score < s.getScore():
            return -1
        return 0

    def transit(self,action,isGold,model):
        state = SegState(self.sentence)
        state.step = self.step + 1
        state.isGold = self.isGold and isGold
        state.prevState = self;
        state.action = action;
        state.fillPrimitiveUnits();
        if model != None :
            stringFeatures = self.getFeatures(action);
            state.localFV = model.getFeatureVector(stringFeatures);
            state.score = self.score + model.score(state.localFV);
        return state

    def isTerminated(self):
        return self.sentence.size() == self.step


    def getAction(self):
        return self.action

    def getStep(self):
        return self.step

    def getActionSequence(self):
        outcomes = []
        curState = self
        while curState.action != None:
            outcomes.append(curState.action)
            curState = curState.prevState
        outcomes.reverse()
        return outcomes

    def getFeatures(self,action):
        unlabeledFeatures = self.getUnlabeledFeatures()
        features = [feature+':'+action for feature in unlabeledFeatures]
        return features

    def getUnlabeledFeatures(self):
        e =[
            #uni-gram
            "C_2:%s"%self.C_2,
            "C_1:%s"%self.C_1,
            "C:%s"%self.C,
            "C1:%s"%self.C1,
            "C2:%s"%self.C2,
            #bi-gram
            "C_2,C_1:%s,%s"%(self.C_2, self.C_1),
            "C_1,C:%s,%s"%(self.C_1, self.C),
            "C,C1:%s,%s"%(self.C, self.C1),
            "C1,C2:%s,%s"%(self.C1, self.C2),
            # skip-gram
            "C_2,C:%s,%s"%(self.C_2, self.C), 
            "C_1,C1:%s,%s"%(self.C_1, self.C1), 
            "C,C2:%s,%s"%(self.C, self.C2), 

            # #Open features
            # "Pu(C0):%s"%self.sCharT.isPunc(self.C), #Pu(C0)
            
            # #T(-1)T(0)T(1)
            # "EnChar:%s,%s,%s"%(self.sCharT.isEnChar(self.C_1),
            # self.sCharT.isEnChar(self.C), self.sCharT.isEnChar(self.C1)),
            # # "EnChar:%s,%s"%(self.sCharT.isEnChar(self.C), self.sCharT.isEnChar(self.C1)),
            
            # #CT(-1)CT(0)CT(1)
            # "ChNum:%s,%s,%s"%(self.sCharT.isChineseNum(self.C_1),
            # self.sCharT.isChineseNum(self.C), self.sCharT.isChineseNum(self.C1)),
            # # "ChNum:%s,%s"%(self.sCharT.isChineseNum(self.C), self.sCharT.isChineseNum(self.C1)),

            # #N(-1)N(0)N(1)
            # "Num:%s,%s,%s"%(self.sCharT.isNum(self.C_1),
            # self.sCharT.isNum(self.C), self.sCharT.isNum(self.C1)),
            # # "Num:%s,%s"%(self.sCharT.isNum(self.C), self.sCharT.isNum(self.C1)),

            # #D(-1)D(0)D(1)
            # "Date:%s,%s,%s"%(self.sCharT.isDate(self.C_1),
            # self.sCharT.isDate(self.C), self.sCharT.isDate(self.C1)),
            # # "Date:%s,%s"%(self.sCharT.isDate(self.C), self.sCharT.isDate(self.C1)),

            # "22=%s"%self.tagprev, # tp1
            # "23=%s"%self.tagprevprev, # tp2
            # "24=%s,%s"%(self.tagprevprev, self.tagprev) # tp2tp1
            ]

        return e

    def getGlobalFeatureVector(self):
        globalFV = FeatureVector()
        curState = self
        while curState.localFV != None:
            globalFV.add(curState.localFV)
            curState = curState.prevState
        return globalFV

    def getPrevState(self):
        return self.prevState

    def IsGold(self):
        return self.isGold

    def getScore(self):
        return self.score

    def getFinalResult(self):
        tags = self.getActionSequence()
        wordSeq = list(self.sentence.getChars())
        for index,tag in enumerate(tags):
            if tag == 'S' or tag == 'E':
                wordSeq[index] += ' '
        return u''.join(wordSeq).strip()


if __name__ == "__main__":
    print 'initial..'
    line =u'我 是 傻逼 ， 这 你 也 信 ？'
    from Sentence import Sentence
    s = Sentence(line)
    print(' '.join(s.characters))
    print(' '.join(s.tags))
    s0 = SegState(s)
    sss = SegState(s)
    print s0.sentence.tags == s.tags
    print 'fillPrimitiveUnits..'
    print s0.C_2,s0.C_1,s0.C,s0.C1,s0.C2
    print 'compareTo..'
    print s0.compareTo(sss) == 0
    print 'getUnlabeledFeatures..'
    print ' '.join(s0.getUnlabeledFeatures())
    print 'getPrevState...'
    print s0.getPrevState()
    print 'isGold..'
    print s0.IsGold()
    print 'getScore..'
    print s0.getScore()
    print 'getFinalResult..'
    s1 = s0.transit('S',True,None)
    print s1.C_2,s1.C_1,s1.C,s1.C1,s1.C2
    print s1.action
    print 'getActionSequence..'
    print s1.getActionSequence()
    print s0.getFeatures('S')
    s2 = s1.transit('S',True,None)
    s3 = s2.transit('S',True,None)
    s4 = s3.transit('S',True,None)
    s5 = s4.transit('S',True,None)
    s6 = s5.transit('S',True,None)
    s7 = s6.transit('S',True,None)
    s8 = s7.transit('S',True,None)
    s9 = s8.transit('S',True,None)
    s10 = s9.transit('S',True,None)
    print 'getFinalResult..'
    print s10.getFinalResult()
    
