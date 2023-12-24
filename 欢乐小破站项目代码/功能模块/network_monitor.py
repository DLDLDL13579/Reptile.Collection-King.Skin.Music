# network_monitor.py
import threading
import time
from tkinter import Label, Button

import speedtest
import tkinter as tk


def measure_speed():
    st = speedtest.Speedtest(source_address='0.0.0.0')  # 使用 0.0.0.0 作为源地址，可以修改为您自己的 IP 地址
    server_info = st.get_best_server()

    # 获取服务器信息
    server_name = server_info['host']
    server_country = server_info['country']
    server_name_cn = server_info.get('host_name_cn', 'N/A')  # 获取中文名称，如果没有则使用默认值 'N/A'

    # 设置测速次数
    num_measurements = 5
    download_speeds = []
    upload_speeds = []

    for _ in range(num_measurements):
        download_speeds.append(st.download() / 1024 / 1024)  # 转换为兆比特每秒（Mbps）
        upload_speeds.append(st.upload() / 1024 / 1024)  # 转换为兆比特每秒（Mbps）

    # 计算平均值
    avg_download_speed = sum(download_speeds) / num_measurements
    avg_upload_speed = sum(upload_speeds) / num_measurements

    return avg_download_speed, avg_upload_speed, server_name, server_country, server_name_cn


def update_speed_label(root, speed_label, refresh_label, clear_refresh_status):
    refresh_label.config(text="小的已快马加鞭，主公请稍等😉...")
    root.update()  # 更新界面以显示刷新中状态

    start_time = time.time()
    download_speed, upload_speed, server_name, server_country, server_name_cn = measure_speed()
    end_time = time.time()

    speed_label.config(text=f"平均下载速度: {download_speed:.2f} Mbps\n"
                            f"平均上传速度: {upload_speed:.2f} Mbps\n"
                            f"测速时间: {end_time - start_time:.2f} 秒\n"
                            f"选择服务器: {server_name} ({server_name_cn})\n"
                            f"服务器所在国家: {server_country}")

    refresh_label.config(text="测速完成，主公久等了😬!")
    root.after(2000, lambda: clear_refresh_status(refresh_label))


def clear_refresh_status(refresh_label):
    refresh_label.config(text="")


def start_speed_measurement(root, speed_label, refresh_label, clear_refresh_status):
    threading.Thread(target=lambda: update_speed_label(root, speed_label, refresh_label, clear_refresh_status),
                     daemon=True).start()


def on_refresh_button_click(root, speed_label, refresh_label, clear_refresh_status):
    # 在按钮点击时手动触发测速更新
    update_speed_label(root, speed_label, refresh_label, clear_refresh_status)


# 创建一个简单的 GUI 窗口
root = tk.Tk()
root.title("主功能选择界面")

# 创建用于显示速度的标签
speed_label = Label(root, text="")
speed_label.pack()

# 创建按钮和标签
speed_button = Button(root, text="测量网络速度",
                      command=lambda: start_speed_measurement(root, speed_label, refresh_label, clear_refresh_status))
speed_button.pack()

# 创建用于显示刷新状态的标签
refresh_label = Label(root, text="")
refresh_label.pack()

# 创建用于显示时间的标签
time_label = Label(root, text="")
time_label.pack()

root.mainloop()
