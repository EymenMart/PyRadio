import tkinter as tk
from tkinter import ttk
import vlc
import json
import os
import sys

# This line finds the folder where the script is running, 
# no matter if the user is "Plus" or "VMUser"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FAV_FILE = os.path.join(SCRIPT_DIR, "pyradio_favs.json")

# --- DATABASE SETUP ---
FAV_FILE = "pyradio_favs.json"

def load_favorites():
    if os.path.exists(FAV_FILE):
        try:
            with open(FAV_FILE, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def save_favorites(favs):
    with open(FAV_FILE, "w") as f:
        json.dump(favs, f)

# --- STATION MASTER LIST ---
ALL_STATIONS = {
    # --- UKRAINE (UA) ---
    "🇺🇦 Hit FM (Kyiv)": "https://online.hitfm.ua/HitFM",
    "🇺🇦 Lviv Wave (News)": "http://onair.lviv.fm:8000/lviv.fm",
    "🇺🇦 Radio ROKS": "http://online.radioroks.ua/RadioROKS",
    "🇺🇦 Kiss FM (Dance)": "http://online.kissfm.ua/KissFM",
    "🇺🇦 Radio Bajraktar": "http://online.radiobayraktar.com.ua/RadioBayraktar",

    # --- POLAND (PL) ---
    "🇵🇱 RMF FM (Kraków)": "http://217.74.72.10:8000/rmf_fm",
    "🇵🇱 Radio ZET": "http://r.zetradio.pl/ZET",
    "🇵🇱 Eska Rock": "http://waw01-01.ic.smcdn.pl/2080-1.mp3",

    # --- GERMANY (DE) ---
    "🇩🇪 Antenne Bayern": "http://mp3channels.webradio.antenne.de/antenne",
    "🇩🇪 80s80s (Retro)": "http://80s80s.hoerradar.de/80s80s-80er-mp3-hq",
    "🇩🇪 TechnoBase.FM": "http://stream.technobase.fm/mp3/128",

    # --- TURKEY (TR) ---
    "🇹🇷 Kral Pop (Hits)": "http://46.20.7.125:80/;",
    "🇹🇷 Power FM": "http://powerfm.listenpowerapp.com/powerfm/mpeg/icecast.audio",
    "🇹🇷 Metro FM": "http://17733.live.streamtheworld.com/METRO_FM_SC",

    # --- INTERNATIONAL (EN) ---
    "🇬🇧 Classic 80s (UK)": "http://media-ice.musicradio.com/Heart80s",
    "🇬🇧 BBC World Service": "http://stream.live.vc.bbcmedia.co.uk/bbc_world_service",
    "🇺🇸 NPR News (USA)": "https://npr-ice.streamguys1.com/live.mp3",
    "🌑 Nightride (Synth)": "https://stream.nightride.fm/nightride.m4a"
}

class PyRadio:
    def __init__(self, root):
        self.root = root
        self.root.title("PyRadio V2.0")
        self.root.geometry("450x600")
        self.root.configure(bg="#0a0a0a")
        
        self.favorites = load_favorites()
        # The 'demux' fix is included here for your Ukrainian stations
        self.instance = vlc.Instance('--no-video', '--network-caching=10000', '--demux=avformat')
        self.player = self.instance.media_player_new()

        # UI: HEADER
        tk.Label(root, text="PyRadio", fg="#00ff41", bg="#0a0a0a", font=("Consolas", 28, "bold")).pack(pady=15)

        # UI: SEARCH SYSTEM
        search_frame = tk.Frame(root, bg="#0a0a0a")
        search_frame.pack(pady=5, fill="x", padx=20) # FIXED: px changed to padx
        
        tk.Label(search_frame, text="SEARCH:", fg="#666", bg="#0a0a0a", font=("Consolas", 10)).pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.update_list)
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var, bg="#1a1a1a", fg="#00ff41", insertbackground="white", borderwidth=0)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=5)

        # UI: STATION LISTBOX
        self.list_frame = tk.Frame(root, bg="#0a0a0a")
        self.list_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        self.station_list = tk.Listbox(self.list_frame, bg="#111", fg="#eee", font=("Consolas", 11), 
                                      selectbackground="#00ff41", selectforeground="#000", borderwidth=0, highlightthickness=0)
        self.station_list.pack(side="left", fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(self.list_frame)
        scrollbar.pack(side="right", fill="y")
        self.station_list.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.station_list.yview)

        # UI: CONTROLS
        ctrl_frame = tk.Frame(root, bg="#0a0a0a")
        ctrl_frame.pack(pady=10)
        
        tk.Button(ctrl_frame, text="[ PLAY ]", command=self.play_logic, bg="#1a1a1a", fg="#00ff41", font=("Consolas", 10, "bold"), width=12).grid(row=0, column=0, padx=5)
        tk.Button(ctrl_frame, text="[ STOP ]", command=self.stop_logic, bg="#1a1a1a", fg="#ff3131", font=("Consolas", 10, "bold"), width=12).grid(row=0, column=1, padx=5)
        tk.Button(ctrl_frame, text="[ ⭐ FAV ]", command=self.toggle_favorite, bg="#1a1a1a", fg="#ffaa00", font=("Consolas", 10, "bold"), width=12).grid(row=0, column=2, padx=5)

        # UI: ERROR/STATUS DISPLAY
        self.status = tk.Label(root, text="STATUS: IDLE", fg="#444", bg="#0a0a0a", font=("Consolas", 10))
        self.status.pack(pady=10)

        self.update_list()

    def update_list(self, *args):
        search_term = self.search_var.get().lower()
        self.station_list.delete(0, tk.END)
        
        # 1. Show matching favorites at the top
        for name in self.favorites:
            if search_term in name.lower():
                self.station_list.insert(tk.END, f"⭐ {name}")
        
        # 2. Show the rest of the matching stations
        for name in ALL_STATIONS:
            if name not in self.favorites and search_term in name.lower():
                self.station_list.insert(tk.END, name)

    def play_logic(self):
        try:
            selection = self.station_list.curselection()
            if not selection:
                self.status.config(text="ERROR: SELECT A STATION", fg="#ffaa00")
                return

            selection_text = self.station_list.get(selection[0])
            name = selection_text.replace("⭐ ", "")
            url = ALL_STATIONS[name]
            
            self.player.stop()
            self.status.config(text="CONNECTING...", fg="#ffff00")
            
            media = self.instance.media_new(url)
            self.player.set_media(media)
            self.player.play()
            
            # Check for actual audio connection after 2 seconds
            self.root.after(2000, self.check_status)
            
        except Exception as e:
            self.status.config(text=f"ERROR: {str(e)[:20]}", fg="#ff3131")

    def check_status(self):
        state = self.player.get_state()
        if state == vlc.State.Error:
            self.status.config(text="ERROR: CHANNEL UNAVAILABLE", fg="#ff3131")
        elif state == vlc.State.Playing:
            self.status.config(text="STATUS: ONLINE", fg="#00ff41")
        else:
            # If it's still buffering or opening
            self.status.config(text="STATUS: SYNCING...", fg="#ffff00")

    def toggle_favorite(self):
        selection = self.station_list.curselection()
        if not selection: return
        
        selection_text = self.station_list.get(selection[0])
        name = selection_text.replace("⭐ ", "")
        
        if name in self.favorites:
            self.favorites.remove(name)
        else:
            self.favorites.append(name)
            
        save_favorites(self.favorites)
        self.update_list()

    def stop_logic(self):
        self.player.stop()
        self.status.config(text="STATUS: DISCONNECTED", fg="#ff3131")

if __name__ == "__main__":
    root = tk.Tk()
    app = PyRadio(root)
    root.mainloop()