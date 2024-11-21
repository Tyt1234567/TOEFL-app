import tkinter as tk
from PIL import Image, ImageTk
import soundfile as sf
import sounddevice as sd
import threading
from listening2 import Listening2
import numpy as np
from get_audio_time import get_audio_duration
from tkinter import messagebox


class Listening1:
    def __init__(self, root, paper, reading_user, reading_answer):
        self.root = root
        self.paper = paper
        self.reading_user = reading_user
        self.reading_answer = reading_answer
        self.root.title("Listening")
        self.root.screen_width = self.root.winfo_screenwidth()
        self.root.screen_height = self.root.winfo_screenheight()
        self.root.attributes('-fullscreen', True)

        # 创建背景
        self.image = Image.open('bg_img2.png')
        self.image = self.image.resize((self.root.screen_width, self.root.screen_height), Image.LANCZOS)
        self.bg_img = ImageTk.PhotoImage(self.image)  # 保持引用防止被垃圾回收

        self.current_page_index = 0
        self.pages = []

        self.listening_user_choice = ['none'] * 11
        self.listening_answer_choice = ['none'] * 11

        self.total_time_left = 420   #420


        self.create_pages()
        self.display_page(self.current_page_index)
        # 创建标签显示剩余时间
        self.total_time_label = tk.Label(self.root, text=self.format_time(self.total_time_left), font=("Helvetica", 14), bg="#fce3c4")
        self.total_time_label.place(relx=0.936, rely=0.073, relwidth=0.03, relheight=0.03)

        self.stop_flag = threading.Event()
        self.audio_thread = None  # 追踪当前播放线程

        self.update_timer()

    def play_audio(self, audio_path):
        # 每次播放前先停止当前音频
        self.stop_audio()

        # 创建并启动播放音频的线程
        self.audio_thread = threading.Thread(target=self._play_audio, args=(audio_path,))
        self.audio_thread.start()

    def stop_audio(self):
        # 设置停止标志，等待当前播放线程退出
        if self.audio_thread and self.audio_thread.is_alive():
            self.stop_flag.set()  # 设置停止标志
            self.audio_thread.join()  # 等待当前播放线程结束
            self.stop_flag.clear()  # 重置标志以便下次播放

    def _play_audio(self, audio_path):

        # Load the audio file
        self.audio_data, self.sample_rate = sf.read(audio_path)
        self.audio_data = self.audio_data.astype(np.float32)  # Convert to float32
        self.total_time = len(self.audio_data) / self.sample_rate  # Total length in seconds

        # Create a stream and play audio
        with sd.OutputStream(samplerate=self.sample_rate,
                             channels=self.audio_data.shape[1] if self.audio_data.ndim > 1 else 1) as stream:

            # 播放音频，检查停止标志
            for i in range(0, len(self.audio_data), self.sample_rate):
                if self.stop_flag.is_set():
                    break
                stream.write(self.audio_data[i:i + self.sample_rate])


    def update_audio_timer(self, remaining_time):
        # 如果剩余时间大于 0，每隔一秒减少 1
        if remaining_time > 0 :

            # 更新标签文本
            self.time_label = tk.Label(font=("Arial", 18), bg='white',text=self.format_time(remaining_time))
            self.time_label.place(relx=0.5, rely=0.9, anchor='center')
            self.total_time_left += 1
            # 每隔1000ms (1秒) 调用一次update_audio_timer，递减计时
            self.root.after(1000, self.update_audio_timer, remaining_time-1)

        else:

            self.time_label = tk.Label(font=("Arial", 18), bg='white', text='          ')
            self.time_label.place(relx=0.5, rely=0.9, anchor='center')
            self.total_time_left += 1
            self.root.after(2000, self.go_next)



    def play_audio_page(self, audio_path):
        page_frame = tk.Frame(self.root)
        canvas = tk.Canvas(page_frame, width=self.root.screen_width, height=self.root.screen_height)
        canvas.pack(fill=tk.BOTH, expand=True)
        canvas.create_image(0, 0, image=self.bg_img, anchor='nw')

        total_audio_second = int(get_audio_duration(audio_path) // 1)

        # 添加音频时间显示标签
        self.time_label = tk.Label(page_frame, font=("Arial", 18),bg='white')
        self.time_label.place(relx=0.5, rely=0.9, anchor='center')

        page_frame.audio_path = audio_path
        page_frame.audio_length = total_audio_second

        return page_frame



    def create_one_choice_pages(self, page, question, choices):
        page_frame = tk.Frame(self.root)
        canvas = tk.Canvas(page_frame, width=self.root.screen_width, height=self.root.screen_height)
        canvas.pack(fill=tk.BOTH, expand=True)
        canvas.create_image(0, 0, image=self.bg_img, anchor='nw')

        next_button = tk.Button(page_frame, text="Next", command=self.go_next)
        next_button.place(relx=0.937, rely=0.021, relwidth=0.03, relheight=0.03)

        options = choices.split('\n')
        while '' in options:
            options.remove('')
        option_text = ''
        for option in options:
            option_text += option
            option_text += '\n'
            option_text += '\n'
        # 问题文本
        question_text = tk.Text(page_frame, bg="white", fg='black', font=('Arial', 18), wrap='word', borderwidth=0,
                                highlightthickness=0)
        question_text.place(relx=0.1, rely=0.15, relwidth=0.8, relheight=0.5)
        question = question + '\n' + '\n' + option_text
        question_text.insert('1.0', question)
        question_text.config(state=tk.DISABLED)



        var = tk.StringVar(value="Option 1")

        def selection():
            selected_value = var.get()
            self.listening_user_choice[page] = selected_value

        # 创建单选按钮
        A = tk.Radiobutton(page_frame, text='A', variable=var, value="A", command=selection,
                           font=("Helvetica", 15), bg='white')
        A.place(relx=0.2, rely=0.8)

        B = tk.Radiobutton(page_frame, text="B", variable=var, value="B", command=selection,
                           font=("Helvetica", 15), bg='white')
        B.place(relx=0.4, rely=0.8)

        C = tk.Radiobutton(page_frame, text="C", variable=var, value="C", command=selection,
                           font=("Helvetica", 15), bg='white')
        C.place(relx=0.6, rely=0.8)

        D = tk.Radiobutton(page_frame, text="D", variable=var, value="D", command=selection,
                           font=("Helvetica", 15), bg='white')
        D.place(relx=0.8, rely=0.8)

        return page_frame

    def create_multiple_choice_pages(self, page, question, choices):
        page_frame = tk.Frame(self.root)
        canvas = tk.Canvas(page_frame, width=self.root.screen_width, height=self.root.screen_height)
        canvas.pack(fill=tk.BOTH, expand=True)
        canvas.create_image(0, 0, image=self.bg_img, anchor='nw')

        next_button = tk.Button(page_frame, text="Next", command=self.go_next)
        next_button.place(relx=0.937, rely=0.021, relwidth=0.03, relheight=0.03)

        options = choices.split('\n')
        while '' in options:
            options.remove('')
        option_text = ''
        for option in options:
            option_text += option
            option_text += '\n'
            option_text += '\n'
        # 问题文本
        question_text = tk.Text(page_frame, bg="white", fg='black', font=('Arial', 18), wrap='word', borderwidth=0,
                                highlightthickness=0)
        question_text.place(relx=0.1, rely=0.15, relwidth=0.8, relheight=0.5)
        question = question + '\n' + '\n' + option_text
        question_text.insert('1.0', question)
        question_text.config(state=tk.DISABLED)

        var = tk.StringVar(value="Option 1")

        def selection():

            selected_options = [key for key, var in var_dict.items() if var.get()]
            select_text = ''
            for selected_option in selected_options:
                select_text += selected_option
            self.listening_user_choice[page] = select_text

        # 创建多选按钮的变量列表
        var_dict = {}
        abcd = ['A', 'B', 'C', 'D', 'E']
        # 创建多选按钮
        for idx, option in enumerate(options):
            var = tk.BooleanVar()  # 创建一个布尔变量用于多选按钮
            var_dict[abcd[idx]] = var

            check_button = tk.Checkbutton(page_frame, text=abcd[idx], variable=var, font=("Helvetica", 15),
                                          bg='white', command=selection)
            check_button.place(relx=0.1 + idx * 0.2, rely=0.8)  # 根据选项数量动态调整位置

        return page_frame

    def create_sequence_pages(self, page, question, choices):
        page_frame = tk.Frame(self.root)
        canvas = tk.Canvas(page_frame, width=self.root.screen_width, height=self.root.screen_height)
        canvas.pack(fill=tk.BOTH, expand=True)
        canvas.create_image(0, 0, image=self.bg_img, anchor='nw')

        next_button = tk.Button(page_frame, text="Next", command=self.go_next)
        next_button.place(relx=0.937, rely=0.021, relwidth=0.03, relheight=0.03)

        options = choices.split('\n')
        while '' in options:
            options.remove('')
        option_text = ''
        for option in options:
            option_text += option
            option_text += '\n'
            option_text += '\n'

        # 问题文本
        question_text = tk.Text(page_frame, bg="white", fg='black', font=('Arial', 18), wrap='word', borderwidth=0,
                                highlightthickness=0)
        question_text.place(relx=0.1, rely=0.15, relwidth=0.8, relheight=0.5)
        question = question + '\n' + '\n' + option_text
        question_text.insert('1.0', question)
        question_text.config(state=tk.DISABLED)

        # 序号列表，记录用户选择顺序
        user_order = []

        # 创建按钮的点击事件，更新选择顺序
        def button_click(btn, label, choice):
            if choice in user_order:
                # 如果该选项已选中，取消选择
                user_order.remove(choice)
                btn.config(text=label)
            else:
                # 如果该选项未选中，增加到选择顺序中
                user_order.append(choice)
                btn.config(text=f"{label} ({len(user_order)})")
            # 打印当前选择顺序（如果需要记录用户选择）
            user_text = ''
            for i in user_order:
                user_text += i
            self.listening_user_choice[page] = user_text

        # 创建四个按钮，并为每个按钮分配点击事件
        btn_A = tk.Button(page_frame, text="A", command=lambda: button_click(btn_A, "A", "A"),
                          font=("Helvetica", 15), bg='white')
        btn_A.place(relx=0.2, rely=0.8)

        btn_B = tk.Button(page_frame, text="B", command=lambda: button_click(btn_B, "B", "B"),
                          font=("Helvetica", 15), bg='white')
        btn_B.place(relx=0.4, rely=0.8)

        btn_C = tk.Button(page_frame, text="C", command=lambda: button_click(btn_C, "C", "C"),
                          font=("Helvetica", 15), bg='white')
        btn_C.place(relx=0.6, rely=0.8)

        btn_D = tk.Button(page_frame, text="D", command=lambda: button_click(btn_D, "D", "D"),
                          font=("Helvetica", 15), bg='white')
        btn_D.place(relx=0.8, rely=0.8)

        return page_frame

    def create_relisten_pages(self, page, video_path, question, choices):
        page_frame = tk.Frame(self.root)
        canvas = tk.Canvas(page_frame, width=self.root.screen_width, height=self.root.screen_height)
        canvas.pack(fill=tk.BOTH, expand=True)
        canvas.create_image(0, 0, image=self.bg_img, anchor='nw')

        next_button = tk.Button(page_frame, text="Next", command=self.go_next)
        next_button.place(relx=0.937, rely=0.021, relwidth=0.03, relheight=0.03)

        options = choices.split('\n')
        while '' in options:
            options.remove('')
        option_text = ''
        for option in options:
            option_text += option
            option_text += '\n'
            option_text += '\n'

        # self.play_audio(video_path)
        page_frame.audio_path = video_path

        # 问题文本
        question_text = tk.Text(page_frame, bg="white", fg='black', font=('Arial', 18), wrap='word', borderwidth=0,
                                highlightthickness=0)
        question_text.place(relx=0.1, rely=0.15, relwidth=0.8, relheight=0.5)
        question = question + '\n' + '\n' + option_text
        question_text.insert('1.0', question)
        question_text.config(state=tk.DISABLED)

        var = tk.StringVar(value="Option 1")

        def selection():
            selected_value = var.get()
            self.listening_user_choice[page] = selected_value

        # 创建单选按钮
        A = tk.Radiobutton(page_frame, text='A', variable=var, value="A", command=selection,
                           font=("Helvetica", 15), bg='white')
        A.place(relx=0.2, rely=0.8)

        B = tk.Radiobutton(page_frame, text="B", variable=var, value="B", command=selection,
                           font=("Helvetica", 15), bg='white')
        B.place(relx=0.4, rely=0.8)

        C = tk.Radiobutton(page_frame, text="C", variable=var, value="C", command=selection,
                           font=("Helvetica", 15), bg='white')
        C.place(relx=0.6, rely=0.8)

        D = tk.Radiobutton(page_frame, text="D", variable=var, value="D", command=selection,
                           font=("Helvetica", 15), bg='white')
        D.place(relx=0.8, rely=0.8)

        return page_frame


    def create_first_page(self):
        page_frame = tk.Frame(self.root)
        canvas = tk.Canvas(page_frame, width=self.root.screen_width, height=self.root.screen_height)
        canvas.pack(fill=tk.BOTH, expand=True)
        canvas.create_image(0, 0, image=self.bg_img, anchor='nw')

        next_button = tk.Button(page_frame, text="start listening part1", bg='white', command=self.go_next)
        next_button.place(relx=0.44, rely=0.55, relwidth=0.12, relheight=0.06)
        return page_frame

    def format_time(self, seconds):
        """将秒数格式化为分钟和秒数"""
        minutes, seconds = divmod(seconds, 60)
        return f"{minutes:02}:{seconds:02}"

    def go_next(self):
        sd.stop()
        if self.current_page_index < len(self.pages) - 1:
            for widget in self.root.winfo_children():
                widget.forget()
            self.current_page_index += 1
            self.display_page(self.current_page_index)
        else:
            self.go_to_listening2()

    def go_to_listening2(self):
        self.stop_audio()
        result = messagebox.askokcancel("确认", "Are you ready to enter the next part?")

        if result:
            for widget in self.root.winfo_children():
                widget.destroy()

            Listening2(self.root, self.paper, self.reading_user, self.reading_answer,self.listening_user_choice,self.listening_answer_choice)

    #总倒计时
    def update_timer(self):
        """更新倒计时"""
        try:
            if self.total_time_left > 0 :
                self.total_time_left -= 1
                if self.current_page_index == 0:
                    self.total_time_left +=1
                if self.total_time_label:
                    self.total_time_label.config(text=self.format_time(self.total_time_left))
                self.timer_id = self.root.after(1000, self.update_timer)  # 每秒调用一次更新函数
            else:
                self.on_time_up()
        except tk.TclError:
            # 忽略 TclError 错误
            pass


    def on_time_up(self):
        self.stop_audio()
        for widget in self.root.winfo_children():
            widget.destroy()
        Listening2(self.root, self.paper, self.reading_user,self.reading_answer,self.listening_user_choice,self.listening_answer_choice)


    def display_page(self, index):
        if 0 <= index < len(self.pages):
            # 清理当前窗口
            for widget in self.root.winfo_children():
                widget.forget()

            # 显示页面
            page = self.pages[index]
            if page:
                page.pack(fill='both', expand=True)

                # 如果页面有音频路径，进入页面时播放音频
                if hasattr(page, 'audio_path'):
                    self.play_audio(page.audio_path)
                    if hasattr(page, 'audio_length'):
                        # 开始倒计时
                        self.update_audio_timer(page.audio_length)


    def create_pages(self):
        C1_audio_path = self.paper.get('C1 音频路径')
        L1_audio_path = self.paper.get('L1 音频路径')


        page = self.create_first_page()
        self.pages.append(page)

        page = self.play_audio_page(C1_audio_path)
        self.pages.append(page)

        for c1 in range(5):
            question_type = self.paper.get(f'C1-{c1 + 1} 题型（单选/多选/排序/重听）')
            question = self.paper.get(f'C1-{c1 + 1} 题干')
            choices = self.paper.get(f'C1-{c1 + 1} 选项')
            relisten_video = self.paper.get(f'C1-{c1 + 1} 重听题音频路径')
            answer = self.paper.get(f'C1-{c1 + 1} 答案')
            self.listening_answer_choice[c1] = answer
            if question_type[:2] == '单选':
                page = self.create_one_choice_pages(c1, question, choices)
                self.pages.append(page)
            if question_type[:2] == '多选':
                page = self.create_multiple_choice_pages(c1, question, choices)
                self.pages.append(page)
            if question_type[:2] == '排序':
                page = self.create_sequence_pages(c1, question, choices)
                self.pages.append(page)
            if question_type[:2] == '重听':
                page = self.create_relisten_pages(c1, relisten_video, question, choices)
                self.pages.append(page)

        page = self.play_audio_page(L1_audio_path)
        self.pages.append(page)

        for l1 in range(5, 11):
            question_type = self.paper.get(f'L1-{l1 - 4} 题型（单选/多选/排序/重听）')
            question = self.paper.get(f'L1-{l1 - 4} 题干')
            choices = self.paper.get(f'L1-{l1 - 4} 选项')
            relisten_video = self.paper.get(f'L1-{l1 - 4} 重听题音频路径')
            answer = self.paper.get(f'L1-{l1 - 4} 答案')
            self.listening_answer_choice[l1] = answer
            if question_type[:2] == '单选':
                page = self.create_one_choice_pages(l1, question, choices)
                self.pages.append(page)
            if question_type[:2] == '多选':
                page = self.create_multiple_choice_pages(l1, question, choices)
                self.pages.append(page)
            if question_type[:2] == '排序':
                page = self.create_sequence_pages(l1, question, choices)
                self.pages.append(page)
            if question_type[:2] == '重听':
                page = self.create_relisten_pages(l1, relisten_video, question, choices)
                self.pages.append(page)

if __name__ == '__main__':
    root = tk.Tk()
    Listening1(root, {'C1 音频路径':'paper_source\\audio\\模考8-L2-重听题.mp3',
                       'C1-1 题型（单选/多选/排序/重听）': '单选',
                       'C1-1 题干': '1. Why does the woman go to see the professor',
                       'C1-1 选项': 'A. To ask his opinion regarding a debate about the origins of the Berber people\n\nB. To get feedback on a paper that she recently submitted\n\nC. To propose an alternative topic for a paper she is working on\n\nD. To clarify a point that the professor made in class\n\n',
                       'C1-1 重听题音频路径': 'paper_source\\audio\\模考8-L2-重听题.mp3',
                        'C1-1 答案': 'C', 'C1-2 题型（单选/多选/排序/重听）': '多选',
                       'C1-2 题干': '2. According to the woman, what error did she make in writing her original paper',
                       'C1-2 选项': "A. She did not follow the advice of the professor's graduate assistant.\n\nB. She forgot to include information about the ancient Romans and Egyptians in the paper.\n\nC. She began writing the paper before completing all the necessary research.\n\nD. She did not provide citations for all the sources she used to write the paper.\n\nE. She did not provide citations for all the sources she used to write the paper.",
                       'C1-2 重听题音频路径': '', 'C1-2 答案': 'C', 'C1-3 题型（单选/多选/排序/重听）': '重听',
                       'C1-3 题干': '3. How does the professor respond when the woman tells him that she wrote a new proposal',
                       'C1-3 选项': "A. He suggests that the woman's original proposal was stronger than the new proposal.\n\nB. He indicates that he could have helped the woman find suitable material for her original proposal.\n\nC. He expresses disappointment that he did not have an opportunity to suggest a new topic for the woman.\n\nD. He suggests possible sources of information about the woman's new topic.\n\n",
                       'C1-3 重听题音频路径': 'paper_source\\audio\\模考8-L2-重听题.mp3', 'C1-3 答案': 'B', 'C1-4 题型（单选/多选/排序/重听）': '单选',
                       'C1-4 题干': "4. What topic is covered in the woman's new proposal",
                       'C1-4 选项': 'A. The difference between civilizations that have writing and those that do not\n\nB. The ways in which international organizations interact with contemporary African governments\n\nC. The role of education in premodern Berber societies\n\nD. The ways in which children in some modern-day nomadic communities are educated\n\n',
                       'C1-4 重听题音频路径': '', 'C1-4 答案': 'D', 'C1-5 题型（单选/多选/排序/重听）': '单选',
                       'C1-5 题干': "5. What is the professor's opinion of the woman's new topic",
                       'C1-5 选项': "A. It is preferable to her original topic.\n\nB. It meets the assignment's requirements.\n\nC. It is too broad to be covered adequately.\n\nD. It is not relevant to current events\n\n",
                       'C1-5 重听题音频路径': '', 'C1-5 答案': 'B',
                        'L1 音频路径': 'paper_source\\audio\\模考8-L2-重听题.mp3',
                       'L1-1 题型（单选/多选/排序/重听）': '单选', 'L1-1 题干': '1. What is the lecture mainly about?',
                       'L1-1 选项': 'A. Early rivalries between France and England in the field of photography.\n\nB. Louis Daguerre’s role in the invention of the photograph.\n\nC. Various contributions to the invention of photography.\n\nD. The sequence of events leading to production of the first negative image.\n\n',
                       'L1-1 重听题音频路径': '', 'L1-1 答案': 'C', 'L1-2 题型（单选/多选/排序/重听）': '单选',
                       'L1-2 题干': '2. What does the professor imply about the historical record of the early days of photography?',
                       'L1-2 选项': 'A. It is incomplete.\n\nB. It was sometimes falsified by inventors.\n\nC. It was written mostly by people who had little knowledge of photography.\n\nD. It is more detailed than most other historical records from that time period.\n\n',
                       'L1-2 重听题音频路径': '', 'L1-2 答案': 'A', 'L1-3 题型（单选/多选/排序/重听）': '单选',
                       'L1-3 题干': '3. According to the professor, what circumstances led Anteine Florence to invent light writing?',
                       'L1-3 选项': 'A. He was inspired by the beauty of his surroundings.\n\nB. He was influenced by printing techniques used in Brazil.\n\nC. He did not have access to printing equipment and supplie\n\nD. He did not have formal training in printing techniques\n\n',
                       'L1-3 重听题音频路径': '', 'L1-3 答案': 'C', 'L1-4 题型（单选/多选/排序/重听）': '单选',
                       'L1-4 题干': '4. Why does the professor mention diplomas?',
                       'L1-4 选项': 'A. To indicate the capability of Florence’s light writing techniques.\n\nB. To explain why scientists at universities were unaware of Florence’s work.\n\nC. To indicate the level of education attained by most inventors of photography.\n\nD. To point out that photographs were printed on diplomas in the early 1830s.\n\n',
                       'L1-4 重听题音频路径': '', 'L1-4 答案': 'A', 'L1-5 题型（单选/多选/排序/重听）': '单选',
                       'L1-5 题干': '5. What was William Talbot’s major contribution to the development of photography?',
                       'L1-5 选项': 'A. A way to make paper sensitive to light.\n\nB. A device that gives photographers precise control of exposure times.\n\nC. A process for printing images on objects such as leaves.\n\nD. A process for producing photographs from a negative image.\n\n',
                       'L1-5 重听题音频路径': '', 'L1-5 答案': 'D', 'L1-6 题型（单选/多选/排序/重听）': '重听',
                       'L1-6 题干': '6. What is the professor’s opinion of Joseph Niepce’s contribution to the invention of photography?',
                       'L1-6 选项': 'A. Niepce would have made more progress if he had kept his methods a secret.\n\nB. Niepce should be acknowledged as the co-inventor of the daguerreotype.\n\nC. Niepce deserved more support from his colleagues.\n\nD. Niepce should not have claimed the ideas of other inventors as his own.\n\n',
                       'L1-6 重听题音频路径': 'paper_source\\audio\\模考8-L2-重听题.mp3', 'L1-6 答案': 'B',
                        'C2 音频路径': 'paper_source\\audio\\模考8-C2.mp3',
                       'C2-1 题型（单选/多选/排序/重听）': '单选',
                       'C2-1 题干': '1. Why does the man go to see the woman?',
                       'C2-1 选项': 'A. To ask for advice about discussing a paper\n\nB. B. to get help with an assignment\n\nC. C. To review paper he has written\n\nD. D. to get help from her\n\n',
                       'C2-1 重听题音频路径': '', 'C2-1 答案': 'B', 'C2-2 题型（单选/多选/排序/重听）': '单选',
                       'C2-2 题干': '2. What happen when the man went to the security office?',
                       'C2-2 选项': 'A. Security officer said that he had to pay a fee.\n\nB. He was unable to schedule an appointment.\n\nC. He found the office had just closed.\n\nD. The equipment used to make badges broke\n\n',
                       'C2-2 重听题音频路径': '', 'C2-2 答案': 'D', 'C2-3 题型（单选/多选/排序/重听）': '单选',
                       'C2-3 题干': '3. Why does the woman mention specific paragraph?',
                       'C2-3 选项': 'A. She thinks the man has included too.\n\nB. She thinks the man should reread.\n\nC. She wants the man to understand.\n\nD. She expect the man to explain\n\n',
                       'C2-3 重听题音频路径': '', 'C2-3 答案': 'C', 'C2-4 题型（单选/多选/排序/重听）': '单选',
                       'C2-4 题干': '4. What similarity is there between the current introduction and the conclusion in the man’s paper?',
                       'C2-4 选项': 'A. Both need to be shortened.\n\nB. Both engage his audience.\n\nC. Both contain bias.\n\nD. Both have to be specific\n\n',
                       'C2-4 重听题音频路径': '', 'C2-4 答案': 'A', 'C2-5 题型（单选/多选/排序/重听）': '单选',
                       'C2-5 题干': '5. What is the woman’s opinion about the concluding paragraph and the introduction',
                       'C2-5 选项': 'A. They should provide a brief summary and an average.\n\nB. They often oversimplify the main point of the paper.\n\nC. They are frequently unclear.\n\nD. They should offer readers a new hypothesis.\n\n',
                       'C2-5 重听题音频路径': '', 'C2-5 答案': 'A', 'L2 音频路径': 'paper_source\\audio\\模考8-L2.mp3',
                       'L2-1 题型（单选/多选/排序/重听）': '单选',
                       'L2-1 题干': '1. What is the main purpose of the lecture?',
                       'L2-1 选项': 'A. To compare the behaviors of three different bear species\n\nB. To examine changes to the habitat in which polar bears live\n\nC. To discuss recent insights into polar bear evolution\n\nD. To illustrate a new method of DNA analysis used in climate studies\n\n',
                       'L2-1 重听题音频路径': '', 'L2-1 答案': 'C', 'L2-2 题型（单选/多选/排序/重听）': '多选',
                       'L2-2 题干': '2. Why did the professor mentions use mitochondrial DNA for testing instead of nuclear DNA? Click on 2 answers',
                       'L2-2 选项': 'A. Mitochondrial DNA has a more stable structure than nuclear DNA has.\n\nB. Mitochondrial DNA has a shape that is more easily identifiable than that of nuclear DNA.\n\nC. Mitochondrial DNA is present in larger quantities in cells than nuclear DNA.\n\nD. Mitochondrial DNA analysis is a better-understood research tool than nuclear DNA analysis\n\n',
                       'L2-2 重听题音频路径': '', 'L2-2 答案': 'AC', 'L2-3 题型（单选/多选/排序/重听）': '单选',
                       'L2-3 题干': '3. What point does the professor make about brown bears?',
                       'L2-3 选项': 'A. They now compare with polar bears for food- and territory.\n\nB. They are the ancestors of polar bears.\n\nC. They face the same environmental threat as polar bears.\n\nD. Their jawbones can be easily distinguished from those of polar bears\n\n',
                       'L2-3 重听题音频路径': '', 'L2-3 答案': 'B', 'L2-4 题型（单选/多选/排序/重听）': '单选',
                       'L2-4 题干': '4. According to the professor, what do researchers believe about the Svalbard islands?',
                       'L2-4 选项': 'A. Polar bears first came into existence as a species on the islands.\n\nB. The separate islands were once joined together in a single large landmass.\n\nC. Interbreeding between polar bears and a species of brown bear occurred on the islands.\n\nD. The islands provided a refuge for polar bears during an ancient warming period.\n\n',
                       'L2-4 重听题音频路径': '', 'L2-4 答案': 'D', 'L2-5 题型（单选/多选/排序/重听）': '单选',
                       'L2-5 题干': '5. What does the professor imply when she discusses the current warming period?',
                       'L2-5 选项': 'A. The consequences of the current warming period will not be as serious as most scientists believe.\n\nB. The current warming period is progressing more slowly than previous warming periods.\n\nC. Arctic temperatures today are similar to temperatures during previous warming periods.\n\nD. The fast pace of the current warming period will threaten polar bears’ long-term survival.\n\n',
                       'L2-5 重听题音频路径': '', 'L2-5 答案': 'D', 'L2-6 题型（单选/多选/排序/重听）': '重听',
                       'L2-6 题干': 'Why does the professor imply when she says this:',
                       'L2-6 选项': 'A. The size of the grizzly bear population will soon stabilize.\n\nB. The future of the polar bear as a distinct species might be at risk.\n\nC. Hybridization has already diminished the polar bear population within a short period of time.\n\nD Hybrid species do not adapt well to sudden changes in the environment.\n\n',
                       'L2-6 重听题音频路径': 'paper_source\\audio\\模考8-L2-重听题.mp3', 'L2-6 答案': 'B',
                       'L3 音频路径': 'paper_source\\audio\\模考8-L3.mp3', 'L3-1 题型（单选/多选/排序/重听）': '单选',
                       'L3-1 题干': '1. What is the main purpose of the lecture?',
                       'L3-1 选项': 'A. To explain methods astronomers use to classify stars\n\nB. To explain the formation of molecular clouds in the universe\n\nC. To discuss how some stellar embryos fail to become stars\n\nD. To discuss similarities between brown dwarfs and planets\n\n',
                       'L3-1 重听题音频路径': '', 'L3-1 答案': 'C', 'L3-2 题型（单选/多选/排序/重听）': '单选',
                       'L3-2 题干': '2. According to the professor, why is the study of brown dwarfs particularly challenging?',
                       'L3-2 选项': 'A. They cannot be detected directly.\n\nB. They combine characteristics of very distinct celestial objects.\n\nC. They appear in colors ranging from brown to red.\n\nD. They are always near very bright stars.\n\n',
                       'L3-2 重听题音频路径': '', 'L3-2 答案': 'B', 'L3-3 题型（单选/多选/排序/重听）': '单选',
                       'L3-3 题干': '3. Why does the professor discuss how stars originate?',
                       'L3-3 选项': 'A. To explain how brown dwarfs begin to form\n\nB. To suggest that brown dwarfs do not originate in molecular clouds\n\nC. To explain why brown dwarfs emit light billions of years\n\nD. To show that stellar embryos cause turbulence within molecular clouds\n\n',
                       'L3-3 重听题音频路径': '', 'L3-3 答案': 'A', 'L3-4 题型（单选/多选/排序/重听）': '单选',
                       'L3-4 题干': '4. According to the ejection theory, why do some stellar embryos stop growing before they become stars?',
                       'L3-4 选项': 'A. The motion of dust and gas inhibits their growth.\n\nB. The cores in which they form are not dense enough.\n\nC. They start forming in the area of a molecular cloud with the least amount of material.\n\nD. They are moved by gravitational forces to areas outside cores.\n\n',
                       'L3-4 重听题音频路径': '', 'L3-4 答案': 'D', 'L3-5 题型（单选/多选/排序/重听）': '单选',
                       'L3-5 题干': '5. Why does the professor mention that newborn stars are surrounded by disks of dust and gas?',
                       'L3-5 选项': 'A. To describe a method for testing two theories about brown dwarfs\n\nB. To clarify how brown dwarfs are drawn into star systems\n\nC. To emphasize that brown dwarfs move at low velocities\n\nD. To introduce planet formation as the topic of the next lecture\n\n',
                       'L3-5 重听题音频路径': '', 'L3-5 答案': 'A', 'L3-6 题型（单选/多选/排序/重听）': '单选',
                       'L3-6 题干': '6. What is the professor’s attitude toward the two theories?',
                       'L3-6 选项': 'A. He is convinced that neither of them can explain why brown dwarfs have stellar disks.\n\nB. He hopes both theories will be confirmed by computer simulations.\n\nC. He thinks evidence supports the turbulence theory even if he cannot rule out the ejection theory.\n\nD. He finds the ejection theory more attractive than the turbulence theory.\n\n',
                       'L3-6 重听题音频路径': '', 'L3-6 答案': 'C',
                       '口语1 问题': 'Task 1. Some people believe that businesses should be required to spend a certain amount of their profits on social programs that benefit the public and the communities where they operate. Others believe that businesses should be able to decide for themselves how to spend their profits. Which point of view do you agree with? Use details and examples to explain your opinion.\n\n',
                       '口语2 标题': 'University to Introduce Fitness Passes',
                       '口语2 题干': 'Besides providing equipment for individuals to work out, the university gym also offers weekly group fitness classes in activities like aerobics and yoga. Currently students pay a fee for each class session they attend. But soon they will be able to purchase a Fitness Pass, a special card giving students unlimited access to fitness classes for the whole semester. The pass will help students who attend fitness classes regularly to save money since it costs less than paying for individual sessions. The Fitness Pass will also ensure that classes start promptly since students can simply show their cards when they enter each class instead of waiting to pay.\n\n',
                       '口语2 问题': 'The woman expresses her opinion about the plan described in the announcement. Briefly summarize the plan. Then state her opinion about the plan and explain the reasons she gives for holding that opinion.\n\n',
                       '口语2 音频路径': 'paper_source\\audio\\模考8-口语-Task2.mp3', '口语3 标题': 'Channel Conflict',
                       '口语3 题干': 'Manufacturers that create products often rely on other businesses or stores to sell those products to consumers.These stores are the channel through which the products reach consumers. Sometimes a disagreement arises between the manufacturer and a store. This is called a channel conflict. Such disputes commonly occur because the manufacturer and the store selling the products may have different goals or priorities. In order to resolve the conflict, the manufacturer and store may need to negotiate and reach an agreement over how their opposing needs can be met.\n\n',
                       '口语3 问题': "Explain how the example from the professor's lecture illustrates the concept of a channel conflict.",
                       '口语3 音频路径': 'paper_source\\audio\\模考8-口语-Task3.mp3',
                       '口语4 问题': "Task 4. Summarize the professor's lecture about the effects of increased carbon dioxide in the atmosphere. Be sure to include the example of the caterpillar.\n\n",
                       '口语4 音频路径': 'paper_source\\audio\\模考8-口语-Task4.mp3',
                       '综合写作文章': "An intriguing underwater rock structure exists off the coast of Japan. Since the discovery of the rock formation in the 1980s, archaeologists and geologists have debated whether the structure is the result of natural processes or of human construction. Several scholars have argued that it was made by humans based on several pieces of evidence.\n\nAncient Civilization\n\nFirst, there is evidence that an ancient civilization was present in the region around 10,000 years ago. At that time, the sea level was lower, and the structure would have been on dry land. Recent expeditions to the area have uncovered bones, pottery fragments, and parts of tools that are many thousands of years old. With this archaeological evidence, it's reasonable to hypothesize that ancient people living around the structure could have carved it when the area was not yet underwater.\n\nFeatures Designed for Human Use\n\nSecond, pictures of the structure reveal features that seem to be intended for human use (see illustration). For example, there is a section that appears to be a wide, flat platform with stairs along its sides, as well as several large rock pieces that are likely walls. The presence of stairs and walls suggests that the structure was made for human use and was built by humans. Based on such features, some archaeologists have proposed that the whole structure may be a remnant of an ancient city.\n\nStraight Edges\n\nFinally, the rock from the structure has very straight, clear edges. If the rocky structure had been created by a natural process such as water erosion, its edges would be round. There are also several rock elements that intersect at sharp 90-degree angles. These straight edges and angles suggest that the rock was carved by humans rather than by waves and currents of the ocean, which would have left gentler curved edges.\n\n",
                       '综合写作问题': 'Directions: You have 20 minutes to plan and write your response. Your response will be judged on the basis of the quality of your writing and on how well your response presents the points in the lecture and their relationship to the reading passage. Typically, an effective response will be 150 to 225 words.\n\nQuestion: Summarize the points made in the lecture, being sure to explain how they challenge the specific theories presented in the reading passage.\n\n',
                       '综合写作音频路径': 'paper_source\\audio\\模考8-综合写作.mp3',
                       '独立写作截图路径': 'paper_source\\pictures\\模考8.png'},1,1
                )
    root.mainloop()


















