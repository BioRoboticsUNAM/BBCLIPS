# -*- coding: utf-8 -*-
'''
@author: arcra
'''

import time
import threading
import clips

_clipsLock = threading.Lock()
_sleepingLock = threading.Lock()
sleeping = False


def PrintOutput():
    
    locked = _clipsLock.acquire(False)
    
    o = clips.TraceStream.Read()
    if o:
        print o
    o = clips.StdoutStream.Read()
    if o:
        print o
    o = clips.ErrorStream.Read()
    if o:
        index = o.find('[PRCCODE4] Execution halted during the actions of defrule respond_command-rule.')
        if index > -1:
            o = o[:index] + o[index + 79:]
        print o
    
    if locked:
        _clipsLock.release()

def PrintFacts():
    _clipsLock.acquire()
    clips.PrintFacts()
    _clipsLock.release()

def PrintRules():
    _clipsLock.acquire()
    clips.PrintRules()
    _clipsLock.release()
    
def PrintAgenda():
    _clipsLock.acquire()
    clips.PrintAgenda()
    _clipsLock.release()
    
def Reset():
    _clipsLock.acquire()
    clips.Reset()
    _clipsLock.release()
    
def Run(times = ''):
    _clipsLock.acquire()
    clips.SendCommand('(run ' + str(times) + ')')
    _clipsLock.release()
    
def Assert(fact):
    
    asserted = False
    
    while not asserted:
        _clipsLock.acquire()
        try:
            clips.Assert(fact)
            asserted = True
        except:
            #print 'Fact: ' + str(fact) + ' could not be asserted, trying again...'
            pass
        _clipsLock.release()
        if not asserted:
            time.sleep(100)

