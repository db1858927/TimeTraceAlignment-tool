import re

def check_duration_exists(input_lines):
    if 'Duration' in input_lines:
            return True
    return False

def check_timelags_exists(input_lines):
    if 'Time-Lags' in input_lines:
            return True
    return False

def extract_activity(line):
    # Espressione regolare per catturare l'attività dalla riga 'bind A: Duration'
    activity_pattern = re.compile(r'\bbind\s+(\w+):\s*Duration\b', re.IGNORECASE)
    match = activity_pattern.match(line)
    if match:
        return match.group(1)
    return None

def extract_duration(line):
    # Espressione regolare per catturare la durata dalla riga 'Duration: integer between 1 and 4'
    duration_pattern = re.compile(r'Duration:\s*(integer|float)\s*between\s*(\d+(\.\d+)?)\s*and\s*(\d+(\.\d+)?)', re.IGNORECASE)
    match = duration_pattern.match(line)
    if match:
        min_duration = match.group(2)
        max_duration = match.group(4)
        return min_duration, max_duration
    return None, None

def extract_timelags(line):
    # Espressione regolare per catturare la durata dalla riga 'Duration: integer between 1 and 4'
    timelags_pattern = re.compile(r'Time-Lags\s*(\w+)-(\w+):\s*(integer|float)\s*between\s*(\d+(\.\d+)?)\s*and\s*(\d+(\.\d+)?)', re.IGNORECASE)
    match = timelags_pattern.match(line)
    if match:
        activity1 = match.group(1)
        activity2 = match.group(2)
        min_time_condition = match.group(4)
        max_time_condition = match.group(6)
                
        return activity1,activity2, min_time_condition, max_time_condition
    return None, None, None, None

def process_duration(file_path):
    current_activity = None
    results = []

    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            
            # Estrai l'attività
            activity = extract_activity(line)
            if activity:
                current_activity = activity
                continue
            
            # Estrai la durata
            min_duration, max_duration = extract_duration(line)
            if min_duration and max_duration and current_activity:
                results.append((current_activity, min_duration, max_duration))
                current_activity = None  # Resetta l'attività corrente dopo aver aggiunto

    return results

def process_timelags(file_path):
    
    results = []

    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            
            # Estrai la timelags
            activity1, activity2, min_time_condition, max_time_condition = extract_timelags(line)
            if min_time_condition and max_time_condition:
                results.append((activity1, activity2, min_time_condition, max_time_condition))
                

    return results

def extract_time_constraints(values):
    
    constraints_list = []
    for constraint in values:
        parts = constraint.split(',')
        activity = parts[0].strip() 
        min_time = parts[1].strip() if len(parts) > 1 else 0
        max_time = parts[2].strip() if len(parts) > 2 else 10000
        
        
        constraints_list.append((activity, min_time, max_time))
    
    return constraints_list

def extract_states(automaton):
    
    states = set()
    
    # Usa una regex per trovare tutti gli stati nel formato lettera + numero (es. a0, b1, c2)
    matches = re.findall(r'\b[a-z]\d+\b', automaton)
    
    for match in matches:
        states.add(match)
    
    # Ordina gli stati per avere una lista ordinata
    sorted_states = sorted(states)
    
    return sorted_states

def extract_final_states(automaton):
    
    states = set()
    
    # Usa una regex per trovare tutti gli stati nel formato lettera + numero (es. a0, b1, c2)
    matches = re.findall(r'final_state_s \b[a-z]\d+\b', automaton)
    for match in matches:
        state = re.findall(r'\b[a-z]\d+\b', match)
        for s in state:
            states.add(s)
        
    
    
    # Ordina gli stati per avere una lista ordinata
    sorted_states = sorted(states)
    
    return sorted_states

