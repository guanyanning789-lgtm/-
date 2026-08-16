import json
import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(APP_DIR, "study_progress.json")

DAY1 = {
    "title": "Day 1｜5 小時 IELTS 基礎實戰",
    "hours": [
        {
            "name": "第 1 小時｜單字與語法打底",
            "content": """今日 20 個高頻基礎單字\n\n1. cause (v.) 導致\n2. lead to (phr.) 導致\n3. effect (n.) 影響\n4. allow (v.) 允許\n5. prevent (v.) 預防；阻止\n6. increase (v.) 增加\n7. decrease (v.) 減少\n8. government (n.) 政府\n9. public (n./adj.) 公眾；公共的\n10. lifestyle (n.) 生活方式\n11. skill (n.) 技能\n12. environment (n.) 環境\n13. pollution (n.) 污染\n14. device (n.) 設備\n15. opinion (n.) 觀點\n16. suggest (v.) 建議\n17. problem (n.) 問題\n18. solution (n.) 解決方案\n19. improve (v.) 改善\n20. provide (v.) 提供\n\n黃金句型\nA + lead to + B（A 導致 B）\n\n造句示例\nHeavy traffic leads to air pollution.""",
        },
        {
            "name": "第 2 小時｜聽力精聽",
            "content": """Listening - Section 1\n\n考點詞彙\n• register — 登記\n• deposit — 押金\n• membership — 會員\n• address — 地址\n\n聽寫句子\nYou need to pay a 50-dollar deposit for the membership.\n\n練習要求\n1. 先聽 3 次，不看文本。\n2. 寫出你聽到的內容。\n3. 對照原句，圈出漏聽詞。\n4. 再跟讀 5 次。\n\n重點：聽到數字 50 與 deposit 時要快速反應。""",
        },
        {
            "name": "第 3 小時｜閱讀定位",
            "content": """Reading - Passage 1\n\n同義替換\n• improve → make better\n• prevent → stop\n\n句子解剖\nOriginal: The new policy helps to prevent young people from smoking.\nQuestion: The government aims to stop youth smoking.\nAnswer: TRUE\n\n練習要求\n• 找出題目中的定位詞。\n• 找到原文同義替換。\n• 不要只看單字相同，要看意思是否一致。""",
        },
        {
            "name": "第 4 小時｜口語 Part 1 對練",
            "content": """主題：Hometown\n\nQ: What do you like most about your hometown?\nA: I like the public transport system. The local government has done a lot to improve the buses recently.\n\n今日任務\n1. 朗讀示例 5 次。\n2. 不看文本回答 3 次。\n3. 用 improve / public 各造 1 句。\n4. 錄音 60 秒，聽回自己的停頓與文法。""",
        },
        {
            "name": "第 5 小時｜寫作簡單句",
            "content": """Writing Task 2 基礎\n\n題目：有些人認為政府應該花錢改善大眾運輸，你同意嗎？\n\n示例\n1. I agree that the government should provide better buses and trains.\n2. Good public transport can reduce cars and lead to cleaner air.\n\n今日任務\n• 仿寫 5 句。\n• 至少使用 government / provide / lead to。\n• 每句只寫一個清楚意思，先求正確，再求複雜。""",
        },
    ],
}

DAY2_BANK = {
    "tense": {
        "title": "Day 2｜動詞時態修復日",
        "focus": "你在 Day 1 回報了時態／動詞變形問題，因此今天優先練『一般現在式 vs 過去式』。",
        "grammar": "I work / I worked / She works / They worked\n\n規則：\n• 習慣、事實 → 一般現在式\n• 已經完成的過去事件 → 過去式\n• he/she/it 現在式動詞通常 + s",
        "words": ["change", "develop", "decide", "happen", "support", "reduce", "create", "use", "need", "work", "study", "travel", "live", "help", "plan", "learn", "start", "finish", "choose", "practice"],
    },
    "vocab": {
        "title": "Day 2｜詞彙鞏固日",
        "focus": "你在 Day 1 回報了單字問題，因此今天增加詞彙重複與造句。",
        "grammar": "句型：A can help B to + 動詞原形。\nExample: Public transport can help people to save money.",
        "words": ["benefit", "cost", "local", "community", "service", "transport", "traffic", "health", "education", "work", "family", "city", "change", "important", "common", "reason", "result", "support", "reduce", "develop"],
    },
    "default": {
        "title": "Day 2｜基礎能力連接日",
        "focus": "Day 1 已完成。今天繼續把單字、聽力、閱讀、口語、寫作串在一起。",
        "grammar": "句型：There are several reasons why + 句子。\nExample: There are several reasons why public transport is important.",
        "words": ["reason", "result", "benefit", "service", "community", "health", "education", "transport", "traffic", "cost", "local", "important", "common", "support", "reduce", "develop", "change", "future", "people", "city"],
    },
}


class IELTSApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("IELTS Daily 5H｜Day 1")
        self.geometry("1180x760")
        self.minsize(980, 650)
        self.configure(bg="#f4f4f4")
        self.state_data = self.load_state()
        self.current_hour = 0
        self.build_style()
        self.build_ui()
        self.show_hour(0)
        self.refresh_progress()

    def build_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TButton", font=("Microsoft JhengHei UI", 11), padding=10)
        style.configure("Accent.TButton", font=("Microsoft JhengHei UI", 11, "bold"), padding=11)
        style.configure("TProgressbar", thickness=14)

    def build_ui(self):
        top = tk.Frame(self, bg="white", height=92)
        top.pack(fill="x")
        top.pack_propagate(False)
        tk.Label(top, text="IELTS DAILY 5H", bg="white", fg="#111", font=("Segoe UI", 23, "bold")).pack(side="left", padx=28, pady=20)
        tk.Label(top, text="Day 1｜基礎打底", bg="white", fg="#666", font=("Microsoft JhengHei UI", 12)).pack(side="left", pady=28)

        body = tk.Frame(self, bg="#f4f4f4")
        body.pack(fill="both", expand=True)

        sidebar = tk.Frame(body, bg="#111111", width=280)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="今日 5 小時", bg="#111", fg="white", font=("Microsoft JhengHei UI", 16, "bold")).pack(anchor="w", padx=22, pady=(24, 12))
        self.hour_buttons = []
        for i, item in enumerate(DAY1["hours"]):
            button = tk.Button(
                sidebar,
                text=item["name"],
                anchor="w",
                command=lambda x=i: self.show_hour(x),
                bg="#111",
                fg="#ddd",
                activebackground="#2a2a2a",
                activeforeground="white",
                relief="flat",
                bd=0,
                padx=22,
                pady=14,
                font=("Microsoft JhengHei UI", 10),
            )
            button.pack(fill="x")
            self.hour_buttons.append(button)

        tk.Frame(sidebar, bg="#333", height=1).pack(fill="x", padx=20, pady=15)
        tk.Button(
            sidebar,
            text="✓ 晚上打卡 / 生成 Day 2",
            command=self.open_checkin,
            bg="white",
            fg="#111",
            relief="flat",
            padx=12,
            pady=12,
            font=("Microsoft JhengHei UI", 10, "bold"),
        ).pack(fill="x", padx=20)

        main = tk.Frame(body, bg="#f4f4f4")
        main.pack(side="left", fill="both", expand=True, padx=24, pady=22)

        card = tk.Frame(main, bg="white", bd=0)
        card.pack(fill="both", expand=True)
        self.title_label = tk.Label(card, text="", bg="white", fg="#111", font=("Microsoft JhengHei UI", 20, "bold"), anchor="w")
        self.title_label.pack(fill="x", padx=28, pady=(26, 12))

        self.text = tk.Text(card, wrap="word", bg="white", fg="#222", relief="flat", font=("Microsoft JhengHei UI", 12), padx=28, pady=12, spacing1=3, spacing3=8)
        self.text.pack(fill="both", expand=True)
        self.text.configure(state="disabled")

        bottom = tk.Frame(card, bg="white")
        bottom.pack(fill="x", padx=28, pady=18)
        self.complete_btn = ttk.Button(bottom, text="標記本小時完成", style="Accent.TButton", command=self.mark_complete)
        self.complete_btn.pack(side="right")
        ttk.Button(bottom, text="上一小時", command=self.prev_hour).pack(side="left")
        ttk.Button(bottom, text="下一小時", command=self.next_hour).pack(side="left", padx=8)

        progress_frame = tk.Frame(main, bg="#f4f4f4")
        progress_frame.pack(fill="x", pady=(16, 0))
        self.progress = ttk.Progressbar(progress_frame, maximum=5)
        self.progress.pack(side="left", fill="x", expand=True)
        self.progress_label = tk.Label(progress_frame, text="0 / 5 完成", bg="#f4f4f4", fg="#444", font=("Microsoft JhengHei UI", 10, "bold"))
        self.progress_label.pack(side="left", padx=(14, 0))

    def show_hour(self, idx):
        self.current_hour = idx
        item = DAY1["hours"][idx]
        self.title_label.config(text=item["name"])
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        self.text.insert("1.0", item["content"])
        self.text.configure(state="disabled")
        for i, button in enumerate(self.hour_buttons):
            button.config(bg="#2a2a2a" if i == idx else "#111", fg="white" if i == idx else "#ddd")
        done = str(idx) in self.state_data.get("completed_hours", [])
        self.complete_btn.config(text="✓ 已完成" if done else "標記本小時完成")

    def prev_hour(self):
        self.show_hour(max(0, self.current_hour - 1))

    def next_hour(self):
        self.show_hour(min(4, self.current_hour + 1))

    def mark_complete(self):
        completed = set(self.state_data.get("completed_hours", []))
        completed.add(str(self.current_hour))
        self.state_data["completed_hours"] = sorted(completed)
        self.save_state()
        self.refresh_progress()
        self.show_hour(self.current_hour)
        if len(completed) == 5:
            messagebox.showinfo("完成", "Day 1 的 5 小時已全部完成！\n現在可以進行晚上打卡。")

    def refresh_progress(self):
        completed_count = len(self.state_data.get("completed_hours", []))
        self.progress["value"] = completed_count
        self.progress_label.config(text=f"{completed_count} / 5 完成")

    def open_checkin(self):
        window = tk.Toplevel(self)
        window.title("Day 1 晚上打卡")
        window.geometry("720x560")
        window.configure(bg="white")
        window.transient(self)
        tk.Label(window, text="Day 1 晚上打卡", bg="white", fg="#111", font=("Microsoft JhengHei UI", 20, "bold")).pack(anchor="w", padx=28, pady=(25, 8))
        tk.Label(window, text="把今天最明顯的錯誤直接寫下來。系統會依錯誤生成 Day 2 重點。", bg="white", fg="#666", font=("Microsoft JhengHei UI", 11)).pack(anchor="w", padx=28)
        box = tk.Text(window, wrap="word", font=("Microsoft JhengHei UI", 12), relief="solid", bd=1, height=10, padx=12, pady=12)
        box.pack(fill="both", expand=True, padx=28, pady=18)
        box.insert("1.0", self.state_data.get("day1_note", ""))

        def submit():
            note = box.get("1.0", "end").strip()
            self.state_data["day1_note"] = note
            self.state_data["day1_checked_in_at"] = datetime.now().isoformat(timespec="seconds")
            self.state_data["day2"] = self.generate_day2(note)
            self.save_state()
            window.destroy()
            self.show_day2()

        ttk.Button(window, text="完成打卡並生成 Day 2", style="Accent.TButton", command=submit).pack(pady=(0, 25))

    def generate_day2(self, note):
        note_lower = note.lower()
        if any(keyword in note_lower for keyword in ["時態", "时态", "過去式", "过去式", "動詞", "动词", "tense", "verb"]):
            key = "tense"
        elif any(keyword in note_lower for keyword in ["單字", "单词", "詞彙", "词汇", "vocab", "word"]):
            key = "vocab"
        else:
            key = "default"
        bank = DAY2_BANK[key]
        return {
            "generated_from": note,
            "title": bank["title"],
            "focus": bank["focus"],
            "grammar": bank["grammar"],
            "words": bank["words"],
        }

    def show_day2(self):
        day2 = self.state_data.get("day2") or self.generate_day2("")
        window = tk.Toplevel(self)
        window.title(day2["title"])
        window.geometry("850x680")
        window.configure(bg="white")
        tk.Label(window, text=day2["title"], bg="white", fg="#111", font=("Microsoft JhengHei UI", 21, "bold")).pack(anchor="w", padx=30, pady=(26, 8))
        tk.Label(window, text=day2["focus"], bg="white", fg="#555", wraplength=760, justify="left", font=("Microsoft JhengHei UI", 11)).pack(anchor="w", padx=30)
        content = (
            "\n\n【第 1 小時重點語法】\n"
            + day2["grammar"]
            + "\n\n【Day 2 新 20 詞】\n"
            + "\n".join(f"{i + 1}. {word}" for i, word in enumerate(day2["words"]))
            + "\n\n其餘 4 小時會沿用同一主題，把今天的弱點放進聽力、閱讀、口語與寫作。"
        )
        text = tk.Text(window, wrap="word", font=("Microsoft JhengHei UI", 12), relief="flat", padx=30, pady=20)
        text.pack(fill="both", expand=True)
        text.insert("1.0", content)
        text.configure(state="disabled")

    def load_state(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as file:
                    return json.load(file)
            except Exception:
                pass
        return {"completed_hours": [], "day1_note": ""}

    def save_state(self):
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(self.state_data, file, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    IELTSApp().mainloop()
