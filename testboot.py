import app

from multiprocessing import Process
from time import sleep
from urllib.request import urlopen

server = Process(target=app.app.run)
server.start()
sleep(2)
urlopen("http://127.0.0.1:5000/", timeout=1)
server.terminate()
server.join()
