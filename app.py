import json
import os
import re
import subprocess
import threading
import tkinter as tk
import urllib.request
from difflib import SequenceMatcher
from datetime import datetime

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(APP_DIR, "study_progress.json")
BG, FG, MUTED = "#000000", "#FFFFFF", "#BEBEBE"
FONT = "Segoe UI"

VOCAB_RAW = [
("cause","v.","caus(e)","导致"),("effect","n.","effect","影响"),("allow","v.","allow","允许"),("prevent","v.","pre- + vent","阻止"),("increase","v.","in- + crease","增加"),("decrease","v.","de- + crease","减少"),("government","n.","govern + -ment","政府"),("public","adj.","publ-","公共的"),("lifestyle","n.","life + style","生活方式"),("skill","n.","skill","技能"),
("environment","n.","environ + -ment","环境"),("pollution","n.","pollute + -ion","污染"),("device","n.","device","设备"),("opinion","n.","opin + -ion","观点"),("suggest","v.","sug- + gest","建议"),("problem","n.","problem","问题"),("solution","n.","solut + -ion","解决方案"),("improve","v.","im- + prove","改善"),("provide","v.","pro- + vide","提供"),("benefit","n./v.","bene- + fit","益处"),
("education","n.","educate + -ion","教育"),("health","n.","heal + -th","健康"),("transport","n.","trans- + port","交通"),("traffic","n.","traffic","交通流量"),("community","n.","commun + -ity","社区"),("technology","n.","techn + -ology","科技"),("information","n.","inform + -ation","信息"),("communication","n.","communicate + -ion","交流"),("development","n.","develop + -ment","发展"),("economy","n.","eco- + -nomy","经济"),
("economic","adj.","econom + -ic","经济的"),("society","n.","soci + -ety","社会"),("social","adj.","soci + -al","社会的"),("culture","n.","cult + -ure","文化"),("cultural","adj.","culture + -al","文化的"),("population","n.","populate + -ion","人口"),("employment","n.","employ + -ment","就业"),("unemployment","n.","un- + employ + -ment","失业"),("industry","n.","industr- + -y","产业"),("business","n.","busy + -ness","商业"),
("company","n.","company","公司"),("service","n.","serv + -ice","服务"),("system","n.","system","系统"),("policy","n.","policy","政策"),("law","n.","law","法律"),("education","n.","educate + -ion","教育"),("research","n./v.","re- + search","研究"),("science","n.","sci + -ence","科学"),("scientific","adj.","science + -ific","科学的"),("energy","n.","energ- + -y","能源"),
("climate","n.","climate","气候"),("natural","adj.","nature + -al","自然的"),("resource","n.","re- + source","资源"),("protect","v.","pro- + tect","保护"),("protection","n.","protect + -ion","保护"),("reduce","v.","re- + duce","减少"),("reuse","v.","re- + use","再利用"),("recycle","v.","re- + cycle","回收"),("waste","n./v.","waste","浪费"),("sustainable","adj.","sustain + -able","可持续的"),
("important","adj.","import + -ant","重要的"),("essential","adj.","essent + -ial","必要的"),("significant","adj.","sign + -ificant","显著的"),("major","adj.","major","主要的"),("common","adj.","common","常见的"),("popular","adj.","popul + -ar","流行的"),("positive","adj.","posit + -ive","积极的"),("negative","adj.","negat + -ive","消极的"),("effective","adj.","effect + -ive","有效的"),("efficient","adj.","effic + -ient","高效的"),
("possible","adj.","poss + -ible","可能的"),("impossible","adj.","im- + possible","不可能的"),("necessary","adj.","necess + -ary","必要的"),("available","adj.","avail + -able","可用的"),("different","adj.","differ + -ent","不同的"),("similar","adj.","simil + -ar","相似的"),("modern","adj.","modern","现代的"),("traditional","adj.","tradition + -al","传统的"),("global","adj.","glob + -al","全球的"),("individual","n./adj.","in- + divide + -ual","个人"),
("responsibility","n.","responsible + -ity","责任"),("opportunity","n.","opportune + -ity","机会"),("challenge","n.","challenge","挑战"),("advantage","n.","advantage","优点"),("disadvantage","n.","dis- + advantage","缺点"),("agree","v.","agree","同意"),("disagree","v.","dis- + agree","不同意"),("believe","v.","believe","相信"),("consider","v.","con- + sider","考虑"),("support","v.","support","支持"),
("argue","v.","argue","论证"),("explain","v.","ex- + plain","解释"),("describe","v.","de- + scribe","描述"),("compare","v.","com- + pare","比较"),("contrast","v.","contra- + st","对比"),("increase","v.","in- + crease","增加"),("decline","v.","de- + cline","下降"),("improve","v.","im- + prove","改善"),("achieve","v.","achieve","实现"),("require","v.","re- + quire","需要")]
VOCAB = VOCAB_RAW[:100]
MEANINGS = {w.lower(): m for w,_,_,m in VOCAB}

