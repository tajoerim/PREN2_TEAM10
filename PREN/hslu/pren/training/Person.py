'''
Created on 07.12.2015

@author: Christoph
'''

class Person():
    def __init__(self, firstname="", lastname=""):
        self.firstname = firstname
        self.lastname = lastname
    def __str__(self):
        return self.firstname + " " + self.lastname
