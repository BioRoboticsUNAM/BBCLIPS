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

(deffunction str-replace
	(?str ?old ?new)
	(bind ?len (str-length ?old))
	(bind ?pos (str-index ?old ?str))
	(while (neq ?pos FALSE) do
		(bind ?str_len (str-length ?str))
		(bind ?str
			(str-cat
				(sub-string 1 (- ?pos 1) ?str)
				?new
				(sub-string (+ ?pos ?len) ?str_len ?str)
			)
		)
		(bind ?pos (str-index ?old ?str))
	)
	(return ?str)
)

(deffunction setCmdTimer
	(?time ?cmd ?id)
	(python-call setCmdTimer ?time ?cmd ?id)
)

(deffunction setTimer
	; Receives time in miliseconds and a symbol to identify fact that indicates the timer ran off.
	(?time ?sym)
	(bind ?new_sym (gensym*))
	(python-call setTimer ?time ?new_sym)
	(assert
		(BBCLIPS_timer ?new_sym ?sym)
		(timer_sent ?sym)
	)
)

(defrule clear_timers
	(declare (salience -9501))
	?t <-(BB_timer $?)
	=>
	(retract ?t)
)

(defrule timer_alarm
	(declare (salience 10000))
	?bbt <-(BB_timer ?new_sym)
	?bbct <-(BBCLIPS_timer ?new_sym ?sym)
	(not (BBCLIPS_timer ~?new_sym ?sym))
	?t <-(timer_sent ?sym)
	=>
	(retract ?t ?bbt ?bbct)
	(assert
		(BB_timer ?sym)
	)
)

(defrule timer_alarm-old_timer
	(declare (salience 10000))
	?bbt <-(BB_timer ?new_sym)
	?bbct <-(BBCLIPS_timer ?new_sym ?sym)
	;(timer_sent ?sym)
	(BBCLIPS_timer ~?new_sym ?sym)
	=>
	(retract ?bbt ?bbct)
)

(deffunction sleep
	; Receives time in miliseconds.
	; Prevents python from running during that time, even when messages are received.
	(?ms)
	(bind ?sym (gensym*))
	(python-call sleep ?ms ?sym)
	(halt)
)

(deffunction stop
	()
	(log-message WARNING "Stop function called. EXECUTION HALTED.")
	(python-call stop)
	(halt)
)

(deffunction set_delete
	(?fact ?time_in_secs)
	(bind ?sym (gensym*))
	(setTimer (* ?time_in_secs 1000) ?sym)
	(assert
		(BB_set_delete ?fact ?sym)
	)
)

(defrule set_delete-delete_fact
	(BB_timer ?sym)
	?f <-(BB_set_delete ?fact ?sym)
	(test (fact-existp ?fact))
	=>
	(retract ?f ?fact)
)

(defrule set_delete-delete_delete_flag
	(BB_timer ?sym)
	?f <-(BB_set_delete ?fact ?sym)
	(not (test (fact-existp ?fact)))
	=>
	(retract ?f)
)
