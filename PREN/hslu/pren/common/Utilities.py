'''
Created on 07.12.2015

@author: Christoph

@todo: implement
'''


def SerializeMethodWithParameters(method, array_args):
    '''
    Bildet aus einem Methodennamen und einem Array aus Parametern
    einen serialisierten String zum aufrufen entfernter Methoden
    
    @param method: Methodenname
    @param array_args: Array von argumenten
    
    @return: serialisierter Methodenaufruf
    '''
    
    ret = method + "("
    for arg in array_args:
        ret = ret + str(arg) + ","
    ret = ret + ")"
    ret = ret.replace(",)", ")") #Damit das letzte Komma entfernt wird... einfacher als substring o.ae
    return ret