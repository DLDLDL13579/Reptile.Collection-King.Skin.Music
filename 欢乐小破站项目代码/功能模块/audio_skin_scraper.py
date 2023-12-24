import os
import threading
import tkinter as tk
from tkinter import Label, Button, Listbox, Scrollbar, simpledialog
import json
import chardet
import requests
from PIL import ImageTk, Image
from io import BytesIO
from subprocess import Popen
from tqdm import tqdm
from fake_useragent import UserAgent

# 游戏语音和皮肤爬取模块

# 随机产生请求头
ua = UserAgent()

# 提前创建一个文件夹，方便创建子文件夹

audio_folder = "./audios"
if not os.path.exists(audio_folder):
    os.makedirs(audio_folder)


def random_ua():
    headers = {
        "accept-encoding": "gzip",  # gzip压缩编码 能提高传输文件速率
        "user-agent": ua.random
    }
    return headers



def download(file_name, text, path):  # 下载函数
    file_path = path + file_name
    print(f"Downloading {file_name} to {file_path}")  # 添加调试语句
    with open(file_path, 'wb') as f:
        f.write(text)
        f.close()


def get_json(page):
    url = 'https://m.ximalaya.com/m-revision/common/album/queryAlbumTrackRecordsByPage?'
    param = {
        'albumId': '41725731',
        'page': '{}'.format(page),
        'pageSize': '10',
        'asc': 'true',
        'countKeys': 'play,comment',
        'v': '1630511230862'
    }
    res = requests.get(url=url, headers=random_ua(), params=param)
    res.encoding = chardet.detect(res.content)["encoding"]  # 确定编码格式
    res = res.text

    text_json = json.loads(res)  # 数据json化
    return text_json


# 在全局变量中保存当前音频的 Popen 对象
current_audio_process = None

def reset_audio_process(process):
    process.wait()
    global current_audio_process
    current_audio_process = None

def pause_audio():
    global current_audio_process

    if current_audio_process and current_audio_process.poll() is None:
        current_audio_process.terminate()
        current_audio_process.wait()
        current_audio_process = None

def play_audio(audio_name):
    global current_audio_process

    if not listbox.curselection():
        return  # 没有选中的项，不执行播放

    audio_path = os.path.join(audio_folder, audio_name)
    pause_audio()  # 先暂停当前播放的音频（如果有）

    # 使用open命令打开应用程序播放音频
    current_audio_process = Popen(['open', '-a', 'NeteaseMusic', audio_path])




def save_and_view_image(image_path):
    Popen(["open", image_path])  # 适用于MacOS


