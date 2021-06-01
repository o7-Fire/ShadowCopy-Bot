from flask import Flask
from threading import Thread
import urllib.request
import os
import time
import random
app = Flask('')
hdr = { 'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)',
        'Authorization': os.getenv('o7APIKey'),
 }
url = "https://o7-api.glitch.me/api/json/graphical/classification/https://github.com/o7-Fire/General/raw/master/Human/Logo/o7A.png"


def main():
  return "alive 200"

def assad(path):
  return path +" assad" + str(random.randint(60, 250))

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def all_routes(path):
    if path.startswith('assad'):
      return assad(path)
    else:
      return main()


def fetch(url):
  try:
   req = urllib.request.Request(url, headers=hdr)
   response = urllib.request.urlopen(req)
   return str(response.read().decode())
  except Exception as e:
    return str(e)

def alive():
  while True:
    time.sleep(int(random.randint(160, 250)))
    try:
      fetch(url)
    except Exception as e:
      print(e)

def run():
  app.run(host="0.0.0.0", port=8080)

def keep_alive():
  server = Thread(target=run)
  server.start()
  aliveT = Thread(target=alive)
  aliveT.start()