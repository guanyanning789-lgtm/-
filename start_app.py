import json
import re
import subprocess
import threading
import time
import tkinter as tk
import urllib.request
from collections import Counter

import app

BG = app.BG
FG = app.FG
MUTED = app.MUTED
FONT = app.FONT

# -----------------------------------------------------------------------------
# Shared 60-minute real countdown. It continues while the app stays open and
# does not reset when the learner moves to the next item inside the same module.
# -----------------------------------------------------------------------------

def ensure_timer_state(self):
    if not hasattr(self, "module_deadlines"):
        self.module_deadlines = {}
        self.timer_jobs = []


def attach_timer(self, parent, module):
    ensure_timer_state(self)
    if module not in self.module_deadlines:
        self.module_deadlines[module] = time.monotonic() + 60 * 60
    label = tk.Label(parent, text="60:00", bg=BG, fg=FG, font=(FONT, 14, "bold"))
    label.pack(pady=(0, 10))

    def tick():
        if not label.winfo_exists():
            return
        remaining = max(0, int(self.module_deadlines[module] - time.monotonic()))
        mm, ss = divmod(remaining, 60)
        label.config(text=f"{mm:02d}:{ss:02d}")
        if remaining > 0:
            label.after(1000, tick)
        else:
            label.config(text="00:00 · SESSION COMPLETE")
    tick()
    return label


# -----------------------------------------------------------------------------
# Reading: normal paragraph. Click words in the paragraph without changing the
# paragraph into separate word buttons.
# -----------------------------------------------------------------------------
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
    return max(0, round(100 * hits / max(1, len(targets))) - round(25 * false_clicks / max(1, len(targets))))


def enhanced_show_reading(self):
    self.clear(); self.read_step = 0; self.read_selected_indices = set()
    self.read_item = READING_INTERACTIVE[self.read_i % len(READING_INTERACTIVE)]
    outer = self.center()
    self.heading(outer, "READING", f"COMPLEX SENTENCE {self.read_i + 1} / {len(READING_INTERACTIVE)}")
    attach_timer(self, outer, "READING")
    self.read_step_label = tk.Label(outer, text="STEP 1 / 5 · FINITE VERBS", bg=BG, fg=FG, font=(FONT, 16, "bold")); self.read_step_label.pack(pady=(0, 8))
    self.read_instruction = tk.Label(outer, text=STEP_INFO[0][1], bg=BG, fg=MUTED, font=(FONT, 14)); self.read_instruction.pack(pady=(0, 16))
    self.read_text = tk.Text(outer, width=92, height=4, bg=BG, fg=FG, insertbackground=FG, relief="flat", bd=0, wrap="word", font=(FONT, 22, "bold"), spacing1=8, spacing3=8, padx=10, pady=10, cursor="hand2")
    self.read_text.pack(pady=8); self.read_text.insert("1.0", self.read_item["sentence"]); self.read_text.configure(state="disabled")
    self.read_text.tag_configure("chosen", background=FG, foreground=BG)
    self.read_text.bind("<Button-1>", lambda event: reading_click(self, event))
    self.read_feedback = tk.Label(outer, text="Click directly inside the paragraph. Click again to unselect.", bg=BG, fg=MUTED, font=(FONT, 13), wraplength=1150, justify="center"); self.read_feedback.pack(pady=10)
    self.btn(outer, "CHECK", lambda: check_reading_step(self), 18).pack(pady=7); self.back(outer)


def reading_click(self, event):
    index = self.read_text.index(f"@{event.x},{event.y}"); char_offset = len(self.read_text.get("1.0", index)); positions = word_positions(self.read_item["sentence"])
    chosen = next((i for i, (_, start, end) in enumerate(positions) if start <= char_offset <= end), None)
    if chosen is None: return "break"
    self.read_selected_indices.symmetric_difference_update({chosen}); render_read_selection(self); return "break"


def render_read_selection(self):
    self.read_text.configure(state="normal"); self.read_text.tag_remove("chosen", "1.0", "end"); positions = word_positions(self.read_item["sentence"])
    for i in self.read_selected_indices:
        if i < len(positions):
            _, start, end = positions[i]; self.read_text.tag_add("chosen", f"1.0+{start}c", f"1.0+{end}c")
    self.read_text.configure(state="disabled")


