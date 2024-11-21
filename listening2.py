import tkinter as tk
from PIL import Image, ImageTk
import soundfile as sf
import sounddevice as sd
import threading
import numpy as np
from get_audio_time import get_audio_duration
from process_reading_listening_result import generate_rl_result
from tkinter import messagebox
from speaking import Speaking


class Listening2:
    def __init__(self, root, paper, reading_user, reading_answer, listening1_user, listening1_answer):
        self.root = root
        self.paper = paper
        self.reading_user = reading_user
        self.reading_answer = reading_answer
        self.listening1_user = listening1_user
        self.listening1_answer = listening1_answer
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

        self.listening_user_choice = ['none'] * 17
        self.listening_answer_choice = ['none'] * 17

        self.total_time_left = 650


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
            self.total_time_left += 2
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

    def create_first_page(self):
        page_frame = tk.Frame(self.root)
        canvas = tk.Canvas(page_frame, width=self.root.screen_width, height=self.root.screen_height)
        canvas.pack(fill=tk.BOTH, expand=True)
        canvas.create_image(0, 0, image=self.bg_img, anchor='nw')

        next_button = tk.Button(page_frame, text="start listening part2", bg='white', command=self.go_next)
        next_button.place(relx=0.44, rely=0.55, relwidth=0.12, relheight=0.06)
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
        abcd = ['A', 'B', 'C', 'D','E']
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

    def format_time(self, seconds):
        """将秒数格式化为分钟和秒数"""
        minutes, seconds = divmod(seconds, 60)
        return f"{minutes:02}:{seconds:02}"

    def go_next(self):
        if self.current_page_index < len(self.pages) - 1:
            for widget in self.root.winfo_children():
                widget.forget()
            self.current_page_index += 1
            self.display_page(self.current_page_index)
        else:
            self.go_to_speaking()


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
        reading_score, listening_score = generate_rl_result(self.paper.get('name'), self.reading_user, self.reading_answer, self.listening1_user, self.listening1_answer, self.listening_user_choice, self.listening_answer_choice)

        for widget in self.root.winfo_children():
            widget.destroy()
        Speaking(self.root, self.paper, reading_score, listening_score)

    def go_to_speaking(self):
        result = messagebox.askokcancel("确认", "Are you ready to enter the next part?")

        if result:
            for widget in self.root.winfo_children():
                widget.destroy()
        reading_score, listening_score = generate_rl_result(self.paper.get('name'), self.reading_user,
                                                            self.reading_answer, self.listening1_user,
                                                            self.listening1_answer, self.listening_user_choice,
                                                            self.listening_answer_choice)
        Speaking(self.root, self.paper, reading_score, listening_score)

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

        page = self.create_first_page()
        self.pages.append(page)

        C2_audio_path = self.paper.get('C2 音频路径')
        L2_audio_path = self.paper.get('L2 音频路径')
        L3_audio_path = self.paper.get('L3 音频路径')

        page = self.play_audio_page(C2_audio_path)
        self.pages.append(page)

        for c2 in range(5):
            question_type = self.paper.get(f'C2-{c2 + 1} 题型（单选/多选/排序/重听）')
            question = self.paper.get(f'C2-{c2 + 1} 题干')
            choices = self.paper.get(f'C2-{c2 + 1} 选项')
            relisten_video = self.paper.get(f'C2-{c2 + 1} 重听题音频路径')
            answer = self.paper.get(f'C2-{c2 + 1} 答案')
            self.listening_answer_choice[c2] = answer
            if question_type[:2] == '单选':
                page = self.create_one_choice_pages(c2, question, choices)
                self.pages.append(page)
            if question_type[:2] == '多选':
                page = self.create_multiple_choice_pages(c2, question, choices)
                self.pages.append(page)
            if question_type[:2] == '排序':
                page = self.create_sequence_pages(c2, question, choices)
                self.pages.append(page)
            if question_type[:2] == '重听':
                page = self.create_relisten_pages(c2, relisten_video, question, choices)
                self.pages.append(page)

        page = self.play_audio_page(L2_audio_path)
        self.pages.append(page)

        for l2 in range(5, 11):
            question_type = self.paper.get(f'L2-{l2 - 4} 题型（单选/多选/排序/重听）')
            question = self.paper.get(f'L2-{l2 - 4} 题干')
            choices = self.paper.get(f'L2-{l2 - 4} 选项')
            relisten_video = self.paper.get(f'L2-{l2 - 4} 重听题音频路径')
            answer = self.paper.get(f'L2-{l2 - 4} 答案')
            self.listening_answer_choice[l2] = answer
            if question_type[:2] == '单选':
                page = self.create_one_choice_pages(l2, question, choices)
                self.pages.append(page)
            if question_type[:2] == '多选':
                page = self.create_multiple_choice_pages(l2, question, choices)
                self.pages.append(page)
            if question_type[:2] == '排序':
                page = self.create_sequence_pages(l2, question, choices)
                self.pages.append(page)
            if question_type[:2] == '重听':
                page = self.create_relisten_pages(l2, relisten_video, question, choices)
                self.pages.append(page)

        page = self.play_audio_page(L3_audio_path)
        self.pages.append(page)

        for l3 in range(11, 17):
            question_type = self.paper.get(f'L3-{l3 - 10} 题型（单选/多选/排序/重听）')
            question = self.paper.get(f'L3-{l3 - 10} 题干')
            choices = self.paper.get(f'L3-{l3 - 10} 选项')
            relisten_video = self.paper.get(f'L3-{l3 - 10} 重听题音频路径')
            answer = self.paper.get(f'L3-{l3 - 10} 答案')
            self.listening_answer_choice[l3] = answer
            if question_type[:2] == '单选':
                page = self.create_one_choice_pages(l3, question, choices)
                self.pages.append(page)
            if question_type[:2] == '多选':
                page = self.create_multiple_choice_pages(l3, question, choices)
                self.pages.append(page)
            if question_type[:2] == '排序':
                page = self.create_sequence_pages(l3, question, choices)
                self.pages.append(page)
            if question_type[:2] == '重听':
                page = self.create_relisten_pages(l3, relisten_video, question, choices)
                self.pages.append(page)


