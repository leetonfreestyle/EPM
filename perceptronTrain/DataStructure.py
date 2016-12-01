#!/usr/bin/env python
# -- coding:utf-8 --

class MaxHeap(object):
    """docstring for MaxHeap"""
    List = []
    size = 0
    minElement = None

    def __init__(self, sz):
        super(MaxHeap, self).__init__()
        self.size = sz
    
    def add(self,o):
        if self.minElement == None:
            self.minElement = o
        elif o.compareTo(self.minElement) < 0:
            if self.List.__len__() < self.size:
                self.minElement = o
            else:
                return
        self.List.append(o)
        i = self.List.__len__() - 1
        while i > 0 and self.List[self.parent(i)].compareTo(o) < 0:
            self.List[i] = self.List[self.parent(i)]
            i = self.parent(i)
        self.List[i] = o

    def extract(self):
        if self.List.__len__() == 0:
            return None
        top = self.List[0]
        last = self.List.__len__() - 1
        if last != 0:
            self.List[0] = self.List[last]
            del self.List[last]
            self.heapify(0)
        else:
            del self.List[last]
        return top

    def parent(self,i):
        return (i - 1) / 2

    def left(self,i):
        return (i + 1) * 2 - 1

    def right(self,i):
        return (i + 1) * 2

    def heapify(self,i):
        while True:
            l = self.left(i)
            r = self.right(i)
            if l < self.List.__len__() and self.List[l].compareTo(self.List[i]) > 0:
                greatest = l
            else:
                greatest = i
            if r < self.List.__len__() and self.List[r].compareTo(self.List[greatest]) > 0:
                greatest = r
            if greatest != i:
                self.swap(greatest,i)
                i = greatest
            else:
                break

    def swap(self,x,y):
        ox = self.List[x]
        oy = self.List[y]
        self.List[x] = oy
        self.List[y] = ox

    def clear(self):
        self.List = []

    def isEmpty(self):
        return self.List.__len__() == 0

class Inter(object):
    """docstring for Inter"""
    arg = 0
    def __init__(self, arg):
        super(Inter, self).__init__()
        self.arg = arg
    def compareTo(self,o):
        return self.arg - o.arg
        

def main():
    elements = [9, 5, 10, 6, 4, 1,7,3,  8, 2, 0]
    heap = MaxHeap(5)
    for one in elements:
        heap.add(Inter(one))
    while heap.List.__len__() != 0:
        print heap.extract().arg

if __name__ == '__main__':
    main()