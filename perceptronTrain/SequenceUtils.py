# coding=utf-8

class SequenceUtils(object):
    """docstring for SequenceUtils"""

    @staticmethod
    def labeledSeq2WordSeq(sentence, labels):
        """将标签序列转换为词序列"""
        wordSeq = ""
        for i in xrange(len(sentence)):
            curLabel = labels[i]
            curChar = sentence[i]
            if curLabel == "S" or curLabel == "E":
                wordSeq += curChar + " "
            else:
                wordSeq += curChar
        return wordSeq.strip()

    @staticmethod
    def wordSeq2CharSeq(sentence):
        """将词序列转换为标签序列 """
        charSeq = []
        words = sentence.split()
        for i in xrange(len(words)):
            for k in range(len(words[i])):
                charSeq.append(words[i][k])
        return charSeq

    @staticmethod
    def wordSeq2LabeledSeq(sentence):
        words = sentence.split()
        labels = []
        for i in xrange(len(words)):
            labels.extend(SequenceUtils.tags4word(words[i]))
        return labels

    @staticmethod
    def tags4word(word):
        labels = []
        word_len = len(word)
        if word_len == 1:
            labels.append("S") 
        elif word_len == 2:
            labels.append("B")
            labels.append("E")
        elif word_len == 3:
            labels.append("B")
            labels.append("I")
            labels.append("E")
        else:
            labels.append("B")
            labels.extend(["I"] * (word_len - 2))
            labels.append("E")
        return labels
        

