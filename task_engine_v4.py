import re, tkinter as tk
import learning_engine_v3 as v3
from curriculum_v3 import DAY1

app=v3.app; BG,FG,MUTED,FONT=v3.BG,v3.FG,v3.MUTED,v3.FONT

LISTENING_TASKS=[
 {"title":"SECTION 1 · FORM COMPLETION","audio":"Good morning. I would like to register for the city travel programme. The annual membership costs fifty dollars, but full-time students receive a twenty percent discount. Please write your current address on the form and pay a ten-dollar deposit when you collect the card.","instructions":"Complete the form. Write NO MORE THAN TWO WORDS AND/OR A NUMBER for each answer.","questions":[("1  Annual membership fee: $", "50"),("2  Student discount: ","20 percent"),("3  Required personal detail: current ","address"),("4  Deposit: $", "10")]},
 {"title":"SECTION 2 · NOTE COMPLETION","audio":"The council is introducing a new transport plan next month. During peak hours, buses will run every ten minutes. The main aim is to reduce traffic congestion in the city centre. Two new routes will serve the northern suburbs, and passengers are advised to use the mobile application to check revised departure times.","instructions":"Complete the notes. Write NO MORE THAN TWO WORDS AND/OR A NUMBER.","questions":[("5  Peak-hour buses: every ___ minutes","10"),("6  Main aim: reduce traffic ___","congestion"),("7  New routes serve the ___ suburbs","northern"),("8  Check departure times using the mobile ___","application")]},
 {"title":"SECTION 3 · MULTIPLE CHOICE","audio":"Two students are discussing a research project on urban transport. Mia initially wanted to study ticket prices, but Daniel argues that reliability has a greater influence on whether commuters leave their cars at home. They finally agree to compare both factors, while also collecting information about journey time.","instructions":"Choose the correct answer A, B or C.","questions":[("9  What does Daniel think most strongly affects commuters?\nA ticket prices   B reliability   C journey time","B"),("10  What do the students finally decide to do?\nA study only reliability   B study journey time only   C compare more than one factor","C")]}
]

READING_PASSAGE="""Public transport is often presented as a solution to urban congestion and pollution. Although governments in many cities have invested heavily in rail and bus infrastructure, investment alone does not necessarily persuade commuters to leave their cars at home. Research suggests that passengers are more likely to use public transport when services are reliable, frequent and affordable.\n\nPrice is therefore only one part of the decision. A cheap service that is frequently delayed may be less attractive than a more expensive system that allows passengers to arrive on time. Accessibility is also significant, particularly for people who live far from major transport routes. For these residents, private vehicles may remain the most practical option.\n\nNevertheless, well-designed public transport can produce benefits beyond shorter journeys. Reducing the number of private vehicles can lower emissions, improve air quality and make urban areas safer for pedestrians. For this reason, some researchers argue that transport policy should be treated not simply as an infrastructure issue but as an important part of environmental and social policy."""
READING_TASKS=[
 ("TRUE / FALSE / NOT GIVEN","1  Government investment always causes commuters to stop using private cars.","FALSE"),
 ("TRUE / FALSE / NOT GIVEN","2  Research indicates that reliability can influence people's transport choices.","TRUE"),
 ("TRUE / FALSE / NOT GIVEN","3  The passage states that most commuters prefer rail services to buses.","NOT GIVEN"),
 ("TRUE / FALSE / NOT GIVEN","4  Cheap public transport is necessarily more attractive than an expensive service.","FALSE"),
 ("SENTENCE COMPLETION","5  People living far from major transport routes may continue to use ___.","private vehicles"),
 ("SENTENCE COMPLETION","6  Fewer private vehicles can improve ___.","air quality"),
 ("MULTIPLE CHOICE","7  What is the writer's main point in the final paragraph?\nA Transport only affects journey time.\nB Transport policy has wider environmental and social effects.\nC Private vehicles should be prohibited.","B")]

def norm(x): return re.sub(r'[^a-z0-9 ]','',x.lower()).strip()