LISTENING = [
"The library will remain open until nine o'clock on weekdays.",
"Students are required to submit the form before Friday afternoon.",
"The monthly membership fee includes access to the swimming pool.",
"Public transport can reduce traffic congestion in large cities.",
"The lecture has been moved from room twelve to room twenty-one.",
"Please bring your passport and a recent photograph to the appointment.",
"The new recycling program has significantly reduced household waste.",
"Participants should arrive at least fifteen minutes before the session.",
"Many young people choose online courses because they offer greater flexibility.",
"The research suggests that regular exercise can improve mental health.",
"The museum provides discounted tickets for full-time students.",
"Applicants must provide two references and proof of their current address."
]

READING = [
("Although public transport requires significant investment, it can reduce traffic congestion and improve the quality of life for people who live in large cities.", "Main clause: it can reduce traffic congestion and improve the quality of life. | Connector: Although | Subordinate clause: public transport requires significant investment | Modifier: who live in large cities -> people"),
("People who regularly use public parks are more likely to meet recommended levels of physical activity than those who do not have easy access to green spaces.", "Main clause: People are more likely to meet recommended levels. | Relative clause: who regularly use public parks -> People | Comparison: than those... | Relative clause: who do not have easy access... -> those"),
("Because technology develops so rapidly, skills that were valuable only a few years ago may no longer be sufficient for workers entering the modern labour market.", "Main clause: skills may no longer be sufficient. | Reason clause: Because technology develops so rapidly | Relative clause: that were valuable... -> skills | Participle phrase: entering the modern labour market -> workers"),
("While some people argue that governments should focus on economic growth, others believe that protecting the environment must be an equally important priority.", "Main clauses: some people argue... / others believe... | Connector: While | Noun clause: that governments should focus... | Noun clause: that protecting the environment..."),
("Students who learn how to identify the main clause before translating every word usually understand complex academic sentences more accurately.", "Main clause: Students usually understand complex academic sentences more accurately. | Relative clause: who learn... -> Students | Embedded question: how to identify the main clause | Time phrase: before translating every word")
]

WRITING = [
("Write one clear sentence explaining one benefit of public transport.", "Public transport can reduce traffic congestion and improve air quality."),
("Write one sentence giving a reason why governments should invest in education.", "Governments should invest in education because a skilled population supports long-term economic growth."),
("Write one sentence comparing online learning with classroom learning.", "Online learning is more flexible than classroom learning, although it may provide less face-to-face interaction."),
("Write one sentence about an environmental problem and its effect.", "Air pollution can cause serious health problems, especially in densely populated cities."),
("Write one sentence giving your opinion about technology in education.", "I believe technology can improve education when it is used to support, rather than replace, effective teaching.")
]

SPEAKING = [
"Describe one thing you like about your hometown and explain why.",
"Do you prefer studying alone or with other people? Why?",
"How has technology changed the way people learn?",
"What kind of public transport is common where you live?",
"Do you think people should spend more time outdoors? Why?"
]

class Tooltip:
    def __init__(self, widget, text):
        self.widget, self.text, self.tip = widget, text, None
        widget.bind("<Enter>", self.show, add="+")
        widget.bind("<Leave>", self.hide, add="+")
    def show(self, _=None):
        if self.tip or not self.text: return
        x = self.widget.winfo_rootx() + 20; y = self.widget.winfo_rooty() + 30
        self.tip = tk.Toplevel(self.widget); self.tip.overrideredirect(True); self.tip.geometry(f"+{x}+{y}")
        tk.Label(self.tip, text=self.text, bg="#FFFFFF", fg="#000000", font=("Microsoft YaHei UI", 12), padx=10, pady=6).pack()
    def hide(self, _=None):
        if self.tip: self.tip.destroy(); self.tip = None

