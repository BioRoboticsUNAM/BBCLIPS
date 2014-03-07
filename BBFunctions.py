# -*- coding: utf-8 -*-
'''
@author: arcra
'''
from main import gui
import clipsFunctions
import pyRobotics.BB as BB


#####################################################
#                HANDLERS
#####################################################
def ResponseReceived(r):
    clipsFunctions.Assert('(BB_received "{0}" {1} {2} "{3}")'.format(r.name, r._id, r.successful, r.params))
    clipsFunctions.PrintOutput()
    clipsFunctions.Run(gui.getRunTimes())
    clipsFunctions.PrintOutput()

def SharedVarUpdated(sv):
    
    s = '(BB_sv_updated "' + sv.varName + '" ' 
    if sv.svType in [BB.SharedVarTypes.INT, BB.SharedVarTypes.LONG, BB.SharedVarTypes.DOUBLE]:
        s += str(sv.data)
    elif sv.svType in [BB.SharedVarTypes.INT_ARRAY, BB.SharedVarTypes.LONG_ARRAY, BB.SharedVarTypes.DOUBLE_ARRAY, BB.SharedVarTypes.BYTE_ARRAY]:
        s += str(sv.size) + ' ' + ' '.join([str(x) for x in sv.data])
    elif sv.svType == BB.SharedVarTypes.STRING:
        s += '"' + sv.data + '"'
    elif sv.svType == BB.SharedVarTypes.RECOGNIZED_SPEECH:
        s += str(len(sv.data)) + ' ' + ' '.join(['"' + x + '" ' + str(y) for x, y in sv.data])
    elif sv.svType == BB.SharedVarTypes.VAR:
        s += str(sv.data)
    elif sv.svType == BB.SharedVarTypes.MATRIX:
        s += str(len(sv.data)) + ' ' + str(len(sv.data[0])) + ' '
        for r in sv.data:
            for c in r:
                s += ' ' + str(c)
    else:
        print 'ERROR: Parsing shared var: "{0}" failed'.format(sv.varName)
        return
        
    s += ')'
    
    clipsFunctions.Assert(s)
    clipsFunctions.PrintOutput()
    clipsFunctions.Run(gui.getRunTimes())
    clipsFunctions.PrintOutput()

#####################################################
#          SHARED VARIABLES MANIPULATION
#####################################################
def CreateSharedVar(sharedVarType, name):
    return BB.CreateSharedVar( str(sharedVarType), name)

def WriteSharedVar(sharedVarType, name, *data):
    
    sharedVarType = str(sharedVarType)
    
    if sharedVarType in [BB.SharedVarTypes.INT, BB.SharedVarTypes.LONG, BB.SharedVarTypes.DOUBLE]:
        data = str(data[0])
    elif sharedVarType in [BB.SharedVarTypes.INT_ARRAY, BB.SharedVarTypes.LONG_ARRAY, BB.SharedVarTypes.DOUBLE_ARRAY]:
        data = [str(x) for x in data]
    elif sharedVarType == BB.SharedVarTypes.BYTE_ARRAY:
        data = '0x' + ''.join([ "%02X" % x for x in data ])
    elif sharedVarType == BB.SharedVarTypes.STRING:
        data = data[0]
    elif sharedVarType == BB.SharedVarTypes.RECOGNIZED_SPEECH:
        data = 1
    elif sharedVarType == BB.SharedVarTypes.VAR:
        pass
    elif sharedVarType == BB.SharedVarTypes.MATRIX:
        l = []
        rows = data[0]
        columns = data[1]
        data = data[2:]
        for r in range(rows):
            row = []
            for c in range(columns):
                row.append(data[r*columns + c])
            l.append(row)
        data = l
    else:
        print 'ERROR: Writing to shared var: "{0}" failed'.format(name)
        return
    
    return BB.WriteSharedVar(sharedVarType, name, data)

def SubscribeToSharedVar(name, subscriptionType = 'WRITE_OTHERS', reportType = 'CONTENT'):
    if subscriptionType not in [x for x in dir(BB.SubscriptionTypes) if x[:2] != "__"]:
        return False
    if reportType not in [x for x in dir(BB.ReportTypes) if x[:2] != "__"]:
        return False
    return BB.SubscribeToSharedVar(name, SharedVarUpdated, getattr(BB.SubscriptionTypes, subscriptionType), getattr(BB.ReportTypes, reportType))
    