import pysal.core.FileIO as FileIO
from pysal.weights import W
  
class GalIO(FileIO.FileIO):

    FORMATS = ['gal']
    MODES = ['r','w']

    def __init__(self,*args,**kwargs):
        FileIO.FileIO.__init__(self,*args,**kwargs)
        self.file = open(self.dataPath, self.mode)

    def read(self, n=-1):
        return self._read()

    def seek(self, pos):
        if pos == 0:
            self.file.seek(0)
            self.pos = 0

    def _read(self):
        if self.pos > 0:
            raise StopIteration
        weights={}
        neighbors={}
        ids=[]
        # handle case where more than n is specified in first line
        header=self.file.readline().strip().split()
        header_n= len(header)
        n=int(header[0])
        if header_n > 1:
            n=int(header[1])
        w={}
        for i in range (n):
            id,n_neighbors=self.file.readline().strip().split()
            n_neighbors = int(n_neighbors)
            neighbors_i = self.file.readline().strip().split()
            weights[id]=[1]*n_neighbors
            neighbors[id]=neighbors_i
            ids.append(id)
        #original_neighbors=neighbors
        #zo=self.__zero_offset(neighbors,weights,original_ids)
        #neighbors=zo['new_neighbors']
        #original_ids=zo['old_ids']
        #ids = zo['new_ids']
        #weights=zo['new_weights']
        #original_weights=weights
        #n=len(weights)
        d = {}
        d['ids']=ids
        d['weights'] = weights
        d['neighbors'] = neighbors
        #d['original_neighbors'] = original_neighbors
        #d['new_ids'] = ids
        #d['original_ids'] = original_ids

        self.pos += 1 
        return W(d)

    def write(self,obj):
        """ .write(weightsObject)

        write a weights object to the opened file.
        """
        self._complain_ifclosed(self.closed)
        if issubclass(type(obj),W):
            self.file.write('%d\n'%(obj.n))
            if obj.old_ids: #back to real ids
                IDS = obj.old_ids #back to real ids
            else: 
                IDS = obj.neighbors.keys()
            for id in IDS:
                neighbors = obj.neighbors[obj.old_ids[id]]
                neighbors = [obj.new_ids[i] for i in neighbors] #go back to real ids
                self.file.write('%d %d\n'%(id,len(neighbors)))
                self.file.write(' '.join(map(str,neighbors))+'\n')
            self.pos += 1
        else:
            raise TypeError,"Expected a pysal weights object, got: %s"%(type(obj))
    def close(self):
        self.file.close()
        FileIO.FileIO.close(self)

    @staticmethod
    def __zero_offset(neighbors,weights,original_ids=None):
        if not original_ids:
            original_ids=neighbors.keys()
        old_weights=weights
        new_weights={}
        new_ids={}
        old_ids={}
        new_neighbors={}
        for i in original_ids:
            new_i=original_ids.index(i)
            new_ids[new_i]=i
            old_ids[i]=new_i
            neighbors_i=neighbors[i]
            new_neighbors_i=[original_ids.index(j) for j in neighbors_i]
            new_neighbors[new_i]=new_neighbors_i
            new_weights[new_i]=weights[i]
        info={}
        info['new_ids']=new_ids
        info['old_ids']=old_ids
        info['new_neighbors']=new_neighbors
        info['new_weights']=new_weights
        return info




