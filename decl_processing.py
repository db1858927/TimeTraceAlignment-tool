import re
from helpers import check_duration_exists, check_timelags_exists, process_duration, process_timelags, extract_states, extract_time_constraints, process_declare

def process_decl_file(file_decl, user_input):

    time_constraints = []
    automata_dict = {}
    states = []
    activities = []
    durations =[]
    timelags = []
    automata_list = []

    # Lettura del file decl
    with open(file_decl, 'r') as file:
        for line in file:
            line = line.strip()
            duration_exists = check_duration_exists(line)
            if duration_exists:
                durations = process_duration(file_decl)
            timelags_exists = check_timelags_exists(line)
            if timelags_exists:
                timelags = process_timelags(file_decl)
            if line.startswith("activity"):
                activity = line.split()[1].strip()
                activities.append(activity)
            elif "|" in line:
                parts = line.split("|")
                template_info = parts[0].strip()
                values = parts[-1].strip()
                values = values.split('/')
                time_constraints = extract_time_constraints(values)
                template_key = f"{template_info}"
                template_type = template_key.split('[')[0].strip()
                automata_dict[template_key] = time_constraints
                automata_list = process_declare(automata_dict, user_input, activities)
                
                for automata in automata_list:
                    state = extract_states(automata)
                
    
    return automata_dict, durations, timelags, activities, automata_list