import tkinter as tk
from PIL import Image, ImageTk
import tkinter.font
from docx import Document
from datetime import datetime
from tkinter import font
import os
from tkinter import messagebox
from independent_writing import Independent_writing

class Comprehensive_Writing:

    def __init__(self, root,file_contents,reading_score,listening_score):
        self.root = root
        self.file_contents = file_contents
        self.root.bg_img = r'bg_img.png'
        self.reading_score = reading_score
        self.listening_score = listening_score
        self.article = self.file_contents.get('综合写作文章')
        self.question = self.file_contents.get('综合写作问题')

        # 获取屏幕宽度和高度
        self.root.screen_width = self.root.winfo_screenwidth()
        self.root.screen_height = self.root.winfo_screenheight()
        # 设置全屏
        self.root.attributes('-fullscreen', True)
        self.root.img_path = r'bg_img.png'
        self.root.canvas = tk.Canvas(self.root, width=self.root.screen_width, height=self.root.screen_height)
        self.root.canvas.pack(fill='both', expand=True)


        # 加载背景图片
        image = Image.open(self.root.img_path)
        # 调整图像大小以适应屏幕
        image = image.resize((self.root.screen_width, self.root.screen_height), Image.LANCZOS)
        self.root.bg_img = ImageTk.PhotoImage(image)  # 保持引用防止被垃圾回收
        # 在 Canvas 上创建图像
        self.root.canvas.create_image(0, 0, image=self.root.bg_img, anchor='nw')

        self.save_button = tk.Button(self.root, text='Next', font=("Helvetica", 14), command=self.save_to_doc)
        self.save_button.place(relx=0.937317, rely=0.020833, relwidth=0.029291, relheight=0.020833)
        #添加倒计时
        # 初始化时间
        self.time_left = 20 * 60  # 20分钟的秒数
        # 创建标签显示剩余时间
        self.time_label = tk.Label(self.root, text=self.format_time(self.time_left), font=("Helvetica", 14),bg="white")
        self.time_label.place(relx = 0.9, rely = 0.075, relwidth = 0.05, relheight = 0.03)
        self.word_count_label = None
        # 启动倒计时
        self.update_timer()
        self.create_writing_page()

    def format_time(self, seconds):
        """将秒数格式化为分钟和秒数"""
        minutes, seconds = divmod(seconds, 60)
        return f"{minutes:02}:{seconds:02}"

    def update_timer(self):
        """更新倒计时"""
        try:
            if self.time_left > 0:
                self.time_left -= 1
                if self.time_label:
                    self.time_label.config(text=self.format_time(self.time_left))
                self.timer_id = self.root.after(1000, self.update_timer)  # 每秒调用一次更新函数
            else:
                self.on_time_up()
        except tk.TclError:
            # 忽略 TclError 错误
            pass

    def on_time_up(self):
        self.save_to_doc()
        for widget in self.root.winfo_children():
            widget.destroy()
        Independent_writing(self.root,self.file_contents,self.reading_score,self.listening_score)



    def create_writing_page(self):
        # 创建滚动条和文章显示区域
        frame = tk.Frame(self.root)
        frame.place(relx=0.017575, rely=0.130208, relwidth=0.468658, relheight=0.833333)
        text = tk.Text(frame, wrap='word', font=tkinter.font.Font(family='Helvetica', size=17), borderwidth=0,
                       highlightthickness=0)
        text.pack(side='left', fill='both', expand=True)
        scrollbar = tk.Scrollbar(frame, command=text.yview)
        scrollbar.pack(side='right', fill='y')
        text.config(yscrollcommand=scrollbar.set)

        # 插入文章并设置段落间距
        article = self.article.replace('\n\n', '\n')
        text.insert('1.0', article)
        text.tag_configure('spacing', spacing3=20)
        text.tag_add('spacing', '1.0', 'end')
        text.config(state='disabled')

        # 创建词数显示标签
        self.word_count_label = tk.Label(self.root, font=("Arial", 16), bg='white', text="Word count: 0")
        self.word_count_label.place(relx=0.55, rely=0.11, anchor='center')

        # 创建作文写入界面
        custom_font = font.Font(family='Arial', size=14)
        self.text_input = tk.Text(self.root, wrap='word', font=custom_font)
        self.text_input.place(relx=0.503808, rely=0.134583, relwidth=0.492091, relheight=0.86)

        # 绑定按键释放事件，实时更新词数
        self.text_input.bind("<KeyRelease>", self.count_words)

    def count_words(self, event=None):
        """计算输入框中的单词总数，并更新词数计数标签"""
        # 获取用户输入的文本
        input_text = self.text_input.get("1.0", "end-1c")

        # 按空格分割单词，并过滤掉空字符串，计算单词数
        word_count = len([word for word in input_text.split() if word])

        # 更新词数显示
        self.word_count_label.config(text=f"Word count: {word_count}")

    def save_to_doc(self):
        text_content = self.text_input.get("1.0", "end-1c")
        name = self.file_contents.get('name')
        time = datetime.now().strftime('%Y-%m-%d')
        file_path = rf'results/{name}/{time}/comprehensive_writing.doc'
        if os.path.exists(file_path):
            os.remove(file_path)
        doc = Document()
        # 添加文本到文档
        doc.add_paragraph(text_content)
        # 保存文档
        doc.save(file_path)
        self.go_to_independent_writing()
    def go_to_independent_writing(self):
        result = messagebox.askokcancel("确认", "Are you ready to enter the next part")
        if result:
            for widget in self.root.winfo_children():
                widget.destroy()

            Independent_writing(self.root, self.file_contents, self.reading_score, self.listening_score)




