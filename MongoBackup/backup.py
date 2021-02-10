import os
import time
import shutil
from dotenv import load_dotenv
load_dotenv()

interval = int(os.getenv('interval'))
destination = os.getenv('destination')

def run_backup():
  timestamp = time.strftime("%Y-%m-%d-%H:%M:%S")
  path = destination + timestamp
  print("Backup running")
  command = "mongodump"
  command += " --uri " + os.getenv('connectionString')
  command += " --out " + path
  os.system(command)
  print(command)
  if os.path.isdir(path):
    for dir in os.listdir(destination):
      if dir != timestamp:
        shutil.rmtree(destination + dir)
  print("Backup complete")

print(f'Mongo db backup will run every {interval} minutes')

while True:
  run_backup()
  time.sleep(interval * 60)