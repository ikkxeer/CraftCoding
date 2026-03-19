import customtkinter as ctk
import pygetwindow as gw
import pyautogui
import time
import sqlite3
import os
import datetime
import random
from tkinter import messagebox, filedialog

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
    PILLOW_OK = True
except ImportError:
    PILLOW_OK = False

try:
    import psutil
    PSUTIL_OK = True
except ImportError:
    PSUTIL_OK = False

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, "craftcoding.db")
IMG_DIR  = os.path.join(BASE_DIR, "img")

# Rutas de medallas
MEDAL_PATHS = {
    "pure":   os.path.join(IMG_DIR, "artisancoder.png"),
    "hybrid": os.path.join(IMG_DIR, "hybridprogramer.png"),
    "failed": os.path.join(IMG_DIR, "vibecoder.png"),
}

IA_PROCESSES = [
    "cursor.exe", "cursor", "copilot", "codeium",
    "tabnine", "ghostwriter", "continue", "supermaven",
    "windsurf.exe", "windsurf",
]

IA_WINDOW_KEYWORDS = [
    "chatgpt", "claude", "deepseek", "perplexity",
    "gemini", "copilot", "cursor", "bard", "phind",
    "codeium", "blackbox", "you.com", "grok", "mistral",
    "openai", "anthropic", "huggingface", "poe.com",
]

IA_DOMAINS = [
    "chat.openai.com", "chatgpt.com", "claude.ai",
    "gemini.google.com", "deepseek.com", "perplexity.ai",
    "copilot.microsoft.com", "bing.com/chat", "phind.com",
    "you.com", "blackbox.ai", "codeium.com", "mistral.ai",
    "grok.com", "poe.com", "huggingface.co/chat", "aistudio.google.com",
]

