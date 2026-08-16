import json
import os
import tkinter as tk
from datetime import datetime

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(APP_DIR, "study_progress.json")

BG = "#000000"
FG = "#FFFFFF"
MUTED = "#BEBEBE"
FONT_CN = "Microsoft YaHei UI"
FONT_EN = "Segoe UI"

VOCAB = [
    ("cause", "导致"), ("lead to", "导致"), ("effect", "影响"), ("allow", "允许"),
    ("prevent", "阻止"), ("increase", "增加"), ("decrease", "减少"), ("government", "政府"),
    ("public", "公共的"), ("lifestyle", "生活方式"), ("skill", "技能"), ("environment", "环境"),
    ("pollution", "污染"), ("device", "设备"), ("opinion", "观点"), ("suggest", "建议"),
    ("problem", "问题"), ("solution", "解决方案"), ("improve", "改善"), ("provide", "提供"),
    ("benefit", "好处"), ("cost", "成本"), ("local", "当地的"), ("community", "社区"),
    ("service", "服务"), ("transport", "交通"), ("traffic", "交通流量"), ("health", "健康"),
    ("education", "教育"), ("family", "家庭"), ("city", "城市"), ("change", "改变"),
    ("important", "重要的"), ("common", "常见的"), ("reason", "原因"), ("result", "结果"),
    ("support", "支持"), ("reduce", "减少"), ("develop", "发展"), ("future", "未来"),
    ("people", "人们"), ("work", "工作"), ("study", "学习"), ("travel", "旅行"),
    ("live", "居住"), ("help", "帮助"), ("plan", "计划"), ("learn", "学习"),
    ("start", "开始"), ("finish", "完成"), ("choose", "选择"), ("practice", "练习"),
    ("change", "变化"), ("create", "创造"), ("use", "使用"), ("need", "需要"),
    ("decide", "决定"), ("happen", "发生"), ("save", "节省"), ("money", "金钱"),
    ("time", "时间"), ("technology", "技术"), ("society", "社会"), ("culture", "文化"),
    ("country", "国家"), ("school", "学校"), ("student", "学生"), ("teacher", "教师"),
    ("company", "公司"), ("job", "工作"), ("experience", "经验"), ("knowledge", "知识"),
    ("information", "信息"), ("communication", "沟通"), ("language", "语言"), ("ability", "能力"),
    ("quality", "质量"), ("choice", "选择"), ("difference", "差异"), ("example", "例子"),
    ("challenge", "挑战"), ("advantage", "优点"), ("disadvantage", "缺点"), ("agree", "同意"),
    ("disagree", "不同意"), ("believe", "相信"), ("consider", "考虑"), ("possible", "可能的"),
    ("necessary", "必要的"), ("successful", "成功的"), ("available", "可用的"), ("different", "不同的"),
    ("similar", "相似的"), ("modern", "现代的"), ("traditional", "传统的"), ("natural", "自然的"),
    ("global", "全球的"), ("individual", "个人"), ("responsibility", "责任"), ("opportunity", "机会")
]

LISTENING = {
    "title": "听力",
    "instruction": "先看任务，然后隐藏原句。听写完成后再核对。",
    "sentence": "You need to pay a 50-dollar deposit for the membership.",
    "translation": "你需要为会员资格支付50美元押金。",
}

READING = {
    "title": "长难句",
    "instruction": "先自己拆分句子，再看结构提示。",
    "sentence": "Although public transport requires significant investment, it can reduce traffic congestion and improve the quality of life for people who live in large cities.",
    "translation": "虽然公共交通需要大量投资，但它可以减少交通拥堵，并改善居住在大城市中的人们的生活质量。",
    "structure": "Although + 从句，主句 + and + 并列谓语，who + 定语从句。",
}

SPEAKING = {
    "title": "口语",
    "instruction": "大声回答一次。控制在60秒以内。完成后继续。",
    "question": "What do you like most about your hometown?",
    "sample": "I like the public transport system because it is convenient and helps people save time.",
}

