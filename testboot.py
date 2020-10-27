print("Loading...")
debug_mode_enabled = True
exec(open("app.py", "r").read())
from multiprocessing import Process
from time import sleep
from urllib.request import urlopen

server = Process(target=app.run)
server.start()
print("Waiting for 2 seconds...")
sleep(2)
print("Pinging the server...")
rpy = urlopen("http://127.0.0.1:5000/", timeout=1)
print("Done!")
server.terminate()
server.join()
print("Bye!")
