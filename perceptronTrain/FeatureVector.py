import math
class FeatureVector(object):


    def __init__(self,line=''):
        self.features = {}
        self.__FeatureVector(line)
        return

    def __FeatureVector(self,line):
        if line != '':
            items = line.split()
            for item in items:
                try:
                    self.__add(int(item),1.0)
                except ValueError:
                    print "FeatureVector initialize failed"
                    print "ERROR---%s cannot be convert to int!!!"%item
        return
        
    def __add(self,key,value):
        count = self.features.get(key, 0.0)
        self.features[key] = count + value
        return
    
    def add(self,arg1,value=1.0,factor=1.0):
        if isinstance(arg1, int):
            self.__add(arg1, value*factor)
        elif isinstance(arg1, FeatureVector):
            for key, f_value in arg1.features.iteritems():
                self.__add(key, f_value*value)
        else:
            print "TypeError: the type of arg1 should be int or FeatureVector!"

    def subtract(self,fv,factor=1.0):
        for key in fv.features:
            if fv.features[key] != 0:
                self.__add(key, -1.0 * fv.features[key] * factor)
                if self.features[key] == 0:
                    del self.features[key]

    def multi(self,lamada):
        for key in self.features:
            if self.features[key] > 0:
                self.setCount(key, lamada*self.features[key])

    def change2Binary(self):
        for key in self.features:
            if self.features[key] > 0:
                self.setCount(key, 1.0)

    # Concatenates two feature vectors
    @staticmethod
    def cat(fv1,fv2):
        new_fv = FeatureVector()
        new_fv.add(fv1)
        new_fv.add(fv2)
        return new_fv
    # Creates and returns the distance vector(fv1 - fv2) of both the FeatureVectors.
    @staticmethod
    def getDistVector(fv1,fv2):
        new_fv = FeatureVector()
        new_fv.add(fv1)
        new_fv.subtract(fv2)
        return new_fv
    # Computes the dot product of both the FeatureVectors.
    @staticmethod
    def dotProduct(fv1,fv2):
        result = 0.0
        for key in fv1.features:
            if key in fv2.features:
                result += fv1.features[key] * fv2.features[key]
        return result
    @staticmethod
    def oneNorm(fv1):
        return sum(fv1.features.itervalues())
    @staticmethod
    def twoNorm(fv1):
        temp = sum(map(lambda x:math.pow(x, 2.0), fv1.features.itervalues()))
        return math.sqrt(temp)

    def tostring(self):
        ls=[]
        for key in self.keySet():
            ls.append('{}:{} '.format(key,self.features[key]))
        return ''.join(ls)

    def clone(self):
        fv = FeatureVector()
        fv.features = self.features.copy()
        return fv

    def getValue(self,key):
        return self.features.get(key, 0.0)

    def keySet(self):
        return set(self.features.keys())

    def size(self):
        return len(self.features)

    def isEmpty(self):
        return len(self.features) == 0

    def containsKey(self,key):
        return self.features.has_key(key)

    def setCount(self,key,count):
        self.features[key] = count
        return

    def removeKey(self,key):
        del self.features[key]
        return

    def clear(self):
        self.features.clear()
        return
    
if __name__ == '__main__':
    print 'initialize...'
    fv1 = FeatureVector()
    fv2 = FeatureVector('1 2')
    print fv1.features == {} and fv2.features == {1:1.0,2:1.0}
    print 'add()...'
    fv1.add(1,2,3)
    fv2.add(1)
    fv1.add(fv2,2)
    print fv1.features == {1:10,2:2}
    print 'subtract()...'
    fv1.subtract(fv2,2)
    print fv1.features == {1:6}
    print 'multi()...'
    fv1.multi(2)
    print fv1.features == {1:12}
    print 'change2Binary()...'
    fv1.change2Binary()
    print fv1.features == {1:1}
    print 'cat()...'
    print FeatureVector.cat(fv1,fv2).features == {1:3,2:1}
    print 'getDistVector()...'
    print FeatureVector.getDistVector(fv1,fv2).features == {1:-1,2:-1}
    print 'dotProduct()...'
    print FeatureVector.dotProduct(fv1,fv2) == 2
    print 'oneNorm()...'
    print FeatureVector.oneNorm(fv2) == 3
    print 'twoNorm()...'
    print FeatureVector.twoNorm(fv2) == math.sqrt(5)
    print 'tostring()...'
    print fv2.tostring()
    print 'clone()...'
    print fv1.clone().features == {1:1}
    print 'finished'
