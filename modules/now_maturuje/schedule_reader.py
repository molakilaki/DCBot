
import csv

def read_schedule(filename: str):
    schedule = dict()

    curr_day = None

    with open(filename, "r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)

        for row in reader:

            if row[0] != "":
                curr_day = int(row[0])

            if curr_day == None:
                raise RuntimeError("u prvního řádku není určen den")

            if curr_day not in schedule:
                schedule[curr_day] = list() # inicializace prázdného listu, pokud jsme tenhle den ještě neviděli

            schedule[curr_day].append(row[1:]) # přidat pepka na seznam pro aktuální den

    return schedule