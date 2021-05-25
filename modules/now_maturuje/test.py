
import schedule_reader
import os

test = schedule_reader.read_schedule(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "schedule.csv"))

pass