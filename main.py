# -*- coding: utf-8 -*-
'''
@author: arcra
'''
import time, threading, os
import Tkinter as tk

import clipsFunctions
import pyRobotics.BB as BB

from pyRobotics.Messages import Command
from clipsFunctions import clips
from GUI import clipsGUI

defaultTimeout = 2000
defaultAttempts = 1
gui = clipsGUI()

def setCmdTimer(t, cmd, cmdId):
    t = threading.Thread(target=timerThread, args = (t, cmd, cmdId))
    t.daemon = True
    t.start()
    return True

def timerThread(t, cmd, cmdId):
    time.sleep(t/1000)
    clipsFunctions.Assert('(BB_timer "{0}" {1})'.format(cmd, cmdId))
    clipsFunctions.PrintOutput()
    clipsFunctions.Run(gui.getRunTimes())
    clipsFunctions.PrintOutput()
    

def SendCommand(cmdName, params, timeout = defaultTimeout, attempts = defaultAttempts):
    cmd = Command(cmdName, params)
    BB.Send(cmd)
    return cmd._id

def ResponseReceived(r):
    clipsFunctions.Assert('(BB_received "{0}" {1} {2} "{3}")'.format(r.name, r._id, r.successful, r.params))
    clipsFunctions.PrintOutput()
    clipsFunctions.Run(gui.getRunTimes())
    clipsFunctions.PrintOutput()

def testSharedVarUpdated(s):
    clipsFunctions.Assert('(BB_sv_updated {0} "{1}" )'.format('test_shared_var', s))
    clipsFunctions.PrintOutput()
    clipsFunctions.Run(gui.getRunTimes())
    clipsFunctions.PrintOutput()

def Initialize():
    clips.Memory.Conserve = True
    clips.Memory.EnvironmentErrorsEnabled = True
    
    clips.RegisterPythonFunction(SendCommand)
    clips.RegisterPythonFunction(setCmdTimer)
    
    clips.BuildGlobal('defaultTimeout', defaultTimeout)
    clips.BuildGlobal('defaultAttempts', defaultAttempts)
    
    filePath = os.path.dirname(os.path.abspath(__file__))
    clips.BatchStar(filePath + os.sep + 'CLIPS' + os.sep + 'BB_interface.clp')
    
    BB.Initialize(2000, asyncHandler = ResponseReceived)
    
    BB.Start()
    
    BB.SubscribeToSharedVar('test_shared_var', testSharedVarUpdated)
    

def main():
    Initialize()
    
    tk.mainloop()

if __name__ == "__main__":
    main()