import json
import re
import threading
import tkinter as tk
import urllib.request

import app

BG = app.BG
FG = app.FG
MUTED = app.MUTED
FONT = app.FONT

READING_INTERACTIVE = [
    {
        "sentence": "Although public transport requires significant investment, it can reduce traffic congestion and improve the quality of life for people who live in large cities.",
        "finite_verbs": ["requires", "can", "reduce", "improve", "live"],
        "connectors": ["although", "who"],
        "main_clause": ["it", "can", "reduce", "traffic", "congestion", "and", "improve", "the", "quality", "of", "life"],
        "modifiers": ["who", "live", "in", "large", "cities"],
        "translation": "虽然公共交通需要大量投资，但它可以减少交通拥堵，并改善居住在大城市的人们的生活质量。",
    },
    {
        "sentence": "People who regularly use public parks are more likely to meet recommended levels of physical activity than those who do not have easy access to green spaces.",
        "finite_verbs": ["use", "are", "do", "have"],
        "connectors": ["who", "than", "who"],
        "main_clause": ["people", "are", "more", "likely", "to", "meet", "recommended", "levels", "of", "physical", "activity"],
        "modifiers": ["who", "regularly", "use", "public", "parks", "than", "those", "who", "do", "not", "have", "easy", "access", "to", "green", "spaces"],
        "translation": "经常使用公共公园的人比那些无法方便接触绿地的人更有可能达到建议的身体活动水平。",
    },
    {
        "sentence": "Because technology develops so rapidly, skills that were valuable only a few years ago may no longer be sufficient for workers entering the modern labour market.",
        "finite_verbs": ["develops", "were", "may", "be"],
        "connectors": ["because", "that"],
        "main_clause": ["skills", "may", "no", "longer", "be", "sufficient"],
        "modifiers": ["that", "were", "valuable", "only", "a", "few", "years", "ago", "for", "workers", "entering", "the", "modern", "labour", "market"],
        "translation": "由于技术发展非常迅速，几年前还很有价值的技能，对于进入现代劳动力市场的劳动者来说可能已经不再足够。",
    },
    {
        "sentence": "While some people argue that governments should focus on economic growth, others believe that protecting the environment must be an equally important priority.",
        "finite_verbs": ["argue", "should", "focus", "believe", "must", "be"],
        "connectors": ["while", "that", "that"],
        "main_clause": ["others", "believe"],
        "modifiers": ["that", "protecting", "the", "environment", "must", "be", "an", "equally", "important", "priority"],
        "translation": "虽然一些人认为政府应该专注于经济增长，但另一些人认为保护环境必须同样成为重要的优先事项。",
    },
    {
        "sentence": "Students who learn how to identify the main clause before translating every word usually understand complex academic sentences more accurately.",
        "finite_verbs": ["learn", "understand"],
        "connectors": ["who", "how", "before"],
        "main_clause": ["students", "usually", "understand", "complex", "academic", "sentences", "more", "accurately"],
        "modifiers": ["who", "learn", "how", "to", "identify", "the", "main", "clause", "before", "translating", "every", "word"],
        "translation": "那些学会在逐词翻译之前先识别主句的学生，通常能更准确地理解复杂的学术句子。",
    },
]

STEP_INFO = [
    ("FINITE VERBS", "Click the finite verbs in the paragraph.", "finite_verbs"),
    ("CONNECTORS", "Click the connectors that join clauses or ideas.", "connectors"),
    ("MAIN CLAUSE", "Click the words that form the main clause.", "main_clause"),
    ("MODIFIERS", "Click the words that form the key modifying part.", "modifiers"),
]


def clean_word(text):
    return re.sub(r"[^A-Za-z']", "", text).lower()


def word_positions(sentence):
    return [(m.group(), m.start(), m.end()) for m in re.finditer(r"[A-Za-z']+", sentence)]


