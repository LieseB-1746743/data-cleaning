from data_cleaning.cleaningmodules.read_all_tables import read_all_tables
from os.path import abspath, split, join
from pathlib import Path

(head, tail) = split(abspath(__file__))
filepath = join(str(Path(head).parents[0]), "tables.txt")
tables, tablenames, foreign_keys, global_settings = read_all_tables(filepath)