def check_reading_step(self):
    if self.read_step >= 4: return
    _, _, key = STEP_INFO[self.read_step]; positions = word_positions(self.read_item["sentence"])
    selected = [positions[i][0] for i in sorted(self.read_selected_indices) if i < len(positions)]; score = multiset_score(selected, self.read_item[key])
    if score < 80:
        self.read_feedback.config(text=f"{score}% · Try again. Find the structure first.", fg=FG); return
    self.read_step += 1; self.read_selected_indices = set(); render_read_selection(self)
    if self.read_step < 4:
        title, instruction, _ = STEP_INFO[self.read_step]; self.read_step_label.config(text=f"STEP {self.read_step + 1} / 5 · {title}"); self.read_instruction.config(text=instruction); self.read_feedback.config(text=f"{score}% · Correct.", fg=MUTED)
    else: show_translation_stage(self)


def show_translation_stage(self):
    self.clear(); outer=self.center(); self.heading(outer,"READING",f"TRANSLATION · SENTENCE {self.read_i+1}"); attach_timer(self,outer,"READING")
    tk.Label(outer,text=self.read_item["sentence"],bg=BG,fg=FG,font=(FONT,21,"bold"),wraplength=1250,justify="center").pack(pady=(0,22))
    tk.Label(outer,text="Translate the meaning into Chinese. Do not translate word by word.",bg=BG,fg=MUTED,font=(FONT,14)).pack(pady=8)
    self.translation_box=tk.Text(outer,width=74,height=4,bg=BG,fg=FG,insertbackground=FG,relief="solid",bd=1,font=("Microsoft YaHei UI",17),wrap="word",padx=12,pady=12); self.translation_box.pack(pady=14); self.translation_box.focus_set()
    self.translation_feedback=tk.Label(outer,text="",bg=BG,fg=FG,font=("Microsoft YaHei UI",13),wraplength=1150,justify="center"); self.translation_feedback.pack(pady=8)
    self.btn(outer,"CHECK TRANSLATION",lambda:check_translation(self),20).pack(pady=7); self.back(outer)


def ai_call(prompt, timeout=20):
    try:
        payload=json.dumps({"model":"qwen3:8b","prompt":prompt,"stream":False,"options":{"temperature":0.1}}).encode()
        req=urllib.request.Request("http://127.0.0.1:11434/api/generate",data=payload,headers={"Content-Type":"application/json"})
        with urllib.request.urlopen(req,timeout=timeout) as r:return json.loads(r.read().decode())["response"].strip()
    except Exception:return ""


def check_translation(self):
    learner=self.translation_box.get("1.0","end").strip()
    if not learner:self.translation_feedback.config(text="请先完成翻译。");return
    self.translation_feedback.config(text="Checking...")
    prompt=f"Score semantic accuracy 0-100. Return two lines SCORE: and FEEDBACK: in Chinese. English: {self.read_item['sentence']} Chinese: {learner}"
    def worker():
        result=ai_call(prompt); text=(result+"\n\n参考翻译："+self.read_item["translation"]) if result else ("本地 AI 未连接，暂不生成虚假正确率。\n\n参考翻译："+self.read_item["translation"])
        self.after(0,lambda:finish_translation(self,text,learner))
    threading.Thread(target=worker,daemon=True).start()


def finish_translation(self,text,learner):
    self.translation_feedback.config(text=text); self.state_data.setdefault("reading_translation_history",[]).append({"sentence":self.read_item["sentence"],"translation":learner,"feedback":text}); self.save_state(); self.btn(self.translation_feedback.master,"NEXT SENTENCE",lambda:next_interactive_reading(self),18).pack(pady=8)

def next_interactive_reading(self): self.read_i=(self.read_i+1)%len(READING_INTERACTIVE); self.show_reading()


# -----------------------------------------------------------------------------
# Listening: real timer + long-term memory of misspellings and missed chunks.
# -----------------------------------------------------------------------------
BASE_SHOW_LISTENING = app.IELTSApp.show_listening


def enhanced_show_listening(self):
    BASE_SHOW_LISTENING(self)
    parent=self.listen_entry.master
    attach_timer(self,parent,"LISTENING")
    self.listen_memory=tk.Label(parent,text="",bg=BG,fg=MUTED,font=(FONT,12),wraplength=1100,justify="center")
    self.listen_memory.pack(pady=5)


def token_diff(answer,target):
    a=re.findall(r"[a-z']+",answer.lower()); t=re.findall(r"[a-z']+",target.lower())
    missing=[]; wrong=[]
    # simple positional diagnostics are useful for dictation practice
    for i,word in enumerate(t):
        if i>=len(a): missing.append(word)
        elif a[i]!=word:
            if word not in a: wrong.append((a[i],word))
    # words absent from answer are also candidates for missed connected speech
    missing += [w for w in t if w not in a and w not in missing]
    return missing[:8],wrong[:8]


def connected_chunks(target,missing):
    words=re.findall(r"[A-Za-z']+",target)
    low=[w.lower() for w in words]; chunks=[]
    for m in missing:
        for i,w in enumerate(low):
            if w==m:
                chunks.append(" ".join(words[max(0,i-1):min(len(words),i+2)])); break
    return list(dict.fromkeys(chunks))[:5]


