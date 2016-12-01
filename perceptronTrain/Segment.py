#!/usr/bin/env python
# -- coding:utf-8 --

import time
import os
import re
import math
import multiprocessing
import random
import sys
from FeatureVector import FeatureVector
from SentenceReader import SentenceReader
from HandCraftedModel import HandCraftedModel
from DataStructure import *
from QPSolver import QPSolver

class Segment(object):
    '''
        
    '''
    
    def __init__(self, model, beamSize=10, kMIRA=5, isAllTerminated=False):
        ''' Construct Function
        
        Args:
            model: the learning model for segment
            beamSize: int, search beamSize when decode
            kMIRA: int, kMIRA while use MIRA training
            isAllTerminated: bool, true when is all terminated
        Returns:
            None
        Raise:
            None
        
        '''
        self.model = model
        self.beamSize = beamSize
        self.kMIRA = kMIRA
        self.isAllTerminated = isAllTerminated
        self.quiet = False
    
    def initialize(self, trainSet, numThreads, numPerTheads, threshold=0.0):
        ''' Initialize model
            initialize model args and set up feature mapping
        Args:
            trainSet: SentenceReader, train set in the form of SentenceReader
            numThreads: int, num of threads
            numPerTheads: int, num of train samples per thread
            threshold: float, filter the feature counts less than threshold
        Returns:
            None
        Raise:
            None
        
        '''
        self.model.initialize(trainSet, numThreads, numPerTheads, threshold)
    
    def trainForStructureLinearModel(self, trainSet, devSet, Iter, miniSize,
        numThreads, trainType, evaluateWhileTraining):
        ''' Main training function
        Args:
            trainSet: SentenceReader, train set in the form of SentenceReader
            devSet: SentenceReader, dev set in the form of SentenceReader
            Iter: count of iteration
            miniSize: int, num of train samples per thread #useless
            numThreads: int, num of threads
            trainType: str, MIRA or Standard or ...
            evaluateWhileTraining: bool, true for eval while training
        Returns:
            None
        Raise:
            None
        '''
        bestAccuracy = 0.0
        bestIter = 0
        bestParams = None
        
        trainSet.reset()
        sentences = []
        while trainSet.hasNext():
            sentences.append(trainSet.next())
        # number of sentences for each batch
        num = miniSize * numThreads
        # number of batch for each iteration
        batchSize = int(math.ceil(1.0*len(sentences)/num))
        print('Iterate %d times, '
        'the batch size for each iteration is %d'%(Iter, batchSize))
        # build multi-process pool
        resultQueue = multiprocessing.Queue()
        inputQueue = multiprocessing.Queue()
        workerPool = []
        for k in xrange(numThreads):
            worker = multiprocessing.Process(target=self.Task,
                                args=(trainType, inputQueue, resultQueue))
            worker.daemon = True
            workerPool.append(worker)
        for worker in workerPool:
            worker.start()
        # train iteration
        for it in xrange(Iter):
            print "Iteration %d\n Batch:"%it
            startTime = time.time()
            random.shuffle(sentences)
            for i in xrange(batchSize):
                # send model paraments
                for worker in workerPool:
                    inputQueue.put([None, self.model.getParam()])
                # send sentences
                start = num * i
                end = start + num
                end = min(end, len(sentences))
                if i%10 == 0:
                    print i,
                    sys.stdout.flush()
                for k in xrange(start, end):
                    inputQueue.put([sentences[k], None])
                # calculate gradient
                gradient = FeatureVector()
                factor = 1.0/(end - start)
                # parse result
                for k in xrange(end - start):
                    gradient.add(resultQueue.get(), factor)
                avg_upd = 1.0 * Iter * batchSize - (batchSize*(it-1)+(i+1)) + 1
                # avg_upd = 1.0
                self.model.perceptronUpdate(gradient, avg_upd)
            # batch iter end
            print '\nTrain Time: %f'%(time.time() - startTime)
            # evaluate and update model paraments
            if evaluateWhileTraining:
                startTime = time.time()
                averageParams = self.model.averageParam()
                # update model paraments
                for worker in workerPool:
                    inputQueue.put([None, averageParams])
                # evaluate averageParams
                accuracy = self.evaluate(devSet, numThreads, miniSize, inputQueue, resultQueue)
                print 'Dev Acc is %f'%accuracy
                if accuracy >= bestAccuracy:
                    bestIter = it
                    bestAccuracy = accuracy
                    bestParams = averageParams
                print 'Eval time: %f'%(time.time() - startTime)
        # train iter end
        for k in xrange(numThreads):
            inputQueue.put(None)
        for worker in workerPool:
            worker.join()
        if bestParams:
            self.model.setParam(bestParams)
        print 'The best iteration is %d'%bestIter

    def Task(self, trainType, inputQueue, resultQueue):
        ''' parallelising function
        '''
        while 1:
            inputOne = inputQueue.get()
            # terminal signal
            if inputOne is None:
                break
            # update model paraments
            if inputOne[0] is None:
                self.model.setParam(inputOne[1])
                continue
            # train decode
            if inputOne[1] is None:
                states = self.decodeBeamSearch(inputOne[0], trainType)
            # evaluate decode
            else:
                states = self.decodeBeamSearch(inputOne[1], "test")
                resultQueue.put((inputOne[0], states[1].getFinalResult()))
                continue
            gradient = FeatureVector()
            if trainType == 'MIRA':
                K = 0 # number of candidates
                for kk in xrange(1, len(states)):
                    if states[kk] != None:
                        K += 1
                    else:
                        break
                b = [0.0 for kk in xrange(K)]
                lam_dist = [0.0 for kk in xrange(K)]
                dist = [FeatureVector() for kk in xrange(K)]

                goldFV = states[0].getGlobalFeatureVector()
                for kk in xrange(K):
                    # the score difference between 
                    # gold-standard tree and auto tree
                    lam_dist[kk] = (states[0].getScore()
                                - states[kk+1].getScore())
                    b[kk] = self.loss(states[0], states[kk+1])
                    b[kk] -= lam_dist[kk]
                    #the FV difference
                    dist[kk] = FeatureVector.getDistVector(goldFV,
                                states[kk+1].getGlobalFeatureVector())

                alpha = QPSolver.hildreth(dist, b)
                for kk in xrange(K):
                    gradient.add(dist[kk], alpha[kk])
            else:
                if not states[1].IsGold():
                    gradient.add(states[0].getGlobalFeatureVector())
                    gradient.subtract(states[1].getGlobalFeatureVector())
            resultQueue.put(gradient)
    
    def decodeBeamSearch(self,sent,trainType):
        '''解码函数
        Args:
            sent:类型为Sentence
            trainType:提供多种模式，有test, standard, early, max,MIRA
        Return:
            一个SegState对象数组，通常为两个元素，MIRA模式下返回多个元素，第一个元素为最佳解，其余为次优解
        Raise:
            None
        '''
        isTrainMode = False
        goldActions = [] # <str>
        goldState = None
        goldActionPosition = 0
        results = [None] * 2 # <SegState>
        agenda = [] # <SegState>
        heap = MaxHeap(self.beamSize) # <SegState>
        scoreBoard = [float("-inf")] * self.beamSize # <float>
        # for gold-standard state
        if trainType != "test":
            isTrainMode = True
            goldActions = sent.getAllActions()
            goldState = sent.buildInitState()
        # for max-violation
        if trainType == "max":
            goldPartialStates = [] # <SegState>
            predPartialStates = [] # <SegState>
            maxViolationPosition = -1
            maxMargin = float("-inf")
        if trainType == "MIRA":
            results = [None] * (self.kMIRA + 1)
        agenda.append(sent.buildInitState())
        circle = 0
        while True:
            circle += 1
            # ==========get gold action for the current step====================
            goldAction = ""
            lengthOfGoldActions = goldActions.__len__()
            if lengthOfGoldActions != 0:
                if goldActionPosition < lengthOfGoldActions:
                    goldAction = goldActions[goldActionPosition]
                goldActionPosition += 1
            if goldAction != "":
                goldState = goldState.transit(goldAction, True, self.model)
            # ==========one step transit for each state==============
            scoreBoard = [float("-inf")] * self.beamSize
            heap.clear()
            # build new state
            for state in agenda:
                if state.isTerminated():
                    heap.add(state)
                    continue
                unlabeledFeatures = state.getUnlabeledFeatures()
                actions = self.getAllValidActions(state,isTrainMode)
                # for every action, caculate its score and add into scoreBoard
                for action in actions:
                    labeledFeatures = ['%s:%s'%(feature, action) for feature in unlabeledFeatures]
                    localFV = self.model.getFeatureVector(labeledFeatures)
                    score = self.model.score(localFV) + state.getScore()
                    if score < min(scoreBoard):
                        continue
                    if goldAction == "":
                        newState = state.transit(action, True, None)
                    else:
                        newState = state.transit(action,goldAction == action, None)
                    newState.localFV = localFV
                    newState.score = score
                    heap.add(newState)
                    scoreBoard[-1] = newState.getScore()
                    scoreBoard.sort(reverse=True)
            # keep k-best state
            agenda = []
            if heap.isEmpty():
                print "Parsing Fault."
                exit(-1)
            else:
                while not heap.isEmpty() and (agenda.__len__() < self.beamSize):
                    agenda.append(heap.extract())
            # ==========================
            if trainType == "early":
                containedGoldState = None
                for state in agenda:
                    if state.IsGold():
                        containedGoldState = state
                        break
                if containedGoldState == None:
                    results[0] = goldState
                    results[1] = agenda[0]
                    return results
            else:
                if trainType == "max":
                    curMargin = agenda[0].getScore() - goldState.getScore()
                    if curMargin > maxMargin:
                        maxMargin = curMargin
                        maxViolationPosition += 1
                        goldPartialStates.append(goldState)
                        predPartialStates.append(agenda[0])
            # ===========check terminated===================
            if self.isAllTerminated:# terminated when all state in the beam reach terminal state
                allterm = True
                for state in agenda:
                    if not state.isTerminated():
                        allterm = False
                if allterm:
                    break
            else:# terminated when the best state reach the terminal state
                if agenda.__len__() != 0 and agenda[0].isTerminated():
                    break
        if trainType == "max":
            results[0] = goldPartialStates[maxViolationPosition]
            results[1] = predPartialStates[maxViolationPosition]
        elif trainType == "MIRA":
            results[0] = goldState
            for index,one in enumerate(agenda):
                if index + 1 <= self.kMIRA:
                    results[index + 1] = one
        else:
            results[0] = goldState
            if agenda.__len__() != 0:
                results[1] = agenda[0]
        return results

    def decodeParalle(self,testSet,outpath,numThreads,numPerTheads,inputQueue=None,resultQueue=None):
        '''多线程解码函数
        Args:
            testSet:测试数据集
            outpath:解码结果的保存路径
            numThreads:总线程数
            numPerTheads:每个线程中的任务数
        Return:
            None
        Raise:
            None
        '''
        startTime = time.time()
        batch = 0
        isNewPool = False
        testSet.reset()
        if inputQueue is None or resultQueue is None:
            resultQueue = multiprocessing.Queue()
            inputQueue = multiprocessing.Queue()
            parserPool = []
            for k in xrange(numThreads):
                parser = multiprocessing.Process(target=self.Task,
                                                args=("test",inputQueue,resultQueue))
                parser.daemon = True
                parserPool.append(parser)
            for parser in parserPool:
                parser.start()
            isNewPool = True
        with open(outpath,'w') as outFile:
            while testSet.hasNext():
                if not self.quiet:
                    print str(batch) + " ",
                batch += 1
                sentence_idx = 0
                for i in xrange(numThreads * numPerTheads):
                    if testSet.hasNext():
                        inputQueue.put((sentence_idx, testSet.next()))
                        sentence_idx += 1
                # fetch the results
                results = []
                for i in xrange(sentence_idx):
                    results.append(resultQueue.get())
                results.sort(key=lambda x:x[0]) #sort by sentence idx
                # write file
                for idx, one in results:
                    outFile.write(one.encode('utf-8') + '\n')
        if isNewPool:
            for k in xrange(numThreads):
                inputQueue.put(None)
            for parser in parserPool:
                parser.join()
        if not self.quiet:
            print "Time: %f"%(time.time() - startTime)

    def getAllValidActions(self, state, isTrainMode):
        ''' get all valid tag
        Args:
            state: State, the current state
            isTrainMode: bool, isTrainMode
        Returns:
            valideActions: list, contains valid tags
        Raise:
            None
        '''
        if isTrainMode:
            return self.model.allPossibleActions()
        else:
            preTag = '#'
            if state.getAction():
                preTag = state.getAction()
            return self._vsMap[preTag]
    # validSequence map, used in getAllValidActions()
    _vsMap = {
        '#':['B', 'S'],
        'B':['I', 'E'],
        'I':['I', 'E'],
        'E':['B', 'S'],
        'S':['S', 'B']
    }
    # change to staticmethod maybe better
    def loss(self, goldState, predState):
        ''' Loss function for MIRA training
        '''
        if goldState.getStep() != predState.getStep():
            raise RuntimeError( "Undefined POSTagger.loss()")
        loss_f = 0.0
        while goldState.getAction() and predState.getAction():
            if goldState.getAction() != predState.getAction():
                loss_f += 1.0
            goldState = goldState.getPrevState()
            predState = predState.getPrevState()
        return loss_f
    
    def evaluate(self, devSet, numThreads, numPerTheads, inputQueue=None, resultQueue=None):
        ''' evaluate the F_score in the devSet
        '''
        tmpPath = './tmp.seg.%d.%d'%(numThreads, int(time.time()))
        self.decodeParalle(devSet, tmpPath, numThreads, numPerTheads, inputQueue, resultQueue)
        F_score = self.eval(tmpPath, devSet.getPath())
        if os.access(tmpPath, os.F_OK):
            os.remove(tmpPath)
        return F_score
    
    @staticmethod
    def eval(testPath, goldPath):
        ''' evaluate accuracy and return F1 with the given testSet
        '''
        goldReader = SentenceReader(goldPath)
        predReader = SentenceReader(testPath)
        total = 0.0
        corr = 0.0
        while goldReader.hasNext() and predReader.hasNext():
            goldSent = goldReader.next()
            predSent = predReader.next()
            total += goldSent.size()
            for i in xrange(goldSent.size()):
                if goldSent.getAction(i) == predSent.getAction(i):
                    corr += 1.0
        print 'ACC is %f'%(corr/total)
        
        goldTotal = 0.0
        predTotal = 0.0
        correct = 0.0
        #TODO io handle
        with open(testPath, 'r') as file_in:
            predIn = file_in.readlines()
        with open(goldPath, 'r') as file_in:
            goldIn = file_in.readlines()
        
        for i in xrange(len(predIn)):
            goldSet = Segment._collect(goldIn[i].strip())
            goldTotal += len(goldSet)
            predSet = Segment._collect(predIn[i].strip())
            predTotal += len(predSet)
            correct += len(predSet & goldSet)
        
        precision = correct / predTotal
        recall = correct / goldTotal
        if precision == 0.0 or recall == 0.0:
            F1 = 0.0
        else:
            F1 = 2 * precision * recall / (precision + recall)
        print 'P=%.2f\tR=%.2f\tF=%.2f'%(precision*100, recall*100, F1*100)
        return F1
    
    @staticmethod
    def _collect(line):
        ''' inner function for eval to collect words
        '''
        wordSet = set()
        words = re.split(r'\s+', line)
        start = 0
        for word in words:
            end = start + len(word)
            wordSet.add((word, start, end))
            start = end
        return wordSet

