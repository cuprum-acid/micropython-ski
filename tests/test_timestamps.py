# Создание файла с timestamp
import time
t = time.gmtime()
DATA_DIR = "data/"

timestamp = "{:04d}-{:02d}-{:02d}_{:02d}-{:02d}-{:02d}".format(
    t[0], t[1], t[2], t[3], t[4], t[5]
)
# 
filename = DATA_DIR + timestamp + ".txt"
# 
with open(filename, "w") as f:
    f.write("Timestamp: " + timestamp)
# 
print("Created file:", filename)