import re
import time
import threading
from difflib import SequenceMatcher
import tkinter as tk

import start_app

app = start_app.app
BG, FG, MUTED, FONT = app.BG, app.FG, app.MUTED, app.FONT


def ensure_session(self, name, seconds=3600):
    if not hasattr(self, "_session_deadlines"):
        self._session_deadlines = {}
    if name not in self._session_deadlines:
        self._session_deadlines[name] = time.time() + seconds
    return self._session_deadlines[name]


def timer_label(self, parent, name):
    label = tk.Label(parent, text="60:00", bg=BG, fg=FG, font=(FONT, 14, "bold"))
    label.pack(pady=(4, 8))
    deadline = ensure_session(self, name)

    def tick():
        if not label.winfo_exists():
            return
        remain = max(0, int(deadline - time.time()))
        label.config(text=f"{remain // 60:02d}:{remain % 60:02d}")
        if remain > 0:
            label.after(1000, tick)
        else:
            label.config(text="00:00 · SESSION COMPLETE")
    tick()
    return label


# ---------- VOCABULARY: exact old proportions + click pronunciation ----------
def show_vocab_v2(self):
    self.clear(); outer=self.center(); self.heading(outer,"VOCABULARY",f"100 WORDS · PAGE {self.vocab_page+1} / 5 · HOVER FOR MEANING · CLICK TO HEAR")
    grid=tk.Frame(outer,bg=BG); grid.pack()
    start=self.vocab_page*20
    for r,(word,pos,root,meaning) in enumerate(app.VOCAB[start:start+20]):
        tk.Label(grid,text=f"{start+r+1:03d}",bg=BG,fg=MUTED,font=(FONT,13),width=5,anchor="e").grid(row=r,column=0,padx=(0,18),pady=3)
        wl=tk.Label(grid,text=word,bg=BG,fg=FG,font=(FONT,16,"bold"),width=18,anchor="w",cursor="hand2")
        wl.grid(row=r,column=1,pady=3)
        app.Tooltip(wl, meaning)
        wl.bind("<Button-1>", lambda e, w=word: self.speak_text(w), add="+")
        tk.Label(grid,text=pos,bg=BG,fg=MUTED,font=(FONT,12),width=8,anchor="w").grid(row=r,column=2,padx=18)
        tk.Label(grid,text=root,bg=BG,fg=FG,font=(FONT,13),width=24,anchor="w").grid(row=r,column=3)
    nav=tk.Frame(outer,bg=BG); nav.pack(pady=18)
    if self.vocab_page>0: self.btn(nav,"PREVIOUS",self.prev_vocab,12).pack(side="left",padx=5)
    if self.vocab_page<4: self.btn(nav,"NEXT 20",self.next_vocab,12).pack(side="left",padx=5)
    else: self.btn(nav,"COMPLETE",self.complete_vocab,12).pack(side="left",padx=5)
    timer_label(self, outer, "vocabulary")
    self.back(outer)


# ---------- LISTENING: diagnose exact errors, store them, repair before next ----------
def words(s):
    return re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?", s.lower())


def diagnose(expected, learner):
    target, got = words(expected), words(learner)
    sm = SequenceMatcher(None, target, got)
    spelling, missed, extra = [], [], []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        t = target[i1:i2]
        g = got[j1:j2]
        if tag == "replace":
            # Pair likely misspellings one-to-one, otherwise treat as missed/extra chunks.
            common = min(len(t), len(g))
            for k in range(common):
                ratio = SequenceMatcher(None, t[k], g[k]).ratio()
                if ratio >= 0.55:
                    spelling.append((g[k], t[k]))
                else:
                    missed.append(t[k])
                    extra.append(g[k])
            missed.extend(t[common:]); extra.extend(g[common:])
        elif tag == "delete":
            missed.extend(t)
        elif tag == "insert":
            extra.extend(g)
    return spelling, missed, extra


def chunk_missed(expected, missed):
    toks = words(expected)
    missed_set = set(missed)
    chunks=[]; current=[]
    for tok in toks:
        if tok in missed_set:
            current.append(tok)
        elif current:
            chunks.append(" ".join(current)); current=[]
    if current: chunks.append(" ".join(current))
    return [c for c in chunks if c]


def save_listening_errors(self, spelling, missed, chunks):
    mem=self.state_data.setdefault("listening_error_memory", {"spelling":{},"missed_words":{},"connected_chunks":{}})
    for wrong,right in spelling:
        key=f"{wrong} → {right}"; mem["spelling"][key]=mem["spelling"].get(key,0)+1
    for w in missed:
        mem["missed_words"][w]=mem["missed_words"].get(w,0)+1
    for c in chunks:
        mem["connected_chunks"][c]=mem["connected_chunks"].get(c,0)+1
    self.save_state()