if __name__ == '__main__':
    root = tk.Tk()
    Comprehensive_Writing(root,{
                        'name':'tyt',
                       '综合写作文章': "An intriguing underwater rock structure exists off the coast of Japan. Since the discovery of the rock formation in the 1980s, archaeologists and geologists have debated whether the structure is the result of natural processes or of human construction. Several scholars have argued that it was made by humans based on several pieces of evidence.\n\nAncient Civilization\n\nFirst, there is evidence that an ancient civilization was present in the region around 10,000 years ago. At that time, the sea level was lower, and the structure would have been on dry land. Recent expeditions to the area have uncovered bones, pottery fragments, and parts of tools that are many thousands of years old. With this archaeological evidence, it's reasonable to hypothesize that ancient people living around the structure could have carved it when the area was not yet underwater.\n\nFeatures Designed for Human Use\n\nSecond, pictures of the structure reveal features that seem to be intended for human use (see illustration). For example, there is a section that appears to be a wide, flat platform with stairs along its sides, as well as several large rock pieces that are likely walls. The presence of stairs and walls suggests that the structure was made for human use and was built by humans. Based on such features, some archaeologists have proposed that the whole structure may be a remnant of an ancient city.\n\nStraight Edges\n\nFinally, the rock from the structure has very straight, clear edges. If the rocky structure had been created by a natural process such as water erosion, its edges would be round. There are also several rock elements that intersect at sharp 90-degree angles. These straight edges and angles suggest that the rock was carved by humans rather than by waves and currents of the ocean, which would have left gentler curved edges.\n\n",
                       '综合写作问题': 'Directions: You have 20 minutes to plan and write your response. Your response will be judged on the basis of the quality of your writing and on how well your response presents the points in the lecture and their relationship to the reading passage. Typically, an effective response will be 150 to 225 words.\n\nQuestion: Summarize the points made in the lecture, being sure to explain how they challenge the specific theories presented in the reading passage.\n\n',
                       '综合写作音频路径': 'paper_source\\audio\\模考8-L2-重听题.mp3',
                       '独立写作截图路径': 'paper_source\\pictures\\模考8.png'},1,1
                )
    root.mainloop()