import os
import argparse
import subprocess
import csv

from log_processing import process_log_file
from decl_processing import process_decl_file
from pddl_creation import create_pddl_files

def process_files(file_log, file_decl, user_input):
    # Processare il file .xes
    print(f"Processing .xes file: {file_log}")
    trace_activity, activities_trace = process_log_file(file_log)
    print("Done!")

    # Processare il file .decl
    print(f"Processing decl file: {file_decl}")
    automata_dict, durations, timelags, activities, automata_list= process_decl_file(file_decl, user_input)
    print("Done!")

    # Creazione dei file PDDL
    print("Creating PDDL problem files...")
    create_pddl_files(trace_activity, automata_list, activities_trace, automata_dict, durations, timelags, activities, user_input)
    print("Done!")

def main():
    
    # Creare il parser per gli argomenti
    parser = argparse.ArgumentParser(description='Process a .xes and a .decl file.')
    parser.add_argument('-log', '--log_file', type=str, required=True, help='The .xes log file to be processed')
    parser.add_argument('-decl', '--decl_file', type=str, required=True, help='The .decl file to be processed')
    parser.add_argument('-dom', '--domain', type=str, required=True, help='The domain name')

    # Parsing degli argomenti
    args = parser.parse_args()

    # Scegliere il dominio
    domains = ["LTL-d", "MTL", "MTL-d"]

    # Verificare che l'input sia valido
    if args.domain not in domains:
        print("Invalid input. Insert one of these options: LTL-d, MTL, MTL-d.")
        return

    # Processare i file
    process_files(args.log_file, args.decl_file, args.domain)

    rows = []
    output_directory = "Problems"  # Sostituisci con il percorso corretto

    confirm = input(f"Do you want to execute the planner ? (y/n): ").strip().lower()
    if confirm == 'y':
        # Itera su tutti i file nella cartella 'Problems'
        for filename in os.listdir(output_directory):
            if filename.startswith('.'):
                continue
            filepath = os.path.join(output_directory, filename)
            
            # Controlla se il file è un file normale (evita directory, ecc.)
            if os.path.isfile(filepath):
                # Comando Java da eseguire
                if args.domain == 'MTL':
                    command = [
                        "/Library/Java/JavaVirtualMachines/jdk-17.0.5.jdk/Contents/Home/bin/java", "-jar", "enhsp-dist/enhsp.jar",
                        "-o", "../Domains/mtl.pddl",
                        "-f", f"../{filepath}",  # Usa il file corrente
                        "-planner", "opt-blind"
                    ]
                elif args.domain == 'MTL-d':
                    command = [
                        "/Library/Java/JavaVirtualMachines/jdk-17.0.5.jdk/Contents/Home/bin/java", "-jar", "enhsp-dist/enhsp.jar",
                        "-o", "../Domains/mtl_durations.pddl",
                        "-f", f"../{filepath}",  # Usa il file corrente
                        "-planner", "opt-blind"
                    ]
                else:
                    command = [
                        "/Library/Java/JavaVirtualMachines/jdk-17.0.5.jdk/Contents/Home/bin/java", "-jar", "enhsp-dist/enhsp.jar",
                        "-o", "../Domains/align_time.pddl",
                        "-f", f"../{filepath}",  # Usa il file corrente
                        "-planner", "opt-blind"
                    ]

                # Chiede conferma all'utente
                # Specifica la directory di lavoro
                working_directory = "ENHSP-Public-enhsp-20"
                try:
                    # Esegue il comando e mostra l'output in tempo reale
                    result = subprocess.run(command, cwd=working_directory, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    print(result.stdout)
                    print(f"Comando eseguito con successo per il file {filename}")

                    # Processa l'output del comando
                    output_lines = result.stdout.splitlines()
                    plan = []
                    plan_length = ""
                    metric = ""
                    planning_time = ""
                    capturing_plan = False

                    for line in output_lines:
                        if line.startswith("Found Plan:"):
                            capturing_plan = True
                            plan = ""  # Resetta il piano
                        elif line.startswith("Plan-Length:"):
                            plan_length = line.split(":")[1].strip()
                            capturing_plan = False  # Fine del piano
                        elif capturing_plan and ":" in line:
                            plan += line
                            plan+= '\n'
                        elif line.startswith("Metric (Search):"):
                            metric = line.split(":")[1].strip()
                        elif line.startswith("Planning Time (msec):"):
                            planning_time = line.split(":")[1].strip()
                            # Aggiungi i dati estratti alla lista `rows`
                    rows.append({
                        "Filename": filename,
                        "Plan": plan,
                        "Planning Time": planning_time,
                        "Plan-Length": plan_length,
                        "Metric": metric
                    })
                except subprocess.CalledProcessError as e:
                    print(f"Errore durante l'esecuzione del comando per il file {filename}")
                    print("Codice di ritorno:", e.returncode)
                    print("Errore:\n", e.stderr)
                
    csv_file_path = "results.csv"

    # Scrive i dati nel file CSV
    with open(csv_file_path, mode='w', newline='') as csv_file:
        fieldnames = ["Filename", "Plan", "Planning Time", "Plan-Length", "Metric"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        
        writer.writeheader()  # Scrive l'intestazione
        for row in rows:
            writer.writerow(row)

    print(f"I dati sono stati salvati correttamente nel file: {csv_file_path}")


if __name__ == '__main__':
    main()