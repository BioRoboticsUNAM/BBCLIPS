;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;			GLOBALS
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
(defglobal ?*outlog* = t)
(defglobal ?*logLevel* = ERROR) ; INFO | WARNING | ERROR

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;			FUNCTIONS
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
(deffunction log-message
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
	(?time ?sym)
	(python-call setTimer ?time ?sym)
	(assert (timer_sent ?sym))
)

(defrule clear_timers
	(declare (salience -500))
	?t <-(BB_timer ?)
	=>
	(retract ?t)
)

(defrule delete_old_timers
	(declare (salience -500))
	?t <-(timer_sent ?)	
	=>
	(retract ?t)
)

(deffunction sleep
	(?ms)
	(bind ?sym (gensym*))
	(python-call sleep ?ms ?sym)
	(halt)
)
