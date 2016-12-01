# coding=utf-8

from SequenceUtils import SequenceUtils
from SegState import SegState

class Sentence(object):
    """docstring for Sentence"""

    serialVersionUID = 1L
    tags = None

    def __init__(self, line, isTest=False):
        super(Sentence, self).__init__()
        self.characters = SequenceUtils.wordSeq2CharSeq(line)
        if not isTest:
            self.tags = SequenceUtils.wordSeq2LabeledSeq(line)

    def getAction(self, i):
        return None if self.tags is None else self.tags[i]

    def getAllActions(self):
        return self.tags

    def buildInitState(self):
        return SegState(self)

    def size(self):
        return len(self.characters)

    def getChar(self, i):
        return self.characters[i]

    def getChars(self):
        return self.characters

    def getResult(self):
        return SequenceUtils.labeledSeq2WordSeq(self.characters, self.tags)


