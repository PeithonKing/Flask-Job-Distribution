import requests
import time
import os
from tqdm import tqdm

URL = "http://192.168.29.114:5500/"

while True:
    try:
        file = requests.get(URL+"get").text
    except:
        wait = 15
        print(f"Server not found, waiting {wait} seconds before trying again...")
        time.sleep(wait)
        continue
    
    if file=="All Done!":
        print("All Done!")
        break
    
    print("Got a new File!")
    
    lines = file.split("\n")
    name = lines.pop(0)[:-1]
    if len(lines[-1]) <5:
        lines.pop()
    print(f"Doing {name}...")
    ratings = {"name": name}
    for line in tqdm(lines):
        # print(line)
        user, rating = line.split(",")[:2]
        ratings[user] = int(rating)
    print("Done\nNow Sending...", end=" ")
    
    trials = 0
    while True:
        try:
            requests.post(URL+"done", data=ratings)
            break
        except:
            trials += 1
            if trials<3:
                print("\nCould not send, waiting 15 seconds before trying again...")
                time.sleep(15)
            else:
                print("Could not send, giving up...")
                break
    
    print("Sent!\n\nGetting Next File...", end=" ")
    # time.sleep(20)