def enhanced_check_listening(self):
    target=app.LISTENING[self.listen_i]; ans=self.listen_entry.get(); score=self.accuracy(ans,target)
    missing,wrong=token_diff(ans,target); chunks=connected_chunks(target,missing)
    self.listen_result.config(text=f"ACCURACY  {score}%\n\n{target}")
    details=[]
    if wrong: details.append("SPELL / WORD: "+" · ".join(f"{a} → {b}" for a,b in wrong))
    if chunks: details.append("MISSED / CONNECTED SPEECH: "+" · ".join(chunks))
    self.listen_memory.config(text="\n".join(details) if details else "No obvious missed words.")
    memory=self.state_data.setdefault("listening_error_memory",{"wrong_words":{},"missed_chunks":{}})
    for _,correct in wrong: memory["wrong_words"][correct]=memory["wrong_words"].get(correct,0)+1
    for chunk in chunks: memory["missed_chunks"][chunk]=memory["missed_chunks"].get(chunk,0)+1
    self.state_data.setdefault("listening_scores",[]).append(score); self.save_state()
    if not getattr(self,"_next_listen_button",None) or not self._next_listen_button.winfo_exists():
        self._next_listen_button=self.btn(self.listen_result.master,"NEXT DICTATION",self.next_listening,16); self._next_listen_button.pack(pady=10)


# -----------------------------------------------------------------------------
# Writing: preserve learner's idea. No fixed model answer in BETTER feedback.
# -----------------------------------------------------------------------------
BASE_SHOW_WRITING=app.IELTSApp.show_writing

def enhanced_show_writing(self):
    BASE_SHOW_WRITING(self); attach_timer(self,self.write_entry.master,"WRITING")


def adaptive_ollama_correct(self,text,callback):
    def run():
        prompt=("You are an IELTS writing teacher. Correct the learner's sentence but preserve the learner's own idea. "
                "Do NOT substitute a memorized model answer or introduce an unrelated argument. Expand only from what the learner actually wrote. "
                "Return exactly four short lines: CORRECTED:, ERRORS:, BETTER:, WHY:. Sentence: "+text)
        result=ai_call(prompt,15)
        if not result:
            corrected,notes=self.basic_correct(text)
            result="CORRECTED: "+corrected+"\nERRORS: "+(" ".join(notes) if notes else "No obvious basic error detected.")+"\nBETTER: "+corrected+"\nWHY: Keep your own meaning and improve accuracy first."
        self.after(0,lambda:callback(result))
    threading.Thread(target=run,daemon=True).start()


# -----------------------------------------------------------------------------
# Speaking: comes after Writing. Mic button → live Windows speech recognition →
# transcript → grammar review + low-confidence words as pronunciation/clarity
# candidates. This is a clarity proxy, not a phoneme-level pronunciation score.
# -----------------------------------------------------------------------------

def get_latest_writing(self):
    hist=self.state_data.get("writing_history",[])
    return hist[-1].get("input","") if hist else ""


def enhanced_show_speaking(self):
    self.clear(); f=self.center(); latest=get_latest_writing(self)
    prompt=("Explain the idea you wrote in Writing in your own words and add one example." if latest else app.SPEAKING[self.speak_i])
    self.heading(f,"SPEAKING",f"PROMPT {self.speak_i+1} · FINAL 60 MIN SESSION"); attach_timer(self,f,"SPEAKING")
    tk.Label(f,text=prompt,bg=BG,fg=FG,font=(FONT,24,"bold"),wraplength=1150,justify="center").pack(pady=18)
    if latest: tk.Label(f,text="YOUR WRITING:  "+latest,bg=BG,fg=MUTED,font=(FONT,14),wraplength=1100,justify="center").pack(pady=8)
    self.speak_status=tk.Label(f,text="Press START RECORDING, speak naturally, then STOP & CHECK.",bg=BG,fg=MUTED,font=(FONT,14),wraplength=1100,justify="center"); self.speak_status.pack(pady=12)
    row=tk.Frame(f,bg=BG); row.pack(pady=8)
    self.btn(row,"START RECORDING",lambda:start_speech_recognition(self),18).pack(side="left",padx=7)
    self.btn(row,"STOP & CHECK",lambda:stop_and_check_speaking(self,prompt),18).pack(side="left",padx=7)
    self.speak_feedback=tk.Label(f,text="",bg=BG,fg=FG,font=(FONT,13),wraplength=1150,justify="center"); self.speak_feedback.pack(pady=12)
    self.back(f)


