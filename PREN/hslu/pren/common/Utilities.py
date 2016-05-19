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
    
    ret = method + ";"
    if (array_args):
        for arg in array_args:
            ret = ret + str(arg) + ";"
    return ret

def DeserializeMethodWithParameters(method, retMsg):
    '''
    
    @param method: Methodenname
    @param retMsg: Antowort von Freedom o.ae
    
    @return: deserialisierter returnwert
    '''

    print "[UTIL] Return value RAW: " + retMsg;
    
    ret = retMsg.replace(method, "")
    ret = ret.replace(";", "")
    return ret