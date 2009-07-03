'''
Created on 2009-06-30

'''

class Bestia:
    
    first = 1
    last  = 20
        
    def getPazurki(self):
        for i in range(self.first, self.last):
            yield i 

bestia = Bestia()

pazurki = (bestia.getPazurki())

print 'Piramidka %s' % ' Bestii'

for i in pazurki:
    print '-' * i 