WRITING = {
    "title": "写作",
    "instruction": "自己写一句英文。只表达一个清楚的意思，完成后再核对示例。",
    "prompt": "政府应该改善公共交通。请写一句表达同意的英文句子。",
    "sample": "I agree that the government should provide better public transport because it can reduce traffic and improve daily life.",
}


class IELTSApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("IELTS Daily")
        self.configure(bg=BG)
        self.attributes("-fullscreen", True)
        self.bind("<Escape>", lambda e: self.attributes("-fullscreen", False))
        self.bind("<F11>", self.toggle_fullscreen)

        self.state_data = self.load_state()
        self.page = "home"
        self.vocab_page = 0
        self.reveal = False

        self.root_frame = tk.Frame(self, bg=BG)
        self.root_frame.pack(fill="both", expand=True)
        self.show_home()

    def toggle_fullscreen(self, event=None):
        self.attributes("-fullscreen", not self.attributes("-fullscreen"))

    def load_state(self):
        if not os.path.exists(DATA_FILE):
            return {"date": datetime.now().strftime("%Y-%m-%d"), "completed": []}
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if data.get("date") != datetime.now().strftime("%Y-%m-%d"):
                return {"date": datetime.now().strftime("%Y-%m-%d"), "completed": []}
            return data
        except Exception:
            return {"date": datetime.now().strftime("%Y-%m-%d"), "completed": []}

    def save_state(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.state_data, f, ensure_ascii=False, indent=2)

    def clear(self):
        for widget in self.root_frame.winfo_children():
            widget.destroy()

    def center_container(self, max_width=1180):
        outer = tk.Frame(self.root_frame, bg=BG)
        outer.pack(fill="both", expand=True)
        box = tk.Frame(outer, bg=BG, width=max_width)
        box.place(relx=0.5, rely=0.5, anchor="center")
        return box

    def label(self, parent, text, size=24, bold=False, muted=False, pady=8):
        font = (FONT_CN, size, "bold" if bold else "normal")
        w = tk.Label(parent, text=text, bg=BG, fg=MUTED if muted else FG,
                     font=font, justify="center", wraplength=1180)
        w.pack(pady=pady)
        return w

    def button(self, parent, text, command, width=18, pady=8):
        b = tk.Button(parent, text=text, command=command, bg=FG, fg=BG,
                      activebackground=FG, activeforeground=BG,
                      font=(FONT_CN, 18, "bold"), relief="flat", bd=0,
                      cursor="hand2", width=width, padx=12, pady=10)
        b.pack(pady=pady)
        return b

    def text_button(self, parent, text, command):
        b = tk.Button(parent, text=text, command=command, bg=BG, fg=FG,
                      activebackground=BG, activeforeground=FG,
                      font=(FONT_CN, 15), relief="flat", bd=0,
                      cursor="hand2")
        b.pack(pady=6)
        return b

    def mark_complete(self, key):
        done = set(self.state_data.get("completed", []))
        done.add(key)
        self.state_data["completed"] = sorted(done)
        self.save_state()

    def is_done(self, key):
        return key in self.state_data.get("completed", [])

    def show_home(self):
        self.page = "home"
        self.clear()
        box = self.center_container()
        self.label(box, "IELTS DAILY", 42, True, pady=4)
        self.label(box, "今天的学习", 22, False, True, pady=(0 if False else 6))

        completed = len(self.state_data.get("completed", []))
        self.label(box, f"已完成 {completed} / 9", 18, False, True, pady=16)

        menu = [
            ("单词 100", self.show_vocab, self.is_done("vocab")),
            ("听力 1句", self.show_listening, self.is_done("listening")),
            ("长难句 1句", self.show_reading, self.is_done("reading")),
            ("口语 1题", self.show_speaking, self.is_done("speaking")),
            ("写作 1句", self.show_writing, self.is_done("writing")),
        ]
        for title, cmd, done in menu:
            text = f"{title}    已完成" if done else title
            self.text_button(box, text, cmd)

        self.label(box, "F11 全屏    Esc 退出全屏", 13, False, True, pady=20)

    def show_vocab(self):
        self.page = "vocab"
        self.clear()
        box = self.center_container(1280)
        start = self.vocab_page * 20
        end = start + 20
        words = VOCAB[start:end]

        self.label(box, "单词", 34, True, pady=2)
        self.label(box, f"100个    第 {self.vocab_page + 1} / 5 页", 16, False, True, pady=4)

        grid = tk.Frame(box, bg=BG)
        grid.pack(pady=18)
        for idx, (word, meaning) in enumerate(words, start=start + 1):
            row = tk.Frame(grid, bg=BG)
            row.pack(fill="x", pady=4)
            tk.Label(row, text=f"{idx:03d}", bg=BG, fg=MUTED,
                     font=(FONT_EN, 15), width=5, anchor="e").pack(side="left", padx=(0, 20))
            tk.Label(row, text=word, bg=BG, fg=FG,
                     font=(FONT_EN, 19, "bold"), width=22, anchor="w").pack(side="left")
            tk.Label(row, text=meaning, bg=BG, fg=FG,
                     font=(FONT_CN, 18), width=20, anchor="w").pack(side="left", padx=(28, 0))

        nav = tk.Frame(box, bg=BG)
        nav.pack(pady=14)
        if self.vocab_page > 0:
            tk.Button(nav, text="上一页", command=self.prev_vocab, bg=BG, fg=FG,
                      activebackground=BG, activeforeground=FG, relief="flat",
                      font=(FONT_CN, 15), cursor="hand2").pack(side="left", padx=25)
        if self.vocab_page < 4:
            tk.Button(nav, text="下一页", command=self.next_vocab, bg=FG, fg=BG,
                      activebackground=FG, activeforeground=BG, relief="flat",
                      font=(FONT_CN, 16, "bold"), padx=26, pady=8,
                      cursor="hand2").pack(side="left", padx=25)
        else:
            tk.Button(nav, text="完成100个单词", command=self.finish_vocab, bg=FG, fg=BG,
                      activebackground=FG, activeforeground=BG, relief="flat",
                      font=(FONT_CN, 16, "bold"), padx=26, pady=8,
                      cursor="hand2").pack(side="left", padx=25)
        self.text_button(box, "返回今天", self.show_home)

    def prev_vocab(self):
        self.vocab_page = max(0, self.vocab_page - 1)
        self.show_vocab()

    def next_vocab(self):
        self.vocab_page = min(4, self.vocab_page + 1)
        self.show_vocab()

    def finish_vocab(self):
        self.mark_complete("vocab")
        self.show_listening()

    def show_listening(self):
        self.page = "listening"
        self.reveal = False
        self.render_listening()

    def render_listening(self):
        self.clear()
        box = self.center_container()
        self.label(box, "听力", 38, True)
        self.label(box, "1句    目标时间 20分钟以内", 16, False, True)
        self.label(box, LISTENING["instruction"], 21, False, False, pady=20)
        if not self.reveal:
            self.label(box, "听写完成以后，再显示原句。", 18, False, True, pady=20)
            self.button(box, "显示原句", self.reveal_listening)
        else:
            self.label(box, LISTENING["sentence"], 28, True, pady=18)
            self.label(box, LISTENING["translation"], 20, False, True, pady=8)
            self.button(box, "完成并继续", self.finish_listening)
        self.text_button(box, "返回今天", self.show_home)

    def reveal_listening(self):
        self.reveal = True
        self.render_listening()

    def finish_listening(self):
        self.mark_complete("listening")
        self.show_reading()

    def show_reading(self):
        self.page = "reading"
        self.reveal = False
        self.render_reading()

    def render_reading(self):
        self.clear()
        box = self.center_container()
        self.label(box, "长难句", 38, True)
        self.label(box, "1句    目标时间 20分钟以内", 16, False, True)
        self.label(box, READING["sentence"], 27, True, pady=24)
        if not self.reveal:
            self.label(box, READING["instruction"], 19, False, True)
            self.button(box, "我已拆分", self.reveal_reading)
        else:
            self.label(box, READING["structure"], 19, False, False, pady=12)
            self.label(box, READING["translation"], 19, False, True, pady=12)
            self.button(box, "完成并继续", self.finish_reading)
        self.text_button(box, "返回今天", self.show_home)

    def reveal_reading(self):
        self.reveal = True
        self.render_reading()

    def finish_reading(self):
        self.mark_complete("reading")
        self.show_speaking()

    def show_speaking(self):
        self.page = "speaking"
        self.reveal = False
        self.render_speaking()

    def render_speaking(self):
        self.clear()
        box = self.center_container()
        self.label(box, "口语", 38, True)
        self.label(box, "1题    目标时间 15分钟以内", 16, False, True)
        self.label(box, SPEAKING["question"], 30, True, pady=24)
        self.label(box, SPEAKING["instruction"], 19, False, True)
        if not self.reveal:
            self.button(box, "回答完成", self.reveal_speaking)
        else:
            self.label(box, "示例", 16, False, True, pady=8)
            self.label(box, SPEAKING["sample"], 23, False, False, pady=8)
            self.button(box, "完成并继续", self.finish_speaking)
        self.text_button(box, "返回今天", self.show_home)

    def reveal_speaking(self):
        self.reveal = True
        self.render_speaking()

    def finish_speaking(self):
        self.mark_complete("speaking")
        self.show_writing()

    def show_writing(self):
        self.page = "writing"
        self.reveal = False
        self.render_writing()

    def render_writing(self):
        self.clear()
        box = self.center_container()
        self.label(box, "写作", 38, True)
        self.label(box, "1句    目标时间 20分钟以内", 16, False, True)
        self.label(box, WRITING["prompt"], 25, True, pady=22)
        self.label(box, WRITING["instruction"], 18, False, True)

        entry = tk.Text(box, height=4, width=66, bg=BG, fg=FG, insertbackground=FG,
                        font=(FONT_EN, 20), relief="solid", bd=1,
                        highlightthickness=1, highlightbackground=FG,
                        highlightcolor=FG, wrap="word")
        entry.pack(pady=18)
        saved = self.state_data.get("writing_answer", "")
        if saved:
            entry.insert("1.0", saved)

        def save_and_reveal():
            self.state_data["writing_answer"] = entry.get("1.0", "end").strip()
            self.save_state()
            self.reveal = True
            self.render_writing_revealed()

        self.button(box, "写完了", save_and_reveal)
        self.text_button(box, "返回今天", self.show_home)

    def render_writing_revealed(self):
        self.clear()
        box = self.center_container()
        self.label(box, "写作", 38, True)
        self.label(box, "你的句子", 16, False, True)
        self.label(box, self.state_data.get("writing_answer", ""), 24, False, False, pady=15)
        self.label(box, "示例", 16, False, True)
        self.label(box, WRITING["sample"], 23, False, False, pady=15)
        self.button(box, "完成今天", self.finish_writing)
        self.text_button(box, "返回今天", self.show_home)

    def finish_writing(self):
        self.mark_complete("writing")
        self.show_done()

    def show_done(self):
        self.clear()
        box = self.center_container()
        self.label(box, "今天完成", 44, True, pady=10)
        self.label(box, "100个单词    1句听力    1句长难句    1题口语    1句写作", 21, False, True, pady=10)
        self.label(box, "明天继续。", 25, True, pady=22)
        self.button(box, "返回今天", self.show_home)


if __name__ == "__main__":
    app = IELTSApp()
    app.mainloop()
