
import os

file_path = r"C:\Users\user\Desktop\保管庫\ユニコの脳みそ\05\2025-12-29_AutonomousAgents_Summary.md"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()
    print(len(content))