def process_declare(automata_dict, user_input, events):

    # -----------EXISTENCE TEMPLATE-------------------#
    def handle_existence(activity,min_time,max_time):
        result = f";existence\n(cur_state_s a0)\n(automaton a0 {activity} a1)\n(final_state_s a1)\n"
        if (user_input == 'MTL' or user_input == 'MTL-d'):
            result += f"\n(= (min_t_condition a0 a1 {activity}) {min_time})\n(= (max_t_condition a0 a1 {activity}) {max_time})\n"
        return result
    # -----------CHOICE TEMPLATE-------------------;
    def handle_choice(activity1, activity2, time_constraints):
        result = f";choice\n(cur_state_s b0)\n(automaton b0 {activity1} b1)(automaton b0 {activity2} b1)\n(final_state_s b1)\n"
       
        if (user_input == 'MTL' or user_input == 'MTL-d'):
            for (activity, min_time, max_time) in time_constraints:
                if activity:
                    result += f"(= (min_t_condition b0 b1 {activity}) {min_time})\n(= (max_t_condition b0 b1 {activity}) {max_time})\n"
                else:
                    result += f"(= (min_t_condition b0 b1 {activity1}) 0)\n(= (max_t_condition b0 b1 {activity1}) 10000)\n"
                    result += f"(= (min_t_condition b0 b1 {activity2}) 0)\n(= (max_t_condition b0 b1 {activity2}) 10000)\n"
            return result
   
    def handle_exclusive_choice(activity1, activity2, time_constraints):
        result = f";exclusive-choice\n(cur_state_s c0)\n(automaton c0 {activity2} c1)(automaton c0 {activity1} c3)(automaton c3 {activity2} c2)(automaton c1 {activity1} c2)\n(final_state_s c0)(final_state_s c1)(final_state_s c3)\n"
        transitions = [
            ('c0', 'c3', activity1),
            ('c0', 'c1', activity2),
        ]
        if (user_input == 'MTL' or user_input == 'MTL-d'):
            result += f"\n(clock c0 c3)\n(clock c0 c1)\n\n"
            for (from_state, to_state, activity) in transitions:
                for (act, min_time, max_time) in time_constraints:
                    if act == activity:
                        result += f"(= (min_t_condition {from_state} {to_state} {activity}) {min_time})\n"
                        result += f"(= (max_t_condition {from_state} {to_state} {activity}) {max_time})\n"
                    else:
                        result += f"(= (min_t_condition {from_state} {to_state} {activity}) 0)\n"
                        result += f"(= (max_t_condition {from_state} {to_state} {activity}) 10000)\n"
            
            result += f"(= (min_t_condition c3 c2 {activity2}) 0)\n"
            result += f"(= (max_t_condition c3 c2 {activity2}) 10000)\n"
            result += f"(= (min_t_condition c1 c2 {activity1}) 0)\n"
            result += f"(= (max_t_condition c1 c2 {activity1}) 10000)\n"
        return result
    
    #----------------RELATION TEMPLATE-------------------
    def handle_response(activity1, activity2, time_constraints):
        result = f";Response \n(cur_state_s d0)\n(automaton d0 {activity1} d1)\n(automaton d1 {activity2} d0)\n(final_state_s d0)"
        if (user_input == 'MTL' or user_input == 'MTL-d'):
            result += f"\n(clock d0 d1)\n\n"

            for (act, min_time, max_time) in time_constraints:
                if act:
                    result += f"(= (min_t_condition d1 d0 {activity2}) {min_time})\n"
                    result += f"(= (max_t_condition d1 d0 {activity2}) {max_time})\n"
                else:
                    result += f"(= (min_t_condition d1 d0 {activity2}) 0)\n"
                    result += f"(= (max_t_condition d1 d0 {activity2}) 10000)\n"
                
                result += f"(= (min_t_condition d0 d1 {activity1}) 0)\n"
                result += f"(= (max_t_condition d0 d1 {activity1}) 10000)\n"
        return result

    def handle_alternate_response(activity1, activity2, time_constraints):
        result = f";Alternate Response \n(cur_state_s e0)\n(automaton e0 {activity1} e1)(automaton e1 {activity2} e0)(automaton e1 {activity1} e2)\n(final_state_s e0)"
        if (user_input == 'MTL' or user_input == 'MTL-d'):
            result += f"\n(clock e0 e1)\n\n"

            for (act, min_time, max_time) in time_constraints:
                    
                result += f"(= (min_t_condition e1 e0 {activity2}) 0)\n"
                result += f"(= (max_t_condition e1 e0 {activity2}) 10000)\n"
                
                result += f"(= (min_t_condition e0 e1 {activity1}) {min_time})\n"
                result += f"(= (max_t_condition e0 e1 {activity1}) {max_time})\n"

                result += f"(= (min_t_condition e1 e2 {activity1}) 0)\n"
                result += f"(= (max_t_condition e1 e2 {activity1}) 10000)\n"
        return result
    
    
    def handle_precedence(activity1, activity2,time_constraints):
        result = f";Precedence \n(cur_state_s g0)(automaton g0 {activity2} g1)(automaton g0 {activity1} g2)(automaton g2 {activity2} g3)(final_state_s g0)(final_state_s g2)(final_state_s g3)\n"
        if (user_input == 'MTL' or user_input == 'MTL-d'):
            result += f"\n(clock g0 g2)\n\n"

            for (act, min_time, max_time) in time_constraints:
                result += f"(= (min_t_condition g2 g3 {activity2}) {min_time})\n"
                result += f"(= (max_t_condition g2 g3 {activity2}) {max_time})\n"
                
                result += f"(= (min_t_condition g0 g1 {activity1}) 0)\n"
                result += f"(= (max_t_condition g0 g1 {activity1}) 10000)\n"

                result += f"(= (min_t_condition g0 g2 {activity1}) 0)\n"
                result += f"(= (max_t_condition g0 g2 {activity1}) 10000)\n"

        return result

    
    def handle_alternate_precedence(activity1, activity2,time_constraints):
        result = f";Alternate Precedence \n(cur_state_s h0)\n(automaton h0 {activity2} h1)(automaton h0 {activity1} h2)(automaton h2 {activity2} h0)\n(final_state_s h0)\n"
        if (user_input == 'MTL' or user_input == 'MTL-d'):
            result += f"\n(clock h0 h2)\n\n"

            for (act, min_time, max_time) in time_constraints:
                result += f"(= (min_t_condition h2 h0 {activity2}) {min_time})\n"
                result += f"(= (max_t_condition h2 h0 {activity2}) {max_time})\n"
                
                result += f"(= (min_t_condition h0 h1 {activity2}) 0)\n"
                result += f"(= (max_t_condition h0 h1 {activity2}) 10000)\n"

                result += f"(= (min_t_condition h0 h2 {activity1}) 0)\n"
                result += f"(= (max_t_condition h0 h2 {activity1}) 10000)\n"

        return result

    
    def handle_responded_existence(activity1, activity2,time_constraints):
        result = f";Responded Existence \n(cur_state_s l0)\n(automaton l0 {activity2} l1)(automaton l0 {activity1} l2)(automaton l2 {activity2} l1)\n(final_state_s l0)(final_state_s l1)\n"
        if (user_input == 'MTL' or user_input == 'MTL-d'):
            result += f"\n(clock l0 l2)\n\n"

            for (act, min_time, max_time) in time_constraints:
                result += f"(= (min_t_condition l2 l1 {activity2}) {min_time})\n"
                result += f"(= (max_t_condition l2 l1 {activity2}) {max_time})\n"
                
                result += f"(= (min_t_condition l0 l1 {activity2}) 0)\n"
                result += f"(= (max_t_condition l0 l1 {activity2}) 10000)\n"

                result += f"(= (min_t_condition l0 l2 {activity1}) 0)\n"
                result += f"(= (max_t_condition l0 l2 {activity1}) 10000)\n"

        return result
    
    def handle_co_existence(activity1, activity2,time_constraints):
        result = f";Co Existence \n(cur_state_s m0)\n(automaton m0 {activity2} m1)(automaton m0 {activity1} m3)(automaton m1 {activity1} m2)(automaton m3 {activity2} m2)\n(final_state_s m0)(final_state_s m2)\n"
        if (user_input == 'MTL' or user_input == 'MTL-d'):
            result += f"\n(clock m0 m1)\n(clock m0 m3)\n\n"
            
            for (act, min_time, max_time) in time_constraints:
                
                if act == activity1:
                    result += f"(= (min_t_condition m1 m2 {activity1}) {min_time})\n"
                    result += f"(= (max_t_condition m1 m2 {activity1}) {max_time})\n"
                else:
                    result += f"(= (min_t_condition m1 m2 {activity1}) 0)\n"
                    result += f"(= (max_t_condition m1 m2 {activity1}) 10000)\n"
                if act == activity2:
                    result += f"(= (min_t_condition m3 m2 {activity2}) {min_time})\n"
                    result += f"(= (max_t_condition m3 m2 {activity2}) {max_time})\n"
                else: 
                    result += f"(= (min_t_condition m3 m2 {activity2}) 0)\n"
                    result += f"(= (max_t_condition m3 m2 {activity2}) 10000)\n"

            result += f"(= (min_t_condition m0 m1 {activity2}) 0)\n"
            result += f"(= (max_t_condition m0 m1 {activity2}) 10000)\n"

            result += f"(= (min_t_condition m0 m3 {activity1}) 0)\n"
            result += f"(= (max_t_condition m0 m3 {activity1}) 10000)\n"

        return result
    
    def handle_succession(activity1,activity2,time_constraints):
        result = f";Succession \n(cur_state_s n0)\n(automaton n0 {activity2} n1)(automaton n0 {activity1} n2)(automaton n2 {activity2} n3)(automaton n3 {activity1} n2)\n(final_state_s n0)(final_state_s n3)\n"
        if (user_input == 'MTL' or user_input == 'MTL-d'):
            result += f"\n(clock n0 n2)\n(clock n3 n2)\n\n"
            
            for (act, min_time, max_time) in time_constraints:
                
                result += f"(= (min_t_condition n2 n3 {activity2}) {min_time})\n"
                result += f"(= (max_t_condition n2 n3 {activity2}) {max_time})\n"

            result += f"(= (min_t_condition n3 n2 {activity1}) 0)\n"
            result += f"(= (max_t_condition n3 n2 {activity1}) 10000)\n"
                    
            result += f"(= (min_t_condition n0 n1 {activity2}) 0)\n"
            result += f"(= (max_t_condition n0 n1 {activity2}) 10000)\n"

            result += f"(= (min_t_condition n0 n2 {activity1}) 0)\n"
            result += f"(= (max_t_condition n0 n2 {activity1}) 10000)\n"

        return result
    
    def handle_alternate_succession(activity1,activity2,time_constraints):
        result = f";Alternate Succession \n(cur_state_s n0)\n(automaton n0 {activity2} n1)(automaton n0 {activity1} n2)(automaton n2 {activity2} n0)(automaton n2 {activity1} n1)\n(final_state_s n0)\n"
        if (user_input == 'MTL' or user_input == 'MTL-d'):
            result += f"\n(clock n0 n2)\n\n"
            
            for (act, min_time, max_time) in time_constraints:
                
                result += f"(= (min_t_condition n2 n0 {activity2}) {min_time})\n"
                result += f"(= (max_t_condition n2 n0 {activity2}) {max_time})\n"

            result += f"(= (min_t_condition n2 n1 {activity1}) 0)\n"
            result += f"(= (max_t_condition n2 n1 {activity1}) 10000)\n"
                    
            result += f"(= (min_t_condition n0 n1 {activity2}) 0)\n"
            result += f"(= (max_t_condition n0 n1 {activity2}) 10000)\n"

            result += f"(= (min_t_condition n0 n2 {activity1}) 0)\n"
            result += f"(= (max_t_condition n0 n2 {activity1}) 10000)\n"

        return result
    
    def handle_chain_response(activity1,activity2,time_constraints):
        return  handle_chain_res(automata_dict,events)
    
    def handle_chain_succession(activity1,activity2,time_constraints):
        template_type = 'Chain Succession'
        return  handle_chain_succ(automata_dict,events)
    
    def handle_chain_precedence(activity1,activity2,time_constraints):
        template_type = 'Chain Precedence'
        return  handle_chain_prec(automata_dict,events)
  


    # Templates
    templates = {
        'Existence': handle_existence,
        'Choice': handle_choice,
        'Exclusive Choice': handle_exclusive_choice,
        'Response': handle_response,
        'Alternate Response': handle_alternate_response,
        'Precedence' : handle_precedence,
        'Alternate Precedence': handle_alternate_precedence,
        'Responded Existence' : handle_responded_existence,
        'Co-Existence':handle_co_existence,
        'Succession' : handle_succession,
        'Alternate Succession': handle_alternate_succession,
        'Chain Response': handle_chain_response,
        'Chain Succession': handle_chain_succession,
        'Chain Precedence': handle_chain_precedence
        
        
    }

    automata_lines = []

    # Itera attraverso il dizionario automata_dict
    for template_activity, time_constraints in automata_dict.items():
       
        template_type = template_activity.split('[')[0].strip()

        
        if template_type not in templates:
            return f"Template non supportato: {template_type}"

        activities_part = template_activity.split('[')[1].strip(']').strip()
        activities = activities_part.split(',')

        if len(activities) == 1:
            if time_constraints[0][0]:
                activity, min_time, max_time = time_constraints[0]
            else:
                # Altrimenti usa valori predefiniti
                activity = activities[0]
                min_time = 0
                max_time = 10000
            
            automata_lines.append(templates[template_type](activity, min_time, max_time))
        else:
            automata_lines.append(templates[template_type](*activities, time_constraints))

    
    return automata_lines