# ── DB ─────────────────────────────────────────────────────────────────────────
def init_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS proyectos (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre          TEXT UNIQUE,
            tiempo_segundos INTEGER DEFAULT 0,
            score           INTEGER DEFAULT 100,
            estado          TEXT DEFAULT 'En curso',
            infracciones    INTEGER DEFAULT 0,
            fecha_inicio    TEXT,
            fecha_fin       TEXT,
            sello           TEXT DEFAULT 'Pure Coder'
        )''')
        existing = {row[1] for row in c.execute("PRAGMA table_info(proyectos)")}
        for col, td in {"infracciones":"INTEGER DEFAULT 0","fecha_inicio":"TEXT",
                        "fecha_fin":"TEXT","sello":"TEXT DEFAULT 'Pure Coder'"}.items():
            if col not in existing:
                c.execute(f"ALTER TABLE proyectos ADD COLUMN {col} {td}")
        conn.commit(); conn.close()
    except Exception as e:
        messagebox.showerror("Error DB", str(e))

def db_get_all():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT nombre,tiempo_segundos,score,estado,infracciones,sello,fecha_inicio FROM proyectos ORDER BY id DESC")
    rows = c.fetchall(); conn.close(); return rows

def db_delete(nombre):
    conn = sqlite3.connect(DB_PATH)
    conn.cursor().execute("DELETE FROM proyectos WHERE nombre=?", (nombre,))
    conn.commit(); conn.close()

# ── FUENTES ────────────────────────────────────────────────────────────────────
def _font(size, bold=False):
    from PIL import ImageFont
    paths = (["C:/Windows/Fonts/consolab.ttf","C:/Windows/Fonts/arialbd.ttf",
               "C:/Windows/Fonts/calibrib.ttf",
               "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
             if bold else
             ["C:/Windows/Fonts/consola.ttf","C:/Windows/Fonts/arial.ttf",
              "C:/Windows/Fonts/calibri.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"])
    for fp in paths:
        try: return ImageFont.truetype(fp, size)
        except: continue
    try: return ImageFont.load_default(size=size)
    except: return ImageFont.load_default()

# ── CERTIFICADO PNG ────────────────────────────────────────────────────────────
def generate_certificate(project_name, hours, minutes, seconds,
                          score, infractions, seal_type, save_path):
    W, H = 1600, 820
    img  = Image.new("RGB", (W, H), (7, 7, 10))
    draw = ImageDraw.Draw(img)

    P = {
        "pure":   dict(hi=(255,220,80), mid=(212,175,55), lo=(90,68,10),
                       bg=(14,11,2), label="ARTISAN CODER",
                       sub="100% Human Logic  ·  Zero AI Assistance Detected"),
        "hybrid": dict(hi=(140,210,255), mid=(80,160,230), lo=(28,72,128),
                       bg=(3,10,22), label="HYBRID CODER",
                       sub="Partially Assisted  ·  AI Hints Were Used"),
        "failed": dict(hi=(255,100,100), mid=(200,55,55), lo=(80,15,15),
                       bg=(16,3,3), label="VIBE CODER",
                       sub="AI Assistance Detected  ·  Certificate Denied"),
    }
    p = P.get(seal_type, P["hybrid"])
    hi, mid, lo = p["hi"], p["mid"], p["lo"]

    # Ruido de fondo
    rng = random.Random(42)
    for _ in range(2500):
        x,y = rng.randint(0,W), rng.randint(0,H)
        v = rng.randint(14,30)
        draw.point((x,y), fill=(v,v,v))
    for y in range(0, H, 5):
        draw.line([(0,y),(W,y)], fill=(0,0,0,35), width=1)

    # Franja lateral
    draw.rectangle([0,0,10,H], fill=mid)
    for i in range(50):
        a = int(160*(1-i/50))
        r,g,b = mid
        draw.rectangle([10,0,10+i,H], fill=(r,g,b,a))

    # Marco doble
    draw.rounded_rectangle([16,16,W-16,H-16], radius=18, outline=lo, width=1)
    draw.rounded_rectangle([22,22,W-22,H-22], radius=16, outline=mid, width=1)

    PAD = 58
    # Cabecera
    draw.text((PAD,44), "CRAFT", fill=hi, font=_font(20,True))
    draw.text((PAD+74,44), "CODING", fill=(80,80,86), font=_font(20,True))
    draw.text((PAD+186,51), "·  Certificate of Authorship", fill=(48,48,54), font=_font(13))
    now = datetime.datetime.now().strftime("%d %b %Y  ·  %H:%M")
    draw.text((W-PAD,51), now, fill=(52,52,58), font=_font(13), anchor="rm")

    # Barra score bajo cabecera
    draw.rectangle([PAD,88,W-PAD,89], fill=(20,20,26))
    draw.rectangle([PAD,88,PAD+int((W-PAD*2)*score/100),89], fill=lo)

    # Nombre proyecto
    name_d = project_name.upper()[:22]
    draw.text((PAD,118), name_d, fill=(222,222,228), font=_font(68,True))
    draw.rounded_rectangle([PAD,200,PAD+210,220], radius=4, fill=(18,18,24))
    draw.text((PAD+10,203), "VERIFIED BUILD  ·  CRAFTCODING", fill=(52,52,60), font=_font(10))

    # 4 tarjetas stats
    CY,CH,GAP = 234,110,14
    CW = (W-PAD*2-GAP*3)//4
    for i,(lbl,val,unit) in enumerate([
        ("TIME INVESTED", f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}", "hh : mm : ss"),
        ("HUMAN SCORE",   str(score),  "points out of 100"),
        ("AI DETECTIONS", str(infractions), "total events"),
        ("CERTIFICATE",   seal_type.upper(), "issued by craftcoding"),
    ]):
        cx = PAD + i*(CW+GAP)
        draw.rounded_rectangle([cx,CY,cx+CW,CY+CH], radius=10,
                                fill=(10,10,15), outline=(26,26,34), width=1)
        draw.rounded_rectangle([cx,CY,cx+CW,CY+3], radius=2, fill=lo)
        draw.text((cx+13,CY+13), lbl, fill=(55,55,64), font=_font(10))
        draw.text((cx+13,CY+32), val, fill=hi, font=_font(32,True))
        draw.text((cx+13,CY+78), unit, fill=(40,40,48), font=_font(10))

    # Separador
    SEP = CY+CH+24
    draw.rectangle([PAD,SEP,W-PAD,SEP+1], fill=(18,18,24))

    # Badge principal
    BY = SEP+20
    BH = H-BY-50
    BX,BW = PAD, W-PAD*2
    draw.rounded_rectangle([BX,BY,BX+BW,BY+BH], radius=14,
                            fill=p["bg"], outline=mid, width=2)
    draw.rectangle([BX+2,BY+2,BX+BW-2,BY+4], fill=lo)

    # ── Medalla PNG ───────────────────────────────────────────────────────────
    medal_path = MEDAL_PATHS.get(seal_type)
    MEDAL_SIZE = BH - 24
    medal_placed = False

    if PILLOW_OK and medal_path and os.path.exists(medal_path):
        try:
            medal = Image.open(medal_path).convert("RGBA")
            # Redimensionar manteniendo proporción
            medal.thumbnail((MEDAL_SIZE, MEDAL_SIZE), Image.LANCZOS)
            mw, mh = medal.size
            mx = BX + 20
            my = BY + (BH - mh) // 2
            # Pegar con transparencia
            img.paste(medal, (mx, my), medal)
            medal_placed = True
            text_x = BX + 20 + mw + 28
        except Exception:
            medal_placed = False

    if not medal_placed:
        # Fallback: círculo con símbolo
        syms = {"pure":"✓","hybrid":"~","failed":"✗"}
        CCX = BX+110; CCY = BY+BH//2; CR=52
        draw.ellipse([CCX-CR+5,CCY-CR+5,CCX+CR+5,CCY+CR+5], fill=(0,0,0))
        draw.ellipse([CCX-CR,CCY-CR,CCX+CR,CCY+CR], fill=lo, outline=mid, width=3)
        draw.ellipse([CCX-CR+10,CCY-CR+10,CCX+CR-10,CCY+CR-10], outline=hi, width=1)
        sym=syms.get(seal_type,"?"); sf=_font(40,True)
        bb=draw.textbbox((0,0),sym,font=sf)
        draw.text((CCX-(bb[2]-bb[0])//2,CCY-(bb[3]-bb[1])//2-3),sym,fill=hi,font=sf)
        text_x = BX+196

    # Texto del sello
    TY_center = BY + BH//2
    draw.text((text_x, TY_center-40), p["label"], fill=hi, font=_font(44,True))
    draw.text((text_x, TY_center+16), p["sub"],   fill=(80,80,88), font=_font(15))

    # Score ring derecha
    RX=BX+BW-130; RY=BY+BH//2; RR=46
    draw.ellipse([RX-RR,RY-RR,RX+RR,RY+RR], outline=(22,22,28), width=7)
    if score>0:
        fh=int(RR*1.8*score/100)
        draw.rounded_rectangle([RX-RR+13,RY+RR-fh-5,RX+RR-13,RY+RR-5], radius=4, fill=lo)
    draw.text((RX,RY-9),f"{score}%",fill=hi,font=_font(19,True),anchor="mm")
    draw.text((RX,RY+13),"SCORE",fill=(50,50,58),font=_font(9),anchor="mm")

    # Pie
    FY=BY+BH+16
    uid=abs(hash(project_name+now))%999999
    draw.text((PAD,FY),"Verified by CraftCoding  ·  Pure Logic Tool  ·  craftcoding.app",
              fill=(32,32,38),font=_font(11))
    draw.text((W-PAD,FY),f"ID: CC-{uid:06d}",fill=(32,32,38),font=_font(11),anchor="rm")

    img.filter(ImageFilter.SMOOTH).save(save_path,"PNG",dpi=(150,150))
    return save_path


# ── VENTANA LISTA DE PROYECTOS ─────────────────────────────────────────────────
class ProjectListWindow(ctk.CTkToplevel):
    ESTADO_C = {"En curso":"#F39C12","Certificado":"#2ECC71","Pausado":"#7F8C8D"}
    SELLO_C  = {"PURE":"#D4AF37","HYBRID":"#5BA8E5","VIBE":"#C0392B",
                "PURE CODER":"#D4AF37","HYBRID CODER":"#5BA8E5","VIBE CODER":"#C0392B"}

    def __init__(self, parent, on_open):
        super().__init__(parent)
        self.title("CraftCoding — Mis Proyectos")
        self.geometry("900x620")
        self.resizable(True,True)
        self.grab_set()
        self.on_open = on_open
        self._build(); self._load()

    def _build(self):
        self.grid_columnconfigure(0,weight=1)
        self.grid_rowconfigure(1,weight=1)

        # Cabecera
        hdr = ctk.CTkFrame(self,fg_color="#0d0d0d",corner_radius=0,height=64)
        hdr.grid(row=0,column=0,sticky="ew"); hdr.grid_propagate(False)
        hdr.grid_columnconfigure(1,weight=1)

        ctk.CTkLabel(hdr,text="⚒️  MIS PROYECTOS",
                     font=ctk.CTkFont(size=18,weight="bold"),
                     text_color="#D4AF37").grid(row=0,column=0,padx=24,pady=18)

        self.q = ctk.StringVar()
        self.q.trace_add("write", lambda *_: self._load())
        ctk.CTkEntry(hdr,placeholder_text="🔍  Buscar…",textvariable=self.q,
                     width=220,height=34).grid(row=0,column=1,padx=10)

        # Filtro por estado
        self.filter_var = ctk.StringVar(value="Todos")
        ctk.CTkSegmentedButton(hdr,values=["Todos","En curso","Certificado"],
                               variable=self.filter_var,width=240,
                               command=lambda _: self._load()
                               ).grid(row=0,column=2,padx=10)

        ctk.CTkButton(hdr,text="↺",command=self._load,width=38,height=34,
                      fg_color="#1a1a1a",hover_color="#2a2a2a",
                      font=ctk.CTkFont(size=14)).grid(row=0,column=3,padx=(0,16))

        self.scroll = ctk.CTkScrollableFrame(self,fg_color="transparent",label_text="")
        self.scroll.grid(row=1,column=0,sticky="nsew",padx=14,pady=(6,0))
        self.scroll.grid_columnconfigure(0,weight=1)

        foot = ctk.CTkFrame(self,fg_color="#0d0d0d",corner_radius=0,height=40)
        foot.grid(row=2,column=0,sticky="ew")
        self.count_lbl = ctk.CTkLabel(foot,text="",font=ctk.CTkFont(size=11),text_color="#555")
        self.count_lbl.pack(side="left",padx=20,pady=10)

    def _fmt(self, s):
        h,r=divmod(s or 0,3600); m,s=divmod(r,60)
        return f"{h:02}:{m:02}:{s:02}"

    def _load(self):
        for w in self.scroll.winfo_children(): w.destroy()
        q  = self.q.get().strip().lower()
        fv = self.filter_var.get()
        rows = db_get_all()
        if q:   rows=[r for r in rows if q in (r[0] or "").lower()]
        if fv != "Todos": rows=[r for r in rows if (r[3] or "")==fv]

        if not rows:
            ctk.CTkLabel(self.scroll,
                text="No hay proyectos.\nCrea uno desde la pantalla principal.",
                font=ctk.CTkFont(size=14),text_color="#3a3a3a").pack(pady=80)
            self.count_lbl.configure(text="0 proyectos"); return

        for i,row in enumerate(rows):
            self._card(i,*row)
        n=len(rows)
        self.count_lbl.configure(text=f"{n} proyecto{'s' if n!=1 else ''}")

    def _card(self, idx, nombre, secs, score, estado, infrac, sello, fecha):
        score=score or 100; infrac=infrac or 0
        estado=estado or "En curso"; sello=sello or ""

        card=ctk.CTkFrame(self.scroll,fg_color="#111116",corner_radius=12,
                          border_width=1,border_color="#222228")
        card.grid(row=idx,column=0,sticky="ew",pady=(0,8))
        card.grid_columnconfigure(1,weight=1)

        # Barra lateral de color
        ec=self.ESTADO_C.get(estado,"#555")
        bar=ctk.CTkFrame(card,width=5,corner_radius=0,fg_color=ec)
        bar.grid(row=0,column=0,rowspan=2,sticky="ns",padx=(0,12),pady=0)
        bar.grid_propagate(False)

        # Fila superior: nombre + badges
        top=ctk.CTkFrame(card,fg_color="transparent")
        top.grid(row=0,column=1,sticky="ew",padx=(0,14),pady=(12,2))
        top.grid_columnconfigure(0,weight=1)

        ctk.CTkLabel(top,text=nombre,font=ctk.CTkFont(size=15,weight="bold"),
                     text_color="#E0E0E0",anchor="w").grid(row=0,column=0,sticky="w")

        # Badge estado
        ctk.CTkLabel(top,text=f"  {estado}  ",font=ctk.CTkFont(size=10),
                     text_color=ec,fg_color="#1a1a1f",corner_radius=4
                     ).grid(row=0,column=1,padx=(8,0))

        # Badge sello
        if sello:
            sc=self.SELLO_C.get(sello.upper(),"#555")
            ctk.CTkLabel(top,text=f"  {sello}  ",font=ctk.CTkFont(size=10,weight="bold"),
                         text_color=sc,fg_color="#16161c",corner_radius=4
                         ).grid(row=0,column=2,padx=(6,0))

        # Fila inferior: stats
        bot=ctk.CTkFrame(card,fg_color="transparent")
        bot.grid(row=1,column=1,sticky="ew",padx=(0,14),pady=(2,12))
        for col,(icon,val) in enumerate([
            ("⏱",self._fmt(secs)),("🧠",f"{score}%"),
            ("⚠",f"{infrac} detect."),("📅",fecha or "—")
        ]):
            ctk.CTkLabel(bot,text=f"{icon}  {val}",font=ctk.CTkFont(size=11),
                         text_color="#5a5a64").grid(row=0,column=col,padx=(0,24))

        # Botones
        btns=ctk.CTkFrame(card,fg_color="transparent")
        btns.grid(row=0,column=2,rowspan=2,padx=(0,14),pady=12)

        if estado != "Certificado":
            ctk.CTkButton(btns,text="▶  Abrir",width=96,height=28,
                          command=lambda n=nombre:self._open(n),
                          fg_color="#1a4a7a",hover_color="#0d3560",
                          font=ctk.CTkFont(size=11)).pack(pady=(0,5))

        ctk.CTkButton(btns,text="🗑",width=96,height=28,
                      command=lambda n=nombre:self._delete(n),
                      fg_color="#2a0a0a",hover_color="#4a1414",
                      font=ctk.CTkFont(size=11)).pack()

    def _open(self, n): self.destroy(); self.on_open(n)

    def _delete(self, n):
        if messagebox.askyesno("Borrar",f"¿Borrar «{n}» permanentemente?"):
            db_delete(n); self._load()


# ── APP PRINCIPAL ──────────────────────────────────────────────────────────────
class CraftCodingApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        init_db()
        self.title("CraftCoding — Pure Logic")
        self.geometry("1040x800")
        self.minsize(900, 700)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.is_running      = False
        self.seconds_elapsed = 0
        self.project_sealed  = False
        self.infractions     = 0
        self.is_alert_active = False
        self.last_detection  = ""
        self.hint_used       = False
        self._session_start  = None   # para calcular tiempo de sesión actual

        self._build_ui()
        self._pulse()   # animación sutil del timer cuando está corriendo

    # ── UI ─────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ── SIDEBAR ──────────────────────────────────────────────────────────
        sb = ctk.CTkFrame(self, width=240, fg_color="#0a0a0d", corner_radius=0)
        sb.grid(row=0, column=0, sticky="nsew")
        sb.grid_propagate(False)
        sb.grid_rowconfigure(8, weight=1)

        ctk.CTkLabel(sb, text="⚒️", font=ctk.CTkFont(size=36)).grid(
            row=0, column=0, pady=(32,4))
        ctk.CTkLabel(sb, text="CRAFTCODING",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color="#D4AF37").grid(row=1, column=0, pady=(0,2))
        ctk.CTkLabel(sb, text="PURE LOGIC TRACKER",
                     font=ctk.CTkFont(size=9), text_color="#333").grid(row=2, column=0)

        ctk.CTkFrame(sb, height=1, fg_color="#1e1e1e").grid(
            row=3, column=0, sticky="ew", padx=16, pady=18)

        # Score con barra de progreso visual
        score_frame = ctk.CTkFrame(sb, fg_color="#111116", corner_radius=10)
        score_frame.grid(row=4, column=0, padx=14, pady=(0,8), sticky="ew")

        ctk.CTkLabel(score_frame, text="HUMAN SCORE",
                     font=ctk.CTkFont(size=10), text_color="#555").pack(pady=(10,2))
        self.score_label = ctk.CTkLabel(score_frame, text="100%",
                     font=ctk.CTkFont(size=28, weight="bold"), text_color="#2ECC71")
        self.score_label.pack()
        self.score_bar = ctk.CTkProgressBar(score_frame, width=180, height=6,
                                             progress_color="#2ECC71",
                                             fg_color="#1a1a22")
        self.score_bar.set(1.0)
        self.score_bar.pack(pady=(4,10))

        # Detecciones
        det_frame = ctk.CTkFrame(sb, fg_color="#111116", corner_radius=10)
        det_frame.grid(row=5, column=0, padx=14, pady=(0,8), sticky="ew")

        ctk.CTkLabel(det_frame, text="DETECCIONES IA",
                     font=ctk.CTkFont(size=10), text_color="#555").pack(pady=(10,2))
        self.infractions_label = ctk.CTkLabel(det_frame, text="0",
                     font=ctk.CTkFont(size=28, weight="bold"), text_color="#888")
        self.infractions_label.pack(pady=(0,10))

        ctk.CTkFrame(sb, height=1, fg_color="#1e1e1e").grid(
            row=6, column=0, sticky="ew", padx=16, pady=8)

        # Status dots
        status_frame = ctk.CTkFrame(sb, fg_color="transparent")
        status_frame.grid(row=7, column=0, padx=14, pady=4, sticky="ew")
        for txt, ok in [("Proceso-monitor (psutil)", PSUTIL_OK),
                        ("Certificados PNG (Pillow)", PILLOW_OK),
                        ("Medallas /img", os.path.isdir(IMG_DIR))]:
            color = "#2ECC71" if ok else "#E74C3C"
            ctk.CTkLabel(status_frame, text=f"{'●' if ok else '○'}  {txt}",
                         font=ctk.CTkFont(size=10), text_color=color,
                         anchor="w").pack(anchor="w", pady=1)

        # Spacer
        ctk.CTkFrame(sb, fg_color="transparent").grid(row=8, column=0, sticky="nsew")

        # Botón proyectos (abajo del sidebar)
        ctk.CTkFrame(sb, height=1, fg_color="#1e1e1e").grid(
            row=9, column=0, sticky="ew", padx=16, pady=8)
        ctk.CTkButton(sb, text="📂  Mis Proyectos",
                      command=self.open_project_list,
                      fg_color="#161620", hover_color="#22223a",
                      border_width=1, border_color="#2a2a3a",
                      font=ctk.CTkFont(size=12), width=200, height=36
                      ).grid(row=10, column=0, padx=14, pady=(0,24))

        # ── MAIN ─────────────────────────────────────────────────────────────
        mf = ctk.CTkFrame(self, fg_color="transparent")
        mf.grid(row=0, column=1, padx=(30,40), pady=30, sticky="nsew")
        mf.grid_columnconfigure(0, weight=1)
        mf.grid_rowconfigure(3, weight=1)

        # Proyecto entry + seal en una fila
        top_row = ctk.CTkFrame(mf, fg_color="transparent")
        top_row.grid(row=0, column=0, sticky="ew", pady=(0,16))
        top_row.grid_columnconfigure(0, weight=1)

        self.project_entry = ctk.CTkEntry(
            top_row, placeholder_text="✏️  Nombre del proyecto…",
            height=46, font=ctk.CTkFont(size=15))
        self.project_entry.grid(row=0, column=0, sticky="ew", padx=(0,10))
        self.project_entry.bind("<Return>", lambda e: self.seal_project())

        self.seal_button = ctk.CTkButton(
            top_row, text="SELLAR", command=self.seal_project,
            fg_color="#2E7D32", hover_color="#1B5E20",
            width=90, height=46, font=ctk.CTkFont(size=13, weight="bold"))
        self.seal_button.grid(row=0, column=1)

        # Panel de estado del proyecto (visible cuando está sellado)
        self.status_panel = ctk.CTkFrame(mf, fg_color="#0e0e14",
                                          corner_radius=10, border_width=1,
                                          border_color="#1e1e2a")
        self.status_panel.grid(row=1, column=0, sticky="ew", pady=(0,10))
        self.status_panel.grid_columnconfigure(0, weight=1)
        self.status_panel.grid_remove()  # oculto hasta sellar

        self.status_project_lbl = ctk.CTkLabel(
            self.status_panel, text="",
            font=ctk.CTkFont(size=13, weight="bold"), text_color="#D4AF37")
        self.status_project_lbl.grid(row=0, column=0, padx=18, pady=(10,2), sticky="w")
        self.status_info_lbl = ctk.CTkLabel(
            self.status_panel, text="",
            font=ctk.CTkFont(size=11), text_color="#555")
        self.status_info_lbl.grid(row=1, column=0, padx=18, pady=(0,10), sticky="w")

        # Modo switch + label explicativo
        mode_row = ctk.CTkFrame(mf, fg_color="transparent")
        mode_row.grid(row=2, column=0, sticky="ew", pady=(0,8))

        ctk.CTkLabel(mode_row, text="MODO  ",
                     font=ctk.CTkFont(size=11), text_color="#444").pack(side="left")
        self.mode_var = ctk.StringVar(value="Amable")
        ctk.CTkSegmentedButton(mode_row, values=["Amable","Estricto"],
                               variable=self.mode_var, width=220,
                               command=self._on_mode_change).pack(side="left")
        self.mode_hint = ctk.CTkLabel(mode_row, text="  Solo avisos",
                                       font=ctk.CTkFont(size=11), text_color="#444")
        self.mode_hint.pack(side="left")

        # Timer grande — centro
        timer_frame = ctk.CTkFrame(mf, fg_color="transparent")
        timer_frame.grid(row=3, column=0)

        self.timer_label = ctk.CTkLabel(
            timer_frame, text="00:00:00",
            font=ctk.CTkFont(family="Consolas", size=100, weight="bold"),
            text_color="#1e1e26")
        self.timer_label.pack()

        self.session_lbl = ctk.CTkLabel(
            timer_frame, text="",
            font=ctk.CTkFont(size=11), text_color="#333")
        self.session_lbl.pack()

        # Botones acción
        btn_row = ctk.CTkFrame(mf, fg_color="transparent")
        btn_row.grid(row=4, column=0, pady=(8,0))

        self.action_button = ctk.CTkButton(
            btn_row, text="▶  INICIAR FORJA", command=self.toggle_session,
            width=240, height=58, state="disabled",
            fg_color="#111118", border_width=1, border_color="#2a2a3a",
            font=ctk.CTkFont(size=15, weight="bold"))
        self.action_button.pack(side="left", padx=(0,10))

        self.finish_button = ctk.CTkButton(
            btn_row, text="🏆  CERTIFICAR",
            command=self.finish_project,
            state="disabled", width=160, height=58,
            fg_color="#111118", border_width=1, border_color="#2a3a2a",
            font=ctk.CTkFont(size=13))
        self.finish_button.pack(side="left")

        # Panel modo emergencia (más compacto)
        emg = ctk.CTkFrame(mf, fg_color="#100808", corner_radius=10,
                           border_width=1, border_color="#2a1414")
        emg.grid(row=5, column=0, sticky="ew", pady=(16,0))
        emg.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(emg, text="🆘  MODO EMERGENCIA",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color="#5a3030").grid(row=0, column=0, sticky="w",
                     padx=16, pady=(10,0))
        ctk.CTkLabel(emg, text="Pedir pista → sello HYBRID CODER  −10 pts de score",
                     font=ctk.CTkFont(size=10), text_color="#3a2020"
                     ).grid(row=1, column=0, sticky="w", padx=16)
        self.hint_button = ctk.CTkButton(
            emg, text="PEDIR PISTA  (−10 pts)",
            command=self.use_hint, state="disabled",
            fg_color="#3a1000", hover_color="#5a1800",
            font=ctk.CTkFont(size=11), height=30, width=200)
        self.hint_button.grid(row=0, column=1, rowspan=2, padx=16, pady=8)

    # ── PULSE ──────────────────────────────────────────────────────────────────
    def _pulse(self):
        """Parpadeo sutil del timer cuando está corriendo."""
        if self.is_running:
            current = self.timer_label.cget("text_color")
            self.timer_label.configure(
                text_color="#FFFFFF" if current != "#FFFFFF" else "#d0d0d0")
        self.after(800, self._pulse)

    def _on_mode_change(self, val):
        self.mode_hint.configure(
            text="  Redirige a StackOverflow" if val == "Estricto" else "  Solo avisos")

    # ── LISTA DE PROYECTOS ────────────────────────────────────────────────────
    def open_project_list(self):
        ProjectListWindow(self, on_open=self._load_from_list)

    def _load_from_list(self, nombre):
        if self.project_sealed:
            self.save_progress()
            self.project_sealed = False
        self.is_running=False; self.seconds_elapsed=0
        self.infractions=0; self.hint_used=False
        self._set_score(100)
        self.infractions_label.configure(text="0")
        self.project_entry.configure(state="normal")
        self.project_entry.delete(0,"end")
        self.project_entry.insert(0, nombre)
        self.seal_project()

    # ── SCORE ─────────────────────────────────────────────────────────────────
    def _get_score(self):
        try:  return int(self.score_label.cget("text").replace("%",""))
        except: return 100

    def _set_score(self, val):
        val = max(0, min(100, val))
        if val > 70:   color, bc = "#2ECC71", "#2ECC71"
        elif val > 40: color, bc = "#F39C12", "#F39C12"
        else:          color, bc = "#E74C3C", "#E74C3C"
        self.score_label.configure(text=f"{val}%", text_color=color)
        self.score_bar.configure(progress_color=bc)
        self.score_bar.set(val/100)

    def update_timer_display(self):
        h,r=divmod(self.seconds_elapsed,3600); m,s=divmod(r,60)
        self.timer_label.configure(text=f"{h:02}:{m:02}:{s:02}")

    def _update_status_panel(self):
        name = self.project_entry.get().strip()
        score = self._get_score()
        if self.project_sealed and name:
            self.status_panel.grid()
            self.status_project_lbl.configure(text=f"⚒  {name}")
            mode = self.mode_var.get()
            seal_preview = "ARTISAN CODER" if self.infractions==0 and score>=90 else \
                           "HYBRID CODER" if score>=50 else "VIBE CODER"
            self.status_info_lbl.configure(
                text=f"Sello proyectado: {seal_preview}  ·  Modo: {mode}  ·  Score: {score}%")
        else:
            self.status_panel.grid_remove()

    # ── DB ────────────────────────────────────────────────────────────────────
    def save_progress(self):
        name = self.project_entry.get().strip()
        if not name: return
        try:
            conn=sqlite3.connect(DB_PATH); c=conn.cursor()
            c.execute("""INSERT INTO proyectos
                (nombre,tiempo_segundos,score,estado,infracciones,fecha_inicio)
                VALUES(?,?,?,'En curso',?,?)
                ON CONFLICT(nombre) DO UPDATE SET
                tiempo_segundos=excluded.tiempo_segundos,
                score=excluded.score,infracciones=excluded.infracciones""",
                (name,self.seconds_elapsed,self._get_score(),self.infractions,
                 datetime.datetime.now().strftime("%Y-%m-%d")))
            conn.commit(); conn.close()
        except Exception as e: print(f"Error guardando: {e}")

    def load_project_data(self, name):
        try:
            conn=sqlite3.connect(DB_PATH); c=conn.cursor()
            c.execute("SELECT tiempo_segundos,score,infracciones FROM proyectos WHERE nombre=?",(name,))
            row=c.fetchone(); conn.close()
            if row:
                self.seconds_elapsed=row[0] or 0
                self._set_score(row[1] or 100)
                self.infractions=row[2] or 0
                self.infractions_label.configure(text=str(self.infractions))
                self.update_timer_display()
        except Exception as e: print(f"Error cargando: {e}")

    # ── CONTROL ───────────────────────────────────────────────────────────────
    def seal_project(self):
        name = self.project_entry.get().strip()
        if not name: return
        self.project_sealed = not self.project_sealed
        if self.project_sealed:
            self.load_project_data(name)
            self.project_entry.configure(state="disabled")
            self.action_button.configure(state="normal",
                fg_color="#0d1f35", border_color="#1F6AA5")
            self.timer_label.configure(text_color="#2a2a40")
            self.seal_button.configure(text="ABRIR", fg_color="#5a0d0d",
                                       hover_color="#7a1111")
            self._update_status_panel()
        else:
            self.save_progress(); self.is_running=False
            self.project_entry.configure(state="normal")
            self.action_button.configure(state="disabled",
                fg_color="#111118", border_color="#2a2a3a",
                text="▶  INICIAR FORJA", text_color="white")
            self.timer_label.configure(text_color="#1e1e26")
            self.finish_button.configure(state="disabled",
                fg_color="#111118", border_color="#2a3a2a")
            self.hint_button.configure(state="disabled")
            self.seal_button.configure(text="SELLAR", fg_color="#2E7D32",
                                       hover_color="#1B5E20")
            self.session_lbl.configure(text="")
            self.status_panel.grid_remove()

    def toggle_session(self):
        if not self.is_running:
            self.is_running=True
            self._session_start=datetime.datetime.now()
            self.action_button.configure(text="⏸  PAUSAR",
                fg_color="#3a2800", border_color="#c8960c", text_color="#c8960c")
            self.finish_button.configure(state="normal",
                border_color="#2a5a2a", text_color="#2ECC71")
            self.hint_button.configure(state="normal")
            self.run_engine()
        else:
            self.is_running=False; self.save_progress()
            self.action_button.configure(text="▶  CONTINUAR",
                fg_color="#0d1f35", border_color="#1F6AA5", text_color="white")
            self.session_lbl.configure(text="Sesión pausada — progreso guardado")

    # ── MOTOR ─────────────────────────────────────────────────────────────────
    def run_engine(self):
        if not self.is_running: return
        if not self.is_alert_active:
            det = self._scan_for_ai()
            if det: self.show_toast(det)
        self.seconds_elapsed += 1
        self.update_timer_display()
        # Actualizar label de sesión cada minuto
        if self._session_start and self.seconds_elapsed % 60 == 0:
            elapsed = int((datetime.datetime.now()-self._session_start).total_seconds())
            m,s=divmod(elapsed,60)
            self.session_lbl.configure(text=f"Sesión activa: {m:02}:{s:02}")
        self._update_status_panel()
        self.after(1000, self.run_engine)

    def _scan_for_ai(self):
        # Capa 1: todas las ventanas abiertas
        try:
            for win in gw.getAllWindows():
                if not win.title: continue
                t=win.title.lower()
                for kw in IA_WINDOW_KEYWORDS:
                    if kw in t:
                        d=f"Ventana: {win.title[:50]}"
                        if d!=self.last_detection:
                            self.last_detection=d; return d
        except: pass

        if not PSUTIL_OK: return None

        try:
            for proc in psutil.process_iter(["name","cmdline"]):
                pname=(proc.info.get("name") or "").lower()
                # Capa 2: cmdline de navegadores
                if any(b in pname for b in ("chrome","msedge","firefox","brave","opera")):
                    try:
                        cmd=" ".join(proc.info.get("cmdline") or []).lower()
                        for dom in IA_DOMAINS:
                            if dom in cmd:
                                d=f"URL: {dom}"
                                if d!=self.last_detection:
                                    self.last_detection=d; return d
                    except: pass
                # Capa 3: procesos IA nativos
                for ia in IA_PROCESSES:
                    if ia in pname:
                        d=f"Proceso: {proc.info['name']}"
                        if d!=self.last_detection:
                            self.last_detection=d; return d
        except: pass

        # Capa 4: archivos de sesión del navegador
        return self._scan_browser_session_files()

    # ── TOAST ─────────────────────────────────────────────────────────────────
    def show_toast(self, detection_info):
        if self.is_alert_active: return
        self.is_alert_active=True

        toast=ctk.CTkToplevel(self)
        toast.overrideredirect(True)
        toast.attributes("-topmost",True)
        w,h=580,108; x=(toast.winfo_screenwidth()-w)//2
        toast.geometry(f"{w}x{h}+{x}+28")

        fr=ctk.CTkFrame(toast,fg_color="#0f0005",border_color="#D4AF37",border_width=2)
        fr.pack(fill="both",expand=True)
        fr.grid_columnconfigure(0,weight=1)

        ctk.CTkLabel(fr,text="⚠️  IA DETECTADA",
                     font=ctk.CTkFont(size=13,weight="bold"),
                     text_color="#D4AF37").grid(row=0,column=0,pady=(8,0),padx=14,sticky="w")
        ctk.CTkLabel(fr,text=detection_info[:60],
                     font=ctk.CTkFont(size=10),text_color="#666"
                     ).grid(row=1,column=0,padx=14,sticky="w")

        mode=self.mode_var.get()
        act="Cerrando pestaña IA…" if mode=="Estricto" else "Modo Amable — solo aviso"
        ctk.CTkLabel(fr,text=act,font=ctk.CTkFont(size=10),text_color="#444"
                     ).grid(row=2,column=0,padx=14,sticky="w")

        count_lbl=ctk.CTkLabel(fr,text="5",
                               font=ctk.CTkFont(size=22,weight="bold"),
                               text_color="#FF4C4C")
        count_lbl.grid(row=0,column=1,rowspan=3,padx=20)

        def cd(n):
            if n>0:
                count_lbl.configure(text=str(n))
                toast.after(1000,lambda:cd(n-1))
            else:
                self.infractions+=1
                self.infractions_label.configure(text=str(self.infractions))
                self._set_score(self._get_score()-5)
                self._update_status_panel()
                if self.mode_var.get()=="Estricto": self._redirect()
                toast.destroy(); self.is_alert_active=False
        cd(5)

    def _redirect(self):
        try:
            win=gw.getActiveWindow()
            if win:
                win.activate(); time.sleep(0.3)
                pyautogui.hotkey("ctrl","l"); time.sleep(0.2)
                pyautogui.write("https://stackoverflow.com")
                pyautogui.press("enter")
        except: pass

    # ── MODO EMERGENCIA ───────────────────────────────────────────────────────
    def use_hint(self):
        if messagebox.askyesno("Modo Emergencia",
            "¿Confirmas que quieres usar una pista?\n\n"
            "→ Sello cambiará a HYBRID CODER\n"
            "→ −10 puntos de score"):
            self.hint_used=True
            self._set_score(self._get_score()-10)
            self.infractions+=1
            self.infractions_label.configure(text=str(self.infractions))
            self._update_status_panel()

    # ── FINALIZAR ─────────────────────────────────────────────────────────────
    def finish_project(self):
        self.is_running=False
        name=self.project_entry.get().strip()
        score=self._get_score()
        seal=("pure" if self.infractions==0 and score>=90 and not self.hint_used
              else "hybrid" if score>=50 else "failed")

        h,rem=divmod(self.seconds_elapsed,3600); m,s=divmod(rem,60)

        try:
            conn=sqlite3.connect(DB_PATH); c=conn.cursor()
            c.execute("""UPDATE proyectos SET estado='Certificado',fecha_fin=?,
                sello=?,score=?,infracciones=? WHERE nombre=?""",
                (datetime.datetime.now().strftime("%Y-%m-%d"),
                 seal.upper(),score,self.infractions,name))
            conn.commit(); conn.close()
        except Exception as e: print(f"Error certificando: {e}")
        self.save_progress()

        names={"pure":"ARTISAN CODER 🥇","hybrid":"HYBRID CODER 🥈","failed":"VIBE CODER ❌"}
        medal_ok = os.path.exists(MEDAL_PATHS.get(seal,""))
        msg=(f"Proyecto:       {name}\n"
             f"Tiempo total:   {h:02}h {m:02}m {s:02}s\n"
             f"Score:          {score}%\n"
             f"Detecciones IA: {self.infractions}\n"
             f"Sello:          {names[seal]}\n"
             f"Medalla:        {'✅ incluida' if medal_ok else '⚠️ no encontrada en /img'}\n\n"
             "¿Exportar certificado PNG?")

        if messagebox.askyesno("✅  Proyecto certificado", msg):
            if not PILLOW_OK:
                messagebox.showwarning("Pillow no instalado","pip install Pillow")
            else:
                path=filedialog.asksaveasfilename(
                    defaultextension=".png",filetypes=[("PNG","*.png")],
                    initialfile=f"CraftCoding_{name.replace(' ','_')}.png")
                if path:
                    try:
                        generate_certificate(name,h,m,s,score,
                                             self.infractions,seal,path)
                        messagebox.showinfo("✅  Guardado",f"Certificado exportado:\n{path}")
                    except Exception as e:
                        messagebox.showerror("Error generando PNG",str(e))
        self.destroy()

    # ── BROWSER DETECTION LAYER 4 ─────────────────────────────────────────────
    def _scan_browser_session_files(self):
        """
        Solo lee archivos que reflejan pestañas AHORA ABIERTAS.
        El historial SQLite NO se usa: guarda visitas pasadas aunque la
        pestaña esté cerrada → causa falsos positivos.
        """
        BROWSERS = [
            ("Edge",   r"~\AppData\Local\Microsoft\Edge\User Data",   ["msedge.exe"]),
            ("Chrome", r"~\AppData\Local\Google\Chrome\User Data",    ["chrome.exe"]),
            ("Brave",  r"~\AppData\Local\BraveSoftware\Brave-Browser\User Data", ["brave.exe"]),
        ]
        for bname, bpath, bprocs in BROWSERS:
            # Solo intentar si el proceso del navegador está corriendo
            if not self._browser_is_running(bprocs):
                continue
            r = self._scan_chromium_tabs(bname, bpath)
            if r:
                return r
        return self._scan_firefox()

    def _browser_is_running(self, proc_names):
        """Devuelve True si alguno de los procesos del navegador está activo."""
        if not PSUTIL_OK:
            return True  # sin psutil asumimos que puede estar abierto
        try:
            running = {p.info["name"].lower()
                       for p in psutil.process_iter(["name"])}
            return any(p in running for p in proc_names)
        except Exception:
            return True

    def _scan_chromium_tabs(self, browser_name, base_path_raw):
        """
        Lee SOLO el archivo de pestañas activas más reciente de la carpeta
        Sessions. Edge/Chrome actualizan este archivo en tiempo real cuando
        abres o cierras pestañas, por lo que refleja el estado actual exacto.

        Se descarta cualquier archivo con más de 5 minutos de antigüedad
        (indicaría que el navegador lo escribió en una sesión anterior).
        """
        base = os.path.expanduser(base_path_raw)
        if not os.path.isdir(base):
            return None

        now_ts = time.time()

        for profile in ["Default"] + [f"Profile {i}" for i in range(1, 6)]:
            sd = os.path.join(base, profile, "Sessions")
            if not os.path.isdir(sd):
                continue

            # Recoger candidatos ordenados por fecha de modificación
            candidates = []
            for fn in os.listdir(sd):
                if fn.startswith("Tabs_") or fn == "Current Tabs":
                    fp = os.path.join(sd, fn)
                    try:
                        mtime = os.path.getmtime(fp)
                        candidates.append((mtime, fp))
                    except Exception:
                        continue

            if not candidates:
                continue

            # Solo el más reciente
            candidates.sort(reverse=True)
            newest_mtime, newest_fp = candidates[0]

            # Si tiene más de 5 minutos → sesión antigua, ignorar
            if now_ts - newest_mtime > 300:
                continue

            try:
                raw = open(newest_fp, "rb").read().decode("utf-8", errors="ignore").lower()
                for dom in IA_DOMAINS:
                    if dom in raw:
                        d = f"{browser_name} · pestaña abierta: {dom}"
                        if d != self.last_detection:
                            self.last_detection = d
                            return d
            except Exception:
                continue

        return None

    def _scan_firefox(self):
        ff=os.path.expanduser(r"~\AppData\Roaming\Mozilla\Firefox\Profiles")
        if not os.path.isdir(ff): return None
        for pdir in os.listdir(ff):
            pp=os.path.join(ff,pdir)
            if not os.path.isdir(pp): continue
            for cand in [os.path.join(pp,"sessionstore-backups","recovery.jsonlz4"),
                         os.path.join(pp,"sessionstore.jsonlz4"),
                         os.path.join(pp,"sessionstore.js")]:
                if not os.path.exists(cand): continue
                try:
                    raw=(self._read_mozlz4(cand) if cand.endswith(".jsonlz4")
                         else open(cand,"r",encoding="utf-8",errors="ignore").read())
                    if raw:
                        for dom in IA_DOMAINS:
                            if dom in raw.lower():
                                d=f"Firefox · pestaña: {dom}"
                                if d!=self.last_detection:
                                    self.last_detection=d; return d
                except: continue
        return None

    def _read_mozlz4(self, path):
        MAGIC=b"mozLz40\0"
        try:
            import lz4.block
            with open(path,"rb") as f:
                if f.read(8)!=MAGIC: return None
                return lz4.block.decompress(f.read()).decode("utf-8",errors="ignore")
        except ImportError:
            try:
                raw=open(path,"rb").read()
                chunks=[]; cur=[]
                for b in raw:
                    if 32<=b<127: cur.append(chr(b))
                    else:
                        if len(cur)>8: chunks.append("".join(cur))
                        cur=[]
                return " ".join(chunks)
            except: return None
        except: return None

    def on_closing(self):
        if self.is_running: self.save_progress()
        self.destroy()


if __name__ == "__main__":
    app = CraftCodingApp()
    app.mainloop()