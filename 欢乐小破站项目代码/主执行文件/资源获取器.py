# main_file.py

import tkinter as tk
import subprocess

def start_file(file_name):
    subprocess.Popen(["python3", file_name])

root = tk.Tk()
root.title("你小子，仅供学习使用晓得不👊👊👊")
# 按钮1：启动第一个文件
button1 = tk.Button(root, text="得到你想要的music(手动🐶)", command=lambda: start_file("../功能模块/kugou_gui.py"))
button1.pack(pady=10)

# 按钮2：启动第二个文件
button2 = tk.Button(root, text="网络状态检测🛜", command=lambda: start_file("../功能模块/network_monitor.py"))
button2.pack(pady=10)

# 按钮3：启动第三个文件
button3 = tk.Button(root, text="王者农药英雄皮肤语音💼", command=lambda: start_file("../功能模块/audio_skin_scraper.py"))
button3.pack(pady=10)
# 按钮4:其他
button4 = tk.Button(root, text="🔥          火辣舞蹈，别太激动，低调使用           🔥", command=lambda: start_file("../功能模块/其他功能.py"))
button4.pack(pady=10)

root.mainloop()