def handle_chain_res(automata_dict,events):

    result=''
    
    
    for template_activity , time_constraints in automata_dict.items():
        template_type = template_activity.split('[')[0].strip()
        activities_part = template_activity.split('[')[1].strip(']').strip()
        activities = activities_part.split(':')
        
        if len(activities) == 1:
            if time_constraints[0][0]:
                activity, min_time, max_time = time_constraints[0]
            else:
                # Altrimenti usa valori predefiniti
                activity = activities[0]
                min_time = 0
                max_time = 10000
        
        
        if template_type == 'Chain Response':
            for activity in activities:
                result+=(f";Chain Response \n(cur_state_s f0)\n(automaton f0 {activity[0]} f1)(automaton f1 {activity[3]} f0)")
            for i in range(len(events)):
                for activity in activities:
                    if (events[i].split(':')[0] != activity[2]):
                        result+=(f"(automaton f1 {events[i].split(':')[0]} f2)")
            result+=("(final_state_s f0)\n")
            result+=("\n(clock f0 f1)\n\n")
            
            for i in range(len(events)):
                for activity in activities:
                    if (events[i].split(':')[0] != activity[2]):
                        result+=(f"(= (min_t_condition f1 f2 {events[i].split(':')[0]}) 0)\n")
                        result+=(f"(= (max_t_condition f1 f2 {events[i].split(':')[0]}) 10000)\n")
            
            for (act, min_time, max_time) in time_constraints:
                if (act == activity[2]):
                    result += f"(= (min_t_condition f1 f0 {activity[3]}) {min_time})\n"
                    result += f"(= (max_t_condition f1 f0 {activity[3]}) {max_time})\n"
                else:
                    result += f"(= (min_t_condition f2 f0 {activity[3]}) 0)\n"
                    result += f"(= (max_t_condition f2 f0 {activity[3]}) 10000)\n"
            
            result += f"(= (min_t_condition f0 f1 {activity[0]}) 0)\n"
            result += f"(= (max_t_condition f0 f1 {activity[0]}) 10000)\n\n"

    return result

