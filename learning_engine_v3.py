import re, time, threading, tkinter as tk
from difflib import SequenceMatcher
import learning_engine_v2 as v2
from curriculum_v3 import DAY1

app=v2.app; BG,FG,MUTED,FONT=v2.BG,v2.FG,v2.MUTED,v2.FONT
app.LISTENING=DAY1['listening']
v2.start_app.READING_INTERACTIVE=DAY1['reading']

# Keep vocabulary layout exactly as V2. Only make the 20 focus words visibly tied to today.
BASE_HOME=app.IELTSApp.show_home

def home(self):
    self.clear(); f=self.center(); self.heading(f,'IELTS · DAY 1',DAY1['theme'].upper()+' · 5 HOURS')
    tk.Label(f,text='GRAMMAR  ·  '+'   |   '.join(DAY1['grammar']),bg=BG,fg=MUTED,font=(FONT,11),wraplength=1200,justify='center').pack(pady=(0,14))
    for title,sub,cmd in [
      ('VOCABULARY','100 words · today focus: 20 shared words · 60 min',self.show_vocab),
      ('LISTENING','today vocabulary + grammar · diagnose + repair · 60 min',self.show_listening),
      ('READING','same theme + grammar · structure + translation · 60 min',self.show_reading),
      ('WRITING','reuse today vocabulary + grammar · instant correction · 60 min',self.show_writing),
      ('SPEAKING','final output from everything learned today · 60 min',self.show_speaking)]:
        self.btn(f,title,cmd,30).pack(pady=5); tk.Label(f,text=sub,bg=BG,fg=MUTED,font=(FONT,10)).pack(pady=(0,7))

# Robust listening: bind button directly to this checker; show diagnostics immediately.
def align_errors(expected, learner):
    t=v2.words(expected); g=v2.words(learner); sm=SequenceMatcher(None,t,g)
    spelling=[]; missed=[]; extra=[]
    for tag,i1,i2,j1,j2 in sm.get_opcodes():
        if tag=='equal': continue
        T=t[i1:i2]; G=g[j1:j2]
        if tag=='replace':
            n=min(len(T),len(G))
            for k in range(n):
                ratio=SequenceMatcher(None,T[k],G[k]).ratio()
                if ratio>=.58: spelling.append((G[k],T[k]))
                else: missed.append(T[k]); extra.append(G[k])
            missed+=T[n:]; extra+=G[n:]
        elif tag=='delete': missed+=T
        elif tag=='insert': extra+=G
    return spelling,missed,extra

def listening(self):
    self.clear(); f=self.center(); target=app.LISTENING[self.listen_i%len(app.LISTENING)]
    self.heading(f,'LISTENING',f"DICTATION {self.listen_i+1} / {len(app.LISTENING)} · {DAY1['theme'].upper()}")
    tk.Label(f,text="Listen → type → diagnose → repair → use it later in Writing and Speaking.",bg=BG,fg=FG,font=(FONT,16)).pack(pady=10)
    self.btn(f,'▶ PLAY',lambda:self.speak_text(target),16).pack(pady=8)
    self.listen_entry=tk.Entry(f,bg=BG,fg=FG,insertbackground=FG,relief='solid',bd=1,font=(FONT,18),justify='center',width=72); self.listen_entry.pack(ipady=10,pady=14); self.listen_entry.focus_set()
    self.listen_result=tk.Label(f,text='',bg=BG,fg=FG,font=(FONT,13),wraplength=1200,justify='center'); self.listen_result.pack(pady=8)
    self.listen_actions=tk.Frame(f,bg=BG); self.listen_actions.pack(pady=5)
    self.btn(self.listen_actions,'CHECK',lambda:check_listening(self),16).pack()
    v2.timer_label(self,f,'listening'); self.back(f)

def check_listening(self):
    target=app.LISTENING[self.listen_i%len(app.LISTENING)]; ans=self.listen_entry.get().strip()
    if not ans: self.listen_result.config(text='Type what you hear first.'); return
    score=self.accuracy(ans,target); spelling,missed,extra=align_errors(target,ans); chunks=v2.chunk_missed(target,missed)
    v2.save_listening_errors(self,spelling,missed,chunks)
    lines=[f'ACCURACY  {score}%',target]
    if spelling: lines.append('SPELLING  ·  '+'   '.join(f'{a} → {b}' for a,b in spelling))
    if missed: lines.append('MISSED / UNCLEAR  ·  '+'   '.join(missed))
    if extra: lines.append('EXTRA / WRONG  ·  '+'   '.join(extra))
    if not(spelling or missed or extra): lines.append('CLEAN DICTATION · no obvious word-level error')
    self.listen_result.config(text='\n\n'.join(lines))
    self._repair_queue=[('SPELLING',b) for _,b in spelling]+[('MISSED / CONNECTED SPEECH',c) for c in chunks]
    for w in self.listen_actions.winfo_children(): w.destroy()
    if self._repair_queue:self.btn(self.listen_actions,'REPAIR ERRORS',lambda:v2.start_repair(self),18).pack()
    else:self.btn(self.listen_actions,'NEXT DICTATION',lambda:next_listen(self),18).pack()

def next_listen(self): self.listen_i=(self.listen_i+1)%len(app.LISTENING); self.show_listening()

