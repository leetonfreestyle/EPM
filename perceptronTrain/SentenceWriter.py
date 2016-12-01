# coding=utf-8

class SentenceWriter(object):
    """docstring for SentenceReader"""
    def __init__(self, path):
        super(SentenceWriter, self).__init__()
        self.Path = path
        self.line = None
        self.tags = None
        self.length = 0
        try:
            self.outfile = open(self.Path, "w+")
        except IOError, e:
            print(str(e))
            raise e 

    def writeLine(self,line,tagsList):
        self.length = line.__len__()
        self.tags = ["BSME "] * self.length
        self.line = list(line)
        for tags in tagsList:
            for one in tags:
                if one[0] != 0:
                    self.tags[one[0] - 1] = 'ES '
                self.tags[one[0]] = 'BS '
                if one[1] != self.length - 1:
                    self.tags[one[1] + 1] = 'BS '
                self.tags[one[1]] = 'ES '
        for index,one in enumerate(self.line):
            self.outfile.write('%s_%s'%(one.encode('utf-8'),self.tags[index]))
        self.outfile.write('\n')
        self.outfile.flush()

    def close(self):
        if not self.outfile.closed:
            self.outfile.close()
