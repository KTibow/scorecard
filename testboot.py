exec(open("app.py", "r").read())
from multiprocessing import Process
from time import sleep
server = Process(target=app.run)
server.start()
sleep(20)
server.terminate()
server.join()