# Writing must use today's language. Gibberish is rejected rather than 'corrected'.
def writing(self):
    self.clear(); f=self.center(); idx=self.write_i%len(DAY1['writing_prompts']); prompt=DAY1['writing_prompts'][idx]
    self.heading(f,'WRITING',f'SENTENCE {idx+1} / {len(DAY1["writing_prompts"])} · {DAY1["theme"].upper()}')
    tk.Label(f,text=prompt,bg=BG,fg=FG,font=(FONT,20,'bold'),wraplength=1150,justify='center').pack(pady=15)
    tk.Label(f,text='TODAY LANGUAGE  ·  '+', '.join(DAY1['focus_words'][:10])+'\nGRAMMAR  ·  '+' | '.join(DAY1['grammar']),bg=BG,fg=MUTED,font=(FONT,11),wraplength=1100,justify='center').pack(pady=8)
    self.write_entry=tk.Entry(f,bg=BG,fg=FG,insertbackground=FG,relief='solid',bd=1,font=(FONT,18),justify='center',width=78); self.write_entry.pack(ipady=10,pady=14); self.write_entry.focus_set()
    self.write_result=tk.Label(f,text='Write a meaningful English sentence. The system will preserve your idea.',bg=BG,fg=MUTED,font=(FONT,13),wraplength=1200,justify='center'); self.write_result.pack(pady=8)
    self.write_actions=tk.Frame(f,bg=BG); self.write_actions.pack(pady=5); self.btn(self.write_actions,'CORRECT NOW',lambda:correct_write(self,prompt),18).pack()
    v2.timer_label(self,f,'writing'); self.back(f)

def looks_gibberish(text):
    toks=re.findall(r'[a-z]+',text.lower()); known=set(DAY1['focus_words']+['i','we','people','the','a','an','is','are','can','should','because','although','to','and','it','they','this','that','of','in','for','more','better','cars','city','cities','travel','costs','air','life'])
    if len(toks)<3:return True
    recognizable=sum(1 for x in toks if x in known or len(x)<=2)
    return recognizable/max(1,len(toks))<.35

def correct_write(self,prompt):
    text=self.write_entry.get().strip()
    if looks_gibberish(text):
        self.write_result.config(text='NOT A VALID ENGLISH SENTENCE · Please express a real idea before correction.\nTry using today’s vocabulary and one grammar pattern.'); return
    self.write_result.config(text='CHECKING...')
    grammar='; '.join(DAY1['grammar']); vocab=', '.join(DAY1['focus_words'])
    ai_prompt=f'''You are an IELTS teacher. Task: {prompt}\nToday's vocabulary: {vocab}\nToday's grammar: {grammar}\nLearner: {text}\nPreserve the learner's meaning. Diagnose spelling, grammar, sentence boundaries, word choice, task relevance, and whether today's vocabulary/grammar was used correctly. Never pretend gibberish is valid English. Return exactly:\nCORRECTED: ...\nERRORS: ...\nTODAY LANGUAGE: ...\nBETTER: ...\nNEXT: ...'''
    def worker():
        result=v2.start_app.ai_call(ai_prompt,25)
        if not result:
            corrected,notes=v2.local_writing_diagnosis(text); result='CORRECTED: '+corrected+'\nERRORS: '+('; '.join(notes) if notes else 'No obvious basic error detected')+'\nTODAY LANGUAGE: Check whether you used today’s target grammar.\nBETTER: '+corrected+'\nNEXT: Add one reason using because.'
        self.after(0,lambda:finish_write(self,text,result))
    threading.Thread(target=worker,daemon=True).start()

def finish_write(self,text,result):
    self.write_result.config(text=result,fg=FG); self.state_data.setdefault('writing_history',[]).append({'input':text,'feedback':result,'theme':DAY1['theme'],'time':time.time()}); self.save_state()
    for w in self.write_actions.winfo_children():w.destroy()
    self.btn(self.write_actions,'NEXT SENTENCE',lambda:next_write(self),18).pack()

def next_write(self): self.write_i=(self.write_i+1)%len(DAY1['writing_prompts']); self.show_writing()

# Speaking is explicitly cumulative. Keep V2 recorder but replace its prompt context.
BASE_SPEAK=v2.start_app.enhanced_show_speaking
def speaking(self):
    self.clear(); f=self.center(); latest=v2.start_app.get_latest_writing(self)
    self.heading(f,'SPEAKING','FINAL OUTPUT · '+DAY1['theme'].upper()); v2.timer_label(self,f,'speaking')
    tk.Label(f,text=DAY1['speaking_prompt'],bg=BG,fg=FG,font=(FONT,22,'bold'),wraplength=1200,justify='center').pack(pady=14)
    tk.Label(f,text='USE TODAY  ·  '+', '.join(DAY1['focus_words'][:12])+'\nGRAMMAR  ·  '+' | '.join(DAY1['grammar']),bg=BG,fg=MUTED,font=(FONT,11),wraplength=1150,justify='center').pack(pady=7)
    if latest:tk.Label(f,text='YOUR WRITING  ·  '+latest,bg=BG,fg=MUTED,font=(FONT,13),wraplength=1100,justify='center').pack(pady=7)
    self.speak_status=tk.Label(f,text='START → speak for 60–90 seconds → STOP & CHECK',bg=BG,fg=MUTED,font=(FONT,13)); self.speak_status.pack(pady=9)
    row=tk.Frame(f,bg=BG);row.pack(pady=6);self.btn(row,'START RECORDING',lambda:v2.start_app.start_speech_recognition(self),18).pack(side='left',padx=6);self.btn(row,'STOP & CHECK',lambda:v2.start_app.stop_and_check_speaking(self,DAY1['speaking_prompt']),18).pack(side='left',padx=6)
    self.speak_feedback=tk.Label(f,text='',bg=BG,fg=FG,font=(FONT,12),wraplength=1150,justify='center');self.speak_feedback.pack(pady=9);self.back(f)

app.IELTSApp.show_home=home
app.IELTSApp.show_listening=listening
app.IELTSApp.show_writing=writing
app.IELTSApp.show_speaking=speaking

if __name__=='__main__': app.IELTSApp().mainloop()
