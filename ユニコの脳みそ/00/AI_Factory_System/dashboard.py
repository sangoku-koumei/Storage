import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import subprocess
import os
import signal
import time
from datetime import datetime

class ToolDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("仮想脳 ツール管理ダッシュボード")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")

        # 状態保持
        self.processes = {
            "auto_accept": None,
            "git_sync": None
        }

        self.setup_ui()

    def setup_ui(self):
        # メインフレーム
        main_frame = tk.Frame(self.root, bg="#f0f0f0", padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # タイトル
        title_label = tk.Label(main_frame, text="🧠 仮想脳 ツール管理システム", font=("Helvetica", 16, "bold"), bg="#f0f0f0")
        title_label.pack(pady=10)

        # ツール表示エリア (左右分割)
        paned = tk.PanedWindow(main_frame, orient=tk.HORIZONTAL, bg="#f0f0f0")
        paned.pack(fill=tk.BOTH, expand=True)

        # --- 自動承認ツールセクション ---
        self.accept_frame = tk.LabelFrame(paned, text="【自動承認ツール】", font=("Helvetica", 12, "bold"), padx=10, pady=10)
        paned.add(self.accept_frame)

        self.accept_status = tk.Label(self.accept_frame, text="停止中", fg="red", font=("Helvetica", 10, "bold"))
        self.accept_status.pack(anchor="w")

        self.accept_log = scrolledtext.ScrolledText(self.accept_frame, height=15, width=40, font=("Consolas", 9))
        self.accept_log.pack(pady=5, fill=tk.BOTH, expand=True)

        btn_frame_1 = tk.Frame(self.accept_frame)
        btn_frame_1.pack(fill="x")
        self.btn_accept_start = tk.Button(btn_frame_1, text="開始 / 再起動", command=self.toggle_auto_accept, bg="#e1e1e1")
        self.btn_accept_start.pack(side="left", padx=2, expand=True, fill="x")

        # --- Git同期ツールセクション ---
        self.git_frame = tk.LabelFrame(paned, text="【Git展開/同期ツール】", font=("Helvetica", 12, "bold"), padx=10, pady=10)
        paned.add(self.git_frame)

        self.git_status = tk.Label(self.git_frame, text="停止中", fg="red", font=("Helvetica", 10, "bold"))
        self.git_status.pack(anchor="w")

        self.git_log = scrolledtext.ScrolledText(self.git_frame, height=15, width=40, font=("Consolas", 9))
        self.git_log.pack(pady=5, fill=tk.BOTH, expand=True)

        btn_frame_2 = tk.Frame(self.git_frame)
        btn_frame_2.pack(fill="x")
        self.btn_git_start = tk.Button(btn_frame_2, text="開始 / 再起動", command=self.toggle_git_sync, bg="#e1e1e1")
        self.btn_git_start.pack(side="left", padx=2, expand=True, fill="x")
        self.btn_git_reset = tk.Button(btn_frame_2, text="状態復旧 (Reset)", command=self.reset_git_state, bg="#ffcccc")
        self.btn_git_reset.pack(side="left", padx=2, expand=True, fill="x")

    def log(self, target, msg):
        target_widget = self.accept_log if target == "accept" else self.git_log
        timestamp = datetime.now().strftime("[%H:%M:%S] ")
        target_widget.insert(tk.END, timestamp + msg + "\n")
        target_widget.see(tk.END)

    def toggle_auto_accept(self):
        if self.processes["auto_accept"]:
            self.stop_process("auto_accept")
        self.start_process("auto_accept")

    def toggle_git_sync(self):
        if self.processes["git_sync"]:
            self.stop_process("git_sync")
        self.start_process("git_sync")

    def reset_git_state(self):
        if messagebox.askyesno("確認", "Gitの状態を強制リセット（インデックスの修復等）しますか？"):
            self.log("git", "🚨 強制リセット実行中...")
            # ここにGitリセット用のロジック（git reset --hard 等）を実装予定
            threading.Thread(target=self.run_git_recovery, daemon=True).start()

    def start_process(self, name):
        def _run():
            self.log(name if name == "auto_accept" else "git", f"🚀 {name} を起動中...")
            cwd = os.path.dirname(os.path.abspath(__file__))
            
            if name == "auto_accept":
                script_path = os.path.join(cwd, "..", "AutoAccept", "auto_accept.py")
                cmd = ["python", script_path]
                status_label = self.accept_status
            else:
                script_path = os.path.join(r"c:\Users\user\Desktop\保管庫\git-auto-tools", "git-auto-push.ps1")
                # ループで動かすためのラッパースクリプトを検討
                cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-File", script_path, "-autoCommit"]
                status_label = self.git_status

            try:
                self.processes[name] = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding='utf-8',
                    errors='replace',
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0,
                    bufsize=1
                )
                
                status_label.config(text="稼働中", fg="green")
                
                for line in iter(self.processes[name].stdout.readline, ''):
                    if line:
                        self.log("accept" if name == "auto_accept" else "git", line.strip())
                
                self.processes[name].wait()
            except Exception as e:
                self.log("accept" if name == "auto_accept" else "git", f"❌ エラー: {str(e)}")
            finally:
                status_label.config(text="停止", fg="red")
                self.processes[name] = None

        threading.Thread(target=_run, daemon=True).start()

    def stop_process(self, name):
        p = self.processes.get(name)
        if p:
            self.log("accept" if name == "auto_accept" else "git", "🛑 停止信号を送信中...")
            # Windowsでの安全な停止
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(p.pid)], capture_output=True)
            self.processes[name] = None

    def run_git_recovery(self):
        # Gitの一般的な復旧処理
        commands = [
            ["git", "status"],
            ["git", "add", "."],
            ["git", "commit", "-m", "復旧自動コミット"],
            ["git", "push", "origin", "HEAD"]
        ]
        repo_path = r"c:\Users\user\Desktop\保管庫"
        for cmd in commands:
            self.log("git", f"実行: {' '.join(cmd)}")
            res = subprocess.run(cmd, cwd=repo_path, capture_output=True, text=True)
            if res.returncode != 0:
                self.log("git", f"警告: {res.stderr.strip()}")
        self.log("git", "✅ 復旧処理完了")

if __name__ == "__main__":
    root = tk.Tk()
    app = ToolDashboard(root)
    root.mainloop()
