# -*- coding: utf-8 -*-
'''
@author: arcra
'''
import time, threading, os
import Tkinter as tk
import argparse

import clipsFunctions
from clipsFunctions import clips, _clipsLock, sleeping, _sleepingLock

import pyRobotics.BB as BB
from pyRobotics.Messages import Command, Response

from GUI import gui, clipsGUI, use_gui, debug
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
    
    if (use_gui and gui.getRunTimes()) or debug:
        clipsFunctions.PrintOutput()
        return
    
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
    
    if (use_gui and gui.getRunTimes()) or debug:
        clipsFunctions.PrintOutput()
        return
    
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
    
    if (use_gui and gui.getRunTimes()) or debug:
        clipsFunctions.PrintOutput()
        return
    
    clipsFunctions.PrintOutput()
    clipsFunctions.Run(gui.getRunTimes())
    clipsFunctions.PrintOutput()

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
    
    use_gui = not params.nogui
    if use_gui:
        gui = clipsGUI()
    else:
        debug = params.debug
    
    if params.file:
        
        module_path = os.path.dirname(os.path.abspath(filePath))
        
        _clipsLock.acquire()
        clips.BuildGlobal('module_path', module_path + os.path.sep)
        _clipsLock.release()
        
        filePath = os.path.abspath(params.file)
        
        if filePath[-3:] == 'clp':
            
            _clipsLock.acquire()
            clips.BatchStar(filePath)
            clips.Reset()
            clipsFunctions.PrintOutput()
            _clipsLock.release()
            print 'File Loaded!'
            return
        
        queue = [os.path.basename(filePath)]
        
        _clipsLock.acquire()
        while queue:
            el = queue.pop(0).strip()
            if el[0] == ';':
                continue
            
            filePath = str(os.path.join(module_path, el))
            
            if el[-3:] == 'clp':
                try:
                    clips.BatchStar(filePath)
                except IOError:
                    print 'ERROR: File ' + filePath + 'could not be open. Make sure that the path is correct.'
                except Exception as e:
                    print 'ERROR: An error occurred trying to open file: ' + filePath
                    print e
            elif el[-3:] == 'lst' or el[-3:] == 'dat':
                try:
                    dir_path = os.path.dirname(el)
                    f = open(filePath, 'r')
                    queue = [str(os.path.join(dir_path, x)) for x in f.readlines() if x.strip()[0] != ';'] + queue
                    f.close()
                except IOError:
                    print 'ERROR: File ' + filePath + 'could not be open. Make sure that the path is correct.'
                except Exception as e:
                    print 'ERROR: An error occurred trying to open file: ' + filePath
                    print e
            else:
                dot = filePath.rfind('.')
                if dot == -1:
                    print '...Skipping file without extension: ' + filePath
                    continue
                print '...Skipping unknown file extension: ' + filePath[dot:] 
        
        clips.Reset()
        clipsFunctions.PrintOutput()
        _clipsLock.release()
        
        print 'Files Loaded!'
    
    BB.Initialize(params.port, functionMap = {'*':RunCommand}, asyncHandler = ResponseReceived)
    
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
            BB.Wait()
    else:
        tk.mainloop()

if __name__ == "__main__":
    main()
