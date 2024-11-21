import tkinter as tk
from PIL import Image, ImageTk
import soundfile as sf
import sounddevice as sd
import threading
import numpy as np
from get_audio_time import get_audio_duration
from comprehensive_writing import Comprehensive_Writing


class Writing_rl:
    def __init__(self, root, paper, reading_score, listening_score):
        self.root = root
        self.paper = paper
        self.reading_score = reading_score
        self.listening_score = listening_score
        self.root.title("Speaking")
        self.root.screen_width = self.root.winfo_screenwidth()
        self.root.screen_height = self.root.winfo_screenheight()
        self.root.attributes('-fullscreen', True)

        # 创建背景
        self.image = Image.open('bg_img2.png')
        self.image = self.image.resize((self.root.screen_width, self.root.screen_height), Image.LANCZOS)
        self.bg_img = ImageTk.PhotoImage(self.image)  # 保持引用防止被垃圾回收

        self.current_page_index = 0
        self.pages = []

        self.recording_data = []
        self.sample_rate = 44100  # 设定采样率
        self.is_recording = False
        self.recording_sequence = 1

        self.left_time = 0
        self.create_pages()
        self.display_page(self.current_page_index)

    def play_audio(self, audio_path):
        # 使用多线程播放音频，避免阻塞主线程
        threading.Thread(target=self._play_audio, args=(audio_path,)).start()

    def _play_audio(self, audio_path):

        # Load the audio file
        self.audio_data, self.sample_rate = sf.read(audio_path)
        self.audio_data = self.audio_data.astype(np.float32)  # Convert to float32
        self.total_time = len(self.audio_data) / self.sample_rate  # Total length in seconds

        # Create a stream and play audio
        with sd.OutputStream(samplerate=self.sample_rate,
                             channels=self.audio_data.shape[1] if self.audio_data.ndim > 1 else 1) as stream:

            # Play the audio
            stream.write(self.audio_data)


    def update_audio_timer(self, remaining_time):
        # 如果剩余时间大于 0，每隔一秒减少 1
        if remaining_time > 0 :

            # 更新标签文本
            self.time_label = tk.Label(font=("Arial", 14), bg="#fce3c4",text=self.format_time(remaining_time))
            self.time_label.place(relx=0.936, rely=0.073, relwidth=0.03, relheight=0.03)
            # 每隔1000ms (1秒) 调用一次update_audio_timer，递减计时
            self.root.after(1000, self.update_audio_timer, remaining_time-1)

        else:
            self.time_label = tk.Label(text='          ',font=("Helvetica", 14), bg="#fce3c4")
            self.time_label.place(relx=0.936, rely=0.073, relwidth=0.03, relheight=0.03)
            self.root.after(2000, self.go_next)



    def play_audio_page(self, audio_path):
        page_frame = tk.Frame(self.root)
        canvas = tk.Canvas(page_frame, width=self.root.screen_width, height=self.root.screen_height)
        canvas.pack(fill=tk.BOTH, expand=True)
        canvas.create_image(0, 0, image=self.bg_img, anchor='nw')

        total_audio_second = int(get_audio_duration(audio_path) // 1)

        # 添加音频时间显示标签
        self.time_label = tk.Label(page_frame, font=("Arial", 14),bg="#fce3c4")
        self.time_label.place(relx=0.936, rely=0.073, relwidth=0.03, relheight=0.03)

        page_frame.audio_path = audio_path
        page_frame.audio_length = total_audio_second

        return page_frame



    def create_question_page(self, question, preparing_time):
        page_frame = tk.Frame(self.root)
        canvas = tk.Canvas(page_frame, width=self.root.screen_width, height=self.root.screen_height)
        canvas.pack(fill=tk.BOTH, expand=True)
        canvas.bg_image = self.bg_img
        canvas.create_image(0, 0, image=self.bg_img, anchor='nw')

        # 问题文本
        question_text = tk.Text(page_frame, bg="white", fg='black', font=('Arial', 18), wrap='word', borderwidth=0,highlightthickness=0)
        question_text.place(relx=0.05, rely=0.15, relwidth=0.9, relheight=0.8)
        question_text.insert('1.0', question)
        question_text.config(state=tk.DISABLED)

        self.timer_label = tk.Label(page_frame, font=("Arial", 14), bg="#fce3c4")
        self.timer_label.place(relx=0.936, rely=0.073, relwidth=0.03, relheight=0.03)
        page_frame.prepare_time = preparing_time

        return page_frame


    #问题准备时间
    def prepare_time_wait(self):
        """每秒更新倒计时，并在倒计时结束时进入下一页"""
        if self.left_time > 0:
            self.timer_label = tk.Label(font=("Arial", 14), bg="#fce3c4",text=self.left_time)
            self.timer_label.place(relx=0.936, rely=0.073, relwidth=0.03, relheight=0.03)

            # 递减时间
            self.left_time -= 1
            # 每1000毫秒（1秒）调用一次自己，继续倒计时
            self.root.after(1000, self.prepare_time_wait)
        else:
            # 倒计时结束，进入下一页
            self.go_next()



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
            self.go_to_comprehensive_writing()

    def go_to_comprehensive_writing(self):

        for widget in self.root.winfo_children():
            widget.destroy()
        Comprehensive_Writing(self.root, self.paper, self.reading_score, self.listening_score)



    def on_time_up(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        Comprehensive_Writing(self.root, self.paper, self.reading_score, self.listening_score)


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
                if hasattr(page, 'prepare_time'):
                    self.left_time += page.prepare_time
                    self.prepare_time_wait()


    def create_pages(self):

        article = self.paper.get('综合写作文章')
        audio_path = self.paper.get('综合写作音频路径')
        text = article.replace('\n\n','\n')
        page = self.create_question_page(text, 180)#180读题
        self.pages.append(page)
        page = self.play_audio_page(audio_path)#听力
        self.pages.append(page)



if __name__ == '__main__':
    root = tk.Tk()
    Writing_rl(root, {
                        'name':'tyt',

                       '综合写作文章': "An intriguing underwater rock structure exists off the coast of Japan. Since the discovery of the rock formation in the 1980s, archaeologists and geologists have debated whether the structure is the result of natural processes or of human construction. Several scholars have argued that it was made by humans based on several pieces of evidence.\n\nAncient Civilization\n\nFirst, there is evidence that an ancient civilization was present in the region around 10,000 years ago. At that time, the sea level was lower, and the structure would have been on dry land. Recent expeditions to the area have uncovered bones, pottery fragments, and parts of tools that are many thousands of years old. With this archaeological evidence, it's reasonable to hypothesize that ancient people living around the structure could have carved it when the area was not yet underwater.\n\nFeatures Designed for Human Use\n\nSecond, pictures of the structure reveal features that seem to be intended for human use (see illustration). For example, there is a section that appears to be a wide, flat platform with stairs along its sides, as well as several large rock pieces that are likely walls. The presence of stairs and walls suggests that the structure was made for human use and was built by humans. Based on such features, some archaeologists have proposed that the whole structure may be a remnant of an ancient city.\n\nStraight Edges\n\nFinally, the rock from the structure has very straight, clear edges. If the rocky structure had been created by a natural process such as water erosion, its edges would be round. There are also several rock elements that intersect at sharp 90-degree angles. These straight edges and angles suggest that the rock was carved by humans rather than by waves and currents of the ocean, which would have left gentler curved edges.\n\n",
                       '综合写作问题': 'Directions: You have 20 minutes to plan and write your response. Your response will be judged on the basis of the quality of your writing and on how well your response presents the points in the lecture and their relationship to the reading passage. Typically, an effective response will be 150 to 225 words.\n\nQuestion: Summarize the points made in the lecture, being sure to explain how they challenge the specific theories presented in the reading passage.\n\n',
                       '综合写作音频路径': 'paper_source\\audio\\模考8-综合写作.mp3',
                       '独立写作截图路径': 'paper_source\\pictures\\模考8.png'},1,1
                )
    root.mainloop()