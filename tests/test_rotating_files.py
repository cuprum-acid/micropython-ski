import os


def clear_data_folder():
    DATA_DIR = "/data/"
    MAX_FILES_CNT = 10
    all_files = os.listdir(DATA_DIR)
    print(all_files)
    all_files.sort(reverse=True)
    print(*all_files, sep='\n')
    while len(all_files) > MAX_FILES_CNT:
        file = all_files.pop()
        filename = DATA_DIR + file
        try:
            os.remove(filename)
        except Exception:
            print(f"Error deleting file {file}")


clear_data_folder()