def show_listening_v2(self):
    self.clear(); f=self.center(); target=app.LISTENING[self.listen_i]
    self.heading(f,"LISTENING",f"DICTATION {self.listen_i+1} / {len(app.LISTENING)} · 60 MIN SESSION")
    tk.Label(f,text="Listen → type → diagnose → repair mistakes → continue.",bg=BG,fg=FG,font=(FONT,17)).pack(pady=12)
    self.btn(f,"▶ PLAY",lambda:self.speak_text(target),16).pack(pady=10)
    self.listen_entry=tk.Entry(f,bg=BG,fg=FG,insertbackground=FG,relief="solid",bd=1,font=(FONT,18),justify="center",width=72)
    self.listen_entry.pack(ipady=10,pady=16); self.listen_entry.focus_set()
    self.listen_result=tk.Label(f,text="",bg=BG,fg=FG,font=(FONT,14),wraplength=1150,justify="center")
    self.listen_result.pack(pady=10)
    self.listen_actions=tk.Frame(f,bg=BG); self.listen_actions.pack(pady=6)
    self.btn(self.listen_actions,"CHECK",self.check_listening_v2,16).pack()
    timer_label(self,f,"listening")
    self.back(f)


def check_listening_v2(self):
    target=app.LISTENING[self.listen_i]; ans=self.listen_entry.get().strip()
    score=self.accuracy(ans,target)
    spelling, missed, extra = diagnose(target, ans)
    chunks=chunk_missed(target, missed)
    save_listening_errors(self, spelling, missed, chunks)
    self._repair_queue=[]
    self._repair_queue += [("SPELL", right) for _,right in spelling]
    self._repair_queue += [("MISSED", c) for c in chunks]
    spell_txt=" · ".join(f"{a} → {b}" for a,b in spelling) or "none"
    missed_txt=" · ".join(missed) or "none"
    extra_txt=" · ".join(extra) or "none"
    self.listen_result.config(text=f"ACCURACY  {score}%\n\n{target}\n\nSPELLING: {spell_txt}\nMISSED / UNCLEAR: {missed_txt}\nEXTRA / WRONG: {extra_txt}")
    for w in self.listen_actions.winfo_children(): w.destroy()
    if self._repair_queue:
        self.btn(self.listen_actions,"REPAIR ERRORS",self.start_repair,18).pack()
    else:
        self.btn(self.listen_actions,"NEXT DICTATION",self.next_listening_v2,18).pack()


def start_repair(self):
    self._repair_pos=0
    show_repair_item(self)


def show_repair_item(self):
    if self._repair_pos >= len(self._repair_queue):
        self.listen_result.config(text="ERROR REPAIR COMPLETE · now continue to the next dictation.")
        for w in self.listen_actions.winfo_children(): w.destroy()
        self.btn(self.listen_actions,"NEXT DICTATION",self.next_listening_v2,18).pack()
        return
    kind, phrase=self._repair_queue[self._repair_pos]
    self.listen_result.config(text=f"{kind} REPAIR {self._repair_pos+1}/{len(self._repair_queue)}\n\nListen to this difficult part and type it correctly.")
    for w in self.listen_actions.winfo_children(): w.destroy()
    self.btn(self.listen_actions,"▶ PLAY ERROR",lambda:self.speak_text(phrase),16).pack(pady=4)
    self.repair_entry=tk.Entry(self.listen_actions,bg=BG,fg=FG,insertbackground=FG,relief="solid",bd=1,font=(FONT,17),justify="center",width=38)
    self.repair_entry.pack(ipady=8,pady=7); self.repair_entry.focus_set()
    self.btn(self.listen_actions,"CHECK REPAIR",lambda:check_repair(self,phrase),16).pack(pady=4)


def check_repair(self, phrase):
    score=self.accuracy(self.repair_entry.get(),phrase)
    if score >= 95:
        self._repair_pos += 1
        show_repair_item(self)
    else:
        self.listen_result.config(text=f"{score}% · Not fixed yet. Listen again and type it once more.")


def next_listening_v2(self):
    self.listen_i=(self.listen_i+1)%len(app.LISTENING); self.show_listening()