if __name__ == "__main__":
    import sys
    train_mode = sys.argv[1]
    print train_mode, type(train_mode)
    from SentenceReader import SentenceReader
    trainSet = SentenceReader('../train.little.seg')
    devSet = SentenceReader('../dev.little.seg')
    #trainSet = SentenceReader('../short_train.seg')
    #devSet = SentenceReader('../short_dev.seg')
    #trainSet = SentenceReader('../train.seg')
    #devSet = SentenceReader('../dev.seg')
    seg = Segment(model = HandCraftedModel())
    NUM_PROC = 8
    seg.initialize(trainSet, numThreads=NUM_PROC, numPerTheads=NUM_PROC, threshold=0.0)
    seg.trainForStructureLinearModel(trainSet, devSet, 20, NUM_PROC, NUM_PROC, 
                                    train_mode, True);
    trainSet.close()
    devSet.close()
    exit()
    print seg._validSequence(preTag='B', tag='I', isTrainMode=False)
    print seg._validSequence(preTag='B', tag='B', isTrainMode=False)
    print seg._collect('123 456')
    print seg.eval('../data/ctb8_seg/chtb_3117.bn.seg.bps', '../data/ctb8_seg/chtb_3117.bn.seg.bps')
    from SegState import SegState
    from Sentence import Sentence
    line =u'我 是 哈哈哈 ， 这 你 也 信 ？'
    sen = Sentence(line)
