import re
import operator
import sys
# def pn_replace(pn):
#     if pn:
#         pn_replace =  re.sub('[- _ \s \\\ \/ |.]','',pn)
#         return pn_replace
#     else:
#         pn_replace = pn
#     return pn_replace
# a = u'a.b/- _ 0'
# print (pn_replace(a))

# number_map_dict = {2:3,1:5}
# largest_map_row = max(number_map_dict.items(), key=operator.itemgetter(0))[0]
# print ('largest_map_row',largest_map_row)

# n = {}
# n.setdefault('a',1)
# b =n.setdefault('a',2)
# print (n,b)

def f1(a):
    print (a)
    
    
try:
    f1(2,4)
except Exception as e:
    print (e.args[0],sys.exc_info()[0])
    print("OS error: {0}".format(e))
    print (e,type(e))