# -*- coding: utf-8 -*-
'''
@author: arcra
'''
import time, threading, os
import Tkinter as tk
import argparse

import clipsFunctions
from clipsFunctions import clips, _clipsLock, _sleeping, _sleepingLock

import pyrobotics.BB as BB
from pyrobotics.messages import Command, Response

import GUI
from BBFunctions import assertQueue, ResponseReceived, CreateSharedVar, WriteSharedVar, SubscribeToSharedVar, RunCommand

defaultTimeout = 2000
defaultAttempts = 1

def setCmdTimer(t, cmd, cmdId):
    t = threading.Thread(target=cmdTimerThread, args = (t, cmd, cmdId))
    t.daemon = True
    t.start()
    return True

def cmdTimerThread(t, cmd, cmdId):
    time.sleep(t/1000)
    assertQueue.append('(BB_timer "{0}" {1})'.format(cmd, cmdId))
    #clipsFunctions.Assert('(BB_timer "{0}" {1})'.format(cmd, cmdId))

def setTimer(t, sym):
    t = threading.Thread(target=timerThread, args = (t, sym))
    t.daemon = True
    t.start()
    return True

def timerThread(t, sym):
    time.sleep(t/1000)
    assertQueue.append('(BB_timer {0})'.format(sym))
    #clipsFunctions.Assert('(BB_timer {0})'.format(sym))

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
    _sleeping = True
    _sleepingLock.release()
    time.sleep(t/1000)
    _sleepingLock.acquire()
    _sleeping = False
    _sleepingLock.release()


def Initialize(params):
    clips.Memory.Conserve = True
    clips.Memory.EnvironmentErrorsEnabled = True
    clips.SetExternalTraceback(True)
    
    clips.DebugConfig.FactsWatched = params.watchfacts
    clips.DebugConfig.GlobalsWatched = params.watchglobals
    clips.DebugConfig.FunctionsWatched = params.watchfunctions
    clips.DebugConfig.RulesWatched = params.watchrules
    
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

    clips.BatchStar(os.path.join(filePath, 'CLIPS', 'utils.clp'))
    clips.BatchStar(os.path.join(filePath, 'CLIPS', 'BB_interface.clp'))
    clipsFunctions.PrintOutput()
    
    GUI.use_gui = not params.nogui
    if GUI.use_gui:
        GUI.gui = GUI.clipsGUI()
    else:
        GUI.debug = params.debug
    
    if params.file:
        GUI.load_file(params.file)
    
    BB.Initialize(params.port, functionMap = {'*':(RunCommand, True)}, asyncHandler = ResponseReceived)
    
    print 'Waiting for BlackBoard to connect...'
    BB.Start()
    print 'BlackBoard connected!'
    BB.SetReady()
    print 'READY!'

def main():
    
    parser = argparse.ArgumentParser(description="Runs an instance of BBCLIPS. (CLIPS interpreter embedded in python with BB communication.)")
    parser.add_argument('-p', '--port', default = '2000', type=int, help='States the port number that this instance module should use.')
    
    parser.add_argument('--nogui', default=False, action='store_const', const=True, help='Runs the program without the GUI.')
    parser.add_argument('--debug', default=False, action='store_const', const=True, help='Show a CLIPS prompt as in an interactive CLIPS session.')
    parser.add_argument('-n', '--steps', default=1, action='store', type=int, help='Number of steps to run when pressing enter on a debug session.')
    parser.add_argument('-f', '--file', help='Specifies the file that should be loaded (mainly for nogui usage).')
    
    watch_group = parser.add_argument_group('Watch options', 'Set the watch flags of the clips interpreter.')
    
    watch_group.add_argument('--watchfunctions', '--wfunctions', '--wfunc', default=False, action='store_const', const=True, help='Enables the watch functions flag of the clips interpreter.')
    watch_group.add_argument('--watchglobals', '--wglobals', '--wg', default=False, action='store_const', const=True, help='Enables the watch globals flag of the clips interpreter.')
    watch_group.add_argument('--watchfacts', '--wfacts', '--wf', default=False, action='store_const', const=True, help='Enables the watch facts flag of the clips interpreter.')
    watch_group.add_argument('--watchrules', '--wrules', '--wr', default=False, action='store_const', const=True, help='Enables the watch rules flag of the clips interpreter.')
    
    log_group = parser.add_argument_group('Log options', 'Set the log level of the BBCLIPS module.')
    
    log_group.add_argument('--log', default='ERROR', choices=['INFO', 'WARNING', 'ERROR'], help='Default is ERROR.')
    
    args = parser.parse_args()
    
    Initialize(args)
    
    if args.nogui:
        if args.debug:
            s = raw_input('[CLIPS]>')
            while s != '(exit)':
                
                if s == '(facts)':
                    clips.PrintFacts()
                elif s == '(rules)':
                    clips.PrintRules()
                elif s == '(agenda)':
                    clips.PrintAgenda()
                elif s == '':
                    assertEnqueuedFacts()
                    
                    clipsFunctions.PrintOutput()
                    clipsFunctions.Run(args.steps)
                    clipsFunctions.PrintOutput()
                else:
                    try:
                        _clipsLock.acquire()
                        #clips.SendCommand(s, True)
                        clips.Eval(s)
                        clipsFunctions.PrintOutput()
                        _clipsLock.release()
                    except:
                        print 'ERROR: Clips could not run the command.'
                        clipsFunctions.PrintOutput()
                        _clipsLock.release()
                s = raw_input('[CLIPS]>')
        else:
            mainLoop()
    else:
        loop_thread  = threading.Thread(target=mainLoop)
        loop_thread.daemon = True
        loop_thread.start()
        tk.mainloop()

def assertEnqueuedFacts():
    _clipsLock.acquire()
        
    while True:
        try:
            f = assertQueue.popleft()
        except:
            break
        
        asserted = False

        while not asserted:
            try:
                clips.Assert(f)
                asserted = True
            except:
                #print 'Fact: ' + str(f) + ' could not be asserted, trying again...'
                pass
            if not asserted:
                time.sleep(50)
    
    _clipsLock.release()

def mainLoop():
    
    while True:
        
        assertEnqueuedFacts()
        
        _sleepingLock.acquire()
        sleeping = _sleeping
        _sleepingLock.release()
        
        if sleeping or (GUI.use_gui and GUI.gui.runTimes):
            clipsFunctions.PrintOutput()
            continue
        
        clipsFunctions.Run(2)
        clipsFunctions.PrintOutput()

if __name__ == "__main__":
    main()
