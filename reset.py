from os import listdir as files
from json import dump

path = "../data/training_set/"

files = files(path)

with open("note/todo.json", "w") as f:
	dump(files, f)

with open("note/doing.json", "w") as f:
	dump([], f)
