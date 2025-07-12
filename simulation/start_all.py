import subprocess

nodes = ["node_1", "node_2", "node_3"]

for node in nodes:
    subprocess.Popen(["python", f"simulation/{node}/main.py"])
