;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;			GLOBALS
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
(defglobal ?*outlog* = t)
(defglobal ?*logLevel* = ERROR) ; INFO | WARNING | ERROR | DEBUG (print always)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;			FUNCTIONS
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
(deffunction log-message
	; Receives level and message chunks that would be concatenated.
	; Level is one of: INFO | WARNING | ERROR | DEBUG (print always)
	(?level ?msg1 $?msg2)

	(bind ?message ?msg1)
	(progn$ (?var $?msg2)
		(bind ?message (str-cat ?message ?var) )
	)
	(if (eq ?level DEBUG) then
		(printout ?*outlog* ?level ": " ?message crlf)
		(return)
	)
	(bind ?currentLogLevel 10)
	(bind ?lvl 10)
	(switch ?*logLevel*
		(case INFO then (bind ?currentLogLevel 0))
		(case ERROR then (bind ?currentLogLevel 20))
		(case WARNING then (bind ?currentLogLevel 10))
	)
	(switch ?level
		(case INFO then (bind ?lvl 0))
		(case ERROR then (bind ?lvl 20))
		(case WARNING then (bind ?lvl 10))
	)
	(if (>= ?lvl ?currentLogLevel) then
		(printout ?*outlog* ?level ": " ?message crlf)
	)
)

(deffunction setCmdTimer
	(?time ?cmd ?id)
	(python-call setCmdTimer ?time ?cmd ?id)
)

(deffunction setTimer
	; Receives time in miliseconds and a symbol to identify fact that indicates the timer ran off.
	(?time ?sym)
	(python-call setTimer ?time ?sym)
	(assert (timer_sent ?sym (time) (/ ?time 1000.0)))
)

(defrule clear_timers
	(declare (salience -1000))
	?t <-(BB_timer $?)
	=>
	(retract ?t)
)

(defrule delete_old_timers
	(declare (salience -1000))
	?t <-(timer_sent ? ?time ?duration)
	(test (> (time) (+ ?time ?duration) ) )
	=>
	(retract ?t)
)

(deffunction sleep
	; Receives time in miliseconds.
	; Prevents python from running during that time, even when messages are received.
	(?ms)
	(bind ?sym (gensym*))
	(python-call sleep ?ms ?sym)
	(halt)
)
