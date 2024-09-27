(define (domain MTL)
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
        
        (clock ?s1 ?s2 - automaton_state)
        
    )
    
    (:functions
        (total-cost)
        (timestamp ?t1 ?t2 - trace_state)
        (max_t_condition ?s1 ?s2 - automaton_state ?e - activity)
        (min_t_condition ?s1 ?s2 - automaton_state ?e - activity)
        (current_timestamp)
        (start_clock)
        
    )
    
    
    (:action sync
    :parameters (?t1 - trace_state ?e - activity ?t2 - trace_state)
    :precondition (and (cur_state_t ?t1) (trace ?t1 ?e ?t2)
                   (or(not(exists (?s1 ?s2 - automaton_state)(and(cur_state_s ?s1)(automaton ?s1 ?e ?s2))))
                   (exists (?s1 ?s2 - automaton_state)(and(cur_state_s ?s1)(automaton ?s1 ?e ?s2)(<=(-(timestamp ?t1 ?t2)(start_clock))(max_t_condition ?s1 ?s2 ?e))
                                                                                (>=(-(timestamp ?t1 ?t2)(start_clock))(min_t_condition ?s1 ?s2 ?e))
                                                       )
                    )))
    :effect (and (assign (current_timestamp) (timestamp ?t1 ?t2))
            (not (cur_state_t ?t1)) (cur_state_t ?t2)
            
            (forall (?s1 ?s2 - automaton_state)
                    (when (and(automaton ?s1 ?e ?s2)(clock ?s1 ?s2))
                          (and (assign (start_clock)(timestamp ?t1 ?t2)))))
            
            (forall (?s1 ?s2 - automaton_state)
                    (when (and (cur_state_s ?s1)(automaton ?s1 ?e ?s2))
                          (and (not (cur_state_s ?s1))(cur_state_s ?s2))))
            )
            
    )
    
    
    (:action add
    :parameters (?e - activity)
    :precondition (exists (?s1 ?s2 - automaton_state)
                  (and (automaton ?s1 ?e ?s2)(cur_state_s ?s1)(or (and (<= (- (+(current_timestamp)0.1)(start_clock))(max_t_condition ?s1 ?s2 ?e))
                                             (>= (- (+(current_timestamp)0.1)(start_clock))(min_t_condition ?s1 ?s2 ?e)))
                                             ( = (current_timestamp)0))))
    :effect (and (increase (total-cost) 1)
            (assign (current_timestamp) (+(current_timestamp)0.1))
            (forall (?s1 ?s2 - automaton_state)
            (when (and (cur_state_s ?s1) (automaton ?s1 ?e ?s2))
                   (and (not (cur_state_s ?s1))(cur_state_s ?s2))))
            )
    )
    
    (:action del
    :parameters (?t1 - trace_state ?e - activity ?t2 - trace_state)
    :precondition (and (cur_state_t ?t1) (trace ?t1 ?e ?t2))
    :effect (and 
            (increase (total-cost) 1)
             (not (cur_state_t ?t1)) (cur_state_t ?t2)
             )
    
   
    )
)