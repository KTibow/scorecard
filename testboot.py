print("Loading...")
exec(open("app.py", "r").read())
from multiprocessing import Process
from time import sleep
server = Process(target=app.run)
server.start()
print("Waiting for 5 seconds...")
sleep(5)
print("Done!")
server.terminate()
server.join()
print("Bye!")
