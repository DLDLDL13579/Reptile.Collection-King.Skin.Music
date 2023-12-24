# kugou_gui.py

import requests
import os
import json
import re
import tkinter as tk
from tkinter import ttk

class KuGouGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("music白嫖神器")
        self.res = None  # 保存搜索结果的变量

        # 创建并设置小部件
        self.create_widgets()

    def download_song(self):
        song_name = self.entry.get().strip()

        if not song_name:
            return

        try:
            # 调用修改后的搜索函数，获取搜索结果
            self.res = self.search_song(song_name)

            if self.res:
                # 创建新窗口用于显示搜索结果
                result_window = tk.Toplevel(self.root)
                result_window.title("搜索结果")

                # 创建列表框
                listbox = tk.Listbox(result_window, selectmode=tk.SINGLE)
                listbox.pack(pady=10)

                for i, item in enumerate(self.res, start=1):
                    label_text = f"{i}. {item['FileName'].replace('<em>', '').replace('</em>', '')}"
                    listbox.insert(tk.END, label_text)

                # 下载按钮
                download_button = ttk.Button(result_window, text="下载", command=lambda: self.handle_download(listbox.get(tk.ACTIVE)))
                download_button.pack(pady=10)

        except json.JSONDecodeError as json_err:
            print(f"JSON解析错误: {json_err}")
        except Exception as e:
            print(f"搜索出错: {e}")

    def handle_download(self, selected_song):
        if selected_song and self.res:  # 确保已经进行了搜索
            try:
                song_name = selected_song.split('. ')[1]  # 提取歌曲名
                fhash = re.findall('"FileHash":"(.*?)"', self.res[int(selected_song.split('. ')[0]) - 1])[0]
                listen_url = self.get_listen_url(fhash)

                if listen_url:
                    # 在 GUI 上显示下载中的信息
                    download_label = ttk.Label(self.root, text="下载中....别催我，我真的在下载👋....")
                    download_label.grid(row=3, column=0, columnspan=3, pady=10)

                    # 设置定时器，10秒后清空标签内容
                    self.root.after(10000, lambda: download_label.config(text=""))

                    # 下载音乐
                    self.download_music(listen_url, song_name)
                else:
                    print("获取试听链接失败")

            except Exception as e:
                print(f"下载失败: {e}")

    def get_listen_url(self, file_hash):
        try:
            url = "http://www.kugou.com/yy/index.php?r=play/getdata&hash=" + file_hash
            response = requests.get(url)
            response.raise_for_status()  # 抛出 HTTPError 异常（如果请求不成功）

            data = response.json()
            listen_url = data.get('data', {}).get('play_url', '')
            return listen_url

        except requests.exceptions.RequestException as req_err:
            print(f"请求异常: {req_err}")
            print(f"服务端返回的文本: {response.text}")
            return None
        except json.JSONDecodeError as json_err:
            print(f"JSON解析错误: {json_err}")
            print(f"服务端返回的文本: {response.text}")
            return None

    def search_song(self, song_name):
        try:
            url = "http://songsearch.kugou.com/song_search_v2?callback=jQuery112407470964083509348_1534929985284&keyword={}&" \
                  "page=1&pagesize=30&userid=-1&clientver=&platform=WebFilter&tag=em&filter=2&iscorrection=1&privilege_filte" \
                  "r=0&_=1534929985286".format(song_name)
            res = requests.get(url).text

            # 在这里添加对 res 是否为有效 JSON 的检查
            try:
                json_res = json.loads(res[res.index('(') + 1:-2])
                return json_res['data']['lists']
            except json.JSONDecodeError:
                print("搜索结果解析失败")
                return None

        except requests.exceptions.RequestException as req_err:
            print(f"请求异常: {req_err}")
            return None
        except Exception as e:
            print(f"搜索出错: {e}")
            return None

    def download_music(self, listen_url, song_name):
        try:
            # Ensure that the URL has a valid scheme (http:// or https://)
            if not listen_url.startswith(('http://', 'https://')):
                listen_url = 'http://' + listen_url  # Assuming http://, you can adjust based on your requirements

            save_path = os.path.join("..", "music", f"{song_name}.mp3")
            true_path = os.path.abspath(save_path)
            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            # 下载音乐文件
            content = requests.get(listen_url).content

            # 在 GUI 上显示下载中的信息
            download_label = ttk.Label(self.root, text="下载中....别催我，我真的在下载👋....")
            download_label.grid(row=3, column=0, columnspan=3, pady=10)

            # 设置定时器，10秒后清空标签内容
            self.root.after(10000, lambda: download_label.config(text=""))

            with open(save_path, "wb") as fp:
                fp.write(content)
                os.fsync(fp.fileno())

            print(f"{song_name} 已保存至 {true_path}")

        except Exception as e:
            print("下载失败  骗你的🤪.....")

    def create_widgets(self):
        # 标签
        label = ttk.Label(self.root, text="请输入歌名:")
        label.grid(row=0, column=0, padx=10, pady=10)

        # 输入框
        self.entry = ttk.Entry(self.root, width=30)
        self.entry.grid(row=0, column=1, padx=10, pady=10)

        # 搜索按钮
        search_button = ttk.Button(self.root, text="搜索", command=self.download_song)
        search_button.grid(row=0, column=2, padx=10, pady=10)

if __name__ == '__main__':
    root = tk.Tk()
    kugou_gui = KuGouGUI(root)
    root.mainloop()
