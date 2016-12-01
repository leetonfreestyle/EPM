# -*- coding:utf-8 -*-
try:
    import cPickle as pickle
except ImportError:
    import pickle
import gzip
import traceback

class Indexer:

    def __init__(self, indextype):
        """
        :param indextype: type of Indexer,dict(indextype,int)
        :return:
        """
        self.indextype = indextype
        self.totalcount = 0 #instead of total
        self.ObjectToIndex = dict() #(indextype,int)
        self.locked = 0  #a bool value

    def keySet(self):
        return self.ObjectToIndex.keys()

    def total(self):
        return self.totalcount

    def lock(self):
        self.locked = 1

    def unlock(self):
        self.locked = 0

    def hasSeen(self, key):
        return self.ObjectToIndex.has_key(key)

    def size(self):
        return len(self.ObjectToIndex)

    def add(self, obj):
        index = -1
        if self.ObjectToIndex.has_key(obj):
            index = self.ObjectToIndex.get(obj)
        if index <= -1:
            if self.locked:
                raise NameError,'no object: %s' % obj
            index = self.totalcount
            self.totalcount += 1
            self.ObjectToIndex[obj] = index
        return index

    def indexOf(self, obj):
        return self.ObjectToIndex.get(obj)

    def clear(self):
        self.totalcount = 0
        self.ObjectToIndex.clear()
        self.locked = 0

    def toString(self):
        sb = ''
        for key in self.ObjectToIndex.keys():
            sb = '%s%s ' % (sb, str(key))
        return str(sb)

    def serialize(self, filename):
        try:
            if filename.endswith('gz'):
                f = gzip.open(filename, 'wb')
            else:
                f = open(filename, 'wb')
            pickle.dump(self, f)
            f.close()
        except Exception,e:
            traceback.print_exc()

    def deserialize(self,filename):
        model = Indexer('string')
        try:
            if filename.endswith('gz'):
                f = gzip.open(filename,'rb')
            else:
                f = open(filename,'rb')
            model = pickle.load(f)
            f.close()
            return model
        except Exception,e:
            traceback.print_exc()