def listening_task(self):
 self.clear(); self.lt=getattr(self,'lt',0)%len(LISTENING_TASKS); q=LISTENING_TASKS[self.lt]; f=self.center(); self.heading(f,'LISTENING',q['title']); v3.v2.timer_label(self,f,'listening')
 tk.Label(f,text=q['instructions'],bg=BG,fg=MUTED,font=(FONT,13),wraplength=1100,justify='center').pack(pady=6); self.btn(f,'▶ PLAY TASK AUDIO',lambda:self.speak_text(q['audio']),20).pack(pady=9)
 self.l_entries=[]
 for text,ans in q['questions']:
  row=tk.Frame(f,bg=BG); row.pack(pady=5); tk.Label(row,text=text,bg=BG,fg=FG,font=(FONT,14),wraplength=800,justify='left').pack(side='left',padx=8); e=tk.Entry(row,bg=BG,fg=FG,insertbackground=FG,font=(FONT,14),width=22,justify='center',relief='solid',bd=1); e.pack(side='left',ipady=5); self.l_entries.append((e,ans,text))
 self.lres=tk.Label(f,text='',bg=BG,fg=FG,font=(FONT,12),wraplength=1150,justify='center'); self.lres.pack(pady=8); self.btn(f,'SUBMIT TASK',lambda:check_ltask(self),18).pack(pady=6); self.back(f)

def check_ltask(self):
 q=LISTENING_TASKS[self.lt]; correct=0; feedback=[]
 for i,(e,ans,text) in enumerate(self.l_entries):
  got=e.get().strip(); ok=norm(got)==norm(ans); correct+=ok
  if not ok: feedback.append(f'Q{i+1}: {got or "—"} → {ans}'); self.state_data.setdefault('listening_task_errors',[]).append({'task':q['title'],'question':text,'answer':ans,'input':got})
 score=round(100*correct/len(self.l_entries)); self.save_state(); self.lres.config(text=f'SCORE  {correct}/{len(self.l_entries)}  ·  {score}%'+(('\n\nREVIEW  ·  '+'   |   '.join(feedback)) if feedback else '\n\nALL CORRECT'))
 self.btn(self.lres.master,'NEXT TASK',lambda:next_ltask(self),18).pack(pady=6)
def next_ltask(self): self.lt=(self.lt+1)%len(LISTENING_TASKS); self.show_listening()

def reading_task(self):
 self.clear(); f=self.center(); self.heading(f,'READING','IELTS PASSAGE · MIXED QUESTION TYPES'); v3.v2.timer_label(self,f,'reading')
 body=tk.Frame(f,bg=BG); body.pack()
 # Medium size: larger than V4, smaller than the earlier sentence-training screen.
 left=tk.Text(body,width=66,height=21,bg=BG,fg=FG,insertbackground=FG,font=(FONT,16),wrap='word',relief='flat',padx=12,pady=10,spacing1=2,spacing3=7)
 left.grid(row=0,column=0,padx=22); left.insert('1.0',READING_PASSAGE); left.config(state='disabled')
 right=tk.Frame(body,bg=BG); right.grid(row=0,column=1,padx=22,sticky='n'); self.r_entries=[]
 for i,(typ,text,ans) in enumerate(READING_TASKS):
  tk.Label(right,text=typ,bg=BG,fg=MUTED,font=(FONT,11,'bold')).pack(anchor='w',pady=(6,1))
  tk.Label(right,text=text,bg=BG,fg=FG,font=(FONT,13),wraplength=560,justify='left').pack(anchor='w')
  e=tk.Entry(right,bg=BG,fg=FG,insertbackground=FG,font=(FONT,13),width=34,relief='solid',bd=1); e.pack(anchor='w',ipady=5,pady=4); self.r_entries.append((e,ans,text,typ))
 self.rres=tk.Label(f,text='',bg=BG,fg=FG,font=(FONT,12),wraplength=1250,justify='center'); self.rres.pack(pady=7); self.btn(f,'SUBMIT READING',lambda:check_rtask(self),18).pack(pady=5); self.back(f)

def check_rtask(self):
 correct=0; feedback=[]
 for i,(e,ans,text,typ) in enumerate(self.r_entries):
  got=e.get().strip(); ok=norm(got)==norm(ans); correct+=ok
  if not ok: feedback.append(f'Q{i+1}: {got or "—"} → {ans}'); self.state_data.setdefault('reading_task_errors',[]).append({'type':typ,'question':text,'answer':ans,'input':got})
 score=round(100*correct/len(self.r_entries)); self.save_state(); self.rres.config(text=f'SCORE  {correct}/{len(self.r_entries)}  ·  {score}%'+(('\nREVIEW  ·  '+'   |   '.join(feedback)) if feedback else '\nALL CORRECT'))

app.IELTSApp.show_listening=listening_task
app.IELTSApp.show_reading=reading_task
if __name__=='__main__': app.IELTSApp().mainloop()
