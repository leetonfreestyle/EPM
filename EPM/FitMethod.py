# coding: utf-8
import sys
sys.path.append("../perceptronTrain")
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("path")
args = parser.parse_args()
print args
# In[17]:

import cPickle
from Sentence import Sentence
from SentenceReader import SentenceReader
from Segment import Segment
from HandCraftedModel import HandCraftedModel
from WordFeatures import WordFeatures

modelPath = "../model/8.model.gz"
print "model loading..."
with open(modelPath, 'r') as file_in:
    tagger = cPickle.load(file_in)
print "Done"


# In[18]:

import numpy as np
print "old word features extracting..."
wf = WordFeatures("../newWordDetection/pseudoWords_ctb.txt")
resultList = wf.getTrainFeatures()
print len(resultList)
trainFeatTemp=[]
trainIdTemp=[]
for (weights,features) in resultList:
    trainFeatTemp.append(weights)
    parameterTotal = []
    for feature in features:
        i = tagger.model.featureIndexer.indexOf(feature)
        if i is not None:
            parameterTotal.append(tagger.model.parameter[i])
    if len(parameterTotal) != 0:
        trainIdTemp.append(sum(parameterTotal) / float(len(parameterTotal)))
    else:
        trainIdTemp.append(0.0)
train_feat=np.array(trainFeatTemp)
train_id=np.array(trainIdTemp)
print train_feat.shape,train_id.shape
print "new word features extracting..."
wf = WordFeatures("../newWordDetection/pseudoWords.txt")
features,weights = wf.getFeatures()
print len(features),len(weights)
testFeatTemp=[]
for feature in features:
    testFeatTemp.append([weights[feature][0],weights[feature][1],weights[feature][2],weights[feature][3]])
test_feat=np.array(testFeatTemp)
print test_feat.shape


# In[19]:

import time
startTime = time.time()
print "segmentation features weight model training..."
# from sklearn.ensemble import GradientBoostingRegressor
# gbdt=GradientBoostingRegressor(
#   loss='ls'
# , learning_rate=0.1
# , n_estimators=100
# , subsample=1
# , min_samples_split=2
# , min_samples_leaf=1
# , max_depth=3
# , init=None
# , random_state=None
# , max_features=None
# , alpha=0.9
# , verbose=0
# , max_leaf_nodes=None
# , warm_start=False
# )
# gbdt.fit(train_feat,train_id)
# test_feat=np.array(testFeatTemp)
# print test_feat.shape
# pred=gbdt.predict(test_feat)
# print pred

from sklearn.svm import SVR
clf = SVR()
clf.fit(train_feat,train_id)
print "Done"
print test_feat.shape
print "predict segmentation features in target domain corpus..."
pred=clf.predict(test_feat)
print pred
print "total time is %.2f s." % (time.time() - startTime)


# In[22]:
print "add segmentation features of target domain to perceptron model..."
print max(pred),min(pred),len(features),len(pred)
tagger.quiet = True
attachment = []
tagger.model.featureIndexer.unlock()
for i,feature in enumerate(features):
    if tagger.model.featureIndexer.add(feature):
        attachment.append(pred[i])
tagger.model.featureIndexer.lock()

tagger.model.parameter.extend(attachment)
print "add parameters : %d" % len(attachment)

testSet = SentenceReader(args.path)
print("Evaluating ...")
accuracy = tagger.evaluate(testSet, numThreads=8,
                            numPerTheads=1)
print("The accuracy is %f"%accuracy)
testSet.close()

