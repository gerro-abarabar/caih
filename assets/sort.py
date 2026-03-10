# Temp file
import json,os
file_path=os.path.join("final_data.json")
with open(file_path, "r") as f:
    data = json.load(f)


data.sort(key=lambda x: x["id"])
with open(file_path, "w") as f:
    json.dump(data, f, indent=4)