def start_speech_recognition(self):
    self.speech_output=""; self.speech_low_conf=[]
    ps=r'''
Add-Type -AssemblyName System.Speech
$r = New-Object System.Speech.Recognition.SpeechRecognitionEngine([System.Globalization.CultureInfo]::GetCultureInfo('en-US'))
$r.LoadGrammar((New-Object System.Speech.Recognition.DictationGrammar))
$r.SetInputToDefaultAudioDevice()
while ($true) {
  $x=$r.Recognize([TimeSpan]::FromSeconds(3))
  if ($x) {
    $low=@($x.Words | Where-Object {$_.Confidence -lt 0.55} | ForEach-Object {$_.Text}) -join ','
    Write-Output ('TEXT|' + $x.Text)
    if ($low) { Write-Output ('LOW|' + $low) }
  }
}
'''
    try:
        self.speech_proc=subprocess.Popen(["powershell","-NoProfile","-Command",ps],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True,creationflags=0x08000000)
        self.speak_status.config(text="RECORDING... speak now.")
        def reader():
            try:
                for line in self.speech_proc.stdout:
                    line=line.strip()
                    if line.startswith("TEXT|"): self.speech_output+=(" "+line[5:])
                    elif line.startswith("LOW|"): self.speech_low_conf += [x for x in line[4:].split(',') if x]
            except Exception: pass
        threading.Thread(target=reader,daemon=True).start()
    except Exception:
        self.speak_status.config(text="Microphone recognition could not start.")


def stop_and_check_speaking(self,prompt):
    if hasattr(self,"speech_proc"):
        try:self.speech_proc.terminate()
        except Exception:pass
    transcript=getattr(self,"speech_output","").strip(); low=list(dict.fromkeys(getattr(self,"speech_low_conf",[])))
    if not transcript:
        self.speak_feedback.config(text="No speech was recognized. Check the Windows microphone input and try again."); return
    self.speak_status.config(text="TRANSCRIPT: "+transcript)
    self.speak_feedback.config(text="Checking grammar and speaking clarity...")
    prompt_ai=("You are an IELTS speaking teacher. Review this transcript. Preserve the speaker's meaning. Return exactly: "
               "GRAMMAR: ...\nNATURAL VERSION: ...\nFLUENCY: ...\nCONTENT: ...\nDo not claim phoneme-level pronunciation analysis. Transcript: "+transcript)
    def worker():
        result=ai_call(prompt_ai,20) or "GRAMMAR: Local AI unavailable.\nNATURAL VERSION: "+transcript+"\nFLUENCY: Review pauses and repetitions.\nCONTENT: Keep developing your own idea."
        clarity=("\nPRONUNCIATION / CLARITY CANDIDATES: "+" · ".join(low)) if low else "\nPRONUNCIATION / CLARITY CANDIDATES: No low-confidence words detected by Windows speech recognition."
        final=result+clarity+"\nNote: these are recognition-confidence candidates, not a phoneme-level pronunciation score."
        self.state_data.setdefault("speaking_history",[]).append({"transcript":transcript,"feedback":final,"low_confidence_words":low}); self.save_state(); self.after(0,lambda:self.speak_feedback.config(text=final))
    threading.Thread(target=worker,daemon=True).start()


# Home order: Vocabulary → Listening → Reading → Writing → Speaking.
def enhanced_home(self):
    self.clear(); f=self.center(); self.heading(f,"IELTS · DAY 1","5 HOURS · IMMERSIVE TRAINING")
    for title,sub,cmd in [
        ("VOCABULARY","100 words · roots & affixes · 60 min",self.show_vocab),
        ("LISTENING","dictation · error memory · 60 min",self.show_listening),
        ("READING","structure · translation · 60 min",self.show_reading),
        ("WRITING","your sentence → instant correction · 60 min",self.show_writing),
        ("SPEAKING","use your writing → record → review · 60 min",self.show_speaking),
    ]:
        self.btn(f,title,cmd,30).pack(pady=6); tk.Label(f,text=sub,bg=BG,fg=MUTED,font=(FONT,11)).pack(pady=(0,8))


# Vocabulary UI itself is intentionally untouched.
app.IELTSApp.show_home=enhanced_home
app.IELTSApp.show_reading=enhanced_show_reading
app.IELTSApp.next_reading=next_interactive_reading
app.IELTSApp.show_listening=enhanced_show_listening
app.IELTSApp.check_listening=enhanced_check_listening
app.IELTSApp.show_writing=enhanced_show_writing
app.IELTSApp.ollama_correct=adaptive_ollama_correct
app.IELTSApp.show_speaking=enhanced_show_speaking

if __name__ == "__main__":
    app.IELTSApp().mainloop()