def multiset_score(selected, targets):
    selected = [clean_word(x) for x in selected if clean_word(x)]
    targets = [clean_word(x) for x in targets if clean_word(x)]
    remaining = targets[:]
    hits = 0
    for item in selected:
        if item in remaining:
            hits += 1
            remaining.remove(item)
    false_clicks = max(0, len(selected) - hits)
    total = max(1, len(targets))
    return max(0, round(100 * hits / total) - round(25 * false_clicks / total))


def enhanced_show_reading(self):
    self.clear()
    self.read_step = 0
    self.read_selected_indices = set()
    self.read_item = READING_INTERACTIVE[self.read_i % len(READING_INTERACTIVE)]

    outer = self.center()
    self.heading(
        outer,
        "READING",
        f"COMPLEX SENTENCE {self.read_i + 1} / {len(READING_INTERACTIVE)} · 60 MIN SESSION",
    )

    self.read_step_label = tk.Label(
        outer,
        text="STEP 1 / 5 · FINITE VERBS",
        bg=BG,
        fg=FG,
        font=(FONT, 16, "bold"),
    )
    self.read_step_label.pack(pady=(0, 8))

    self.read_instruction = tk.Label(
        outer,
        text=STEP_INFO[0][1],
        bg=BG,
        fg=MUTED,
        font=(FONT, 14),
    )
    self.read_instruction.pack(pady=(0, 20))

    # A normal paragraph, not separate word buttons.
    self.read_text = tk.Text(
        outer,
        width=92,
        height=4,
        bg=BG,
        fg=FG,
        insertbackground=FG,
        relief="flat",
        bd=0,
        wrap="word",
        font=(FONT, 22, "bold"),
        spacing1=8,
        spacing3=8,
        padx=10,
        pady=10,
        cursor="hand2",
    )
    self.read_text.pack(pady=8)
    self.read_text.insert("1.0", self.read_item["sentence"])
    self.read_text.configure(state="disabled")
    self.read_text.tag_configure("chosen", background="#FFFFFF", foreground="#000000")
    self.read_text.tag_configure("correct", underline=True)
    self.read_text.bind("<Button-1>", lambda event: reading_click(self, event))

    self.read_feedback = tk.Label(
        outer,
        text="Click directly inside the paragraph. Click again to unselect.",
        bg=BG,
        fg=MUTED,
        font=(FONT, 13),
        wraplength=1150,
        justify="center",
    )
    self.read_feedback.pack(pady=12)

    self.btn(outer, "CHECK", lambda: check_reading_step(self), 18).pack(pady=8)
    self.back(outer)


def reading_click(self, event):
    index = self.read_text.index(f"@{event.x},{event.y}")
    char_offset = len(self.read_text.get("1.0", index))
    positions = word_positions(self.read_item["sentence"])
    chosen = None
    for i, (_, start, end) in enumerate(positions):
        if start <= char_offset <= end:
            chosen = i
            break
    if chosen is None:
        return "break"

    if chosen in self.read_selected_indices:
        self.read_selected_indices.remove(chosen)
    else:
        self.read_selected_indices.add(chosen)
    render_read_selection(self)
    return "break"


def render_read_selection(self):
    self.read_text.configure(state="normal")
    self.read_text.tag_remove("chosen", "1.0", "end")
    positions = word_positions(self.read_item["sentence"])
    for i in self.read_selected_indices:
        if i >= len(positions):
            continue
        _, start, end = positions[i]
        self.read_text.tag_add("chosen", f"1.0+{start}c", f"1.0+{end}c")
    self.read_text.configure(state="disabled")


def check_reading_step(self):
    if self.read_step >= 4:
        return
    title, instruction, key = STEP_INFO[self.read_step]
    positions = word_positions(self.read_item["sentence"])
    selected_words = [positions[i][0] for i in sorted(self.read_selected_indices) if i < len(positions)]
    score = multiset_score(selected_words, self.read_item[key])

    if score < 80:
        self.read_feedback.config(
            text=f"{score}% · Try again. Look for the sentence structure, not individual meanings.",
            fg=FG,
        )
        return

    self.read_step += 1
    self.read_selected_indices = set()
    render_read_selection(self)

    if self.read_step < 4:
        next_title, next_instruction, _ = STEP_INFO[self.read_step]
        self.read_step_label.config(text=f"STEP {self.read_step + 1} / 5 · {next_title}")
        self.read_instruction.config(text=next_instruction)
        self.read_feedback.config(text=f"{score}% · Correct. Continue to the next structure.", fg=MUTED)
    else:
        show_translation_stage(self, score)


