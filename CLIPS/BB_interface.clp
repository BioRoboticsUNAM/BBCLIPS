;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;		DEFTEMPLATES
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
(deftemplate waiting
	(slot cmd (type STRING))
	(slot id (type INTEGER))
	(slot args (type STRING))
	(slot timeout
		(type INTEGER)
		(range 0 ?VARIABLE)
	)
	(slot attempts
		(type INTEGER)
		(range 1 ?VARIABLE)
	)
)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;		PYTHON FUNCTIONS
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
(deffunction setCmdTimer
	(?time ?cmd ?id)
	(python-call setCmdTimer ?time ?cmd ?id)
)

(deffunction send-command
	; Receives: command, cmd_params and optionally
	;timeout and number of attempts in case it times out or fails
	(?cmd ?args $?settings)
	(bind ?timeout ?*defaultTimeout*)
	(bind ?attempts ?*defaultAttempts*)
	(switch (length$ $?settings)
		(case 1 then
			(bind ?timeout (nth$ 1 $?settings))
		)
		(case 2 then
			(bind ?timeout (nth$ 1 $?settings))
			(bind ?attempts (nth$ 2 $?settings))
		)
	)
	(bind ?id (python-call SendCommand ?cmd ?args))
	(setCmdTimer ?timeout ?cmd ?id)
	(assert
		(waiting (cmd ?cmd) (id ?id) (args ?args) (timeout ?timeout) (attempts ?attempts) )
	)
	(log-message INFO "Sent command: '" ?cmd "' - id: " ?id " - timeout: " ?timeout "ms - attempts: " ?attempts)
)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;		RULES TO HANDLE BB (PYTHON) ASSERTS
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
(defrule BB-waiting-timedout-without_attempts
	?w <-(waiting (cmd ?cmd) (id ?id) (attempts 1) (timeout ?timeout&~0) )
	?BB <-(BB_timer ?cmd ?id)
	(not
		(BB_received ?cmd ?id $?)
	)
	=>
	(retract ?w ?BB)
	(log-message WARNING "Command timedout w/o attempts: '" ?cmd "' - id: " ?id " - timeout: " ?timeout "ms")
)

(defrule BB-waiting-timedout-with_attempts
	?w <-(waiting (cmd ?cmd) (id ?id) (args ?args) (attempts ?attempts&~1) (timeout ?timeout&~0) )
	?BB <-(BB_timer ?cmd ?id)
	(not
		(BB_received ?cmd ?id $?)
	)
	=>
	(retract ?BB)
	(log-message WARNING "Command timedout w/ attempts: '" ?cmd "' - id: " ?id " - timeout: " ?timeout "ms - attempts: " ?attempts)
	(bind ?id (python-call SendCommand ?cmd ?args))
	(setCmdTimer ?timeout ?cmd ?id)
	(bind ?attempts (- ?attempts 1))
	(modify ?w (id ?id) (attempts ?attempts))
	(log-message INFO "Sent command: '" ?cmd "' - id: " ?id " - timeout: " ?timeout "ms - attempts: " ?attempts)
)

(defrule BB-failed-with_attempts
	?w <-(waiting (cmd ?cmd) (id ?id) (args ?args) (attempts ?attempts&~1) (timeout ?timeout&~0) )
	?BB <-(BB_received ?cmd ?id 0 ?)
	=>
	(retract ?BB)
	(log-message WARNING "Command failed w/ attempts: '" ?cmd "' - id: " ?id " - attempts: " ?attempts)
	(bind ?id (python-call SendCommand ?cmd ?args))
	(setCmdTimer ?timeout ?cmd ?id)
	(modify ?w (id ?id) (attempts (- ?attempts 1)))
	(log-message INFO "Sent command: '" ?cmd "' - id: " ?id " - timeout: " ?timeout "ms - attempts: " ?attempts)
)

(defrule BB-clear-timers
	?t <-(BB_timer ?cmd ?id)
	(not
		(waiting (cmd ?cmd) (id ?id))
	)
	=>
	(retract ?t)
	(log-message INFO "Clearing timer for command: '" ?cmd "' - id: " ?id)
)

(defrule BB-clear_response
	?BB <-(BB_received ?cmd ?id $?)
	(not
		(waiting (cmd ?cmd) (id ?id))
	)
	=>
	(retract ?BB)
	(log-message WARNING "Clearing unhandled response from command: '" ?cmd "' - id: " ?id)
)

(defrule BB-set_answer
	?w <-(waiting (cmd ?cmd) (id ?id) (attempts ?attempts))
	?BB <-(BB_received ?cmd ?id ?result ?params)
	(test (or (eq ?result 1) (eq ?attempts 1)))
	=>
	(retract ?w ?BB)
	(assert 
		(BB_answer ?cmd ?result ?params)
	)
	(log-message INFO "Answer received: '" ?cmd "' - id: " ?id " - successful: " ?result " - response: " ?params)
)

;	HANDLE SHARED VAR UPDATES
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
(defrule BB-set_sv_update
	?BB <-(BB_sv_updated ?var ?val)
	=>
	(retract ?BB)
	(printout t "Shared var updated: " ?var crlf "value: " ?val crlf)
)
