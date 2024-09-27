(define (domain MTL-d)
    (:requirements :strips :typing :equality :adl :fluents )
    
    (:types activity automaton_state trace_state timestamp clock )
    
    (:predicates 
        ;there exists a transition in the trace automaton from two different states t1 and t2, 
        ;being e the activity involved in the transition
        (trace ?l1 - trace_state ?e - activity ?l2 - trace_state)
        
        ;there exists a transition from two different states s1 to s2 of a constraint automaton, 
        ;being e the activity involved in the transition.
        (automaton ?s1 - automaton_state ?e - activity  ?s2 - automaton_state)
        
        ;the current state of a constraint/trace automaton
        (cur_state_t ?t - trace_state)
        (cur_state_s ?s - automaton_state)
        
        ;final ac- cepting state of a constraint/trace automaton.
        (final_state_t ?t - trace_state) 
        (final_state_s ?s - automaton_state) 
        
        ;there exists a clock between two automaton_states (when exsits start the clock)
        (clock ?s1 ?s2 - automaton_state)
        
    )
    
    (:functions
        ;metric function
        (total-cost)
        ;timestamp of each action
        (timestamp ?t1 ?t2 - trace_state)
        ;conditions between actions
        (max_t_condition ?s1 ?s2 - automaton_state ?e - activity)
        (min_t_condition ?s1 ?s2 - automaton_state ?e - activity)
        ;current timestamp
        (current_timestamp)
        ;value of the clock, associated to a timestamp
        (start_clock)
        
        ;durations
        (total_duration)
        (duration ?t1 ?t2 - trace_state)
        (min_duration ?e - activity)
        (max_duration ?e - activity)
        
    )
    
    
    (:action sync
    :parameters (?t1 - trace_state ?e - activity ?t2 - trace_state)
    :precondition (and (cur_state_t ?t1) (trace ?t1 ?e ?t2) (>(timestamp ?t1 ?t2)(current_timestamp))
                  ;durations
                  (<= (duration ?t1 ?t2) (max_duration ?e))
                  (>= (duration ?t1 ?t2) (min_duration ?e))
                  (or(not(exists (?s1 ?s2 - automaton_state)(and(cur_state_s ?s1)(automaton ?s1 ?e ?s2))))
                  (exists (?s1 ?s2 - automaton_state)(and(cur_state_s ?s1)(automaton ?s1 ?e ?s2)(<=(-(timestamp ?t1 ?t2)(start_clock))(max_t_condition ?s1 ?s2 ?e))
                                                                                (>=(-(timestamp ?t1 ?t2)(start_clock))(min_t_condition ?s1 ?s2 ?e))
                                                       )
                    ))
                   )
    :effect (and 
            ;assign the current_timestamp 
            (assign (current_timestamp) (timestamp ?t1 ?t2))
            ;move on the trace
            (not (cur_state_t ?t1)) (cur_state_t ?t2)
            
            ;start the clock if exists
            (forall (?s1 ?s2 - automaton_state)
                    (when (and(automaton ?s1 ?e ?s2)(clock ?s1 ?s2))
                          (and (assign(start_clock)(timestamp ?t1 ?t2)))))
                          
            ;move on the automaton if exists an edge
            (forall (?s1 ?s2 - automaton_state)
                    (when (and (cur_state_s ?s1)(automaton ?s1 ?e ?s2))
                          (and (not (cur_state_s ?s1))(cur_state_s ?s2))))
            
            ;increase total duration
            (increase (total_duration)(duration ?t1 ?t2))
            
            )
    )
    
    (:action shrinked_sync_min
    :parameters (?t1 - trace_state ?e - activity ?t2 - trace_state)
    :precondition (and (cur_state_t ?t1) (trace ?t1 ?e ?t2) 
                  (< (duration ?t1 ?t2) (min_duration ?e))
                  (or(not(exists (?s1 ?s2 - automaton_state)(and(cur_state_s ?s1)(automaton ?s1 ?e ?s2))))
                   (exists (?s1 ?s2 - automaton_state)(and(cur_state_s ?s1)(automaton ?s1 ?e ?s2)(<=(-(timestamp ?t1 ?t2)(start_clock))(max_t_condition ?s1 ?s2 ?e))
                                                                                (>=(-(timestamp ?t1 ?t2)(start_clock))(min_t_condition ?s1 ?s2 ?e))
                                                       )
                    ))
                   )
                   
    :effect (and (not (cur_state_t ?t1)) (cur_state_t ?t2)
            
            (assign (current_timestamp)(+(current_timestamp)(min_duration ?e)))
            
            ;increse all the subsequent timestamp
            (forall (?l1 ?l2 - trace_state ?e1 - activity)
            (when (and (trace ?l1 ?e1 ?l2)(> (timestamp ?l1 ?l2)(timestamp ?t1 ?t2)))
                  (and (increase (timestamp ?l1 ?l2)(-(min_duration ?e)(duration ?t1 ?t2))))))
            
            (forall (?s1 ?s2 - automaton_state)
                    (when (and (automaton ?s1 ?e ?s2)(clock ?s1 ?s2))
                          (and (assign(start_clock)(timestamp ?t1 ?t2)))))
            
            (forall (?s1 ?s2 - automaton_state)
                    (when (and (cur_state_s ?s1)(automaton ?s1 ?e ?s2))
                            (and (not (cur_state_s ?s1))(cur_state_s ?s2))))
            
            
            
            (increase (total_duration)(min_duration ?e))
            (increase (total-cost) 1)
            
            )
        )
    
    (:action shrinked_sync_max
    :parameters (?t1 - trace_state ?e - activity ?t2 - trace_state)
    :precondition (and (cur_state_t ?t1) (trace ?t1 ?e ?t2) 
                  (> (duration ?t1 ?t2) (max_duration ?e))
                  (or(not(exists (?s1 ?s2 - automaton_state)(and(cur_state_s ?s1)(automaton ?s1 ?e ?s2))))
                   (exists (?s1 ?s2 - automaton_state)(and(cur_state_s ?s1)(automaton ?s1 ?e ?s2)(<=(-(timestamp ?t1 ?t2)(start_clock))(max_t_condition ?s1 ?s2 ?e))
                                                                                (>=(-(timestamp ?t1 ?t2)(start_clock))(min_t_condition ?s1 ?s2 ?e))
                                                       )
                    ))
                   )
    :effect (and (not (cur_state_t ?t1)) (cur_state_t ?t2)
            
            ;increse all the subsequent timestamp
            (forall (?l1 ?l2 - trace_state ?e1 - activity)
            (when (and (trace ?l1 ?e1 ?l2)(> (timestamp ?l1 ?l2)(timestamp ?t1 ?t2)))
                  (and (decrease (timestamp ?l1 ?l2) (-(duration ?t1 ?t2)(max_duration ?e))))))
            
             (forall (?s1 ?s2 - automaton_state)
                    (when (and (automaton ?s1 ?e ?s2)(clock ?s1 ?s2))
                          (and (assign(start_clock)(timestamp ?t1 ?t2)))))
            
            (forall (?s1 ?s2 - automaton_state)
                    (when (and (cur_state_s ?s1)(automaton ?s1 ?e ?s2))
                            (and (not (cur_state_s ?s1))(cur_state_s ?s2))))
           
                            
            (increase (total_duration)(max_duration ?e))
            (increase (total-cost) 1)
             (assign (current_timestamp)(+(current_timestamp)(max_duration ?e)))
            )
    )
  
    
    (:action add
    :parameters (?e - activity)
    :precondition (exists (?s1 ?s2 - automaton_state)
                  (and (automaton ?s1 ?e ?s2)(cur_state_s ?s1)(or(and(<= (- (+(current_timestamp)(min_duration ?e))(start_clock))(max_t_condition ?s1 ?s2 ?e))
                                             (>= (- (+(current_timestamp)(min_duration ?e))(start_clock))(min_t_condition ?s1 ?s2 ?e))
                                                )(= (current_timestamp)0))))
    :effect (and (increase (total-cost) 2)
            ;(assign (current_timestamp) (+(current_timestamp)0.1))
            (forall (?l1 ?l2 - trace_state ?e1 - activity)
            (when (and (trace ?l1 ?e1 ?l2)(> (timestamp ?l1 ?l2)(current_timestamp)))
                  (and (increase (timestamp ?l1 ?l2)(min_duration ?e)))))
            (forall (?s1 ?s2 - automaton_state)
            
            (when (and (cur_state_s ?s1) (automaton ?s1 ?e ?s2))
                   (and (not (cur_state_s ?s1))(cur_state_s ?s2))))
            (increase (total-duration)(min_duration ?e))
            (increase (current_timestamp)(min_duration ?e))
            
            )
            )
    
    
    (:action del
    :parameters (?t1 - trace_state ?e - activity ?t2 - trace_state)
    :precondition (and (cur_state_t ?t1) (trace ?t1 ?e ?t2))
    :effect (and 
             (not (cur_state_t ?t1)) (cur_state_t ?t2)
             (increase (total-cost) 2)
             (forall (?l1 ?l2 - trace_state ?e1 - activity)
             (when (and (trace ?l1 ?e1 ?l2)(> (timestamp ?l1 ?l2)(timestamp ?t1 ?t2)))
                  (and (decrease (timestamp ?l1 ?l2)(duration ?t1 ?t2)))))))
                 
    
   
    
)