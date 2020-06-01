

class Foo:
    def __init__(self):
        self._bar = {"set_1": None,
                     "set_2": None}   
         
    @property
    def bar(self):
        print('getter method called')
        return self._bar
    @bar.setter
    def bar(self):
        if(x < 10):
            raise ValueError('sorry, the number must be 10 or above')
        print('setter method called')
        self._bar
 
 
mark = Foo()
 
print("bar before:  " + str(mark.bar["set_1"]))
 
mark.bar["set_1"] = 10
 
print("bar after:  " + str(mark.bar["set_1"]))


# Python program showing the use of 
# @property 
  
# class Geeks: 
#      def __init__(self): 
#           self._age = 0
#        
#      # using property decorator 
#      # a getter function 
#      @property
#      def age(self): 
#          print("getter method called") 
#          return self._age 
#        
#      # a setter function 
#      @age.setter 
#      def age(self, a): 
#          if(a < 18): 
#             raise ValueError("Sorry you age is below eligibility criteria") 
#          print("setter method called") 
#          self._age = a 
#   
# mark = Geeks() 
#   
# mark.age = 19
#   
# print(mark.age) 