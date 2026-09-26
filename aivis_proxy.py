from fastapi import FastAPI, Query
import requests
from fastapi.responses import Response
from pydantic import BaseModel
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import asyncio
import winsound
import json
import os

# ========== 配置文件名称 ==========
CONFIG_FILE = "aivis_proxy_config.json"
DEFAULT_AIVIS_BASE = "http://127.0.0.1:10101"
DEFAULT_SPEAKER_ID = 2110072448

# 加载配置文件
def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "aivis_base": DEFAULT_AIVIS_BASE,
        "speaker_id": DEFAULT_SPEAKER_ID
    }

def save_config_file(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)

runtime_cfg = load_config()

app = FastAPI(title="AIVIS转发服务 TkGUI版")

class FakeSovitsReq(BaseModel):
    text: str
    text_lang: str = "ja"
    ref_audio_path: str = ""
    prompt_lang: str = ""
    prompt_text: str = ""


# 业务核心
async def _tts_core(text: str):
    text = text.strip()
    if not text:
        return Response(content=b"", status_code=400)
    AIVIS_BASE = runtime_cfg["aivis_base"]
    SPEAKER_ID = runtime_cfg["speaker_id"]
    # audio_query
    q_resp = requests.post(
        f"{AIVIS_BASE}/audio_query",
        params={"speaker": SPEAKER_ID, "text": text},
        timeout=12
    )
    q_resp.raise_for_status()
    query_json = q_resp.json()
    # synthesis
    wav_resp = requests.post(
        f"{AIVIS_BASE}/synthesis",
        params={"speaker": SPEAKER_ID},
        json=query_json,
        headers={"Accept": "audio/wav"},
        timeout=20
    )
    wav_resp.raise_for_status()
    return wav_resp.content


@app.post("/tts")
async def fake_sovits_post(req: FakeSovitsReq):
    wav_bytes = await _tts_core(req.text)
    return Response(content=wav_bytes, media_type="audio/wav")

@app.get("/tts")
async def fake_sovits_get(
    text: str = Query(""),
    text_lang: str = Query("ja"),
    ref_audio_path: str = Query(""),
    prompt_lang: str = Query(""),
    prompt_text: str = Query(""),
):
    wav_bytes = await _tts_core(text)
    return Response(content=wav_bytes, media_type="audio/wav")


# ---------------- Tkinter GUI ----------------
class TkGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AIVIS连接warashi代理")
        self.root.geometry("620x480")

        # 参数区
        frame_cfg = ttk.LabelFrame(root, text="参数设置")
        frame_cfg.pack(fill=tk.X, padx=10, pady=6)

        ttk.Label(frame_cfg, text="AIVIS_BASE:").grid(row=0, column=0, sticky="w")
        self.var_aivis = tk.StringVar(value=runtime_cfg["aivis_base"])
        ttk.Entry(frame_cfg, textvariable=self.var_aivis, width=45).grid(row=0, column=1, padx=8)

        ttk.Label(frame_cfg, text="SPEAKER_ID:").grid(row=1, column=0, sticky="w")
        self.var_sid = tk.StringVar(value=str(runtime_cfg["speaker_id"]))
        ttk.Entry(frame_cfg, textvariable=self.var_sid, width=45).grid(row=1, column=1, padx=8)

        # SPEAKER_ID查看链接
        tip_link = tk.Label(frame_cfg, text="👉 点击打开 http://127.0.0.1:10101/speakers 查看可用ID", fg="#0066cc", cursor="hand2")
        tip_link.grid(row=2, column=0, columnspan=2, sticky="w", pady=(0,4))
        tip_link.bind("<Button-1>", lambda e: self.open_url("http://127.0.0.1:10101/speakers"))

        ttk.Button(frame_cfg, text="保存配置", command=self.save_cfg).grid(row=3, column=0, columnspan=2, pady=4)

        # 文本输入区
        frame_text = ttk.LabelFrame(root, text="输入文本")
        frame_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=6)
        self.text_box = tk.Text(frame_text, height=6)
        self.text_box.pack(fill=tk.BOTH, expand=True)

        # 按钮
        frame_btn = ttk.Frame(root)
        frame_btn.pack(pady=4)
        ttk.Button(frame_btn, text="生成语音并播放", command=self.gen_thread).pack()

        # 状态
        self.var_status = tk.StringVar(value="就绪")
        ttk.Label(root, textvariable=self.var_status).pack()

        # 左下角链接1
        link1 = tk.Label(root, text="视频演示", fg="blue", cursor="hand2")
        link1.place(x=15, y=450)
        link1.bind("<Button-1>", lambda e: self.open_url("https://link1.test"))

        # 右下角链接2
        link2 = tk.Label(root, text="使用说明", fg="blue", cursor="hand2")
        link2.place(x=540, y=450)
        link2.bind("<Button-1>", lambda e: self.open_url("https://link2.test"))

    def open_url(self, url):
        import webbrowser
        webbrowser.open(url)

    def save_cfg(self):
        try:
            runtime_cfg["aivis_base"] = self.var_aivis.get().strip()
            runtime_cfg["speaker_id"] = int(self.var_sid.get().strip())
            save_config_file(runtime_cfg)
            self.var_status.set("✅配置已保存到 aivis_proxy_config.json")
        except ValueError:
            messagebox.showerror("错误", "speaker_id必须是数字！")
        except Exception as e:
            messagebox.showerror("保存失败", str(e))

    def gen_thread(self):
        t = threading.Thread(target=self.generate_audio)
        t.daemon = True
        t.start()

    def generate_audio(self):
        text = self.text_box.get("1.0", tk.END).strip()
        if not text:
            self.var_status.set("请输入文本！")
            return
        self.var_status.set("生成中...")
        try:
            loop = asyncio.new_event_loop()
            wav_data = loop.run_until_complete(_tts_core(text))
            tmp_path = "_tmp_tts.wav"
            with open(tmp_path, "wb") as f:
                f.write(wav_data)
            winsound.PlaySound(tmp_path, winsound.SND_FILENAME)
            self.var_status.set("✅生成并播放完成")
        except Exception as e:
            self.var_status.set(f"❌失败: {str(e)}")


# 后台启动FastAPI
def start_fastapi():
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=9880)


if __name__ == "__main__":
    api_thread = threading.Thread(target=start_fastapi)
    api_thread.daemon = True
    api_thread.start()

    root = tk.Tk()
    gui = TkGUI(root)
    root.mainloop()
