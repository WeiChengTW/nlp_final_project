import os

folder = os.path.dirname(os.path.abspath(__file__))

for filename in os.listdir(folder):
    # 只處理包含 'data\\processed\\' 的檔名
    if filename.startswith("data\\processed\\"):
        new_name = filename.split("data\\processed\\")[-1]
        old_path = os.path.join(folder, filename)
        new_path = os.path.join(folder, new_name)
        os.rename(old_path, new_path)
        print(f"Renamed: {filename} -> {new_name}")
