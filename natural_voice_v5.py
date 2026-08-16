import os, subprocess, tempfile, threading
import task_engine_v4 as v4

app=v4.app

# Microsoft Edge neural voices. Requires internet and edge-tts package.
VOICE_FEMALE='en-GB-SoniaNeural'
VOICE_MALE='en-GB-RyanNeural'

def ensure_edge_tts():
    try:
        import edge_tts
        return True
    except Exception:
        return False

def play_mp3(path):
    # Windows Media Player COM is available on standard Windows installations.
    ps=f'''$p=New-Object -ComObject WMPlayer.OCX; $m=$p.newMedia("{path}"); $p.currentPlaylist.insertItem(0,$m); $p.controls.play(); while($p.playState -ne 1){{Start-Sleep -Milliseconds 200}}'''
    subprocess.run(['powershell','-NoProfile','-Command',ps],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=0x08000000)

def neural_speak(text, voice=VOICE_FEMALE, rate='+0%'):
    def worker():
        if ensure_edge_tts():
            try:
                import asyncio, edge_tts
                path=os.path.join(tempfile.gettempdir(),'ielts_neural_tts.mp3')
                async def make():
                    c=edge_tts.Communicate(text,voice,rate=rate); await c.save(path)
                asyncio.run(make()); play_mp3(path); return
            except Exception: pass
        # Offline fallback: select a British voice if Windows has one; otherwise default English.
        safe=text.replace("'","''")
        ps=("Add-Type -AssemblyName System.Speech; $s=New-Object System.Speech.Synthesis.SpeechSynthesizer; "
            "$v=$s.GetInstalledVoices() | Where-Object {$_.VoiceInfo.Culture.Name -eq 'en-GB'} | Select-Object -First 1; "
            "if($v){$s.SelectVoice($v.VoiceInfo.Name)}; $s.Rate=0; $s.Speak('"+safe+"')")
        subprocess.run(['powershell','-NoProfile','-Command',ps],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=0x08000000)
    threading.Thread(target=worker,daemon=True).start()

def speak(self,text): neural_speak(text,VOICE_FEMALE)

app.IELTSApp.speak_text=speak

if __name__=='__main__': app.IELTSApp().mainloop()
