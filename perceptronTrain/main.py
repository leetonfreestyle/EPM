# coding=utf-8

import argparse
import cPickle
from Sentence import Sentence
from SentenceReader import SentenceReader
from Segment import Segment
from HandCraftedModel import HandCraftedModel

class CmdLineParser(object):
    """program arguements"""

    def __init__(self):
        # (name = "-train")
        self.trainPath = "../data/train.seg"
        # (name = "-dev")
        self.devPath = "../data/dev.seg" 
        # (name = "-test")
        self.testPath = "../data/test.seg"
        # (name = "-mode")
        self.mode = "train"        # train, test, eval
        # (name = "-iter")
        self.iterations = 20  
        # (name = "-beam")
        self.beamSize = 10  
        # (name = "-kMIRA")
        self.kMIRA = 5
        # (name = "-out")
        self.outputPath = "../data/pred.seg"
        # (name = "-model")
        self.modelPath = "../model/8.model.gz"
        # (name = "-numThreads")
        self.numThreads = 8
        # (name = "-numPerTheads")
        self.numPerTheads = 1
        # (name = "-featureThreshold")
        self.featureThreshold = 0
        # (name = "-evaluateWhileTraining")
        self.evaluateWhileTraining = True
        # (name = "-trainType")
        self.trainType = "standard"   # trainType: test, standard, early, max,MIRA

if __name__ == "__main__":
    options = CmdLineParser()
    parser = argparse.ArgumentParser()
    parser.add_argument("-train", dest="trainPath")
    parser.add_argument("-dev", dest="devPath")
    parser.add_argument("-test", dest="testPath")
    parser.add_argument("-mode", dest="mode")
    parser.add_argument("-iter", dest="iterations",type=int)
    parser.add_argument("-beam", dest="beamSize",type=int)
    parser.add_argument("-kMIRA", dest="kMIRA",type=int)
    parser.add_argument("-out", dest="outputPath")
    parser.add_argument("-model", dest="modelPath")
    parser.add_argument("-numThreads", dest="numThreads",type=int)
    parser.add_argument("-numPerTheads", dest="numPerTheads",type=int)
    parser.add_argument("-featureThreshold", dest="featureThreshold",type=float)
    parser.add_argument("-evaluateWhileTraining", dest="evaluateWhileTraining")
    parser.add_argument("-trainType", dest="trainType")

    parser.parse_args(namespace=options)
    print vars(options)

    if options.trainType not in ["test", "standard", "early", "max", "MIRA"]:
        raise Exception("Unsupported train type.")

    if options.mode == "train":
        # 建立训练集输入流
        trainSet = SentenceReader(options.trainPath)
        devSet = SentenceReader(options.devPath)
        tagger = Segment(model=HandCraftedModel(), beamSize=options.beamSize,
                        kMIRA=options.kMIRA)
        print("Model initializing ... ")
        tagger.initialize(trainSet, numThreads=options.numThreads,
                          numPerTheads=options.numPerTheads,
                          threshold=options.featureThreshold)
        print("Parameter training ...")
        tagger.trainForStructureLinearModel(trainSet, devSet,
                        Iter=options.iterations,
                        miniSize=options.numPerTheads,
                        numThreads=options.numThreads,
                        trainType=options.trainType,
                    evaluateWhileTraining=options.evaluateWhileTraining)
        trainSet.close()
        devSet.close()
        print("Parameter serializing to %s"%options.modelPath)
        with open(options.modelPath, 'w') as file_out:
            cPickle.dump(tagger, file_out)
        print("Done")


    elif options.mode == "test":
        print("Loading model ... ")
        with open(options.modelPath, 'r') as file_in:
            tagger = cPickle.load(file_in)
        print("Done")

        print("Decoding ...")
        tagger.quiet = True
        testSet = SentenceReader(options.testPath, True)
        tagger.decodeParalle(testSet, outpath=options.outputPath,
                            numThreads=options.numThreads,
                            numPerTheads=options.numPerTheads)
        testSet.close()
    elif options.mode == "display":
        print("Loading model ... ")
        with open(options.modelPath, 'r') as file_in:
            tagger = cPickle.load(file_in)
        print("Done")
        while True:
            raw_sent = raw_input("请输入待分词的字符串：")
            if raw_sent.__len__() == 0:
                break
            sent = Sentence(raw_sent.decode('utf-8'))
            states = tagger.decodeBeamSearch(sent, "test")
            print states[1].getFinalResult().encode('utf-8')
        
    elif options.mode == "eval":
        print("Loading model ... ")
        with open(options.modelPath, 'r') as file_in:
            tagger = cPickle.load(file_in)
        print("Done")

        tagger.quiet = False
        testSet = SentenceReader(options.testPath)
        print("Evaluating ...")
        accuracy = tagger.evaluate(testSet, numThreads=options.numThreads,
                                    numPerTheads=options.numPerTheads)
        print("The accuracy is %f"%accuracy)
        testSet.close()

    else:
        print("Unsupport mode!!!")
    print("DONE!")