if __name__ == '__main__':
    root = tk.Tk()
    Listening2(root, {'阅读1 标题': 'Stone Tools and Pottery Fragments', '阅读1 文本': 'Aside from ancient buildings, in sheer bulk the largest part of the archaeological record is made up of stone tools and pottery fragments (shards). Stone tools are the earliest known artifacts, having been first used more than two million years ago, and they have remained in use to the present day. When a chunk of fine-grain stone is struck with sufficient force at the proper angle with another rock or with a wood or bone baton, a shock wave will pass through the stone and detach a flake of the desired size and shape. In analyzing ancient stone tools, many archaeologists have mastered the skills needed to make stone tools themselves. Few things are sharper than a fragment struck from fine-grain flint or from obsidian (volcanic glass). Obsidian is so fine grained that flakes of it can have edges only about twenty molecules thick- hundreds of times thinner than steel tools.\n\nThrough experimentation, some archaeologists are able to produce copies of almost every stone tool type used in antiquity. A common research strategy is to make flint tools, use them to cut up meat, saw wood, clean hides, bore holes, etc, and then compare the resulting wear traces with the marks found on ancient artifacts. Sometimes electron-scanning microscopes are used to study minute variations in these use marks. Some rough correspondence can be found between the types of uses and the characteristics of wear marks, but there are many ambiguities.\n\nEthriographic data from people who still use these tools, like one study of how the IKung hunter- gatherers use different styles of stone spear points to identity their different social groupings, indicate that even crude-looking stone tools may reflect a great deal of the social and economic structure.\n\nCeramics were in use much later than the first stone tools (appearing in quantity in many places about 10,000  years  ago),  but  they  were  used  in   such  massive  quantities  in  antiquity  that,  for  many archaeologists, work life consists mainly of the slow sorting and analyzing of pottery fragments. Ceramic pots were first made by hand and dried in the sun or in low temperature kilns, a process that did not produce a very durable material. But in many areas of Africa, Asia and Europe high-temperature kilns produced pottery that is nearly a form of glass, and fragments of these pots survive even when the pottery is broken.\n\nCeramics form such a large part of archaeologists’ lives because ceramics express so much about the people who made them. Pots are direct indicators of function in that they show how diets and economies changed over time. Archaeologists have documented how pottery in the American Southwest changed in prehistoric times as a diet developed that included boiled seeds of various native plants, and pottery was developed to withstand the heat and mechanical stresses of the boiling process.\n\nCeramics are almost always analyzed on the basis of their style. This idea of style is hard to define, but changing styles are the basis on which archaeologists date much of the archaeological record. But for many  archaeologists,  ceramic  styles  are  more  than  just  convenient  devices  of  dating.  For  many archaeologists, stylistic decoration of artifacts is the primary means by which one can enter the cognitive world of the ancients.  Societies throughout history have invested their objects with styles that have profound and complex meanings and effects. In the case of the Maya and every other early civilization, rulers used particular symbols and styles as mechanisms through which they portrayed, communicated,and implemented their power. In all societies, styles fix social meaning and are powerful ways in which social groups define and construct their culture. Styles of objects, language, and personal behavior identity people in terms of gender, age group, ethnic group, socioeconomic class, and in many other important ways. Some researchers, for example, have argued that a particular kind of pottery, called Ramey incised (which is incised with figures of eyes, fish, arrows, and abstract objects and was used by the people in the area of present-day Missouri and Illinois at about A.D 900), was primarily used to distribute food but was also used to communicate the idea that the society’s elite, for whom the pots were made, were mediators of cosmic forces.\n\n', '阅读题目1-1 题型（单选/双选/句子插入/六选三）': '单选', '阅读题目1-1 题干': 'According to paragraph 1, each of the following is true of stone tools EXCEPT', '阅读题目1-1 选项（A,B,C,D开头，不同选项换行）': 'A. They were first produced more than two million years ago.\n\nB. They are still being used today.\n\nC. They are made of fine-grained stones such as flint or obsidian.\n\nD. Their edges are never as thin or as sharp as those of steel tools.\n\n', '阅读题目1-1 呈现句/词（没有为空）': '', '阅读题目1-1 答案': 'D', '阅读题目1-2 题型（单选/双选/句子插入/六选三）': '单选', '阅读题目1-2 题干': 'According to paragraph 2, archaeologists make and use their own stone tools in order to', '阅读题目1-2 选项（A,B,C,D开头，不同选项换行）': 'A. find out how strong different types of stone tools are\n\nB. find out what kinds of tasks such tools were used for in ancient times\n\nC. study the copies under electron microscopes and to avoid damaging the originals\n\nD. show that ancient multipurpose tools were practical and easy to use\n\n', '阅读题目1-2 呈现句/词（没有为空）': '', '阅读题目1-2 答案': 'B', '阅读题目1-3 题型（单选/双选/句子插入/六选三）': '单选', '阅读题目1-3 题干': 'Which of the following questions about the IKung is answered in paragraph 3?', '阅读题目1-3 选项（A,B,C,D开头，不同选项换行）': 'A. Are the IKung rare among today’s hunter-gatherers in using stone tools?\n\nB. Is the social structure of the IKung more complex than that of most hunter-gatherer societies?\n\nC. Does the IKung’s use of several styles of stone tools have a social function?\n\nD. Do the IKung use stone tools other than spear points?\n\n', '阅读题目1-3 呈现句/词（没有为空）': '', '阅读题目1-3 答案': 'C', '阅读题目1-4 题型（单选/双选/句子插入/六选三）': '单选', '阅读题目1-4 题干': 'According to paragraph 4, which of the following is true of the earliest ceramics?', '阅读题目1-4 选项（A,B,C,D开头，不同选项换行）': 'A. They were in use before the earliest stone tools.\n\nB. They were used in only a few places 10,000 years ago.\n\nC. They appeared in many places about 10,000 years ago.\n\nD. They were all baked in low-temperature kilns.\n\n', '阅读题目1-4 呈现句/词（没有为空）': '', '阅读题目1-4 答案': 'C', '阅读题目1-5 题型（单选/双选/句子插入/六选三）': '单选', '阅读题目1-5 题干': 'Paragraph 4 suggests sun-dried pots', '阅读题目1-5 选项（A,B,C,D开头，不同选项换行）': 'A. interest archaeologists less than stone tools because they are not as old.\n\nB.  account for comparatively few of the pottery fragments that archaeologists study\n\nC. are more common in Africa, Asia, or Europe than other parts of the world.\n\nD. are easier to sort and analyze than pottery made in high-temperature kilns.\n\n', '阅读题目1-5 呈现句/词（没有为空）': '', '阅读题目1-5 答案': 'B', '阅读题目1-6 题型（单选/双选/句子插入/六选三）': '单选', '阅读题目1-6 题干': 'In paragraph 5, the author discusses pottery in the American Southwest in order to', '阅读题目1-6 选项（A,B,C,D开头，不同选项换行）': 'A. emphasize that ceramics are usually the only means of reconstructing the diet and economic activity of prehistoric peoples.\n\nB. argue that changes in the style of pottery are usually a result of changes in food preparation.\n\nC. explain why certain types of prehistoric pottery have been able to survive better than others.\n\nD. support the claim that ceramics provide important dining and economical information about their users\n\n', '阅读题目1-6 呈现句/词（没有为空）': '', '阅读题目1-6 答案': 'D', '阅读题目1-7 题型（单选/双选/句子插入/六选三）': '单选', '阅读题目1-7 题干': 'According  to paragraph  6,decorating  artifacts  in  particular  styles  served  each  of the  following functions in ancient societies EXCEPT', '阅读题目1-7 选项（A,B,C,D开头，不同选项换行）': 'A.to maintain the power of the societies’ rulers\n\nB. to mark socially relevant distinctions between groups\n\nC. to establish the superiority of a society’s artistic values\n\nD. to define important aspects of the society’s culture\n\n', '阅读题目1-7 呈现句/词（没有为空）': '', '阅读题目1-7 答案': 'C', '阅读题目1-8 题型（单选/双选/句子插入/六选三）': '单选', '阅读题目1-8 题干': 'Which of the sentences below best expresses the essential information in the highlighted sentence in the passage? Incorrect choices change the meaning in important ways or leave out essential information.', '阅读题目1-8 选项（A,B,C,D开头，不同选项换行）': 'A. Some researchers argue that pottery of the Ramey Incises style was used not only to distribute food but also to communicate that the society’s elite were mediators of cosmic forces.\n\nB. Some researchers argue that the figures of eyes, fish, arrows and abstract objects were incised on Ramey Incised pottery to communicate that those who provided the pots were members of the elite.\n\nC. Some researchers argue that the primary function of Ramey Incised pottery was food distribution rather than a way of communicating the status of the society’s elite.\n\nD. Some researchers argue that, based on the kinds of symbols incised on pottery, that pottery was sometimes used to mediate cosmic forces.\n\n', '阅读题目1-8 呈现句/词（没有为空）': 'Some researchers, for example, have argued that a particular kind of pottery, called Ramey incised (which is incised with figures of eyes, fish, arrows, and abstract objects and was used by the people in the area of present-day Missouri and Illinois at about A.D 900), was primarily used to distribute food but was also used to communicate the idea that the society’s elite, for whom the pots were made, were mediators of cosmic forces.', '阅读题目1-8 答案': 'A', '阅读题目1-9 题型（单选/双选/句子插入/六选三）': '句子插入', '阅读题目1-9 题干': 'Look at the four squares [■] that indicate where the following sentence could be added to the passage.\n\nMaya rulers, for example, used symbols on their war banners to communicate that they had great power because of the support of patron gods.\n\nWhere would the sentence best fit? Click on a square [■] to add the sentence to the passage.\n\nCeramics are almost always analyzed on the basis of their style. This idea of style is hard to define, but changing styles are the basis on which archaeologists date much of the archaeological record. But for many  archaeologists,  ceramic  styles  are  more  than  just  convenient  devices  of  dating.  For  many archaeologists, stylistic decoration of artifacts is the primary means by which one can enter the cognitive world of the ancients.  Societies throughout history have invested their objects with styles that have profound and complex meanings and effects. [■] In the case of the Maya and every other early civilization, rulers used particular symbols and styles as mechanisms through which they portrayed, communicated, and implemented their power. [■] In all societies, styles fix social meaning and are powerful ways in which social groups define and construct their culture. [■] Styles of objects, language, and personal behavior identity people in terms of gender, age group, ethnic group, socioeconomic class, and in many other important ways. [■] Some researchers, for example, have argued that a particular kind of pottery, called Ramey incised (which is incised with figures of eyes, fish, arrows, and abstract objects and was used by the people in the area of present-day Missouri and Illinois at about A.D 900), was primarily used to distribute food but was also used to communicate the idea that the society’s elite, for whom the pots were made, were mediators of cosmic forces. Where would the sentence best fit?\n\n', '阅读题目1-9 选项（A,B,C,D开头，不同选项换行）': 'A.\n\nB.\n\nC.\n\nD.\n\n', '阅读题目1-9 呈现句/词（没有为空）': 'Some researchers, for example, have argued that a particular kind of pottery, called Ramey incised (which is incised with figures of eyes, fish, arrows, and abstract objects and was used by the people in the area of present-day Missouri and Illinois at about A.D 900), was primarily used to distribute food but was also used to communicate the idea that the society’s elite, for whom the pots were made, were mediators of cosmic forces. Where would the sentence best fit?\n\n', '阅读题目1-9 答案': 'B', '阅读题目1-10 题型（单选/双选/句子插入/六选三）': '六选三', '阅读题目1-10 题干': 'Directions: An  introductory  sentence  for  a  brief  summary  of the  passage  is  provided  below. Complete the summary by selecting the THREE answer choices that express the most important ideas in the passage. Some answer choices do not belong in the summary because they express ideas that are not presented in the passage or are minor ideas in the passage. This question is worth 2 points.\n\nStone tools and pottery fragments are two of the most common kinds of archaeological finds.\n\n', '阅读题目1-10 选项（A,B,C,D开头，不同选项换行）': 'A. Stone tools are the oldest known artifacts, predating the development of ceramics by about two million years.\n\nB. The styles of stone tools produced by prehistoric peoples are more reliable indicators of their society’s social and economic structure than the styles of their ceramics.\n\nC. Some researchers believe that the  figures  and  symbols  found  on pottery  may have multiple meanings, but this has not yet been fully established.\n\nD. Archaeologists know how stone tools were made and can produce copies themselves, but it is often difficult to determine how any particular ancient tool was used.\n\nE. The earliest evidence of ceramic production comes from Africa, Asia, and Europe, where the development of specialized technologies made pots nearly indestructible.\n\nF. Because pottery had both practical and symbolic uses, it can tell researchers a lot about the diet, economy, and social structure of ancient societies.\n\n', '阅读题目1-10 呈现句/词（没有为空）': 'Stone tools and pottery fragments are two of the most common kinds of archaeological finds.', '阅读题目1-10 答案': 'ADF', '阅读2 标题': 'Animal Behavior', '阅读2 文本': 'By the early 1900s the field of animal behavior had split into two major branches. One branch, ethology, developed primarily in Europe. To ethologists, what is striking about animal behaviors in that they are fixed and seemingly unchangeable? For example, kittens and puppies play in characteristic but different ways. Present a kitten with a ball of yarn and invariably it draws back its head and bats the yarn with claws extended. Kittens are generally silent as they play, and their tails twitch. Puppies, by contrast, are most likely to pounce flat-footed on a ball of yarn. They bit and bark and their tails wag. Ethologists came to believe that ultimately even the most complex animal behaviors could be broken down into a series of unchangeable stimulus/response reactions. They became convinced that the details of these patterns were as distinctive of a particular group of animals as were anatomical characteristics. For well over half a century, their search for and description of innate patterns of animal behavior continued.\n\nMeanwhile, mainly in North America, the study of animal behavior took a different tack, developing into comparative behavior. Of interest to comparative behaviorists was where a particular came from, that is, its evolutionary history, how the nervous system controlled it, and the extent to which it could be modified. In 1894, C. Lloyd Morgan, an early comparative behaviorist, insisted that animal behavior be explained as simply as possible without reference to emotions or motivations since these could not be observed or measured. In Morgan’s research, animals were put in simple situations, presented with an easily described stimulus, and their resultant behavior described.\n\nThe extension to animals of behaviorism—the idea that the study of behavior should be restricted to only those elements that can be directly observed—was an important development in comparative behavior. Studies of stimulus/response and the importance of simple rewards to enforce and modify animal behavior were stressed. Not surprisingly, comparative behaviorists worked most comfortably in the laboratory. Comparative behaviorists stressed the idea that animal behavior could be modified, while their ethologist colleagues thought it was innate and unchangeable. Inevitably, the two approaches led to major disagreements.\n\nTo early ethologists, the major driving force in behavior was instinct, behaviors that are inherited and unchangeable. Moths move towards light because they inherit the mechanism to so respond to light. Although dogs have more options available to them, they bark at strangers for much the same reasons. The comparative behaviorists disagreed: learning and rewards are more important factors than instinct in animal behavior. Geese are not born with the ability to retrieve lost eggs when they roll out the nest, they learn to do so. If their behavior seems sometimes silly to humans because it fails to take new conditions into account, that is because the animal’s ability to learn is limited. There were too many examples of behaviors modified by experience for comparative behaviorists to put their faith in instincts.\n\nThe arguments came to a peak in the 1950s and became known as the nature or nurture controversy. Consider how differently an ethologist and a comparative behaviorist would interpret the begging behavior of a hatchling bird. The first time a hatchling bird is approached by its parent, it begs for food. All baby birds of a particular species beg in exactly the same way. Obviously, said the ethologists, they inherited the ability and the tendency to beg. Baby birds did not have to learn the behavior, they were born with it—a clear example of innate, unchanging behavior. Not  so, countered the comparative behaviorists.  Parent  birds  teach  their  young  to beg by  stuffing  food  in  their  open  mouths.  Later experiments showed that before hatching, birds make and respond to noises of their nest mates and adults. Is it not possible that young birds could learn to beg prenatally?\n\nIt was hard for ethologists to accept that innate behaviors could be modified by learning. It was equally difficult for comparative behaviorists to accept that genetic factors could dominate learning experiences. The controversy raged for over a decade. Eventually, however, the distinctions between the two fields narrowed. The current view is that both natural endowments and environmental factors work together to shape behavior.\n\n', '阅读题目2-1 题型（单选/双选/句子插入/六选三）': '单选', '阅读题目2-1 题干': 'According to paragraph  1, what do ethologists think is the most notable characteristic of animal behavior?', '阅读题目2-1 选项（A,B,C,D开头，不同选项换行）': 'A. Animal responses in most situations are predictable and do not vary\n\nB. In similar situations, different animal species often behave in similar ways.\n\nC. Even in ordinary situations, animal behavior can be unusually complex.\n\nD. Animal behavior may sometimes include stimulus/response reactions.\n\n', '阅读题目2-1 呈现句/词（没有为空）': '', '阅读题目2-1 答案': 'A', '阅读题目2-2 题型（单选/双选/句子插入/六选三）': '单选', '阅读题目2-2 题干': 'According to paragraph 2, C. Lloyd Morgan agreed with which of the following statements about animal behavior?', '阅读题目2-2 选项（A,B,C,D开头，不同选项换行）': 'A. Only those elements of animal behavior that could be observed and measured should be used to explain it.\n\nB. Any study of animal behavior should include an explanation of emotions and motivations.\n\nC. Emotions and motivations can be measured indirectly using simple experimental situations.\n\nD. Experimental  situations  are  less  than  ideal  if researchers  want  to  develop  a  comprehensive explanation of animal behavior.\n\n', '阅读题目2-2 呈现句/词（没有为空）': '', '阅读题目2-2 答案': 'A', '阅读题目2-3 题型（单选/双选/句子插入/六选三）': '单选', '阅读题目2-3 题干': 'According to paragraph 2, comparative behaviorists were interested in finding answers to all of the following questions EXCEPT', '阅读题目2-3 选项（A,B,C,D开头，不同选项换行）': 'A. How has animal behavior changed over time?\n\nB.  How can emotions causing a specific behavior in one animal species help explain behavior in other animal species?\n\nC. To what degree can animal behavior be changed?\n\nD. How does the nervous system regulate animal behavior?\n\n', '阅读题目2-3 呈现句/词（没有为空）': '', '阅读题目2-3 答案': 'B', '阅读题目2-4 题型（单选/双选/句子插入/六选三）': '单选', '阅读题目2-4 题干': 'Paragraph 3 suggests that comparative behaviorists’ conclusions concerning animal behavior were based', '阅读题目2-4 选项（A,B,C,D开头，不同选项换行）': 'A. on the observation that rewards do not affect inherited animal behavior\n\nB. on the application of stress to modify animal behavior\n\nC. most often on the results of laboratory experiments\n\nD. more on stimulus/response reactions than on simple rewards\n\n', '阅读题目2-4 呈现句/词（没有为空）': '', '阅读题目2-4 答案': 'C', '阅读题目2-5 题型（单选/双选/句子插入/六选三）': '单选', '阅读题目2-5 题干': 'According to paragraph 4, why did comparative behaviorists believe that their view of instinct in animal behavior was correct?', '阅读题目2-5 选项（A,B,C,D开头，不同选项换行）': 'A. They had observed that animals can respond to the same stimulus in different ways.\n\nB. They had demonstrated that animals could use learned behaviors in new conditions.\n\nC. They had acquired sufficient evidence that instincts vary from one animal to another.\n\nD. They had shown that the behavior of many different animals had been changed by learning.\n\n', '阅读题目2-5 呈现句/词（没有为空）': '', '阅读题目2-5 答案': 'D', '阅读题目2-6 题型（单选/双选/句子插入/六选三）': '单选', '阅读题目2-6 题干': 'In paragraph 5, why does the author discuss the begging behavior of a hatchling bird?', '阅读题目2-6 选项（A,B,C,D开头，不同选项换行）': 'A. To support the view that instinct explains animal behavior better than learning does\n\nB. To demonstrate that ethologists are correct about the limited ability of animals to learn\n\nC. To contrast an ethologist’s explanation of a particular animal behavior with that of a comparative behaviorist\n\nD. To question whether the discussion about the roles of nature and nurture was a valid one\n\n', '阅读题目2-6 呈现句/词（没有为空）': '', '阅读题目2-6 答案': 'C', '阅读题目2-7 题型（单选/双选/句子插入/六选三）': '单选', '阅读题目2-7 题干': 'The word “current” in the passage is closest in meaning to', '阅读题目2-7 选项（A,B,C,D开头，不同选项换行）': 'A. ideal\n\nB. basic\n\nC. alternative\n\nD. present\n\n', '阅读题目2-7 呈现句/词（没有为空）': 'current', '阅读题目2-7 答案': 'D', '阅读题目2-8 题型（单选/双选/句子插入/六选三）': '句子插入', '阅读题目2-8 题干': 'Look at the four squares [■] that indicate where the following sentence could be added to the passage.\n\nNatural flooding, however, does not raise the water table nearly as much and thus does not have these sorts of consequences. Where would the sentence best fit? Click on a square [■] to add the sentence to the passage.\n\nThis view is supported by the behavior of insects as well as animals.\n\nTo early ethologists, the major driving force in behavior was instinct, behaviors that are inherited and unchangeable. [■] Moths move towards light because they inherit the mechanism to so respond to light. [■] Although dogs have more options available to them, they bark at strangers for much the same reasons.\n\n[■] The comparative behaviorists disagreed: learning and rewards are more important factors than instinct in animal behavior. [■] Geese are not born with the ability to retrieve lost eggs when they roll out the nest, they learn to do so. If their behavior seems sometimes silly to humans because it fails to take new conditions into account, that is because the animal’s ability to learn is limited. There were too many examples of behaviors modified by experience for comparative behaviorists to put their faith in instincts.\n\n', '阅读题目2-8 选项（A,B,C,D开头，不同选项换行）': 'A.\n\nB.\n\nC.\n\nD.\n\n', '阅读题目2-8 呈现句/词（没有为空）': '', '阅读题目2-8 答案': 'A', '阅读题目2-9 题型（单选/双选/句子插入/六选三）': '单选', '阅读题目2-9 题干': '此题不存在，请选A', '阅读题目2-9 选项（A,B,C,D开头，不同选项换行）': 'A.\n\nB.\n\nC.\n\nD.\n\n', '阅读题目2-9 呈现句/词（没有为空）': '', '阅读题目2-9 答案': 'A', '阅读题目2-10 题型（单选/双选/句子插入/六选三）': '六选三', '阅读题目2-10 题干': '此题不存在，请选ACE', '阅读题目2-10 选项（A,B,C,D开头，不同选项换行）': 'A.\n\nB.\n\nC.\n\nD.\n\nE.\n\nF.\n\n', '阅读题目2-10 呈现句/词（没有为空）': '', '阅读题目2-10 答案': 'ACE', 'C1 音频路径': 'paper_source\\\\audio\\\\模考5-C1.mp3', 'C1-1 题型（单选/多选/排序/重听）': '单选', 'C1-1 题干': '1.What are the speakers mainly discussing?', 'C1-1 选项': 'A. An artist who was discussed in a recent class\n\nB. The requirements for an upcoming project\n\nC. Reasons that the student will miss an upcoming class\n\nD. The topic of a paper the student was writing\n\n', 'C1-1 重听题音频路径': '', 'C1-1 答案': 'A', 'C1-2 题型（单选/多选/排序/重听）': '单选', 'C1-2 题干': '2. What does the student say about the national debate tournament?', 'C1-2 选项': "A. The tournament site was further away than she would have liked.\n\nB. She was satisfied with her team’s performance at the tournament.\n\nC. More teams were allowed to compete this year.\n\nD. This year's debate topic was unusually complex.\n\n", 'C1-2 重听题音频路径': '', 'C1-2 答案': 'B', 'C1-3 题型（单选/多选/排序/重听）': '单选', 'C1-3 题干': '3. According to the professor, what was Alexander Calder’s most significant contribution to the art world?', 'C1-3 选项': 'A. He produced an impressive range of both painting and sculpture.\n\nB. He used a new material to create his sculptures.\n\nC. He proved that engineers could be artists aswell.\n\nD. He showed how sculpture could involve movement.\n\n', 'C1-3 重听题音频路径': '', 'C1-3 答案': 'D', 'C1-4 题型（单选/多选/排序/重听）': '单选', 'C1-4 题干': "4. What does the professor imply about Alexander Calder's mobiles?", 'C1-4 选项': 'A. They were originally designed with babies in mind.\n\nB. They are difficult for the average museumgoer to understand.\n\nC. They were eventually developed to rely less on motors.\n\nD. The original mobiles had technical problems.\n\n', 'C1-4 重听题音频路径': '', 'C1-4 答案': 'C', 'C1-5 题型（单选/多选/排序/重听）': '重听', 'C1-5 题干': '5. Why does the professor say this:', 'C1-5 选项': "A. To indicate that he does not approve of the student's choice\n\nB. To encourage the student to take trips all around the country\n\nC. To let the student know that he excuses her absence\n\nD. To find out what is important to the student\n\n", 'C1-5 重听题音频路径': 'paper_source\\\\audio\\\\模考5-C1-重听题.mp3', 'C1-5 答案': 'C', 'L1 音频路径': 'paper_source\\\\audio\\\\模考5-L1.mp3', 'L1-1 题型（单选/多选/排序/重听）': '单选', 'L1-1 题干': '1. What is the lecture mainly about?', 'L1-1 选项': 'A. Reasons for the collapse of an ancient society in the Sahara\n\nB. Methods of discovering ancient water sources in the Sahara\n\nC. The impact of climate changes on early settlements in the Sahara\n\nD. Attempts to locate the sites of early settlements in the Sahara\n\n', 'L1-1 重听题音频路径': '', 'L1-1 答案': 'C', 'L1-2 题型（单选/多选/排序/重听）': '单选', 'L1-2 题干': '2. Why does the professor mention satellite images?', 'L1-2 选项': 'A. To describe how evidence of human settlement can be found in the desert.\n\nB. To point out that satellite images can sometimes be misinterpreted.\n\nC. To emphasize that very few people have ever lived in the Sahara.\n\nD. To disprove the claim that people always settled near water sources.\n\n', 'L1-2 重听题音频路径': '', 'L1-2 答案': 'A', 'L1-3 题型（单选/多选/排序/重听）': '单选', 'L1-3 题干': '3. According to the professor, what did the earliest people in the Sahara do as the climate first began to dry out?', 'L1-3 选项': 'A. They increased the time they spent on hunting and gathering.\n\nB. They planted crops that would withstand dry conditions.\n\nC. They moved out of the area.\n\nD. They searched for fossil water.\n\n', 'L1-3 重听题音频路径': '', 'L1-3 答案': 'C', 'L1-4 题型（单选/多选/排序/重听）': '单选', 'L1-4 题干': '4. What does the more recent rock art indicate about the people living in the Sahara about five thousand ears ago?', 'L1-4 选项': 'A. They had already begun to domesticate animals.\n\nB. They had developed advanced tools for hunting.\n\nC. They relocated closer to water sources.\n\nD. They traded cattle with the Romans.\n\n', 'L1-4 重听题音频路径': '', 'L1-4 答案': 'A', 'L1-5 题型（单选/多选/排序/重听）': '单选', 'L1-5 题干': '5. What does the professor imply causes the eventual collapse of the Gara Monte’s society?', 'L1-5 选项': 'A. The region became overpopulated.\n\nB. The water tunnels that the Garamantes built fell apart.\n\nC. The water supply became contaminated.\n\nD. The underground supply of water was exhausted.\n\n', 'L1-5 重听题音频路径': '', 'L1-5 答案': 'D', 'L1-6 题型（单选/多选/排序/重听）': '重听', 'L1-6 题干': '6. Why does the professor say this?', 'L1-6 选项': 'A. To ask the students to share their opinions about a nomadic lifestyle.\n\nB. To indicate that she disagrees with the description of the Garamantes people.\n\nC. To indicate that the lifestyle of the Gara Montes people might be difficult to investigate.\n\nD. To find out if the students understand the concept of a nomadic lifestyle. Listen to part of a lecture in an archaeology class.\n\n', 'L1-6 重听题音频路径': 'paper_source\\\\audio\\\\模考5-L1-重听题.mp3', 'L1-6 答案': 'B', 'C2 音频路径': 'paper_source\\\\audio\\\\模考5-C2.mp3', 'C2-1 题型（单选/多选/排序/重听）': '单选', 'C2-1 题干': '1. Why does the student go to see the professor?', 'C2-1 选项': 'A. To request extra time to complete an assignment\n\nB. To explain why she will miss the next class\n\nC. To clarify the requirements of a class assignment\n\nD. To discuss the results of a lab experiment\n\n', 'C2-1 重听题音频路径': '', 'C2-1 答案': 'C', 'C2-2 题型（单选/多选/排序/重听）': '单选', 'C2-2 题干': '2. What does the professor imply about the student’s extended field trip?', 'C2-2 选项': 'A. He would like to know more about the fieldwork the student did.\n\nB. He was unaware of the problems the student had on the trip\n\nC. He knew that there would be problems on the trip.\n\nD. He has been in similar situations himself.\n\n', 'C2-2 重听题音频路径': '', 'C2-2 答案': 'D', 'C2-3 题型（单选/多选/排序/重听）': '单选', 'C2-3 题干': '3. Why does the professor tell the student about the importance of cane toads to Australia?', 'C2-3 选项': 'A. To remind the student of a topic she studied last semester\n\nB. To provide an example of a concept he is describing\n\nC. To explain the purpose of the lab assignment the student will work on\n\nD. To amuse the student with an anecdote from his own student days\n\n', 'C2-3 重听题音频路径': '', 'C2-3 答案': 'B', 'C2-4 题型（单选/多选/排序/重听）': '单选', 'C2-4 题干': '4. What fact from the radio interview with an ecologist surprised the student?', 'C2-4 选项': 'A. Global warming maybe less harmful to biodiversity than oil palm cultivation.\n\nB. Global warming may have benefited some species of butterflies.\n\nC. Oil palm cultivation has contributed greatly to global warming.\n\nD. Oil palm tree populations have suffered as a result of global warming.\n\n', 'C2-4 重听题音频路径': '', 'C2-4 答案': 'A', 'C2-5 题型（单选/多选/排序/重听）': '多选', 'C2-5 题干': '5. What advantages of the oil palm do the speakers mention? Click on 3 answers', 'C2-5 选项': 'A. It resists damage from imported insects.\n\nB. It is an easy crop to grow.\n\nC. It creates a habitat for rare animal species.\n\nD. It is used in a wide range of products.\n\nE. It has a positive impact on communities where it is grown\n\n', 'C2-5 重听题音频路径': '', 'C2-5 答案': 'BDE', 'L2 音频路径': 'paper_source\\\\audio\\\\模考5-L2.mp3', 'L2-1 题型（单选/多选/排序/重听）': '单选', 'L2-1 题干': '1. What is the lecture mainly about?', 'L2-1 选项': 'A. The decline in the popularity of ballet and ballet music in Paris\n\nB. The reactions of people at the first performance of a piece of music\n\nC. Societal influences on the compose of a famous ballet\n\nD. A comparison of two controversial Parisian ballets\n\n', 'L2-1 重听题音频路径': '', 'L2-1 答案': 'B', 'L2-2 题型（单选/多选/排序/重听）': '多选', 'L2-2 题干': '2. What point does the professor make when discussing the musical instruments used for The Rite of Spring?', 'L2-2 选项': 'A. The instruments were not typically used to perform ballet music.\n\nB. The instruments were played by inexperienced musicians.\n\nC. The instruments could not be heard due to the noise of the dancers.\n\nD. The melodies played by the instruments did not seem to combine well with each other.\n\n', 'L2-2 重听题音频路径': '', 'L2-2 答案': 'D', 'L2-3 题型（单选/多选/排序/重听）': '单选', 'L2-3 题干': '3. What does the professor imply about many members of the audience that came to the premiere performance of The Rite of Spring?', 'L2-3 选项': 'A. They had never seen ballet before.\n\nB. They were professional musicians and dancers.\n\nC. They were expecting an evening of traditional ballet.\n\nD. They objected to the new design of the theater.\n\n', 'L2-3 重听题音频路径': '', 'L2-3 答案': 'C', 'L2-4 题型（单选/多选/排序/重听）': '单选', 'L2-4 题干': '4. Why does the professor quote an eyewitness’s account of the performance in Paris?', 'L2-4 选项': 'A. To describe Nijinsky’s choreography of The Rife of Spring\n\nB. To explain how the choreography of The Rite of Spring influenced later ballets\n\nC. To contrast the two ballets that were performed that evening\n\nD. To illustrate a complaint about the newly reconstructed theater\n\n', 'L2-4 重听题音频路径': '', 'L2-4 答案': 'A', 'L2-5 题型（单选/多选/排序/重听）': '单选', 'L2-5 题干': '5. According to the professor, how did members of the audience react to the Paris performance?', 'L2-5 选项': 'A. They successfully urged police to remove Stravinsky from the theater.\n\nB. They argued and even fought with each other.\n\nC. Many of them protested the performance by leaving the theater.      .\n\nD. Nearly all of them sat silently, refusing to applaud.\n\n', 'L2-5 重听题音频路径': '', 'L2-5 答案': 'B', 'L2-6 题型（单选/多选/排序/重听）': '重听', 'L2-6 题干': 'What is the professor’s opinion about the claim that, in general, the Paris audience was upset more by the dancing than by Stravinsky’s music?', 'L2-6 选项': 'A. He believes it is a valid conclusion, supported by historical evidence.\n\nB. He believes the claim was an intentional exaggeration, made to attract a larger audience.\n\nC. He believes there is no sure way of knowing the true cause of the audience’s reaction.\n\nD. He believes the claim was disproved by audience’ responses to later performances.\n\n', 'L2-6 重听题音频路径': 'paper_source\\\\audio\\\\模考8-L2-重听题.mp3', 'L2-6 答案': 'A', 'L3 音频路径': 'paper_source\\\\audio\\\\模考5-L3.mp3', 'L3-1 题型（单选/多选/排序/重听）': '单选', 'L3-1 题干': '1. What does the professor mainly discuss?', 'L3-1 选项': 'A. How Realist novels differ from Realist plays\n\nB. How Zola’s ideas influenced other Naturalist playwrights\n\nC. Ideas that contributed to the Naturalist movement in theater\n\nD. Realist novels that were adapted as plays\n\n', 'L3-1 重听题音频路径': '', 'L3-1 答案': 'C', 'L3-2 题型（单选/多选/排序/重听）': '单选', 'L3-2 题干': '2. Why does the professor discuss a science book that was published in 1865?', 'L3-2 选项': "A. To give an example of what Zola's contemporaries were reading\n\nB. To describe a major influence on Zola's writing\n\nC. To comment on advances in science in the nineteenth century\n\nD. To point out that the term Naturalism was first used by scientists\n\n", 'L3-2 重听题音频路径': '', 'L3-2 答案': 'B', 'L3-3 题型（单选/多选/排序/重听）': '单选', 'L3-3 题干': "3. According to the professor, what was one of Zola's goals in creating “slice-of-Iife theater”?", 'L3-3 选项': 'A. To adapt Realist novels to the stage\n\nB. To feature characters who live in rural settings\n\nC. To inform his audience about social issues\n\nD. To create a neatly structured story, with beginning, middle, and conclusion\n\n', 'L3-3 重听题音频路径': '', 'L3-3 答案': 'C', 'L3-4 题型（单选/多选/排序/重听）': '单选', 'L3-4 题干': '4. According to the professor, what is a feature of plays that were written using the principles of Naturalism ?', 'L3-4 选项': 'A. They reflect a view of life that is not always happy.\n\nB. They present characters as helpless victims of fate.\n\nC. They are not objective in their representation of human conflict.\n\nD. Their characters are usually members ofthe upper classes.\n\n', 'L3-4 重听题音频路径': '', 'L3-4 答案': 'A', 'L3-5 题型（单选/多选/排序/重听）': '单选', 'L3-5 题干': "5. According to the professor, why were Zola's plays unsuccessful with the theater-goers?", 'L3-5 选项': 'A. They received bad reviews from the critics.\n\nB. They were much longer than other plays written at the time.\n\nC. Their plots contained many unbelievable coincidences.\n\nD. Their characters were not realistically portrayed.\n\n', 'L3-5 重听题音频路径': '', 'L3-5 答案': 'C', 'L3-6 题型（单选/多选/排序/重听）': '单选', 'L3-6 题干': "6. What is the professor's opinion of Henri Becque's plays?", 'L3-6 选项': "A. They illustrate Naturalist principles better than Zola's plays do.\n\nB. They have the same problems that Zola’s Naturalist plays had.\n\nC. They are not as entertaining as Zola’s plays.\n\nD. They should not be considered Naturalist plays.\n\n", 'L3-6 重听题音频路径': '', 'L3-6 答案': 'A', '口语1 问题': 'Task 1. Do you agree or disagree with the following statement? Students should be allowed to take additional classes each semester in order to earn their degrees more quickly. Use specific examples and details in your response.\n\n', '口语2 标题': 'New Housing Arrangement for Students Studying in Spain', '口语2 题干': 'State University students who study abroad in Spain attend classes at Madrid University and have traditionally lived in off-campus housing. Under a new arrangement, however, State students will now be housed in an on-campus dormitory at Madrid University. The head of the program said that housing State students in a Madrid University dormitory will have two benefits. "First, it will save students  money,  because  living  in  a  dormitory  is  less  expensive  than  living  off  campus." "Additionally," he said, "it will help State students learn Spanish, since many of the other students living in the dormitory are native Spanish speakers."\n\n', '口语2 问题': "Using points from the newspaper article, explain the woman's reasons for disagreeing with the university's decision.\n\n", '口语2 音频路径': 'paper_source\\\\audio\\\\模考5-口语-Task2.mp3', '口语3 标题': 'Vividness Bias', '口语3 题干': 'When people consider different kinds of information in order to make decisions, they tend to be heavily influenced by information that is vivid or striking, and grabs their attention. Meanwhile, people may overlook other important information simply because it is less vivid. This phenomenon is known as the vividness bias. By selecting an option\n\nbased only on information that is most noticeable, people may make poor choices that lead to unsatisfactory outcomes. Researchers have found that people can avoid the vividness bias by being aware of this tendency and considering their needs carefully ahead of time, so they will be less likely to be overly influenced by vivid information.\n\n', '口语3 问题': "Explain how the example from the professor's lecture illustrates the concept of a channel conflict.", '口语3 音频路径': 'paper_source\\\\audio\\\\模考5-口语-Task3.mp3', '口语4 问题': 'Task 4. Using points and examples from the lecture, explain two sensory abilities that help plants survive.\n\n', '口语4 音频路径': 'paper_source\\\\audio\\\\模考5-口语-Task4.mp3', '综合写作文章': "Scientists are increasingly interested in solar energy, the conversion of sunlight into electricity. Current solar technologies use large panels in sunny places on Earth, such as deserts, to capture\n\nsunlight. However, some scientists think a better way to capture solar energy would be to place panels above Earth's atmosphere, in space, where they could send solar energy back to Earth as beams or rays of energy. There would be several advantages to using space-based solar power.\n\nCapture more energy\n\nSolar panels in space will capture more energy than panels on Earth. Panels on Earth capture less energy when clouds block the Sun's rays. In addition, the light that reaches Earth is much weaker    than light in space because Earth's atmosphere absorbs sunlight. Space-based panels will capture more energy because they will not be blocked by clouds or Earth's atmosphere.\n\nProtected from impacts\n\nSolar panels on Earth are constantly struck by wind-blown dirt and debris, which over time damages panel surfaces. In space, the most serious threat to solar panels would be high-speed meteoroids (space rocks). But scientists have long had the ability to track meteoroids orbiting Earth, enabling spacecraft to avoid getting struck. This same technology could protect solar panels in space from meteoroid impacts.\n\nBetter for the environment\n\nSpace-based solar panels will be better for the environment than Earth-based solar panels. On Earth, solar panels are generally placed far away from residential areas, in undisturbed ecosystems. Since the panels cover large areas of land and require roads and other infrastructure to make the sites accessible, the valuable ecosystems in which they are built become disrupted and damaged.\n\nSpace-based panels, however, do not disrupt any natural ecosystems, and the Earth-based receivers\n\nrequired to collect their energy would be relatively small, and so would not disrupt the environment either.\n\n", '综合写作问题': 'Directions: You have 20 minutes to plan and write your response. Your response will be judged\n\non the basis of the quality of your writing and on how well your response presents the points in the lecture and their relationship to the reading passage. Typically, an effective response will be 150 to 225 words.\n\nQuestion: Summarize the points made in the lecture, being sure to explain how they challenge the specific theories presented in the reading passage.\n\n', '综合写作音频路径': 'paper_source\\\\audio\\\\模考5-综合写作.mp3', '独立写作截图路径': 'paper_source\\\\pictures\\\\模考5.png'}
,1,1,1,1
                )
    root.mainloop()