def handle_chain_prec(automata_dict,events):
    result=''
    
    for template_activity , time_constraints in automata_dict.items():
        template_type = template_activity.split('[')[0].strip()
        activities_part = template_activity.split('[')[1].strip(']').strip()
        activities = activities_part.split(':')
        
        if len(activities) == 1:
            if time_constraints[0][0]:
                activity, min_time, max_time = time_constraints[0]
            else:
                # Altrimenti usa valori predefiniti
                activity = activities[0]
                min_time = 0
                max_time = 10000
        
        if template_type == 'Chain Precedence':
            for activity in activities:
                result+=(f";Chain Precedence \n(cur_state_s i0)\n(automaton i0 {activity[3]} i1)(automaton i0 {activity[0]} i2)")
            for i in range(len(events)):
                for activity in activities:
                    if (events[i].split(':')[0] != activity[0]):
                        result+=(f"(automaton i2 {events[i].split(':')[0]} i0)")
            result+=("(final_state_s i0)\n")
            result+=("\n(clock i0 i2)\n\n")
            
            for i in range(len(events)):
                for activity in activities:
                    if (events[i].split(':')[0] != activity[0]):
                        result+=(f"(= (min_t_condition i2 i0 {events[i].split(':')[0]}) 0)\n")
                        result+=(f"(= (max_t_condition i2 i0 {events[i].split(':')[0]}) 10000)\n")
            
            for (act, min_time, max_time) in time_constraints:
                
                if (act == activity[2]):
                    result += f"(= (min_t_condition i2 i0 {activity[3]}) {min_time})\n"
                    result += f"(= (max_t_condition i2 i0 {activity[3]}) {max_time})\n"
                else:
                    result += f"(= (min_t_condition i2 i0 {activity[3]}) 0)\n"
                    result += f"(= (max_t_condition i2 i0 {activity[3]}) 10000)\n"
            
            result += f"(= (min_t_condition i0 i1 {activity[3]}) 0)\n"
            result += f"(= (max_t_condition i0 i1 {activity[3]}) 10000)\n"

            result += f"(= (min_t_condition i0 i2 {activity[0]}) 0)\n"
            result += f"(= (max_t_condition i0 i2 {activity[0]}) 10000)\n\n"
    return result

