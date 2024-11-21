import tkinter as tk
from PIL import Image, ImageTk
import tkinter.font
from listening1 import Listening1
from tkinter import messagebox
import re

class Reading:
    def __init__(self, root, paper):
        self.root = root
        self.paper = paper
        self.root.title("Reading")
        self.root.screen_width = self.root.winfo_screenwidth()
        self.root.screen_height = self.root.winfo_screenheight()
        self.root.attributes('-fullscreen', True)

        # 创建背景
        self.image = Image.open('bg_img.png')
        self.image = self.image.resize((self.root.screen_width, self.root.screen_height), Image.LANCZOS)
        self.bg_img = ImageTk.PhotoImage(self.image)  # 保持引用防止被垃圾回收


        self.current_page_index = 0
        self.pages = []

        self.reading_user_choice=['none']*20
        self.reading_answer_choice=['none']*20

        self.create_pages()

        # 添加倒计时
        # 初始化时间
        self.time_left = 36*60 + 3
        # 创建标签显示剩余时间
        self.time_label = tk.Label(self.root, text=self.format_time(self.time_left), font=("Helvetica", 14), bg="green")
        self.time_label.place(relx = 0.93, rely = 0.073, relwidth = 0.03, relheight = 0.03)
        self.change_page_buttons = []
        self.create_navigation_buttons()


        # 启动倒计时
        self.update_timer()
        self.display_page(self.current_page_index)

    def create_navigation_buttons(self):
        for index in range(len(self.pages)):
            change_page_button = tk.Button(self.root, text=str(index + 1), bg='red',
                                           command=lambda idx=index: self.change_page(idx))
            change_page_button.place(relx=0.146456 + 0.0293 * index, rely=0.016667, relwidth=0.023433, relheight=0.041667)
            self.change_page_buttons.append(change_page_button)


    def create_one_choice_pages(self, page, question, choices, title, article, highlight):
        page_frame = tk.Frame(self.root)
        canvas = tk.Canvas(page_frame, width=self.root.screen_width, height=self.root.screen_height)
        canvas.pack(fill=tk.BOTH, expand=True)
        canvas.create_image(0, 0, image=self.bg_img, anchor='nw')

        # 添加按钮
        back_button = tk.Button(page_frame, text="Back", command=self.go_back)
        back_button.place(relx=0.879, rely=0.021, relwidth=0.03, relheight=0.03)
        next_button = tk.Button(page_frame, text="Next", command=self.go_next)
        next_button.place(relx=0.937, rely=0.021, relwidth=0.03, relheight=0.03)

        # 标题文本
        title_text = tk.Text(page_frame, bg="white", fg='black', font=('Arial', 18), wrap='word', borderwidth=0,
                             highlightthickness=0)
        title_text.place(relx=0.02, rely=0.07, relwidth=0.5, relheight=0.03)
        title_text.insert('1.0', title)
        title_text.config(state=tk.DISABLED)
        title_text.tag_configure('center', justify='center')
        title_text.tag_add('center', '1.0', 'end')

        # 问题文本
        left_question_text = tk.Text(page_frame, bg="white", fg='black', font=('Arial', 15), wrap='word', borderwidth=0,
                                     highlightthickness=0)
        left_question_text.place(relx=0.52, rely=0.073, relwidth=0.46, relheight=0.03)
        left_question_text.insert('1.0', f'Question {page} of 20')
        left_question_text.config(state=tk.DISABLED)

        # 文章文本框
        article_text = tk.Text(page_frame, bg="white", fg='black', font=('Arial', 18), wrap='word', borderwidth=0,
                               highlightthickness=0)
        article_text.place(relx=0.01, rely=0.12, relwidth=0.48, relheight=0.85)

        # 将文章按段落拆分（假设每个段落以 '\n\n' 作为分隔符）
        paragraphs = article.split('\n\n')

        current_index = '1.0'
        start_position = []
        end_position = []

        # 插入段落并记录每个段落的起始和结束位置
        for index, paragraph in enumerate(paragraphs, start=1):
            start_position.append(current_index)

            # 插入段落，保持换行符
            article_text.insert(current_index, paragraph + '\n\n')

            # 获取插入结束位置
            current_index = article_text.index(tk.INSERT)
            end_position.append(current_index)

        # 改进的正则表达式，匹配 "Paragraph X" 或 "paragraph X"
        paragraph_regex = re.compile(r'\b[Pp]aragraph\s+(\d+)', re.IGNORECASE)
        match = paragraph_regex.search(question)

        # 如果找到段落编号
        if match:
            paragraph_num = int(match.group(1)) - 1  # 减去 1 匹配 0 索引

            # 确保段落编号有效
            if 0 <= paragraph_num < len(paragraphs):
                start_pos = start_position[paragraph_num]
                end_pos = end_position[paragraph_num]

                # 加粗匹配的段落
                article_text.tag_add('bold', start_pos, end_pos)
                article_text.tag_configure('bold', font=('Arial', 18, 'bold'))
                article_text.see(start_pos)  # 滚动到该段落

        if highlight:
            for idx, paragraph in enumerate(paragraphs, start=1):
                start_pos = start_position[idx - 1]  # 获取每段的起始位置
                pos = article_text.search(highlight, start_pos, stopindex=end_position[idx - 1])
                while pos:
                    end_pos = f"{pos}+{len(highlight)}c"  # 计算匹配字符串的结束位置
                    article_text.tag_add('red', pos, end_pos)
                    article_text.tag_configure('red', foreground='red')
                    pos = article_text.search(highlight, end_pos, stopindex=end_position[idx - 1])


        article_text.config(state=tk.DISABLED)

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
        question_text.place(relx=0.52, rely=0.12, relwidth=0.46, relheight=0.67)
        question = question + '\n' + '\n' + '\n' + option_text
        question_text.insert('1.0', question)
        question_text.config(state=tk.DISABLED)

        options = choices.split('\n')
        while '' in options:
            options.remove('')

        # 创建一个 Tkinter 变量，用于存储选中的值
        var = tk.StringVar(value="Option 1")

        def selection():
            selected_value = var.get()
            self.change_page_buttons[page - 1].config(bg='green')
            self.reading_user_choice[page - 1] = selected_value


        # 创建单选按钮
        A = tk.Radiobutton(page_frame, text='A', variable=var, value="A", command=selection,
                           font=("Helvetica", 15), bg='white')
        A.place(relx=0.55, rely=0.8)

        B = tk.Radiobutton(page_frame, text="B", variable=var, value="B", command=selection,
                           font=("Helvetica", 15), bg='white')
        B.place(relx=0.65, rely=0.8)

        C = tk.Radiobutton(page_frame, text="C", variable=var, value="C", command=selection,
                           font=("Helvetica", 15), bg='white')
        C.place(relx=0.75, rely=0.8)

        D = tk.Radiobutton(page_frame, text="D", variable=var, value="D", command=selection,
                           font=("Helvetica", 15), bg='white')
        D.place(relx=0.85, rely=0.8)

        return page_frame

    def create_two_choices_pages(self, page, question, choices, title, article, highlight):
        page_frame = tk.Frame(self.root)
        canvas = tk.Canvas(page_frame, width=self.root.screen_width, height=self.root.screen_height)
        canvas.pack(fill=tk.BOTH, expand=True)
        canvas.create_image(0, 0, image=self.bg_img, anchor='nw')

        # 添加按钮
        back_button = tk.Button(page_frame, text="Back", command=self.go_back)
        back_button.place(relx=0.879, rely=0.021, relwidth=0.03, relheight=0.03)
        next_button = tk.Button(page_frame, text="Next", command=self.go_next)
        next_button.place(relx=0.937, rely=0.021, relwidth=0.03, relheight=0.03)

        # 标题文本
        title_text = tk.Text(page_frame, bg="white", fg='black', font=('Arial', 18), wrap='word', borderwidth=0,
                             highlightthickness=0)
        title_text.place(relx=0.02, rely=0.07, relwidth=0.5, relheight=0.03)
        title_text.insert('1.0', title)
        title_text.config(state=tk.DISABLED)
        title_text.tag_configure('center', justify='center')
        title_text.tag_add('center', '1.0', 'end')

        # 问题文本
        left_question_text = tk.Text(page_frame, bg="white", fg='black', font=('Arial', 15), wrap='word', borderwidth=0,
                                     highlightthickness=0)
        left_question_text.place(relx=0.52, rely=0.073, relwidth=0.46, relheight=0.03)
        left_question_text.insert('1.0', f'Question {page} of 20')
        left_question_text.config(state=tk.DISABLED)

        # 文章文本框
        article_text = tk.Text(page_frame, bg="white", fg='black', font=('Arial', 18), wrap='word', borderwidth=0,
                               highlightthickness=0)
        article_text.place(relx=0.01, rely=0.12, relwidth=0.48, relheight=0.85)

        # 将文章按段落拆分
        paragraphs = article.split('\n\n')

        current_index = '1.0'
        start_position = []
        end_position = []

        for index, paragraph in enumerate(paragraphs, start=1):
            start_position.append(current_index)
            article_text.insert(current_index, paragraph + '\n\n')
            current_index = article_text.index(tk.INSERT)
            end_position.append(current_index)

        # 匹配段落
        paragraph_regex = re.compile(r'\b[Pp]aragraph\s+(\d+)', re.IGNORECASE)
        match = paragraph_regex.search(question)

        if match:
            paragraph_num = int(match.group(1)) - 1
            if 0 <= paragraph_num < len(paragraphs):
                start_pos = start_position[paragraph_num]
                end_pos = end_position[paragraph_num]
                article_text.tag_add('bold', start_pos, end_pos)
                article_text.tag_configure('bold', font=('Arial', 18, 'bold'))
                article_text.see(start_pos)

        if highlight:
            for idx, paragraph in enumerate(paragraphs, start=1):
                start_pos = start_position[idx - 1]
                pos = article_text.search(highlight, start_pos, stopindex=end_position[idx - 1])
                while pos:
                    end_pos = f"{pos}+{len(highlight)}c"
                    article_text.tag_add('red', pos, end_pos)
                    article_text.tag_configure('red', foreground='red')
                    pos = article_text.search(highlight, end_pos, stopindex=end_position[idx - 1])

        article_text.config(state=tk.DISABLED)

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
        question_text.place(relx=0.52, rely=0.12, relwidth=0.46, relheight=0.67)
        question = question + '\n' + '\n' + '\n' + option_text
        question_text.insert('1.0', question)
        question_text.config(state=tk.DISABLED)

        def selection():
            selected_options = [key for key, var in var_dict.items() if var.get()]
            select_text = ''
            for selected_option in selected_options:
                select_text+=selected_option
            self.change_page_buttons[page - 1].config(bg='green')
            self.reading_user_choice[page -1] = select_text

        # 创建多选按钮的变量列表
        var_dict = {}
        abcd = ['A','B','C','D']
        # 创建多选按钮
        for idx, option in enumerate(options):
            var = tk.BooleanVar()  # 创建一个布尔变量用于多选按钮
            var_dict[abcd[idx]] = var

            check_button = tk.Checkbutton(page_frame, text=abcd[idx], variable=var, font=("Helvetica", 15), bg='white',command=selection)
            check_button.place(relx=0.55 + idx * 0.1, rely=0.8)  # 根据选项数量动态调整位置

        # 返回页面框架
        return page_frame

    def create_six_choose_three_pages(self,page,question,choices):
        page_frame = tk.Frame(self.root)
        canvas = tk.Canvas(page_frame, width=self.root.screen_width, height=self.root.screen_height)
        canvas.pack(fill=tk.BOTH, expand=True)
        canvas.create_image(0, 0, image=self.bg_img, anchor='nw')

        # 添加按钮
        back_button = tk.Button(page_frame, text="Back", command=self.go_back)
        back_button.place(relx=0.879, rely=0.021, relwidth=0.03, relheight=0.03)
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
        question_text.place(relx=0.001, rely=0.1, relwidth=0.99, relheight=0.9)
        question = question + '\n' + '\n' + option_text
        question_text.insert('1.0', question)
        question_text.config(state=tk.DISABLED)

        def selection():
            selected_options = [key for key, var in var_dict.items() if var.get()]
            select_text = ''
            for selected_option in selected_options:
                select_text+=selected_option
            self.change_page_buttons[page - 1].config(bg='green')
            self.reading_user_choice[page - 1] = select_text


        # 创建多选按钮的变量列表
        var_dict = {}
        abcd = ['A','B','C','D','E','F']
        # 创建多选按钮
        for idx, option in enumerate(options):
            var = tk.BooleanVar()  # 创建一个布尔变量用于多选按钮
            var_dict[abcd[idx]] = var

            check_button = tk.Checkbutton(page_frame, text=abcd[idx], variable=var, font=("Helvetica", 15), bg='white',command=selection)
            check_button.place(relx=0.2 + idx * 0.1, rely=0.9)  # 根据选项数量动态调整位置

        # 返回页面框架
        return page_frame

    def create_insert_sentence_pages(self,page,question):
        page_frame = tk.Frame(self.root)
        canvas = tk.Canvas(page_frame, width=self.root.screen_width, height=self.root.screen_height)
        canvas.pack(fill=tk.BOTH, expand=True)
        canvas.create_image(0, 0, image=self.bg_img, anchor='nw')

        # 添加按钮
        back_button = tk.Button(page_frame, text="Back", command=self.go_back)
        back_button.place(relx=0.879, rely=0.021, relwidth=0.03, relheight=0.03)
        next_button = tk.Button(page_frame, text="Next", command=self.go_next)
        next_button.place(relx=0.937, rely=0.021, relwidth=0.03, relheight=0.03)



        # 问题文本
        question_text = tk.Text(page_frame, bg="white", fg='black', font=('Arial', 18), wrap='word', borderwidth=0,
                                highlightthickness=0)
        question_text.place(relx=0.001, rely=0.1, relwidth=0.99, relheight=0.9)
        question = question
        question_text.insert('1.0', question)
        question_text.config(state=tk.DISABLED)

        var = tk.StringVar(value="Option 1")

        def selection():
            selected_value = var.get()
            self.change_page_buttons[page - 1].config(bg='green')
            self.reading_user_choice[page - 1] = selected_value


        # 创建单选按钮
        A = tk.Radiobutton(page_frame, text='A', variable=var, value="A", command=selection,
                           font=("Helvetica", 15), bg='white')
        A.place(relx=0.2, rely=0.9)

        B = tk.Radiobutton(page_frame, text="B", variable=var, value="B", command=selection,
                           font=("Helvetica", 15), bg='white')
        B.place(relx=0.4, rely=0.9)

        C = tk.Radiobutton(page_frame, text="C", variable=var, value="C", command=selection,
                           font=("Helvetica", 15), bg='white')
        C.place(relx=0.6, rely=0.9)

        D = tk.Radiobutton(page_frame, text="D", variable=var, value="D", command=selection,
                           font=("Helvetica", 15), bg='white')
        D.place(relx=0.8, rely=0.9)

        # 返回页面框架
        return page_frame



    def change_page(self,index):
        for widget in self.root.winfo_children():
            widget.forget()
        self.current_page_index = index
        self.display_page(index)
    def display_page(self, index):
        # Display new page
        if 0 <= index < len(self.pages):
            page = self.pages[index]
            if page:
                page.pack(fill='both', expand=True)

    def go_next(self):

        if self.current_page_index < len(self.pages) - 1:
            for widget in self.root.winfo_children():
                widget.forget()
            self.current_page_index += 1
            self.display_page(self.current_page_index)
        else:
            self.go_to_listening1()

    def go_back(self):
        if self.current_page_index > 0:
            for widget in self.root.winfo_children():
                widget.forget()
            self.current_page_index -= 1
            self.display_page(self.current_page_index)

    def go_to_listening1(self):
        result = messagebox.askokcancel("确认", "Are you ready to enter the listening test?")

        if result:
            for widget in self.root.winfo_children():
                widget.destroy()
            Listening1(self.root,self.paper,self.reading_user_choice,self.reading_answer_choice)


    def create_pages(self):

        for article_index in range(1,3):
            article = self.paper.get(f'阅读{article_index} 文本')
            title = self.paper.get(f'阅读{article_index} 标题')
            for question_index in range(1,11):
                question_type = self.paper.get(f'阅读题目{article_index}-{question_index} 题型（单选/双选/句子插入/六选三）')
                question = self.paper.get(f'阅读题目{article_index}-{question_index} 题干')
                choices = self.paper.get(f'阅读题目{article_index}-{question_index} 选项（A,B,C,D开头，不同选项换行）')
                highlight_sentence = self.paper.get(f'阅读题目{article_index}-{question_index} 呈现句/词（没有为空）')
                answers = self.paper.get(f'阅读题目{article_index}-{question_index} 答案')



                total_question_index = article_index*10 - 10 + question_index

                self.reading_answer_choice[total_question_index - 1] = answers

                if question_type[:2]  == '单选':

                    page = self.create_one_choice_pages(total_question_index,question,choices,title,article,highlight_sentence)
                    self.pages.append(page)

                if question_type[:2]  == '双选':

                    page = self.create_two_choices_pages(total_question_index,question,choices,title, article, highlight_sentence)
                    self.pages.append(page)

                if question_type[:2]  == '句子':
                    page = self.create_insert_sentence_pages(total_question_index,question)
                    self.pages.append(page)

                if question_type[:2]  == '六选':

                    page = self.create_six_choose_three_pages(total_question_index,question,choices)
                    self.pages.append(page)





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
        for widget in self.root.winfo_children():
            widget.destroy()
        Listening1(self.root, self.paper, self.reading_user_choice, self.reading_answer_choice)