# ---------- WRITING: preserve learner idea, diagnose spelling/run-on, then AI upgrade ----------
def local_writing_diagnosis(text):
    original=text.strip(); corrected=original
    notes=[]
    spelling={"tranport":"transport","goverment":"government","enviroment":"environment","becuase":"because","imporant":"important","benifit":"benefit","pepole":"people"}
    for wrong,right in spelling.items():
        if re.search(rf"\b{wrong}\b", corrected, re.I):
            corrected=re.sub(rf"\b{wrong}\b",right,corrected,flags=re.I); notes.append(f"Spelling: {wrong} → {right}")
    if corrected and corrected[0].islower():
        corrected=corrected[0].upper()+corrected[1:]; notes.append("Capitalization: start with a capital letter")
    # Catch a common run-on pattern: clause + we/people/they + finite verb with no connector.
    if re.search(r"\b(is|are|was|were|can|should|will)\b.+\b(we|people|they|it)\s+(are|is|can|will|have|feel)\b", corrected, re.I) and not re.search(r"[,;]\s*(so|and|but|because)\b", corrected, re.I):
        notes.append("Sentence structure: two complete ideas are joined without a connector or punctuation")
        corrected=re.sub(r"\s+(we|people|they)\s+(are|feel)\b", r", so \1 \2", corrected, count=1, flags=re.I)
    if corrected and corrected[-1] not in ".!?”?": corrected += "."; notes.append("Punctuation: add end punctuation")
    return corrected, notes


def show_writing_v2(self):
    self.clear(); f=self.center(); self.heading(f,"WRITING",f"SENTENCE {self.write_i+1} / {len(app.WRITING)} · 60 MIN SESSION")
    prompt,_=app.WRITING[self.write_i]
    tk.Label(f,text=prompt,bg=BG,fg=FG,font=(FONT,21,"bold"),wraplength=1100,justify="center").pack(pady=18)
    self.write_entry=tk.Entry(f,bg=BG,fg=FG,insertbackground=FG,relief="solid",bd=1,font=(FONT,18),justify="center",width=78)
    self.write_entry.pack(ipady=10,pady=16); self.write_entry.focus_set()
    self.write_result=tk.Label(f,text="Write your own idea. Feedback must preserve your meaning.",bg=BG,fg=MUTED,font=(FONT,14),wraplength=1200,justify="center")
    self.write_result.pack(pady=10)
    self.write_actions=tk.Frame(f,bg=BG); self.write_actions.pack(pady=6)
    self.btn(self.write_actions,"CORRECT NOW",self.correct_writing_v2,18).pack()
    timer_label(self,f,"writing")
    self.back(f)


def correct_writing_v2(self):
    text=self.write_entry.get().strip()
    if not text:
        self.write_result.config(text="Write one sentence first.",fg=FG); return
    corrected, notes=local_writing_diagnosis(text)
    self.write_result.config(text="CHECKING...",fg=FG)
    prompt,_=app.WRITING[self.write_i]

    def worker():
        ai_prompt=(
            "You are an IELTS writing teacher. Preserve the learner's exact intended idea. Do not replace it with a memorised model answer. "
            "Diagnose spelling, grammar, sentence boundaries, word choice and clarity. Then improve the same idea one level. "
            "Return exactly four short lines in English only:\n"
            "CORRECTED: ...\nERRORS: ...\nBETTER: ...\nNEXT: one short question that helps the learner develop this same idea.\n"
            f"Task: {prompt}\nLearner sentence: {text}\nLocal corrected candidate: {corrected}"
        )
        result=""
        try:
            import json, urllib.request
            payload=json.dumps({"model":"qwen3:8b","prompt":ai_prompt,"stream":False,"options":{"temperature":0.1}}).encode()
            req=urllib.request.Request("http://127.0.0.1:11434/api/generate",data=payload,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=18) as r:
                result=json.loads(r.read().decode())["response"].strip()
        except Exception:
            errors="; ".join(notes) if notes else "No obvious basic error detected"
            better=corrected
            if "public transport" in corrected.lower() and "free" in corrected.lower():
                better="Free public transport can make daily travel more affordable, so people may feel happier about commuting."
            result=f"CORRECTED: {corrected}\nERRORS: {errors}\nBETTER: {better}\nNEXT: Why does this benefit matter in daily life?"
        self.after(0,lambda:finish_writing(self,text,result))
    threading.Thread(target=worker,daemon=True).start()


def finish_writing(self,text,result):
    self.write_result.config(text=result,fg=FG)
    self.state_data.setdefault("writing_history",[]).append({"input":text,"feedback":result,"time":time.time()})
    # Save learner language issues for future review / speaking.
    mem=self.state_data.setdefault("writing_error_memory",{})
    _,notes=local_writing_diagnosis(text)
    for note in notes: mem[note]=mem.get(note,0)+1
    self.save_state()
    for w in self.write_actions.winfo_children(): w.destroy()
    self.btn(self.write_actions,"NEXT SENTENCE",self.next_writing,18).pack()


app.IELTSApp.show_vocab = show_vocab_v2
app.IELTSApp.show_listening = show_listening_v2
app.IELTSApp.check_listening_v2 = check_listening_v2
app.IELTSApp.start_repair = start_repair
app.IELTSApp.show_writing = show_writing_v2
app.IELTSApp.correct_writing_v2 = correct_writing_v2

if __name__ == "__main__":
    app.IELTSApp().mainloop()