class IELTSApp(tk.Tk):
    def __init__(self):
        super().__init__(); self.title("IELTS 5H")
        self.configure(bg=BG); self.attributes("-fullscreen", True)
        self.bind("<Escape>", lambda e: self.attributes("-fullscreen", False))
        self.bind("<F11>", lambda e: self.attributes("-fullscreen", not self.attributes("-fullscreen")))
        self.state_data = self.load_state(); self.vocab_page = 0; self.listen_i = 0; self.read_i = 0; self.write_i = 0; self.speak_i = 0
        self.container = tk.Frame(self, bg=BG); self.container.pack(fill="both", expand=True)
        self.show_home()

    def load_state(self):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f: return json.load(f)
        except Exception: return {}
    def save_state(self):
        self.state_data["updated_at"] = datetime.now().isoformat(timespec="seconds")
        with open(DATA_FILE, "w", encoding="utf-8") as f: json.dump(self.state_data, f, ensure_ascii=False, indent=2)
    def clear(self):
        for w in self.container.winfo_children(): w.destroy()
    def btn(self, parent, text, command, width=24):
        return tk.Button(parent, text=text, command=command, bg=FG, fg=BG, activebackground="#DDDDDD", activeforeground=BG, relief="flat", bd=0, font=(FONT, 16, "bold"), padx=20, pady=12, width=width)
    def center(self):
        frame = tk.Frame(self.container, bg=BG); frame.place(relx=.5, rely=.5, anchor="center"); return frame
    def heading(self, parent, title, sub=""):
        tk.Label(parent, text=title, bg=BG, fg=FG, font=(FONT, 34, "bold")).pack(pady=(0,12))
        if sub: tk.Label(parent, text=sub, bg=BG, fg=MUTED, font=(FONT, 14)).pack(pady=(0,26))
    def back(self, parent):
        tk.Button(parent, text="TODAY", command=self.show_home, bg=BG, fg=FG, activebackground=BG, activeforeground=FG, relief="flat", font=(FONT,13), bd=0).pack(pady=16)

    def show_home(self):
        self.clear(); f=self.center(); self.heading(f,"IELTS · DAY 1","5 HOURS · IMMERSIVE TRAINING")
        for title, sub, cmd in [
            ("VOCABULARY","100 words · roots & affixes · 60 min",self.show_vocab),
            ("LISTENING","dictation loop · audio · accuracy · 60 min",self.show_listening),
            ("READING","complex sentence method · guided practice · 60 min",self.show_reading),
            ("SPEAKING","IELTS prompts · repeated answers · 60 min",self.show_speaking),
            ("WRITING","one sentence → instant correction · 60 min",self.show_writing)]:
            b=self.btn(f,title,cmd,30); b.pack(pady=6); tk.Label(f,text=sub,bg=BG,fg=MUTED,font=(FONT,11)).pack(pady=(0,8))

    def show_vocab(self):
        self.clear(); outer=self.center(); self.heading(outer,"VOCABULARY",f"100 WORDS · PAGE {self.vocab_page+1} / 5 · HOVER FOR MEANING")
        grid=tk.Frame(outer,bg=BG); grid.pack()
        start=self.vocab_page*20
        for r,(word,pos,root,meaning) in enumerate(VOCAB[start:start+20]):
            tk.Label(grid,text=f"{start+r+1:03d}",bg=BG,fg=MUTED,font=(FONT,13),width=5,anchor="e").grid(row=r,column=0,padx=(0,18),pady=3)
            wl=tk.Label(grid,text=word,bg=BG,fg=FG,font=(FONT,16,"bold"),width=18,anchor="w",cursor="hand2"); wl.grid(row=r,column=1,pady=3); Tooltip(wl,meaning)
            tk.Label(grid,text=pos,bg=BG,fg=MUTED,font=(FONT,12),width=8,anchor="w").grid(row=r,column=2,padx=18)
            tk.Label(grid,text=root,bg=BG,fg=FG,font=(FONT,13),width=24,anchor="w").grid(row=r,column=3)
        nav=tk.Frame(outer,bg=BG); nav.pack(pady=18)
        if self.vocab_page>0: self.btn(nav,"PREVIOUS",self.prev_vocab,12).pack(side="left",padx=5)
        if self.vocab_page<4: self.btn(nav,"NEXT 20",self.next_vocab,12).pack(side="left",padx=5)
        else: self.btn(nav,"COMPLETE",self.complete_vocab,12).pack(side="left",padx=5)
        self.back(outer)
    def prev_vocab(self): self.vocab_page-=1; self.show_vocab()
    def next_vocab(self): self.vocab_page+=1; self.show_vocab()
    def complete_vocab(self): self.state_data["vocabulary_complete"]=True; self.save_state(); self.show_home()

    def speak_text(self, text):
        def run():
            safe=text.replace("'","''")
            script=("Add-Type -AssemblyName System.Speech; $s=New-Object System.Speech.Synthesis.SpeechSynthesizer; "
                    "$s.Rate=0; $s.Volume=100; $s.Speak('"+safe+"')")
            try: subprocess.run(["powershell","-NoProfile","-Command",script],capture_output=True,timeout=30)
            except Exception: pass
        threading.Thread(target=run,daemon=True).start()
    def norm(self,s): return re.sub(r"[^a-z0-9 ]","",s.lower()).strip()
    def accuracy(self,a,b):
        na,nb=self.norm(a),self.norm(b)
        if not nb:return 0
        return round(100*SequenceMatcher(None,na,nb).ratio())

    def show_listening(self):
        self.clear(); f=self.center(); self.heading(f,"LISTENING",f"DICTATION {self.listen_i+1} / {len(LISTENING)} · 60 MIN SESSION")
        tk.Label(f,text="Listen. Type exactly what you hear. Check. Repeat.",bg=BG,fg=FG,font=(FONT,17)).pack(pady=14)
        self.btn(f,"▶ PLAY",lambda:self.speak_text(LISTENING[self.listen_i]),16).pack(pady=12)
        self.listen_entry=tk.Entry(f,bg=BG,fg=FG,insertbackground=FG,relief="solid",bd=1,font=(FONT,18),justify="center",width=72)
        self.listen_entry.pack(ipady=10,pady=18); self.listen_entry.focus_set()
        self.listen_result=tk.Label(f,text="",bg=BG,fg=FG,font=(FONT,15),wraplength=1100,justify="center"); self.listen_result.pack(pady=12)
        self.btn(f,"CHECK",self.check_listening,16).pack(pady=8); self.back(f)
    def check_listening(self):
        target=LISTENING[self.listen_i]; ans=self.listen_entry.get(); score=self.accuracy(ans,target)
        self.listen_result.config(text=f"ACCURACY  {score}%\n\n{target}")
        self.state_data.setdefault("listening_scores",[]).append(score); self.save_state()
        self.btn(self.listen_result.master,"NEXT DICTATION",self.next_listening,16).pack(pady=10)
    def next_listening(self): self.listen_i=(self.listen_i+1)%len(LISTENING); self.show_listening()

    def show_reading(self):
        self.clear(); f=self.center(); self.heading(f,"READING",f"COMPLEX SENTENCE {self.read_i+1} / {len(READING)} · 60 MIN SESSION")
        steps="1  Find finite verbs   →   2  Find connectors   →   3  Identify the main clause   →   4  Attach modifiers   →   5  Paraphrase"
        tk.Label(f,text=steps,bg=BG,fg=MUTED,font=(FONT,14),wraplength=1250,justify="center").pack(pady=(0,28))
        sentence=READING[self.read_i][0]
        tk.Label(f,text=sentence,bg=BG,fg=FG,font=(FONT,22,"bold"),wraplength=1250,justify="center").pack(pady=18)
        tk.Label(f,text="First, say the main clause aloud. Then reveal the structure.",bg=BG,fg=MUTED,font=(FONT,15)).pack(pady=12)
        self.read_result=tk.Label(f,text="",bg=BG,fg=FG,font=(FONT,15),wraplength=1200,justify="center"); self.read_result.pack(pady=12)
        self.btn(f,"SHOW STRUCTURE",self.reveal_reading,18).pack(pady=8); self.back(f)
    def reveal_reading(self):
        self.read_result.config(text=READING[self.read_i][1])
        self.btn(self.read_result.master,"NEXT SENTENCE",self.next_reading,18).pack(pady=10)
    def next_reading(self): self.read_i=(self.read_i+1)%len(READING); self.show_reading()

    def show_speaking(self):
        self.clear(); f=self.center(); self.heading(f,"SPEAKING",f"PROMPT {self.speak_i+1} / {len(SPEAKING)} · 60 MIN SESSION")
        tk.Label(f,text=SPEAKING[self.speak_i],bg=BG,fg=FG,font=(FONT,25,"bold"),wraplength=1150,justify="center").pack(pady=30)
        tk.Label(f,text="Answer for 60–90 seconds. Repeat once with fewer pauses and clearer structure.",bg=BG,fg=MUTED,font=(FONT,15)).pack(pady=12)
        self.btn(f,"NEXT PROMPT",self.next_speaking,18).pack(pady=18); self.back(f)
    def next_speaking(self): self.speak_i=(self.speak_i+1)%len(SPEAKING); self.show_speaking()

    def show_writing(self):
        self.clear(); f=self.center(); self.heading(f,"WRITING",f"SENTENCE {self.write_i+1} / {len(WRITING)} · 60 MIN SESSION")
        prompt,model=WRITING[self.write_i]
        tk.Label(f,text=prompt,bg=BG,fg=FG,font=(FONT,21,"bold"),wraplength=1100,justify="center").pack(pady=20)
        self.write_entry=tk.Entry(f,bg=BG,fg=FG,insertbackground=FG,relief="solid",bd=1,font=(FONT,18),justify="center",width=78)
        self.write_entry.pack(ipady=10,pady=18); self.write_entry.focus_set()
        self.write_result=tk.Label(f,text="",bg=BG,fg=FG,font=(FONT,14),wraplength=1200,justify="center"); self.write_result.pack(pady=10)
        self.btn(f,"CORRECT NOW",self.correct_writing,18).pack(pady=8); self.back(f)
    def basic_correct(self,text):
        t=text.strip(); notes=[]
        if t and t[0].islower(): t=t[0].upper()+t[1:]; notes.append("Start with a capital letter.")
        replacements={"people is":"people are","people has":"people have","government should to":"government should","can leads to":"can lead to","can improves":"can improve","can reduces":"can reduce"}
        for a,b in replacements.items():
            if a in t.lower():
                t=re.sub(re.escape(a),b,t,flags=re.I); notes.append(f"Use: {b}")
        if t and t[-1] not in ".!?”": t+="."; notes.append("Add end punctuation.")
        return t, notes
    def ollama_correct(self,text,callback):
        def run():
            try:
                prompt=("Correct this IELTS sentence. Return exactly 3 short lines in English only: CORRECTED:, ERROR:, BETTER:. "
                        "Keep the learner's meaning and explain only the most important grammar or word-choice issue. Sentence: "+text)
                payload=json.dumps({"model":"qwen3:8b","prompt":prompt,"stream":False,"options":{"temperature":0.1}}).encode()
                req=urllib.request.Request("http://127.0.0.1:11434/api/generate",data=payload,headers={"Content-Type":"application/json"})
                with urllib.request.urlopen(req,timeout=8) as r: result=json.loads(r.read().decode())["response"].strip()
                self.after(0,lambda:callback(result))
            except Exception:
                corrected,notes=self.basic_correct(text); model=WRITING[self.write_i][1]
                result="CORRECTED: "+corrected+"\nERROR: "+(" ".join(notes) if notes else "No obvious basic grammar error detected.")+"\nBETTER: "+model
                self.after(0,lambda:callback(result))
        threading.Thread(target=run,daemon=True).start()
    def correct_writing(self):
        text=self.write_entry.get().strip()
        if not text: self.write_result.config(text="Write one sentence first."); return
        self.write_result.config(text="Checking...")
        def done(result):
            self.write_result.config(text=result)
            self.state_data.setdefault("writing_history",[]).append({"input":text,"feedback":result}); self.save_state()
            self.btn(self.write_result.master,"NEXT SENTENCE",self.next_writing,18).pack(pady=10)
        self.ollama_correct(text,done)
    def next_writing(self): self.write_i=(self.write_i+1)%len(WRITING); self.show_writing()

if __name__ == "__main__": IELTSApp().mainloop()
