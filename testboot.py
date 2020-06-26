print("Loading...")
exec(open("app.py", "r").read())
from multiprocessing import Process
from time import sleep, time
from urllib.request import urlopen
debuggy = True
server = Process(target=app.run)
server.start()
stime = time()
print("Waiting for 2 seconds...")
sleep(2)
print("Pinging the server...")
rpy = urlopen("http://127.0.0.1:5000/")
rtime = 3.5 - (time() - stime)
print("Waiting", rtime, "seconds...")
sleep(rtime)
print("Done!")
server.terminate()
server.join()
print("Bye!")