if __name__ == '__main__':
    root = tk.Tk()
    Reading(root,{'阅读1 标题': 'Surface Fluids on Venus and Earth', '阅读1 文本': 'A fluid is a substance, such as a liquid or gas, in which the component particles (usually molecules) can move past one another. Fluids flow easily and conform to the shape of their containers. The geologic processes related to the movement of fluids on a planet’s surface can completely resurface a planet many times. These processes derive their energy from the Sun and the gravitational forces of the planet itself. As these fluids interact with surface materials, they move particles about or react chemically with them to modify or produce materials. On a solid planet with a hydrosphere and an atmosphere, only a tiny fraction of the planetary mass flows as surface fluids. Yet the movements of these fluids can drastically alter a planet. Consider Venus and Earth, both terrestrial planets with atmosphere.\n\nVenus and Earth are commonly regarded as twin planets but not identical twins. They are about the same size, are composed of roughly the same mix of materials, and may have been comparably endowed at their beginning with carbon dioxide and water. However, the twins evolved differently, largely because of differences in their distance from the Sun. With a significant amount of internal heat, Venus may continue to be geologically active with volcanoes, rifting, and folding. However, it lacks any sign of a hydrologic system (water circulation and distribution): there are no streams, lakes, oceans, or glaciers. Space probes suggest that Venus may have started with as much water as Earth, but it was unable to keep its water in liquid form. Because Venus receives more heat from the Sun, water released from the interior evaporated and rose to the upper atmosphere where the Sun’s ultraviolet rays broke the molecules apart. Much of the freed hydrogen escaped into space, and Venus lost its water. Without water, Venus became less and less like Earth and kept an atmosphere filled with carbon dioxide. The carbon dioxide acts as a blanket, creating an intense greenhouse effect and driving surface temperatures high enough to melt lead and to prohibit the formation of carbonate minerals. Volcanoes continually vented more carbon dioxide into the atmosphere. On Earth, liquid water removes carbon dioxide from the atmosphere and combines it with calcium, from rock weathering, to form carbonate sedimentary rocks. Without liquid water to remove carbon from the atmosphere, the level of carbon dioxide in the atmosphere of Venus remains high.\n\nLike Venus, Earth is large enough to be geologically active and for its gravitational field to hold an atmosphere. Unlike Venus, it is just the right distance from the Sun so that temperature ranges allow water to exist as a liquid, a solid, and a gas. Water is thus extremely mobile and moves rapidly over the planet in a continuous hydrologic cycle. Heated by the Sun, the water moves in great cycles from the oceans to the atmosphere, over the landscape in river systems, and ultimately back to the oceans. As a result, Earth’s surface has been continually changed and eroded into delicate systems of river valleys— a remarkable contrast to the surfaces of other planetary bodies where impact craters dominate. Few areas on Earth have been untouched by flowing water. As a result, river valleys are the dominant feature of its landscape. Similarly, wind action has scoured fine particles away from large areas, depositing them elsewhere as vast sand seas dominated by dunes or in sheets ofloess (fine-grained soil deposits). These fluid movements are caused by gravity flow systems energized by heat from the Sun. Other geologic changes occur when the gases in the atmosphere or water react with rocks at the surface to form new chemical components with different properties. An important example of this process was the removal of most of Earth’s carbon dioxide from its atmosphere to form carbonate rocks. However, if Earth were a little closer to the Sun, its oceans would evaporate. If it were farther from the Sun, the oceans would freeze solid. Because liquid water was present, self-replicating molecules of carbon, hydrogen, and oxygen developed life early in Earth’s history and have rapidly modified its surface, blanketing huge parts of the continents with greenery. Life thrives on this planet, and it helped create the planet’s oxygen- and nitrogen-rich atmosphere and moderate temperature.\n\n', '阅读题目1-1 题型（单选/双选/句子插入/六选三）': '双选', '阅读题目1-1 题干': 'Paragraph 1 supports all of the following statements about fluids EXCEPT:', '阅读题目1-1 呈现句/词（没有为空）': '', '阅读题目1-1 选项（A,B,C,D开头，不同选项换行）': 'A. They can chemically react with particles on a planet’s surface.\n\nB. Most of their mass does not flow but remains in place.\n\nC. Their movements can reshape the surface of certain kinds of planets.\n\nD. Their movements is driven by the Sun and by gravity.\n\n', '阅读题目1-1 答案': 'B', '阅读题目1-2 题型（单选/双选/句子插入/六选三）': '单选', '阅读题目1-2 题干': 'According to paragraph 2, what is one difference between Earth and Venus?', '阅读题目1-2 选项（A,B,C,D开头，不同选项换行）': 'A. Earth has less water in its atmosphere than Venus does.\n\nB. Earth has a hydrologic system, but Venus does not.\n\nC. Earth is less geologically active than Venus is.\n\nD. Earth has more carbon dioxide than Venus does.\n\n', '阅读题目1-2 呈现句/词（没有为空）': '', '阅读题目1-2 答案': 'B', '阅读题目1-3 题型（单选/双选/句子插入/六选三）': '单选', '阅读题目1-3 题干': 'It can be inferred from paragraph 2 that Earth evolved differently than Venus did in part because', '阅读题目1-3 选项（A,B,C,D开头，不同选项换行）': 'A. there was more volcanic activity on early Venus than on early Earth\n\nB. they received different amounts of solar energy\n\nC. their interiors contained different amounts of heat\n\nD. their early atmosphere contained different levels of oxygen and nitrogen\n\n', '阅读题目1-3 呈现句/词（没有为空）': '', '阅读题目1-3 答案': 'B', '阅读题目1-4 题型（单选/双选/句子插入/六选三）': '单选', '阅读题目1-4 题干': 'According to paragraph 2, all of the following played a role in keeping carbon dioxide levels high in the atmosphere of Venus EXCEPT', '阅读题目1-4 选项（A,B,C,D开头，不同选项换行）': 'A. the breaking apart of water molecules by ultraviolet rays\n\nB. the evaporation of water released from the planet’s interior\n\nC. the escape of hydrogen into space\n\nD. the release of molecules from melting metals such as lead\n\n', '阅读题目1-4 呈现句/词（没有为空）': '', '阅读题目1-4 答案': 'D', '阅读题目1-5 题型（单选/双选/句子插入/六选三）': '单选', '阅读题目1-5 题干': 'According to paragraph 3, Earth’s surface is different from the surfaces of many other planetary bodies in which of the following ways?', '阅读题目1-5 选项（A,B,C,D开头，不同选项换行）': 'A. It is more strongly marked by river valleys and erosion.\n\nB. It is more geologically active.\n\nC. It is covered by impact craters.\n\nD. It has an atmosphere.\n\n', '阅读题目1-5 呈现句/词（没有为空）': '', '阅读题目1-5 答案': 'A', '阅读题目1-6 题型（单选/双选/句子插入/六选三）': '单选', '阅读题目1-6 题干': 'According to paragraph 3, why is water able to move so freely on Earth?', '阅读题目1-6 选项（A,B,C,D开头，不同选项换行）': 'A. Earth’s temperatures are such that water exists in solid, liquid, and gas forms.\n\nB. Earth is large enough to be geologically active and for its gravitational field to hold an atmosphere.\n\nC. Earth’s surface allows river valleys to develop across the landscape.\n\nD. Earth has active winds that blow across seas and oceans, causing fluid movements.\n\n', '阅读题目1-6 呈现句/词（没有为空）': '', '阅读题目1-6 答案': 'A', '阅读题目1-7 题型（单选/双选/句子插入/六选三）': '单选', '阅读题目1-7 题干': 'Why does the author point out that on Earth “gases in the atmosphere or water react with rocks at the surface to form new chemical components”?', '阅读题目1-7 选项（A,B,C,D开头，不同选项换行）': 'A. To explain why scientists believe that few areas on Earth have been untouched by flowing water\n\nB. To identify one of several ways in which the movement of fluids can affect the surface of a planet\n\nC. To provide evidence that fluid movements are caused by gravity flow systems energized by the Sun\n\nD. To identify an effect of wind scouring fine particles away from large areas\n\n', '阅读题目1-7 呈现句/词（没有为空）': 'gases in the atmosphere or water react with rocks at the surface to form new chemical components', '阅读题目1-7 答案': 'B', '阅读题目1-8 题型（单选/双选/句子插入/六选三）': '单选', '阅读题目1-8 题干': 'Which of the sentences below best expresses the essential information in the highlighted sentence in the passage? Incorrect choices change the meaning in important ways or leave out essential information.', '阅读题目1-8 选项（A,B,C,D开头，不同选项换行）': 'A. Life on Earth is responsible for many changes to the planet’s surface, including blankets of greenery.\n\nB. Self-replicating molecules of carbon, hydrogen, and oxygen led to the development of life early in Earth’s history.\n\nC. The presence of water made it possible for life to develop early in Earth’s history and to significantly change its surface.\n\nD. Early in life’s history on Earth, self-replicating molecules of carbon, hydrogen, and oxygen began blanketing the surface in greenery.\n\n', '阅读题目1-8 呈现句/词（没有为空）': 'Because liquid water was present, self-replicating molecules of carbon, hydrogen, and oxygen developed life early in Earth’s history and have rapidly modified its surface, blanketing huge parts of the continents with greenery.', '阅读题目1-8 答案': 'C', '阅读题目1-9 题型（单选/双选/句子插入/六选三）': '句子插入', '阅读题目1-9 题干': 'Look at the four squares [■] that indicate where the following sentence could be added to the passage.\n\nVenus may not have always been this way.Where would the sentence best fit? Click on a square [■] to add the sentence to the passage.Venus and Earth are commonly regarded as twin planets but not identical twins. They are about the same size, are composed of roughly the same mix of materials, and may have been comparably endowed at their beginning with carbon dioxide and water. However, the twins evolved differently, largely because of differences in their distance from the Sun. With a significant amount of internal heat, Venus may continue to be geologically active with volcanoes, rifting, and folding. ■However, it lacks any sign of a hydrologic system (water circulation and distribution): there are no streams, lakes, oceans, or glaciers. ■Space probes suggest that Venus may have started with as much water as Earth, but it was unable to keep its water in liquid form. ■Because Venus receives more heat from the Sun, water released from the interior evaporated and rose to the upper atmosphere where the Sun’s ultraviolet rays broke the molecules apart. ■Much of the freed hydrogen escaped into space, and Venus lost its water. Without water, Venus became less and less like Earth and kept an atmosphere filled with carbon dioxide. The carbon dioxide acts as a blanket, creating an intense greenhouse effect and driving surface temperatures high enough to melt lead and to prohibit the formation of carbonate minerals. Volcanoes continually vented more carbon dioxide into the atmosphere. On Earth, liquid water removes carbon dioxide from the atmosphere and combines it with calcium, from rock weathering, to form carbonate sedimentary rocks. Without liquid water to remove carbon from the atmosphere, the level of carbon dioxide in the atmosphere of Venus remains high.\n\n', '阅读题目1-9 选项（A,B,C,D开头，不同选项换行）': 'A.\n\nB.\n\nC.\n\nD.\n\n', '阅读题目1-9 呈现句/词（没有为空）': 'Venus and Earth are commonly regarded as twin planets but not identical twins. They are about the same size, are composed of roughly the same mix of materials, and may have been comparably endowed at their beginning with carbon dioxide and water. However, the twins evolved differently, largely because of differences in their distance from the Sun. With a significant amount of internal heat, Venus may continue to be geologically active with volcanoes, rifting, and folding. ■However, it lacks any sign of a hydrologic system (water circulation and distribution): there are no streams, lakes, oceans, or glaciers. ■Space probes suggest that Venus may have started with as much water as Earth, but it was unable to keep its water in liquid form. ■Because Venus receives more heat from the Sun, water released from the interior evaporated and rose to the upper atmosphere where the Sun’s ultraviolet rays broke the molecules apart. ■Much of the freed hydrogen escaped into space, and Venus lost its water. Without water, Venus became less and less like Earth and kept an atmosphere filled with carbon dioxide. The carbon dioxide acts as a blanket, creating an intense greenhouse effect and driving surface temperatures high enough to melt lead and to prohibit the formation of carbonate minerals. Volcanoes continually vented more carbon dioxide into the atmosphere. On Earth, liquid water removes carbon dioxide from the atmosphere and combines it with calcium, from rock weathering, to form carbonate sedimentary rocks. Without liquid water to remove carbon from the atmosphere, the level of carbon dioxide in the atmosphere of Venus remains high.\n\n', '阅读题目1-9 答案': 'B', '阅读题目1-10 题型（单选/双选/句子插入/六选三）': '六选三', '阅读题目1-10 题干': 'Directions: An  introductory  sentence  for  a  brief  summary  of the  passage  is  provided  below. Complete the summary by selecting the THREE answer choices that express the most important ideas in the passage. Some answer choices do not belong in the summary because they express ideas that are not presented in the passage or are minor ideas in the passage. This question is worth 2 points.\n\nOver time, the movement of surface fluids has greatly changed Venus and Earth.\n\n', '阅读题目1-10 选项（A,B,C,D开头，不同选项换行）': 'A. Although Venus is about the same size as Earth, its greater volcanic activity has added considerably to carbon dioxide levels in its atmosphere.\n\nB. Like Venus, Earth has an atmosphere, but Earth’s atmosphere has far more oxygen and nitrogen than does the atmosphere of Venus.\n\nC. On Earth, chemical reactions involving fluids remove carbon dioxide from the atmosphere by giving rise to carbonate rocks, and winds energized by gravity flow systems move fine particles from one place to another.\n\nD. Because Venus  lost  the  water  it  originally  had,  most  of  its  carbon  dioxide  remained  in  its atmosphere, causing the planet to become very warm.\n\nE. On Earth, the dominance of river valley landscapes and the existence of life are due to the planet’s hydrologic cycle.\n\nF. The evaporation of liquid water from Earth’s surface is largely limited by the life forms that have developed, particularly the vegetation.\n\n', '阅读题目1-10 呈现句/词（没有为空）': '', '阅读题目1-10 答案': 'CDE', '阅读2 标题': 'Water Management in Early Agriculture', '阅读2 文本': 'As the first cities formed in Mesopotamia in the Middle East, probably around 3000 B.C., it became necessarily to provide food for larger populations, and thus to find ways of increasing agricultural production. This, in turn, led to the problem of obtaining sufficient water.\n\nIrrigation must have started on a small scale with rather simple constructions, but as its value became apparent, more effort was invested in new construction to divert more water into the canals and to extend the canal system to reach greater areas of potential farmland. Because of changing water levels and clogging by waterborne particles, canals and their intakes required additional labor to maintain, besides the normal labor required to guide water from field to field. Beyond this,some personnel had to be devoted to making decisions about the allocation of available water among the users and ensuring that these directions were carried out. With irrigation water also came potential problems, the most obvious being the susceptibility of low-lying farmlands to disastrous flooding and the longer-term problem of salinization (elevated levels of salt in the soil). To combat flooding from rivers, people from early historic times until today have constructed protective levees (raised barriers of earth) between the river and the settlement or fields to be protected. This, of course, is effective up to a certain level of flooding but changes the basic water patterns of the area and can multiply the damage when the flood level exceeds the height of the levee.\n\nSalinization is caused by an accumulation of salt in the soil near its surface. This salt is carried by river water from the sedimentary rocks in the mountains and deposited on the Mesopotamian fields during natural flooding or purposeful irrigation. Evaporation of water sitting on the surface in hot climates is rapid, concentrating the salts in the remaining water that then descends through the soil to the underlying water table. In southern Mesopotamia, for example, the natural water table comes to within roughly six feet of the surface. Conditions of excessive irrigation bring the water table to eighteen inches, and water can rise further to the root zone, where the high concentration of salts would kill most plants.\n\nSolutions for salinization were not as straightforward as for flooding, but even in ancient times it was understood that the deleterious effects of salinization could be minimized by removing harmful elements through leaching the fields with additional fresh water, digging deep wells to lower the water table, or instituting a system of leaving fields uncultivated. The first two cures would have required considerable labor, and the third solution would have led to diminished productivity, not often viewed as a likely decision in periods of growing population. An effective irrigation system laid the foundation for many of the world’s early civilizations, but it also required a great deal of labor input.\n\nGrowing agrarian societies often tried to meet their food-producing needs by farming less-desirable hill  slopes surrounding the favored low-lying valley bottoms. Since bringing irrigation water to a hill slope  is usually impractical, the key is effective utilization of rainfall. Rainfall either soaks into the soil or runs  off of it due to gravity. A soil that is deep, well-structured, and covered by protective vegetation and much  will normally absorb almost all of the rain that falls on it, provided that the slope is not too steep. However, soils that have lost their vegetative cover and surface mulch will absorb much less, with almost half the  water being carried away by runoff in more extreme conditions. This runoff carries with it topsoil  particles, nutrients, and humus (decayed vegetable matter) that are concentrated in the topsoil. The loss of this material reduces the thickness of the rooting zone and its capacity to absorb moisture for crop needs.\n\nThe most direct solution to this problem of slope runoff was to lay lines of stones along the contours of the slope and hence, perpendicular to the probable flow of water and sediment. These stones could then act as small dams, slowing the downhill flow of water and allowing more water to infiltrate and soil particles to collect behind the dam. This provided a buildup of sediments for plants and improved the landscape’s water-retention properties.\n\n', '阅读题目2-1 题型（单选/双选/句子插入/六选三）': '单选', '阅读题目2-1 题干': 'All of the  following are mentioned in paragraph 2 as operations involved in the Mesopotamian irrigation system EXCEPT', '阅读题目2-1 选项（A,B,C,D开头，不同选项换行）': 'A. determining how much irrigation water should be distributed to various farmers\n\nB. widening existing canals so they could hold more water\n\nC. removing undesirable materials from the intakes of irrigation canals\n\nD. building new canals so irrigation water could be transported to distant areas\n\n', '阅读题目2-1 呈现句/词（没有为空）': '', '阅读题目2-1 答案': 'B', '阅读题目2-2 题型（单选/双选/句子插入/六选三）': '单选', '阅读题目2-2 题干': 'According to paragraph 2, protective levees can have which of the following disadvantages?', '阅读题目2-2 选项（A,B,C,D开头，不同选项换行）': 'A. They can greatly increase the destruction caused by floodwaters when floodwaters are higher than the levee.\n\nB. They can fail even when the flood level remains below the height of the levee.\n\nC. They can lead over time to a serious salinization problem.\n\nD. They can cause damaging floods to occur more frequently by changing basic water patterns.\n\n', '阅读题目2-2 呈现句/词（没有为空）': '', '阅读题目2-2 答案': 'A', '阅读题目2-3 题型（单选/双选/句子插入/六选三）': '单选', '阅读题目2-3 题干': 'Paragraph 2 suggests that irrigation increased the likelihood of destructive floods because', '阅读题目2-3 选项（A,B,C,D开头，不同选项换行）': 'A. irrigated fields were often in locations that tended to flood naturally\n\nB. the canal intakes for irrigation water often did not work\n\nC. most irrigation canals were too narrow and thus overflowed\n\nD. levees built to protect irrigation systems required maintenance\n\n', '阅读题目2-3 呈现句/词（没有为空）': '', '阅读题目2-3 答案': 'A', '阅读题目2-4 题型（单选/双选/句子插入/六选三）': '单选', '阅读题目2-4 题干': 'According to paragraph 3, excessive irrigation can destroy crops by', '阅读题目2-4 选项（A,B,C,D开头，不同选项换行）': 'A. raising salty water to the level of the roots\n\nB. forcing the roots of plants to grow close to the surface\n\nC. taking the place of some natural flooding\n\nD. creating salt deposits on the surface of the soil\n\n', '阅读题目2-4 呈现句/词（没有为空）': '', '阅读题目2-4 答案': 'A', '阅读题目2-5 题型（单选/双选/句子插入/六选三）': '单选', '阅读题目2-5 题干': 'According to paragraph 4, which of the following is true of the more-likely-used solutions to the problem of salinization?', '阅读题目2-5 选项（A,B,C,D开头，不同选项换行）': 'A. They resulted in a decrease in the amount of food that was produced.\n\nB. They succeeded only on areas where the natural water table was especially low.\n\nC. They often demanded much time and effort on the part of their users.\n\nD. They often led to other technological advances.\n\n', '阅读题目2-5 呈现句/词（没有为空）': '', '阅读题目2-5 答案': 'C', '阅读题目2-6 题型（单选/双选/句子插入/六选三）': '单选', '阅读题目2-6 题干': 'According to paragraph 5, which of the following was the main challenge faced by early agricultural societies that wanted to grow crops on hill slopes?', '阅读题目2-6 选项（A,B,C,D开头，不同选项换行）': 'A. Gettingenough irrigation water to the hill slope\n\nB. Growing crops without disturbing the natural vegetative cover\n\nC. Retaining rainwater and thus preventing excessive runoff\n\nD. Identifying crops that do not need a thick rooting zone\n\n', '阅读题目2-6 呈现句/词（没有为空）': '', '阅读题目2-6 答案': 'C', '阅读题目2-7 题型（单选/双选/句子插入/六选三）': '单选', '阅读题目2-7 题干': 'Which of the sentences below best expresses the essential information in the highlighted sentence in the passage? Incorrect choices change the meaning in important ways or leave out essential information.', '阅读题目2-7 选项（A,B,C,D开头，不同选项换行）': 'A. However, soils that are unable to absorb much water experience massive runoff during heavy rains.\n\nB. However, where neither protective vegetation nor mulch covers the soil, much rainwater can be lost to runoff.\n\nC. However, on extremely steep slopes there is no vegetative cover or mulch to prevent runoff.\n\nD. However, in more extreme conditions water that runs off can carry away the vegetative cover and the surface mulch\n\n', '阅读题目2-7 呈现句/词（没有为空）': 'However, soils that have lost their vegetative cover and surface mulch will absorb much less, with almost half the  water being carried away by runoff in more extreme conditions.', '阅读题目2-7 答案': 'B', '阅读题目2-8 题型（单选/双选/句子插入/六选三）': '单选', '阅读题目2-8 题干': 'Which of the following best describes how paragraph 6 relates to paragraph 5?', '阅读题目2-8 选项（A,B,C,D开头，不同选项换行）': 'A. Paragraph 6 describes how the solution to a problem identified in paragraph 5 created unexpected benefits.\n\nB. Paragraph 6 compares two possible solutions to a problem described in paragraph 5.\n\nC. Paragraph 6 explains how the attempt to solve a problem introduced in paragraph 5 led to more difficult problems.\n\nD. Paragraph 6 explains one way in which a difficulty described in paragraph 5 was resolved.\n\n', '阅读题目2-8 呈现句/词（没有为空）': '', '阅读题目2-8 答案': 'D', '阅读题目2-9 题型（单选/双选/句子插入/六选三）': '句子插入', '阅读题目2-9 题干': 'Look at the four squares [■] that indicate where the following sentence could be added to the passage.\n\nNatural flooding, however, does not raise the water table nearly as much and thus does not have these sorts of consequences.Where would the sentence best fit? Click on a square [■] to add the sentence to the passage.Salinization is caused by an accumulation of salt in the soil near its surface. ■This salt is carried by river water from the sedimentary rocks in the mountains and deposited on the Mesopotamian fields during natural flooding or purposeful irrigation. Evaporation of water sitting on the surface in hot climates is rapid, concentrating the salts in the remaining water that then descends through the soil to the underlying water table. ■In southern Mesopotamia, for example, the natural water table comes to within roughly six feet of the surface. ■Conditions of excessive irrigation bring the water table to eighteen inches, and water can rise further to the root zone, where the high concentration of salts would kill most plants.■\n\n', '阅读题目2-9 选项（A,B,C,D开头，不同选项换行）': 'A.\n\nB.\n\nC.\n\nD.\n\n', '阅读题目2-9 呈现句/词（没有为空）': 'Salinization is caused by an accumulation of salt in the soil near its surface. ■This salt is carried by river water from the sedimentary rocks in the mountains and deposited on the Mesopotamian fields during natural flooding or purposeful irrigation. Evaporation of water sitting on the surface in hot climates is rapid, concentrating the salts in the remaining water that then descends through the soil to the underlying water table. ■In southern Mesopotamia, for example, the natural water table comes to within roughly six feet of the surface. ■Conditions of excessive irrigation bring the water table to eighteen inches, and water can rise further to the root zone, where the high concentration of salts would kill most plants.■\n\n', '阅读题目2-9 答案': 'D', '阅读题目2-10 题型（单选/双选/句子插入/六选三）': '六选三', '阅读题目2-10 题干': 'Directions: An  introductory  sentence  for  a  brief  summary  of the  passage  is  provided  below. Complete the summary by selecting the THREE answer choices that express the most important ideas in the passage. Some answer choices do not belong in the summary because they express ideas that are not presented in the passage or are minor ideas in the passage. This question is worth 2 points.\n\nAs cities emerged and populations grew in Mesopotamia, more water had to be provided to increase agricultural production.\n\n', '阅读题目2-10 选项（A,B,C,D开头，不同选项换行）': '', '阅读题目2-10 呈现句/词（没有为空）': 'A. Early on, irrigation was recognized as a valuable practice, even though it was labor-intensive and brought with it problems of salinization and damaging floods.\n\nB. Levees were the major means of protection against flooding, while leaching with added water and lowering the water table helped to control salinization.\n\nC. Because of the enormous amount of labor involved in irrigating fields, farming was increasingly moved to hill slopes, where irrigation systems required less labor.\n\nD. The mountain water that was used to irrigate farmland in Mesopotamia was exceptionally high in salt, causing rapid salinization of the soil.\n\nE. The practice of leaving fields uncultivated periodically was used primarily by societies lacking a large labor force.\n\nF. As cultivation was extended to hill slopes, methods were developed to better retain water from rainfall for crops growing on hillsides.\n\n', '阅读题目2-10 答案': 'ABF', 'C1 音频路径': 'paper_source\\audio\\模考8-C1.WAV', 'C1-1 题型（单选/多选/排序/重听）': '单选', 'C1-1 题干': '1. Why does the woman go to see the professor', 'C1-1 选项': 'A. To ask his opinion regarding a debate about the origins of the Berber people\n\nB. To get feedback on a paper that she recently submitted\n\nC. To propose an alternative topic for a paper she is working on\n\nD. To clarify a point that the professor made in class\n\n', 'C1-1 重听题音频路径': '', 'C1-1 答案': 'C', 'C1-2 题型（单选/多选/排序/重听）': '单选', 'C1-2 题干': '2. According to the woman, what error did she make in writing her original paper', 'C1-2 选项': "A. She did not follow the advice of the professor's graduate assistant.\n\nB. She forgot to include information about the ancient Romans and Egyptians in the paper.\n\nC. She began writing the paper before completing all the necessary research.\n\nD. She did not provide citations for all the sources she used to write the paper.\n\n", 'C1-2 重听题音频路径': '', 'C1-2 答案': 'C', 'C1-3 题型（单选/多选/排序/重听）': '单选', 'C1-3 题干': '3. How does the professor respond when the woman tells him that she wrote a new proposal', 'C1-3 选项': "A. He suggests that the woman's original proposal was stronger than the new proposal.\n\nB. He indicates that he could have helped the woman find suitable material for her original proposal.\n\nC. He expresses disappointment that he did not have an opportunity to suggest a new topic for the woman.\n\nD. He suggests possible sources of information about the woman's new topic.\n\n", 'C1-3 重听题音频路径': '', 'C1-3 答案': 'B', 'C1-4 题型（单选/多选/排序/重听）': '单选', 'C1-4 题干': "4. What topic is covered in the woman's new proposal", 'C1-4 选项': 'A. The difference between civilizations that have writing and those that do not\n\nB. The ways in which international organizations interact with contemporary African governments\n\nC. The role of education in premodern Berber societies\n\nD. The ways in which children in some modern-day nomadic communities are educated\n\n', 'C1-4 重听题音频路径': '', 'C1-4 答案': 'D', 'C1-5 题型（单选/多选/排序/重听）': '单选', 'C1-5 题干': "5. What is the professor's opinion of the woman's new topic", 'C1-5 选项': "A. It is preferable to her original topic.\n\nB. It meets the assignment's requirements.\n\nC. It is too broad to be covered adequately.\n\nD. It is not relevant to current events\n\n", 'C1-5 重听题音频路径': '', 'C1-5 答案': 'B', 'L1 音频路径': 'paper_source\\audio\\模考8-L1.mp3', 'L1-1 题型（单选/多选/排序/重听）': '单选', 'L1-1 题干': '1. What is the lecture mainly about?', 'L1-1 选项': 'A. Early rivalries between France and England in the field of photography.\n\nB. Louis Daguerre’s role in the invention of the photograph.\n\nC. Various contributions to the invention of photography.\n\nD. The sequence of events leading to production of the first negative image.\n\n', 'L1-1 重听题音频路径': '', 'L1-1 答案': 'C', 'L1-2 题型（单选/多选/排序/重听）': '单选', 'L1-2 题干': '2. What does the professor imply about the historical record of the early days of photography?', 'L1-2 选项': 'A. It is incomplete.\n\nB. It was sometimes falsified by inventors.\n\nC. It was written mostly by people who had little knowledge of photography.\n\nD. It is more detailed than most other historical records from that time period.\n\n', 'L1-2 重听题音频路径': '', 'L1-2 答案': 'A', 'L1-3 题型（单选/多选/排序/重听）': '单选', 'L1-3 题干': '3. According to the professor, what circumstances led Anteine Florence to invent light writing?', 'L1-3 选项': 'A. He was inspired by the beauty of his surroundings.\n\nB. He was influenced by printing techniques used in Brazil.\n\nC. He did not have access to printing equipment and supplie\n\nD. He did not have formal training in printing techniques\n\n', 'L1-3 重听题音频路径': '', 'L1-3 答案': 'C', 'L1-4 题型（单选/多选/排序/重听）': '单选', 'L1-4 题干': '4. Why does the professor mention diplomas?', 'L1-4 选项': 'A. To indicate the capability of Florence’s light writing techniques.\n\nB. To explain why scientists at universities were unaware of Florence’s work.\n\nC. To indicate the level of education attained by most inventors of photography.\n\nD. To point out that photographs were printed on diplomas in the early 1830s.\n\n', 'L1-4 重听题音频路径': '', 'L1-4 答案': 'A', 'L1-5 题型（单选/多选/排序/重听）': '单选', 'L1-5 题干': '5. What was William Talbot’s major contribution to the development of photography?', 'L1-5 选项': 'A. A way to make paper sensitive to light.\n\nB. A device that gives photographers precise control of exposure times.\n\nC. A process for printing images on objects such as leaves.\n\nD. A process for producing photographs from a negative image.\n\n', 'L1-5 重听题音频路径': '', 'L1-5 答案': 'D', 'L1-6 题型（单选/多选/排序/重听）': '单选', 'L1-6 题干': '6. What is the professor’s opinion of Joseph Niepce’s contribution to the invention of photography?', 'L1-6 选项': 'A. Niepce would have made more progress if he had kept his methods a secret.\n\nB. Niepce should be acknowledged as the co-inventor of the daguerreotype.\n\nC. Niepce deserved more support from his colleagues.\n\nD. Niepce should not have claimed the ideas of other inventors as his own.\n\n', 'L1-6 重听题音频路径': '', 'L1-6 答案': 'B', 'C2 音频路径': 'paper_source\\audio\\模考8-C2.m4a', 'C2-1 题型（单选/多选/排序/重听）': '单选', 'C2-1 题干': '1. Why does the man go to see the woman?', 'C2-1 选项': 'A. To ask for advice about discussing a paper\n\nB. B. to get help with an assignment\n\nC. C. To review paper he has written\n\nD. D. to get help from her\n\n', 'C2-1 重听题音频路径': '', 'C2-1 答案': 'B', 'C2-2 题型（单选/多选/排序/重听）': '单选', 'C2-2 题干': '2. What happen when the man went to the security office?', 'C2-2 选项': 'A. Security officer said that he had to pay a fee.\n\nB. He was unable to schedule an appointment.\n\nC. He found the office had just closed.\n\nD. The equipment used to make badges broke\n\n', 'C2-2 重听题音频路径': '', 'C2-2 答案': 'D', 'C2-3 题型（单选/多选/排序/重听）': '单选', 'C2-3 题干': '3. Why does the woman mention specific paragraph?', 'C2-3 选项': 'A. She thinks the man has included too.\n\nB. She thinks the man should reread.\n\nC. She wants the man to understand.\n\nD. She expect the man to explain\n\n', 'C2-3 重听题音频路径': '', 'C2-3 答案': 'C', 'C2-4 题型（单选/多选/排序/重听）': '单选', 'C2-4 题干': '4. What similarity is there between the current introduction and the conclusion in the man’s paper?', 'C2-4 选项': 'A. Both need to be shortened.\n\nB. Both engage his audience.\n\nC. Both contain bias.\n\nD. Both have to be specific\n\n', 'C2-4 重听题音频路径': '', 'C2-4 答案': 'A', 'C2-5 题型（单选/多选/排序/重听）': '单选', 'C2-5 题干': '5. What is the woman’s opinion about the concluding paragraph and the introduction', 'C2-5 选项': 'A. They should provide a brief summary and an average.\n\nB. They often oversimplify the main point of the paper.\n\nC. They are frequently unclear.\n\nD. They should offer readers a new hypothesis.\n\n', 'C2-5 重听题音频路径': '', 'C2-5 答案': 'A', 'L2 音频路径': 'paper_source\\audio\\模考8-L2.mp3', 'L2-1 题型（单选/多选/排序/重听）': '单选', 'L2-1 题干': '1. What is the main purpose of the lecture?', 'L2-1 选项': 'A. To compare the behaviors of three different bear species\n\nB. To examine changes to the habitat in which polar bears live\n\nC. To discuss recent insights into polar bear evolution\n\nD. To illustrate a new method of DNA analysis used in climate studies\n\n', 'L2-1 重听题音频路径': '', 'L2-1 答案': 'C', 'L2-2 题型（单选/多选/排序/重听）': '多选', 'L2-2 题干': '2. Why did the professor mentions use mitochondrial DNA for testing instead of nuclear DNA? Click on 2 answers', 'L2-2 选项': 'A. Mitochondrial DNA has a more stable structure than nuclear DNA has.\n\nB. Mitochondrial DNA has a shape that is more easily identifiable than that of nuclear DNA.\n\nC. Mitochondrial DNA is present in larger quantities in cells than nuclear DNA.\n\nD. Mitochondrial DNA analysis is a better-understood research tool than nuclear DNA analysis\n\n', 'L2-2 重听题音频路径': '', 'L2-2 答案': 'AC', 'L2-3 题型（单选/多选/排序/重听）': '单选', 'L2-3 题干': '3. What point does the professor make about brown bears?', 'L2-3 选项': 'A. They now compare with polar bears for food- and territory.\n\nB. They are the ancestors of polar bears.\n\nC. They face the same environmental threat as polar bears.\n\nD. Their jawbones can be easily distinguished from those of polar bears\n\n', 'L2-3 重听题音频路径': '', 'L2-3 答案': 'B', 'L2-4 题型（单选/多选/排序/重听）': '单选', 'L2-4 题干': '4. According to the professor, what do researchers believe about the Svalbard islands?', 'L2-4 选项': 'A. Polar bears first came into existence as a species on the islands.\n\nB. The separate islands were once joined together in a single large landmass.\n\nC. Interbreeding between polar bears and a species of brown bear occurred on the islands.\n\nD. The islands provided a refuge for polar bears during an ancient warming period.\n\n', 'L2-4 重听题音频路径': '', 'L2-4 答案': 'D', 'L2-5 题型（单选/多选/排序/重听）': '单选', 'L2-5 题干': '5. What does the professor imply when she discusses the current warming period?', 'L2-5 选项': 'A. The consequences of the current warming period will not be as serious as most scientists believe.\n\nB. The current warming period is progressing more slowly than previous warming periods.\n\nC. Arctic temperatures today are similar to temperatures during previous warming periods.\n\nD. The fast pace of the current warming period will threaten polar bears’ long-term survival.\n\n', 'L2-5 重听题音频路径': '', 'L2-5 答案': 'D', 'L2-6 题型（单选/多选/排序/重听）': '重听', 'L2-6 题干': 'Why does the professor imply when she says this:', 'L2-6 选项': 'A. The size of the grizzly bear population will soon stabilize.\n\nB. The future of the polar bear as a distinct species might be at risk.\n\nC. Hybridization has already diminished the polar bear population within a short period of time.\n\nD Hybrid species do not adapt well to sudden changes in the environment.\n\n', 'L2-6 重听题音频路径': 'paper_source\\audio\\模考8-L2-重听题.mp3', 'L2-6 答案': 'B', 'L3 音频路径': 'paper_source\\audio\\模考8-L3.mp3', 'L3-1 题型（单选/多选/排序/重听）': '单选', 'L3-1 题干': '1. What is the main purpose of the lecture?', 'L3-1 选项': 'A. To explain methods astronomers use to classify stars\n\nB. To explain the formation of molecular clouds in the universe\n\nC. To discuss how some stellar embryos fail to become stars\n\nD. To discuss similarities between brown dwarfs and planets\n\n', 'L3-1 重听题音频路径': '', 'L3-1 答案': 'C', 'L3-2 题型（单选/多选/排序/重听）': '单选', 'L3-2 题干': '2. According to the professor, why is the study of brown dwarfs particularly challenging?', 'L3-2 选项': 'A. They cannot be detected directly.\n\nB. They combine characteristics of very distinct celestial objects.\n\nC. They appear in colors ranging from brown to red.\n\nD. They are always near very bright stars.\n\n', 'L3-2 重听题音频路径': '', 'L3-2 答案': 'B', 'L3-3 题型（单选/多选/排序/重听）': '单选', 'L3-3 题干': '3. Why does the professor discuss how stars originate?', 'L3-3 选项': 'A. To explain how brown dwarfs begin to form\n\nB. To suggest that brown dwarfs do not originate in molecular clouds\n\nC. To explain why brown dwarfs emit light billions of years\n\nD. To show that stellar embryos cause turbulence within molecular clouds\n\n', 'L3-3 重听题音频路径': '', 'L3-3 答案': 'A', 'L3-4 题型（单选/多选/排序/重听）': '单选', 'L3-4 题干': '4. According to the ejection theory, why do some stellar embryos stop growing before they become stars?', 'L3-4 选项': 'A. The motion of dust and gas inhibits their growth.\n\nB. The cores in which they form are not dense enough.\n\nC. They start forming in the area of a molecular cloud with the least amount of material.\n\nD. They are moved by gravitational forces to areas outside cores.\n\n', 'L3-4 重听题音频路径': '', 'L3-4 答案': 'D', 'L3-5 题型（单选/多选/排序/重听）': '单选', 'L3-5 题干': '5. Why does the professor mention that newborn stars are surrounded by disks of dust and gas?', 'L3-5 选项': 'A. To describe a method for testing two theories about brown dwarfs\n\nB. To clarify how brown dwarfs are drawn into star systems\n\nC. To emphasize that brown dwarfs move at low velocities\n\nD. To introduce planet formation as the topic of the next lecture\n\n', 'L3-5 重听题音频路径': '', 'L3-5 答案': 'A', 'L3-6 题型（单选/多选/排序/重听）': '单选', 'L3-6 题干': '6. What is the professor’s attitude toward the two theories?', 'L3-6 选项': 'A. He is convinced that neither of them can explain why brown dwarfs have stellar disks.\n\nB. He hopes both theories will be confirmed by computer simulations.\n\nC. He thinks evidence supports the turbulence theory even if he cannot rule out the ejection theory.\n\nD. He finds the ejection theory more attractive than the turbulence theory.\n\n', 'L3-6 重听题音频路径': '', 'L3-6 答案': 'C', '口语1 问题': 'Task 1. Some people believe that businesses should be required to spend a certain amount of their profits on social programs that benefit the public and the communities where they operate. Others believe that businesses should be able to decide for themselves how to spend their profits. Which point of view do you agree with? Use details and examples to explain your opinion.\n\n', '口语2 标题': 'University to Introduce Fitness Passes', '口语2 题干': 'Besides providing equipment for individuals to work out, the university gym also offers weekly group fitness classes in activities like aerobics and yoga. Currently students pay a fee for each class session they attend. But soon they will be able to purchase a Fitness Pass, a special card giving students unlimited access to fitness classes for the whole semester. The pass will help students who attend fitness classes regularly to save money since it costs less than paying for individual sessions. The Fitness Pass will also ensure that classes start promptly since students can simply show their cards when they enter each class instead of waiting to pay.\n\n', '口语2 问题': 'The woman expresses her opinion about the plan described in the announcement. Briefly summarize the plan. Then state her opinion about the plan and explain the reasons she gives for holding that opinion.\n\n', '口语2 音频路径': 'paper_source\\audio\\模考8-口语-Task2.mp3', '口语3 标题': 'Channel Conflict', '口语3 题干': 'Manufacturers that create products often rely on other businesses or stores to sell those products to consumers.These stores are the channel through which the products reach consumers. Sometimes a disagreement arises between the manufacturer and a store. This is called a channel conflict. Such disputes commonly occur because the manufacturer and the store selling the products may have different goals or priorities. In order to resolve the conflict, the manufacturer and store may need to negotiate and reach an agreement over how their opposing needs can be met.\n\n', '口语3 问题': "Explain how the example from the professor's lecture illustrates the concept of a channel conflict.", '口语3 音频路径': 'paper_source\\audio\\模考8-口语-Task3.mp3', '口语4 问题': "Task 4. Summarize the professor's lecture about the effects of increased carbon dioxide in the atmosphere. Be sure to include the example of the caterpillar.\n\n", '口语4 音频路径': 'paper_source\\audio\\模考8-口语-Task4.mp3', '综合写作文章': "An intriguing underwater rock structure exists off the coast of Japan. Since the discovery of the rock formation in the 1980s, archaeologists and geologists have debated whether the structure is the result of natural processes or of human construction. Several scholars have argued that it was made by humans based on several pieces of evidence.\n\nAncient Civilization\n\nFirst, there is evidence that an ancient civilization was present in the region around 10,000 years ago. At that time, the sea level was lower, and the structure would have been on dry land. Recent expeditions to the area have uncovered bones, pottery fragments, and parts of tools that are many thousands of years old. With this archaeological evidence, it's reasonable to hypothesize that ancient people living around the structure could have carved it when the area was not yet underwater.\n\nFeatures Designed for Human Use\n\nSecond, pictures of the structure reveal features that seem to be intended for human use (see illustration). For example, there is a section that appears to be a wide, flat platform with stairs along its sides, as well as several large rock pieces that are likely walls. The presence of stairs and walls suggests that the structure was made for human use and was built by humans. Based on such features, some archaeologists have proposed that the whole structure may be a remnant of an ancient city.\n\nStraight Edges\n\nFinally, the rock from the structure has very straight, clear edges. If the rocky structure had been created by a natural process such as water erosion, its edges would be round. There are also several rock elements that intersect at sharp 90-degree angles. These straight edges and angles suggest that the rock was carved by humans rather than by waves and currents of the ocean, which would have left gentler curved edges.\n\n", '综合写作问题': 'Directions: You have 20 minutes to plan and write your response. Your response will be judged on the basis of the quality of your writing and on how well your response presents the points in the lecture and their relationship to the reading passage. Typically, an effective response will be 150 to 225 words.\n\nQuestion: Summarize the points made in the lecture, being sure to explain how they challenge the specific theories presented in the reading passage.\n\n', '综合写作音频路径': 'paper_source\\audio\\模考8-综合写作.m4a', '独立写作截图路径': 'paper_source\\pictures\\模考8.png'}
)
    root.mainloop()