def crawl_skins(hero_name):
    url = "https://pvp.qq.com/web201605/js/herolist.json"
    try:
        response = requests.get(url, headers=random_ua())
        response.raise_for_status()
        hero_list = response.json()

        for hero in hero_list:
            if hero["cname"] == hero_name:
                skins = hero["skin_name"].split("|")
                ename = hero["ename"]
                break
        else:
            raise ValueError("未找到该英雄的皮肤信息")

        save_folder = "./skins"
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)

        for i, skin in enumerate(skins):
            skin_url = f"https://game.gtimg.cn/images/yxzj/img201606/skin/hero-info/{ename}/{ename}-bigskin-{i + 1}.jpg"
            response = requests.get(skin_url, headers=random_ua())
            response.raise_for_status()

            image_path = os.path.join(save_folder, f"{hero_name}_{i + 1}.jpg")

            with open(image_path, "wb") as f:
                f.write(response.content)

                print(f" {hero_name}_{i + 1} 下载success！🎉")
            skin_image = Image.open(BytesIO(response.content))
            skin_image.thumbnail((300, 300))  # 缩放图片大小
            skin_photo = ImageTk.PhotoImage(skin_image)
            label = tk.Label(frame, image=skin_photo)
            label.image = skin_photo
            label.grid(row=i // 3, column=i % 3, padx=10, pady=10)  # 使用网格布局

            # 绑定点击事件，保存并查看图片
            label.bind("<Button-1>", lambda event, path=image_path: save_and_view_image(path))

        for page in tqdm(range(1, 35)):
            text_json = get_json(page)
            data_s = text_json["data"]["trackDetailInfos"]

            for i in range(len(data_s)):
                # 检查标题中是否包含相关内容
                if hero_name.lower() in data_s[i]["trackInfo"]["title"].lower():
                    voice_name = data_s[i]["trackInfo"]["title"] + '.mp3'  # 添加后缀名 .mp3
                    voice = requests.get(url=data_s[i]["trackInfo"]["playPath"], headers=random_ua()).content
                    audio_path = os.path.join(audio_folder, voice_name)

                    with open(audio_path, "wb") as f:
                        f.write(voice)
                        print(f" {voice_name} 下载success！🎉")
                    listbox.insert(tk.END, voice_name)  # 在列表框中添加文件名

    except Exception as e:
        error_label.config(text=str(e))


def control_net_ease_music(command):
    # 使用 os.system 执行命令
    os.system(command)
def crawl_both_websites():
    hero_name = entry.get().strip()
    if not hero_name:
        error_label.config(text="请输入英雄名字")
        return

    crawl_thread = threading.Thread(target=lambda: crawl_skins(hero_name))

    crawl_thread.start()


def get_user_input():
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口

    user_input = simpledialog.askstring("输入", "输入相关内容:")

    root.destroy()
    return user_input


def check_network_connection():
    url_to_check = "https://www.google.com"
    try:
        response = requests.get(url_to_check, timeout=5, headers=random_ua())  # 设置超时时间为5秒
        response.raise_for_status()  # 如果状态码不是2xx，会抛出HTTPError异常
        print("网络连接正常")
        return True
    except requests.RequestException as e:
        print(f"网络连接异常: {e}")
        return False
def play_next_audio():
    selected_index = listbox.curselection()
    if not selected_index:
        return  # 没有选中的项，不执行播放

    next_index = int(selected_index[0]) + 1
    if 0 <= next_index < listbox.size():
        play_audio(listbox.get(next_index))
    else:
        print("已经是最后一首歌曲")
def pause_or_resume_audio():
    global current_audio_process
    if current_audio_process and current_audio_process.poll() is None:
        current_audio_process.terminate()
        current_audio_process.wait()
        current_audio_process = None
    else:
        selected_index = listbox.curselection()
        if selected_index:
            play_audio(listbox.get(selected_index[0]))



def play_previous_audio():
    selected_index = listbox.curselection()
    if not selected_index:
        return  # 没有选中的项，不执行播放

    prev_index = int(selected_index[0]) - 1
    if 0 <= prev_index < listbox.size():
        play_audio(listbox.get(prev_index))
    else:
        print("已经是第一首歌曲")


# 创建一个简单的 GUI 窗口
root = tk.Tk()
root.title("主功能选择界面")


skin_button = Button(root, text="爬取游戏皮肤和音频", command=crawl_both_websites)
skin_button.pack()

# 创建用于显示刷新状态的标签
refresh_label = Label(root, text="")
refresh_label.pack()

# 图片框架
frame = tk.Frame(root)
frame.pack()

# 创建用于显示错误信息的标签
error_label = Label(root, fg="red")
error_label.pack()

# 标签和输入框
label = Label(root, text="请输入英雄名字：")
label.pack()

entry = tk.Entry(root)
entry.pack()

# 创建列表框和滚动条
listbox = Listbox(root, width=50, height=10, selectmode="SINGLE")
scrollbar = Scrollbar(root, command=listbox.yview)
listbox.config(yscrollcommand=scrollbar.set)
scrollbar.pack(side="right", fill="y")
listbox.pack()

# 创建播放控制框架
control_frame = tk.Frame(root)
control_frame.pack()

# 上一曲按钮
prev_button = Button(control_frame, text="上一曲", command=lambda: play_audio(listbox.get(int(listbox.curselection()[0]) - 1)))

prev_button.pack(side=tk.LEFT, padx=5)

# 暂停按钮
pause_resume_button = Button(control_frame, text="暂停/恢复", command=pause_or_resume_audio)
pause_resume_button.pack(side=tk.LEFT, padx=5)

# 下一曲按钮
next_button = Button(control_frame, text="下一曲", command=lambda: play_audio(listbox.get(int(listbox.curselection()[0]) + 1)))
next_button.pack(side=tk.LEFT, padx=5)


# 将部件放置到窗口中
control_frame.pack()

root.mainloop()
