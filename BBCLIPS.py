# -*- coding: utf-8 -*-
'''
@author: arcra
'''
import time, threading, os
import Tkinter as tk
import argparse

import clipsFunctions
from clipsFunctions import clips, sleeping, _sleepingLock

import pyRobotics.BB as BB
from pyRobotics.Messages import Command, Response

from GUI import gui
from BBFunctions import ResponseReceived, CreateSharedVar, WriteSharedVar, SubscribeToSharedVar, RunCommand

defaultTimeout = 2000
defaultAttempts = 1

def setCmdTimer(t, cmd, cmdId):
    t = threading.Thread(target=cmdTimerThread, args = (t, cmd, cmdId))
    t.daemon = True
    t.start()
    return True

def cmdTimerThread(t, cmd, cmdId):
    time.sleep(t/1000)
    clipsFunctions.Assert('(BB_timer "{0}" {1})'.format(cmd, cmdId))
    _sleepingLock.acquire()
    if not sleeping:
        clipsFunctions.PrintOutput()
        clipsFunctions.Run(gui.getRunTimes())
        clipsFunctions.PrintOutput()
    _sleepingLock.release()

def setTimer(t, sym):
    t = threading.Thread(target=timerThread, args = (t, sym))
    t.daemon = True
    t.start()
    return True

def timerThread(t, sym):
    time.sleep(t/1000)
    clipsFunctions.Assert('(BB_timer {0})'.format(sym))
    _sleepingLock.acquire()
    if not sleeping:
        clipsFunctions.PrintOutput()
        clipsFunctions.Run(gui.getRunTimes())
        clipsFunctions.PrintOutput()
    _sleepingLock.release()

def SendCommand(cmdName, params):
    cmd = Command(cmdName, params)
    BB.Send(cmd)
    return cmd._id

def SendResponse(cmdName, cmd_id, result, response):
    result = str(result).lower() not in ['false', '0']
    r = Response(cmdName, result, response)
    r._id = cmd_id
    BB.Send(r)
    
def sleep(ms, sym):
    t = threading.Thread(target=sleepingTimerThread, args = (ms, sym))
    t.daemon = True
    t.start()
    return True

def sleepingTimerThread(t, sym):
    _sleepingLock.acquire()
    sleeping = True
    _sleepingLock.release()
    time.sleep(t/1000)
    _sleepingLock.acquire()
    sleeping = False
    _sleepingLock.release()
    
    clipsFunctions.PrintOutput()
    clipsFunctions.Run(gui.getRunTimes())
    clipsFunctions.PrintOutput()

def Initialize(port):
    clips.Memory.Conserve = True
    clips.Memory.EnvironmentErrorsEnabled = True
    clips.SetExternalTraceback(True)
    
    clips.RegisterPythonFunction(SendCommand)
    clips.RegisterPythonFunction(SendResponse)
    clips.RegisterPythonFunction(setCmdTimer)
    clips.RegisterPythonFunction(setTimer)
    clips.RegisterPythonFunction(CreateSharedVar)
    clips.RegisterPythonFunction(WriteSharedVar)
    clips.RegisterPythonFunction(SubscribeToSharedVar)
    clips.RegisterPythonFunction(sleep)
    
    clips.BuildGlobal('defaultTimeout', defaultTimeout)
    clips.BuildGlobal('defaultAttempts', defaultAttempts)
    
    filePath = os.path.dirname(os.path.abspath(__file__))
    clips.BatchStar(filePath + os.sep + 'CLIPS' + os.sep + 'BB_interface.clp')
    
    BB.Initialize(port, functionMap = {'*':RunCommand}, asyncHandler = ResponseReceived)
    
    BB.Start()
    

def main():
    
    parser = argparse.ArgumentParser(description="Runs an instance of BBCLIPS. (CLIPS interpreter embedded in python with BB communication.)")
    parser.add_argument('-p', '--port', default = '2000', type=int, help='States the port number that this instance module should use.')
    
    args = parser.parse_args()
    
    Initialize(args.port)
    
    tk.mainloop()

if __name__ == "__main__":
    main()