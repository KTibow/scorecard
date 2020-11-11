print("Loading...")
import app

app.debug_mode_enabled = True
from multiprocessing import Process
from time import sleep
from urllib.request import urlopen

server = Process(target=app.app.run)
server.start()
print("Waiting for 2 seconds...")
sleep(2)
print("Pinging the server...")
urlopen("http://127.0.0.1:5000/", timeout=1)
print("Done!")
server.terminate()
server.join()
print("Bye!")