def handle_chain_succ(automata_dict,events):
    result=''
    
    for template_activity , time_constraints in automata_dict.items():
        template_type = template_activity.split('[')[0].strip()
        activities_part = template_activity.split('[')[1].strip(']').strip()
        activities = activities_part.split(':')
        
        if len(activities) == 1:
            if time_constraints[0][0]:
                activity, min_time, max_time = time_constraints[0]
            else:
                # Altrimenti usa valori predefiniti
                activity = activities[0]
                min_time = 0
                max_time = 10000
        
        if template_type == 'Chain Succession':
            
            for activity in activities:
                result+=(f";Chain Succession \n(cur_state_s o0)\n(automaton o0 {activity[3]} o1)(automaton o0 {activity[0]} o2)(automaton o2 {activity[3]} o0)")
            for i in range(len(events)):
                for activity in activities:
                    if (events[i].split(':')[0] != activity[3]):
                        result+=(f"(automaton o2 {events[i].split(':')[0]} o1)")
            result+=("(final_state_s o0)\n")
            result+=("\n(clock o0 o2)\n\n")
            
            for i in range(len(events)):
                for activity in activities:
                    if (events[i].split(':')[0] != activity[3]):
                        result+=(f"(= (min_t_condition o2 o1 {events[i].split(':')[0]}) 0)\n")
                        result+=(f"(= (max_t_condition o2 o1 {events[i].split(':')[0]}) 10000)\n")
            
            for (act, min_time, max_time) in time_constraints:
                if (act == activity[3]):
                    result += f"(= (min_t_condition o2 o0 {activity[3]}) {min_time})\n"
                    result += f"(= (max_t_condition o2 o0 {activity[3]}) {max_time})\n"
                else:
                    result += f"(= (min_t_condition o2 o0 {activity[3]}) 0)\n"
                    result += f"(= (max_t_condition o2 o0 {activity[3]}) 10000)\n"
            
            result += f"(= (min_t_condition o0 o1 {activity[3]}) 0)\n"
            result += f"(= (max_t_condition o0 o1 {activity[3]}) 10000)\n"

            result += f"(= (min_t_condition o0 o2 {activity[0]}) 0)\n"
            result += f"(= (max_t_condition o0 o2 {activity[0]}) 10000)\n\n"

    return result