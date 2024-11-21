import tkinter as tk
import reading
import process_paper
from PIL import Image, ImageTk
from tkinter import filedialog
import os
from datetime import datetime


class Start_page:
    def __init__(self, root):
        self.root = root
        self.setup_fullscreen()

        # 创建 Canvas 并加载背景图片
        self.canvas = tk.Canvas(self.root, width=self.root.screen_width, height=self.root.screen_height)
        self.canvas.pack(fill='both', expand=True)
        self.load_background_image(r'bg_img.png')

        #用于存储用户上传的信息
        self.file_contents = {}

        self.name_var = tk.StringVar()
        self.name_entry = tk.Entry(self.root, textvariable=self.name_var)
        self.name_entry.insert(0,'在此输入姓名')
        self.name_entry.place(x=300, y=300, width=200)


        # 创建题目上传按钮
        reading_button = tk.Button(self.root, text=f"在此上传模考文件", command=self.upload_reading_file)
        reading_button.place(x=300, y=400)  # Adjust position as needed
        global reading_label
        reading_label = tk.Label(self.root, text="No file selected", bg="white", relief="sunken", width=50, anchor='w', borderwidth=0,highlightthickness=0)
        reading_label.place(x=420, y=400, width=300)


        # 创建开始考试按钮
        self.start_button = tk.Button(self.root, text="Start Exam", command=self.on_click_start_button)
        self.start_button.place(x=400, y=700)


    def setup_fullscreen(self):
        self.root.screen_width = self.root.winfo_screenwidth()
        self.root.screen_height = self.root.winfo_screenheight()
        self.root.attributes('-fullscreen', True)

    def load_background_image(self, img_path):
        image = Image.open(img_path)
        image = image.resize((self.root.screen_width, self.root.screen_height), Image.LANCZOS)
        self.bg_img = ImageTk.PhotoImage(image)  # 保持引用防止被垃圾回收
        self.canvas.create_image(0, 0, image=self.bg_img, anchor='nw')

    def on_click_start_button(self):
        user_name = self.name_var.get()
        self.file_contents['name'] = user_name
        self.create_folder()
        # 传递文件内容到 Writing 实例
        for widget in self.root.winfo_children():
            widget.destroy()
        reading.Reading(self.root, self.file_contents)
        #self.start_button.place_forget()



    def create_folder(self):
        # 定义文件夹路径
        base_dir = 'results'
        folder_name = self.file_contents.get('name', 'default_name')  # 获取文件夹名称
        folder_path = os.path.join(base_dir, folder_name)

        # 检查文件夹是否存在
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        today_date = datetime.now().strftime('%Y-%m-%d')
        date_folder_path = os.path.join(folder_path, today_date)

        # 创建日期子文件夹
        if not os.path.exists(date_folder_path):
            os.makedirs(date_folder_path)



    def upload_reading_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if file_path:

            paper = process_paper.read_text(file_path)
            for key,value in paper.items():
                self.file_contents[key] = value
            reading_label.config(text=file_path)


    def get_content(self):
        print(self.file_contents)
        return self.file_contents

class TOEFL_app:
    def __init__(self):
        self.root = tk.Tk()
        self.start_exam_page()
        self.root.mainloop()

    def start_exam_page(self):
        self.start_page = Start_page(self.root)

if __name__ == '__main__':
    TOEFL_app()