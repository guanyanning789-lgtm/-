import os, re, subprocess, tempfile, threading, time, uuid
import task_engine_v4 as v4

app=v4.app

VOICE_FEMALE='en-GB-SoniaNeural'
VOICE_MALE='en-GB-RyanNeural'


def ensure_edge_tts():
    try:
        import edge_tts
        return True
    except Exception:
        return False


def play_mp3(path):
    ps=f'''$p=New-Object -ComObject WMPlayer.OCX; $m=$p.newMedia("{path}"); $p.currentPlaylist.insertItem(0,$m); $p.controls.play(); while($p.playState -ne 1){{Start-Sleep -Milliseconds 150}}'''
    subprocess.run(['powershell','-NoProfile','-Command',ps],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=0x08000000)


def split_for_natural_pauses(text):
    # Keep complete clauses together. Full stops/question marks get a longer pause;
    # semicolons and commas stay inside the neural utterance so prosody remains natural.
    chunks=[x.strip() for x in re.split(r'(?<=[.!?])\s+',text.strip()) if x.strip()]
    return chunks or [text]


def neural_speak(text, voice=VOICE_FEMALE, rate='-3%'):
    def worker():
        chunks=split_for_natural_pauses(text)
        if ensure_edge_tts():
            try:
                import asyncio, edge_tts
                for chunk in chunks:
                    path=os.path.join(tempfile.gettempdir(),f'ielts_tts_{uuid.uuid4().hex}.mp3')
                    async def make(c=chunk,p=path):
                        speech=edge_tts.Communicate(c,voice,rate=rate)
                        await speech.save(p)
                    asyncio.run(make())
                    play_mp3(path)
                    try: os.remove(path)
                    except Exception: pass
                    time.sleep(0.45)
                return
            except Exception:
                pass

        # Offline British-English fallback. Speak sentence by sentence with a pause.
        for chunk in chunks:
            safe=chunk.replace("'","''")
            ps=("Add-Type -AssemblyName System.Speech; $s=New-Object System.Speech.Synthesis.SpeechSynthesizer; "
                "$v=$s.GetInstalledVoices() | Where-Object {$_.VoiceInfo.Culture.Name -eq 'en-GB'} | Select-Object -First 1; "
                "if($v){$s.SelectVoice($v.VoiceInfo.Name)}; $s.Rate=-1; $s.Speak('"+safe+"')")
            subprocess.run(['powershell','-NoProfile','-Command',ps],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=0x08000000)
            time.sleep(0.45)
    threading.Thread(target=worker,daemon=True).start()


def speak(self,text):
    neural_speak(text,VOICE_FEMALE)

app.IELTSApp.speak_text=speak

if __name__=='__main__':
    app.IELTSApp().mainloop()
