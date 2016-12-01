# coding:utf-8
from __future__ import division
from FeatureVector import FeatureVector
from Indexer import Indexer
import math
import time
from collections import Counter
import multiprocessing

class HandCraftedModel:

    def __init__(self):
        self.parameter = list()
        self.total = list()
        self.paramCount = 0
        self.type = 'string'
        self.actionIndexer = Indexer(self.type)
        self.featureIndexer = Indexer(self.type)

    def initialize(self, trainSet, numThreads, numPerTheads, threshold):
        """
        :param trainSet:SentenceReader
        :param numThreads:int
        :param numPerTheads:int
        :param threshold:double
        :return:
        """
        trainSet.reset()
        startTime = time.time()
        featureCounter = Counter()
        # build process pool
        inputQueue = multiprocessing.Queue()
        resultQueue = multiprocessing.Queue()
        workerPool = []
        for k in xrange(numThreads):
            worker = multiprocessing.Process(target=self.loop,
                                args=(inputQueue, resultQueue))
            worker.daemon = True
            workerPool.append(worker)

        for worker in workerPool:
            worker.start()
        # batch iteration
        batch = 0
        while trainSet.hasNext():
            print '%d ' % batch,
            batch = batch + 1
            senCount = 0
            while senCount < numThreads*numPerTheads and trainSet.hasNext():
                sent = trainSet.next() # Sentence sent
                actions = sent.getAllActions()
                for action in actions:
                    self.actionIndexer.add(action)
                inputQueue.put(sent)
                senCount += 1

            None_count = 0
            while 1:
                feature = resultQueue.get()
                if feature is not None:
                    featureCounter[feature] += 1
                else:
                    None_count += 1
                    if None_count == senCount:
                        break
        # send ternimal signal
        for worker in workerPool:
            inputQueue.put(None)
        for worker in workerPool:
            worker.join()
        # create feature indexer
        self.actionIndexer.lock()
        print 'Pruning...'
        featureCount = self.featureIndexer.size()
        self.featureIndexer.unlock()
        # self.featureIndexer = Indexer('string')
        for feature in featureCounter:
            count = featureCounter[feature]
            if count > threshold:
                self.featureIndexer.add(feature)
        self.featureIndexer.lock()
        print 'DONE!'
        print 'Feature Size is %s,action set is %s %s' % (self.featureIndexer.size(),
                         self.actionIndexer.size(), str(self.actionIndexer.keySet()))
        # paraments
        self.paramCount = 0
        self.parameter.extend([0.0 for i in range(self.featureIndexer.size() - featureCount)])
        self.total.extend([0.0 for j in range(self.featureIndexer.size() - featureCount)])
        endTime = time.time()
        print 'Time:%f' % (endTime-startTime)

    def loop(self, inputQueue, resultQueue):
        """
        function：线程中运行的程序
        """
        while 1:
            sent = inputQueue.get()
            if sent is None:
                break
            state = sent.buildInitState()
            actions = sent.getAllActions()
            for action in actions:
                features = state.getFeatures(action)
                for feature in features:
                    resultQueue.put(feature)
                state = state.transit(action, True, None)
            resultQueue.put(None)

    def getFeatureVector(self, features_list):
        """
        :param features_list:list(string)
        :return:FeatureVector
        """
        fv = FeatureVector()
        for feature in features_list:
            if feature in self.featureIndexer.ObjectToIndex:
                fv.add(self.featureIndexer.ObjectToIndex[feature])
        return fv

    def getParam(self):
        return self.parameter

    def setParam(self,params_list):
        self.parameter = params_list

    def averageParam(self):
        return [one/self.paramCount for one in self.total]

    def perceptronUpdate(self, gradients, avg_ipd):
        """
        :param gradients:FeatureVector
        :param avg_ipd: double
        :return:
        """
        self.paramCount += 1
        for key in gradients.features:
            d = gradients.features[key]
            self.parameter[key] += d
            self.total[key] += avg_ipd * d

    def buildGradients(self):
        raise AttributeError, "Undefined HandCraftedModel.buildGradients()"

    def pointwiseTraining(self):
        raise AttributeError, "Undefined HandCraftedModel.buildGradients()"

    def updateWeights(self):
        raise AttributeError, "Undefined HandCraftedModel.buildGradients()"

    def score(self,fv):
        """
        :param fv: FeatureVector
        :return:
        """
        sum = 0
        for key, value in fv.features.iteritems():
            sum += value * self.parameter[key]
        return sum

    def allPossibleActions(self):
        return self.actionIndexer.keySet()

    def toString(self):
        sb = 'parameter: '
        for i in xrange(len(self.parameter)):
            if not math.isnan(self.parameter[i]):
                sb = '%s%d ' %(sb,i)
        sb = '%s\ntotal: ' %sb
        for j in xrange(len(self.total)):
            if not math.isnan(self.total[j]):
                sb = '%s%d ' %(sb,j)
        sb = '%s\nparamCount: %d' %(sb,self.paramCount)
        return sb

if __name__ == '__main__':
    test = HandCraftedModel()
    test.updateWeights()
