(define (domain LTL-d)
    (:requirements :strips :typing :equality :adl :fluents)
    
    (:types activity automaton_state trace_state)
            
    (:predicates 
        ;there exists a transition in the trace automaton from two different states t1 and t2, 
        ;being e the activity involved in the transition
        (trace ?t1 - trace_state ?e - activity ?t2 - trace_state)
        
        ;there exists a transition from two different states s1 to s2 of a constraint automaton, 
        ;being e the activity involved in the transition.
        (automaton ?s1 - automaton_state ?e - activity ?s2 - automaton_state)
        
        ;the current state of a constraint/trace automaton
        (cur_state_t ?t - trace_state)
        (cur_state_s ?s - automaton_state)
        
        ;final accepting state of a constraint/trace automaton.
        (final_state_t ?t - trace_state) 
        (final_state_s ?s - automaton_state) 
        
        (time_condition ?e1 ?e2 - activity)
       
        
    )
    
    (:functions
        (total-cost)
        (total_duration)
        (duration ?t1 ?t2 - trace_state)
        (min_duration ?e - activity)
        (max_duration ?e - activity)
        (timestamp ?t1 ?t2 - trace_state)
        (min_time_condition ?e1 ?e2 - activity)
        (max_time_condition ?e1 ?e2 - activity)
        (t_condition ?t1 ?t2 - trace_state)
        (current_timestamp)
        (save_timestamp)
    )
    
    
    (:action sync
    :parameters (?t1 - trace_state ?e - activity ?t2 - trace_state)
    :precondition (and (cur_state_t ?t1) (trace ?t1 ?e ?t2) 
                  (<= (duration ?t1 ?t2) (max_duration ?e))
                  (>= (duration ?t1 ?t2) (min_duration ?e))
                  ( = (t_condition ?t1 ?t2) 0))
                 
    :effect (and (not (cur_state_t ?t1)) (cur_state_t ?t2)
            ;check if there is a time condition between two activity
            (forall (?l1 ?l2 - trace_state ?e1 - activity)
                (when (and (trace ?l1 ?e1 ?l2)(>(timestamp ?l1 ?l2)(timestamp ?t1 ?t2))
                    (or (> (- (timestamp ?l1 ?l2)(timestamp ?t1 ?t2))(max_time_condition ?e ?e1))
                    (< (- (timestamp ?l1 ?l2)(timestamp ?t1 ?t2))(min_time_condition ?e ?e1))))
                    (and (assign (t_condition ?l1 ?l2) 1)(assign(save_timestamp)(timestamp ?t1 ?t2)))))
            
            (forall (?s1 ?s2 - automaton_state)
                    (when (and (cur_state_s ?s1)(automaton ?s1 ?e ?s2))
                          (and (not (cur_state_s ?s1))(cur_state_s ?s2))))
            
            (increase (total_duration)(duration ?t1 ?t2))
            (assign (current_timestamp)(timestamp ?t1 ?t2)))
    )
    
    (:action shrinked_sync_min
    :parameters (?t1 - trace_state ?e - activity ?t2 - trace_state)
    :precondition (and (cur_state_t ?t1) (trace ?t1 ?e ?t2) 
                  (< (duration ?t1 ?t2) (min_duration ?e))
                  ( = (t_condition ?t1 ?t2) 0))
    
    :effect (and (not (cur_state_t ?t1)) (cur_state_t ?t2)
            
            ;increse all the subsequent timestamp
            (forall (?l1 ?l2 - trace_state ?e1 - activity)
            (when (and (trace ?l1 ?e1 ?l2)(> (timestamp ?l1 ?l2)(current_timestamp)))
                  (and (increase (timestamp ?l1 ?l2)(-(min_duration ?e)(duration ?t1 ?t2))))))
            
            (forall (?s1 ?s2 - automaton_state)
                    (when (and (cur_state_s ?s1)(automaton ?s1 ?e ?s2))
                            (and (not (cur_state_s ?s1))(cur_state_s ?s2))))
            
            
            ;check if there is a time condition between two activity
            (forall (?l1 ?l2 - trace_state ?e1 - activity)
                (when (and (trace ?l1 ?e1 ?l2)(> (timestamp ?l1 ?l2)(current_timestamp))
                (or (> (- (timestamp ?l1 ?l2)(timestamp ?t1 ?t2))(max_time_condition ?e ?e1))
                    (< (- (timestamp ?l1 ?l2)(timestamp ?t1 ?t2))(min_time_condition ?e ?e1))))
                  (and(assign(t_condition ?l1 ?l2) 1)(assign(save_timestamp)(+(timestamp ?t1 ?t2)(-(min_duration ?e)(duration ?t1 ?t2)))))))
                  
            (increase (total_duration)(min_duration ?e))
            (increase (total-cost) 1)
            (increase (current_timestamp)(min_duration ?e))
            )
            
    )

    (:action shrinked_sync_max
    :parameters (?t1 - trace_state ?e - activity ?t2 - trace_state)
    :precondition (and (cur_state_t ?t1) (trace ?t1 ?e ?t2) 
                  (> (duration ?t1 ?t2) (max_duration ?e))
                  ( = (t_condition ?t1 ?t2) 0))
                  
    :effect (and (not (cur_state_t ?t1)) (cur_state_t ?t2)
            ;increse all the subsequent timestamp
            (forall (?l1 ?l2 - trace_state ?e1 - activity)
            (when (and (trace ?l1 ?e1 ?l2)(> (timestamp ?l1 ?l2)(current_timestamp)))
                  (and (decrease (timestamp ?l1 ?l2) (-(duration ?t1 ?t2)(max_duration ?e))))))
            
            (forall (?s1 ?s2 - automaton_state)
                    (when (and (cur_state_s ?s1)(automaton ?s1 ?e ?s2))
                            (and (not (cur_state_s ?s1))(cur_state_s ?s2))))
            
            ;check if there is a time condition between two activity
            (forall (?l1 ?l2 - trace_state ?e1 - activity)
                (when (and (trace ?l1 ?e1 ?l2)(> (timestamp ?l1 ?l2)(current_timestamp))
                (or (> (- (timestamp ?l1 ?l2)(timestamp ?t1 ?t2))(max_time_condition ?e ?e1))
                    (< (- (timestamp ?l1 ?l2)(timestamp ?t1 ?t2))(min_time_condition ?e ?e1))))
                  (and(assign(t_condition ?l1 ?l2) 1)(assign(save_timestamp)(-(timestamp ?t1 ?t2)(-(duration ?t1 ?t2)(max_duration ?e)))))))
                  
            (increase (total_duration)(max_duration ?e))
            (increase (total-cost) 1)
            (increase (current_timestamp)(max_duration ?e))
            
            )
            
    )
    
    (:action add
    :parameters (?e - activity)
    :precondition (not (exists (?e1 - activity)(time_condition ?e1 ?e)))
    :effect (and (increase (total-cost) 2)
            (forall (?l1 ?l2 - trace_state ?e1 - activity)
            (when (and (trace ?l1 ?e1 ?l2)(> (timestamp ?l1 ?l2)(current_timestamp)))
                  (and (increase (timestamp ?l1 ?l2)(min_duration ?e)))))
            (forall (?s1 ?s2 - automaton_state)
            (when (and (cur_state_s ?s1) (automaton ?s1 ?e ?s2))
                   (and (not (cur_state_s ?s1))(cur_state_s ?s2))))
            (increase (total-duration)(min_duration ?e))
            (increase (current_timestamp)(min_duration ?e)))
    )
    
    (:action add_condition
    :parameters (?e - activity)
    :precondition (exists (?e1 - activity)(and (time_condition ?e1 ?e)
                 (>= (- (+ (current_timestamp)(min_duration ?e))(save_timestamp))(min_time_condition ?e1 ?e))
                 (<= (- (+ (current_timestamp)(min_duration ?e))(save_timestamp))(max_time_condition ?e1 ?e))))
    :effect (and (increase (total-cost) 2)
            (forall (?l1 ?l2 - trace_state ?e1 - activity)
            (when (and (trace ?l1 ?e1 ?l2)(> (timestamp ?l1 ?l2)(current_timestamp)))
                  (and (increase (timestamp ?l1 ?l2)(min_duration ?e)))))
            (forall (?s1 ?s2 - automaton_state)
            (when (and (cur_state_s ?s1) (automaton ?s1 ?e ?s2))
                   (and (not (cur_state_s ?s1))(cur_state_s ?s2))))
            (increase (total-duration)(min_duration ?e))
            (increase (current_timestamp)(min_duration ?e)))
    )
    
    (:action del
    :parameters (?t1 - trace_state ?e - activity ?t2 - trace_state)
    :precondition (and (cur_state_t ?t1) (trace ?t1 ?e ?t2))
    :effect (and (not (cur_state_t ?t1)) (cur_state_t ?t2)
            (increase (total-cost) 4)
            (forall (?l1 ?l2 - trace_state ?e1 - activity)
            (when (and (trace ?l1 ?e1 ?l2)(> (timestamp ?l1 ?l2)(timestamp ?t1 ?t2)))
                  (and (decrease (timestamp ?l1 ?l2)(duration ?t1 ?t2)))))))
                  
           
             
    
)