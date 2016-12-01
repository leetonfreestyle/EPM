# coding=utf-8

import codecs
from Sentence import Sentence

class SentenceReader(object):
    """docstring for SentenceReader"""
    def __init__(self, path, isTest=False):
        super(SentenceReader, self).__init__()
        self.inPath = path
        self.line = ''
        self.isTest = isTest
        try:
            self.inFile = codecs.open(self.inPath, "r", "utf-8")
        except IOError, e:
            print(str(e))
            raise e 

    def hasNext(self):
        try:
            if self.line == '':
                self.line = self.inFile.readline()
        except IOError, e:
            print(str(e))
            raise e 
        return (self.line != '')

    def next(self):
        if not self.isTest:
            sent = Sentence(self.line)
        else:
            sent = Sentence(self.line, True)
        self.line = ''
        return sent

    def close(self):
        if not self.inFile.closed:
            self.inFile.close()


    def reset(self):
        self.close()
        try:
            self.inFile = codecs.open(self.inPath, "r", "utf-8")
        except IOError, e:
            print(str(e))
            raise e

    def getPath(self):
        return self.inPath



