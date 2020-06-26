print("Loading...")
exec(open("app.py", "r").read())
from multiprocessing import Process
from time import sleep, time
from urllib.request import urlopen
server = Process(target=app.run)
server.start()
stime = time()
print("Waiting for 2 seconds...")
sleep(2)
print("Pinging the server...")
rpy = urlopen("http://127.0.0.1:5000/")
print("Waiting the other part of 3.5 seconds...")
sleep(1.5 - (time() - stime))
print("Done!")
server.terminate()
server.join()
print("Bye!")
