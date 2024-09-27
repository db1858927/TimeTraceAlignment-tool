import pm4py
from datetime import datetime

def process_log_file(file_log):

    log = pm4py.read_xes(file_log)

    trace_activity = {}
    activities_trace = []

    timestamps = [datetime.fromisoformat(str(ts)) for ts in log['time:timestamp']]
    first_timestamp = timestamps[0]
    

    for i in range(len(list(log['case:concept:name']))):
        name_trace = list(log['case:concept:name'])[i]
        if name_trace not in trace_activity:
            trace_activity[name_trace] = []
            # Impostiamo il primo timestamp della traccia come punto di riferimento
            first_timestamp = datetime.fromisoformat(str(log['time:timestamp'][i]))
        dt = datetime.fromisoformat(str(log['time:timestamp'][i]))
        delta = dt - first_timestamp
        hours = delta.total_seconds() / 3600  # Converte la differenza in ore
        
        # Aggiungi l'attività con il timestamp in ore
        trace_activity[name_trace].append(f"{log['concept:name'][i]}:{hours:.2f}")
        activities_trace.append(list(log['concept:name'])[i])
     
    return trace_activity, activities_trace