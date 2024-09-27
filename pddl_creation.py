import os
from helpers import extract_states, extract_final_states

def create_pddl_files(trace_activity, automata_list, activities_trace, automata_dict, durations, timelags, activities, user_input):
    output_dir = 'Problems'
    os.makedirs(output_dir, exist_ok=True)
    for template_activity , time_constraints in automata_dict.items():
        template_type = template_activity.split('[')[0].strip()

    # Creazione dei file e scrittura delle sequenze di eventi
    for trace, events in trace_activity.items():
        file_path = os.path.join(output_dir, f"{trace}.pddl")
        with open(file_path, 'w') as f:
            f.write(f"(define (problem prob)\n")
            f.write(f"(:domain {user_input})\n")
            #objects
            f.write(f"(:objects \n")
            for i in range(len(events)+1):
                f.write(f"t{i} ")
            f.write(f"- trace_state\n")
            for automata in automata_list:
                states = extract_states(automata)
                for state in states:
                    f.write(f"{state} ")
            f.write(f"- automaton_state\n")
            appended = []
            for act in activities:
                
                if (act not in appended):
                    f.write(f"{act} ")
                    appended.append(act)
            f.write(f"- activity\n)\n")

            #init
            f.write(f"\n(:init\n")
            f.write(f";trace\n")
            f.write(f"(cur_state_t t0)\n")
            for i in range(len(events)):
                f.write(f"(trace t{i} {events[i].split(':')[0]} t{i+1})\n")
            f.write(f"(final_state_t t{i+1})\n")
            f.write(f"\n;automata\n")


            for automata in automata_list:
                f.write(f"{automata}\n\n")
            
            for i in range(len(events)):
                f.write(f"(= (timestamp t{i} t{i+1}) {events[i].split(':')[1]})\n")
            
            if (user_input =="LTL-d"):

                for i in range(len(events)):
                     f.write(f"\n(= (t_condition t{i} t{i+1}) 0)")
                
                for i in range(len(timelags)):
                    f.write(f"\n(time_condition {timelags[i][0]} {timelags[i][1]})")
                    f.write(f"\n(= (min_time_condition {timelags[i][0]} {timelags[i][1]}) {timelags[i][2]})\n")
                    f.write(f"(= (max_time_condition {timelags[i][0]} {timelags[i][1]}) {timelags[i][3]}) \n")
                       

            if (user_input == "MTL-d" or user_input =="LTL-d"):
                f.write("\n")
                current_timestamp = 0
                for i in range(len(events)):
                    f.write(f"(= (duration t{i} t{i+1}) {float(events[i].split(':')[1]) - float(current_timestamp)})\n")
                    current_timestamp = events[i].split(':')[1]
                f.write(f"(= (total_duration) 0)\n")

                
                duration_appended = []
                #definizione delle duration
                for i in range(len(durations)):
                    f.write(f"\n(= (min_duration {durations[i][0]}) {durations[i][1]})\n")
                    f.write(f"(= (max_duration {durations[i][0]}) {durations[i][2]})\n")
                    duration_appended.append(durations[i][0])
                
                for i in range(len(events)):
                    if (events[i].split(':')[0] not in duration_appended):
                        f.write(f"\n(= (min_duration {events[i].split(':')[0]}) 0)\n")
                        f.write(f"(= (max_duration {events[i].split(':')[0]}) 100)\n")
             
            
            if (user_input == "MTL-d" or user_input =="MTL"):
                 f.write(f"(= (start_clock) 0)\n")
            f.write(f"\n(= (current_timestamp) 0)\n(= (total-cost) 0)")
            f.write(f"\n)\n")

            goal_i = len(events)
            # goal
            f.write(f"(:goal (and ")
            f.write(f"(cur_state_t t{goal_i})")

            for automata in automata_list:
                 final_states = [state for state in extract_final_states(automata)]
                
                 if len(final_states) > 1:
                     f.write(f" (or ")
                     for state in final_states:
                         f.write(f"(cur_state_s {state}) ")
                     f.write(f")")
                 elif len(final_states) == 1:
                     f.write(f" (cur_state_s {final_states[0]})")
            
            f.write(f"))\n")
            f.write("(:metric minimize (total-cost))")

            
            f.write(f"\n)")
     