def show_translation_stage(self, score):
    self.clear()
    outer = self.center()
    self.heading(
        outer,
        "READING",
        f"TRANSLATION · SENTENCE {self.read_i + 1} / {len(READING_INTERACTIVE)} · 60 MIN SESSION",
    )
    tk.Label(
        outer,
        text=self.read_item["sentence"],
        bg=BG,
        fg=FG,
        font=(FONT, 21, "bold"),
        wraplength=1250,
        justify="center",
    ).pack(pady=(0, 24))
    tk.Label(
        outer,
        text="Translate the meaning into Chinese. Do not translate word by word.",
        bg=BG,
        fg=MUTED,
        font=(FONT, 14),
    ).pack(pady=8)

    self.translation_box = tk.Text(
        outer,
        width=74,
        height=4,
        bg=BG,
        fg=FG,
        insertbackground=FG,
        relief="solid",
        bd=1,
        font=("Microsoft YaHei UI", 17),
        wrap="word",
        padx=12,
        pady=12,
    )
    self.translation_box.pack(pady=16)
    self.translation_box.focus_set()

    self.translation_feedback = tk.Label(
        outer,
        text="",
        bg=BG,
        fg=FG,
        font=("Microsoft YaHei UI", 13),
        wraplength=1150,
        justify="center",
    )
    self.translation_feedback.pack(pady=10)
    self.btn(outer, "CHECK TRANSLATION", lambda: check_translation(self), 20).pack(pady=8)
    self.back(outer)


def call_translation_ai(english, chinese):
    prompt = (
        "You are an IELTS reading teacher. Score the learner's Chinese translation for semantic accuracy. "
        "Do not require word-for-word translation. Return exactly two lines: SCORE: 0-100 and FEEDBACK: short Chinese feedback. "
        f"English: {english}\nLearner Chinese: {chinese}"
    )
    try:
        payload = json.dumps({"model": "qwen3:8b", "prompt": prompt, "stream": False, "options": {"temperature": 0.1}}).encode()
        req = urllib.request.Request(
            "http://127.0.0.1:11434/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            return json.loads(response.read().decode())["response"].strip()
    except Exception:
        return ""


def check_translation(self):
    learner = self.translation_box.get("1.0", "end").strip()
    if not learner:
        self.translation_feedback.config(text="请先完成翻译。")
        return
    self.translation_feedback.config(text="Checking...")

    def worker():
        result = call_translation_ai(self.read_item["sentence"], learner)
        if result:
            text = result + "\n\n参考翻译：" + self.read_item["translation"]
        else:
            text = "本地 AI 未连接，暂不生成虚假正确率。\n\n参考翻译：" + self.read_item["translation"]
        self.after(0, lambda: finish_translation(self, text, learner))

    threading.Thread(target=worker, daemon=True).start()


def finish_translation(self, text, learner):
    self.translation_feedback.config(text=text)
    self.state_data.setdefault("reading_translation_history", []).append(
        {"sentence": self.read_item["sentence"], "translation": learner, "feedback": text}
    )
    self.save_state()
    self.btn(self.translation_feedback.master, "NEXT SENTENCE", lambda: next_interactive_reading(self), 18).pack(pady=10)


def next_interactive_reading(self):
    self.read_i = (self.read_i + 1) % len(READING_INTERACTIVE)
    self.show_reading()


# Patch Reading only. Vocabulary / Listening / Speaking / Writing remain exactly as app.py defines them.
app.IELTSApp.show_reading = enhanced_show_reading
app.IELTSApp.reveal_reading = lambda self: None
app.IELTSApp.next_reading = next_interactive_reading

if __name__ == "__main__":
    app.IELTSApp().mainloop()
