from flask import Flask, request
import os
import time
import numpy as np
import pandas as pd
import json

with open("note/todo.json") as f:
    todo = json.load(f)  # COMPLETED

with open("note/doing.json") as f:
    doing = json.load(f)  # COMPLETED

globs = {
    "startTime": time.time(),
    "lastSaved": time.time(),
    "saveEvery": 60,  # Save todo and doing every this many seconds
    "todo": todo,
    "doing": doing,
    "totalTodo": sum([os.path.getsize("../data/training_set/"+x)/1024 for x in todo]), # KB
    "connections": {},
    "disconnectAfter": 500, # Asume client disconnected after this many seconds
}

def show_stats(ret = False):  # COMPLETED
    global globs
    restTodo = sum([os.path.getsize("../data/training_set/"+x)/1024 for x in globs["todo"]])
    totalTodo = globs["totalTodo"]
    now = time.time()
    doneKB = totalTodo - restTodo
    avv = doneKB / (now - globs["startTime"])
    if avv: ETA = restTodo/avv
    else: ETA = -1
    
    if ret:
        save_info()
        stats = {
            "totalTodo": totalTodo,
            "doneKB": doneKB,
            "average speed": avv,
            "percent done": doneKB*100/totalTodo,
            "ETA": ETA,
            "total elapsed time": now-globs['startTime'],
            "lastSaved": now-globs["lastSaved"],
            "saveEvery": globs["saveEvery"],
            # "todo": globs["todo"],
            "doing": globs["doing"],
            "connections": globs["connections"],
            "disconnectAfter": globs["disconnectAfter"],
        }
        print("\nSending Stats!")
        return str(stats)
    else:
        print(f"average speed = {round(avv, 5)} KBps")
        print(f"percentage done = {round(doneKB*100/totalTodo, 2)}%")
        print(f"ETA = {ETA/60} min = {ETA/3600} hr\n")
        print(f"total elapsed time = {round((now-globs['startTime'])/60, 2)} min\n")
    
def get_next_file():  # COMPLETED
    global globs
    for file in globs["todo"]:
        if file[:-4] not in globs["doing"]:
            globs["doing"].append(file[:-4])
            return file
    return None

def save_info():  # COMPLETED
    global globs

    for connection in globs["connections"]:
        if (time.time() - globs["connections"][connection]["LastConnected"]) > globs["disconnectAfter"]:
            print(f"Client {connection} disconnected!")
            del globs["connections"][connection]

    if (time.time() - globs["lastSaved"]) > globs["saveEvery"]:
        print("Saving todo and doing...", end = " ")
        with open("note/doing.json", "w") as f:
            json.dump(globs["doing"], f)
        with open("note/todo.json", "w") as f:
            json.dump(globs["todo"], f)
        globs["lastSaved"] = time.time()
        print("Saved!")
        show_stats()

app = Flask(__name__)

@app.route('/done', methods=['GET', 'POST'])
def done():
    global globs
    save_info()
    if request.method == "POST":
        print(f"\nGot a POST Request from {request.remote_addr}")
        data = dict(request.form)
        name = data['name']
        del data['name']
        with open("done/" + name + ".json", "w") as f:
            json.dump(data, f)
        
        file = "mv_" + "0"*(7-len(name)) + name
        globs["doing"].remove(file)
        globs["todo"].remove(file+".txt")
        globs["connections"][request.remote_addr]["Doing"].remove(file)
        return "Done!"

    else: return show_stats(True)

@app.route("/get")
def get():
    global globs
    print(f"\nGot a GET Request from {request.remote_addr}")
    file = get_next_file() # gives the filename only
    if not file: return "All Done!"
    try:
        globs["connections"][request.remote_addr]
    except KeyError:
        globs["connections"][request.remote_addr] = {}
    globs["connections"][request.remote_addr]["LastConnected"] = time.time()
    try:
        globs["connections"][request.remote_addr]["Doing"]
    except KeyError:
        globs["connections"][request.remote_addr]["Doing"] = []
    globs["connections"][request.remote_addr]["Doing"].append(file[:-4])
    save_info()
    with open("../data/training_set/"+file) as f:
        return f.read()

if __name__ == "__main__":
    app.run(host="192.168.29.114", port="5500", debug=True)