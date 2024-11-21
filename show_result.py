import tkinter as tk
from send_email import send_email_with_attachments
from datetime import datetime


class Generate_result:
    def __init__(self, root,paper,reading_score,listening_score):
        self.root = root
        self.paper = paper
        self.reading_score = reading_score
        self.listening_score = listening_score
        self.root.title("results")
        self.root.screen_width = self.root.winfo_screenwidth()
        self.root.screen_height = self.root.winfo_screenheight()
        self.root.attributes('-fullscreen', True)
        self.show_results()

    def show_results(self):
        v = tk.Text(self.root, font=('Arial', 28), wrap='word', bg='#f0f0f0',
                    borderwidth=0, highlightthickness=0)
        v.place(relx=0.4, rely=0.3)
        v.insert('1.0', f'Reading:  {self.reading_score}')
        v.config(state=tk.DISABLED)

        q = tk.Text(self.root, font=('Arial', 28), wrap='word', bg='#f0f0f0',
                    borderwidth=0, highlightthickness=0)
        q.place(relx=0.4, rely=0.5)
        q.insert('1.0', f'Listening:{self.listening_score}')
        q.config(state=tk.DISABLED)

        name = self.paper.get('name')
        time = datetime.now().strftime('%Y-%m-%d')
        file_path = rf'results/{name}/{time}'
        subject = f'{name}考试结果以及口语写作文件'
        email = send_email_with_attachments(subject,subject,file_path)

        e = tk.Text(self.root, font=('Arial', 28), wrap='word', bg='#f0f0f0',
                    borderwidth=0, highlightthickness=0)
        e.place(relx=0.4, rely=0.7)
        if email == 'success':
            e.insert('1.0', f'口语写作文件已成功发送至助教邮箱')
        else:
            e.insert('1.0', f'发送邮箱过程中出现未知错误，请从本机拷贝')
        e.config(state=tk.DISABLED)



if __name__ == '__main__':
    root = tk.Tk()
    Generate_result(root,{
                        'name':'tyt',
                       '综合写作文章': "An intriguing underwater rock structure exists off the coast of Japan. Since the discovery of the rock formation in the 1980s, archaeologists and geologists have debated whether the structure is the result of natural processes or of human construction. Several scholars have argued that it was made by humans based on several pieces of evidence.\n\nAncient Civilization\n\nFirst, there is evidence that an ancient civilization was present in the region around 10,000 years ago. At that time, the sea level was lower, and the structure would have been on dry land. Recent expeditions to the area have uncovered bones, pottery fragments, and parts of tools that are many thousands of years old. With this archaeological evidence, it's reasonable to hypothesize that ancient people living around the structure could have carved it when the area was not yet underwater.\n\nFeatures Designed for Human Use\n\nSecond, pictures of the structure reveal features that seem to be intended for human use (see illustration). For example, there is a section that appears to be a wide, flat platform with stairs along its sides, as well as several large rock pieces that are likely walls. The presence of stairs and walls suggests that the structure was made for human use and was built by humans. Based on such features, some archaeologists have proposed that the whole structure may be a remnant of an ancient city.\n\nStraight Edges\n\nFinally, the rock from the structure has very straight, clear edges. If the rocky structure had been created by a natural process such as water erosion, its edges would be round. There are also several rock elements that intersect at sharp 90-degree angles. These straight edges and angles suggest that the rock was carved by humans rather than by waves and currents of the ocean, which would have left gentler curved edges.\n\n",
                       '综合写作问题': 'Directions: You have 20 minutes to plan and write your response. Your response will be judged on the basis of the quality of your writing and on how well your response presents the points in the lecture and their relationship to the reading passage. Typically, an effective response will be 150 to 225 words.\n\nQuestion: Summarize the points made in the lecture, being sure to explain how they challenge the specific theories presented in the reading passage.\n\n',
                       '综合写作音频路径': 'paper_source\\audio\\模考8-L2-重听题.mp3',
                       '独立写作截图路径': 'paper_source\\pictures\\模考8.png'},25,26
                )
    root.mainloop()