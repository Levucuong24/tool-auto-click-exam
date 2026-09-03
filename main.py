import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
import pyautogui
import keyboard
import threading
import time
from datetime import datetime, timedelta
import os
import cv2
import json
import urllib.request
import urllib.error
import base64
import tempfile
import webbrowser
import pyautogui
import ssl

import ctypes

# Tắt tính năng tự động ngắt của pyautogui khi rê chuột vào góc màn hình
pyautogui.FAILSAFE = False

def make_click_through(win):
    try:
        win.update_idletasks()
        hwnd = win.winfo_id()
        # Lấy Handle cửa sổ thật trên Windows
        parent_hwnd = ctypes.windll.user32.GetParent(hwnd)
        if parent_hwnd:
            hwnd = parent_hwnd
        GWL_EXSTYLE = -20
        WS_EX_TRANSPARENT = 0x00000020
        WS_EX_LAYERED = 0x00080000
        style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style | WS_EX_TRANSPARENT | WS_EX_LAYERED)
    except Exception:
        pass

class AutoClickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto Clicker Pro")
        self.root.geometry("550x880")
        self.root.resizable(False, False)
        
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.tab1 = ttk.Frame(self.notebook)
        self.tab2 = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab1, text="Hẹn giờ Click")
        self.notebook.add(self.tab2, text="Auto Bot Hình Ảnh")
        
        # === TAB 1: HẸN GIỜ CLICK (OLD CODE) ===
        self.is_running_tab1 = False
        self.tasks = []
        self.task_counter = 0
        self.setup_tab1()
        
        # === TAB 2: AUTO BOT HÌNH ẢNH (NEW CODE) ===
        self.is_bot_running = False
        
        self.config_file = "config.json"
        self.roi = None
        
        self.setup_tab2()
        self.load_config()
        

    def load_config(self):
        try:
            with open(self.config_file, "r") as f:
                config = json.load(f)
                if "api_key" in config:
                    self.entry_api.delete(0, tk.END)
                    self.entry_api.insert(0, config["api_key"])
                if "roi" in config:
                    self.roi = tuple(config["roi"]) if config["roi"] else None
                    if self.roi:
                        self.lbl_roi.config(text=f"Đã chọn vùng", fg="green")
                if "interval" in config:
                    self.entry_interval.delete(0, tk.END)
                    self.entry_interval.insert(0, str(config["interval"]))
                if "use_ai" in config:
                    self.use_ai_var.set(config["use_ai"])
                    self.toggle_ai_ui()
        except:
            pass

    def save_config(self):
        try:
            interval = int(self.entry_interval.get().strip())
        except:
            interval = 300
        config = {
            "api_key": self.entry_api.get().strip(),
            "roi": self.roi,
            "interval": interval,
            "use_ai": self.use_ai_var.get()
        }
        try:
            with open(self.config_file, "w") as f:
                json.dump(config, f)
        except:
            pass

    def toggle_ai_ui(self, *args):
        use_ai = self.use_ai_var.get()
        state = tk.NORMAL if use_ai else tk.DISABLED
        self.entry_api.config(state=state)
        self.btn_select_roi.config(state=state)
        self.entry_interval.config(state=state)
        
        cond_state = tk.DISABLED if use_ai else tk.NORMAL
        self.entry_cond.config(state=cond_state)
        if hasattr(self, 'btn_cond'):
            self.btn_cond.config(state=cond_state)

    def select_roi(self):
        self.root.withdraw()
        overlay = tk.Toplevel(self.root)
        overlay.attributes('-alpha', 0.3)
        overlay.attributes('-fullscreen', True)
        overlay.config(cursor="cross")
        
        canvas = tk.Canvas(overlay, cursor="cross", bg="gray")
        canvas.pack(fill=tk.BOTH, expand=True)
        
        self.start_x = None
        self.start_y = None
        self.rect = None
        
        def on_press(event):
            self.start_x = event.x
            self.start_y = event.y
            self.rect = canvas.create_rectangle(self.start_x, self.start_y, 1, 1, outline='red', width=2, fill="black")
            
        def on_drag(event):
            cur_x, cur_y = (event.x, event.y)
            canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)
            
        def on_release(event):
            end_x, end_y = (event.x, event.y)
            x = min(self.start_x, end_x)
            y = min(self.start_y, end_y)
            w = abs(end_x - self.start_x)
            h = abs(end_y - self.start_y)
            
            if w > 10 and h > 10:
                self.roi = (x, y, w, h)
                self.lbl_roi.config(text=f"Đã chọn vùng", fg="green")
            
            overlay.destroy()
            self.root.deiconify()
            
        canvas.bind("<ButtonPress-1>", on_press)
        canvas.bind("<B1-Motion>", on_drag)
        canvas.bind("<ButtonRelease-1>", on_release)

    def check_progress_ai(self, api_key, roi):
        temp_path = None
        try:
            x, y, w, h = roi
            img = pyautogui.screenshot(region=(x, y, w, h))
            
            # Giảm kích thước ảnh nếu quá lớn để tiết kiệm token & dung lượng
            if img.width > 800 or img.height > 800:
                img.thumbnail((800, 800))
                
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
                temp_path = f.name
                
            img.save(temp_path, format="JPEG", quality=80)
            
            with open(temp_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                
            headers = {
                "Content-Type": "application/json"
            }
            
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": "Đọc thông tin từ ảnh này. Tìm phần trăm hoàn thành (ví dụ từ chuỗi '(100%)' hoặc '100%'). Tính thời gian còn lại (nếu đã đủ 100% thì thời gian còn lại là 0). TRẢ VỀ DUY NHẤT một đối tượng JSON hợp lệ với key 'percentage' (số, vd: 100) và 'remaining_minutes' (số, vd: 0). Nếu không thấy, trả về 0. KHÔNG XUẤT THÊM CHỮ NÀO KHÁC."},
                            {
                                "inline_data": {
                                    "mime_type": "image/jpeg",
                                    "data": encoded_string
                                }
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.1,
                    "responseMimeType": "application/json"
                }
            }
            
            # Sử dụng model Gemini 3.6 Flash chuẩn duy nhất để tối ưu lượt gọi API (tránh tốn Quota)
            models = ["gemini-3.6-flash"]
            last_err = ""
            
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            
            for model in models:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
                req = urllib.request.Request(url, headers=headers, data=json.dumps(payload).encode('utf-8'))
                try:
                    with urllib.request.urlopen(req, context=ctx, timeout=35) as response:
                        result = json.loads(response.read().decode('utf-8'))
                        content = result["candidates"][0]["content"]["parts"][0]["text"]
                        content = content.replace("```json", "").replace("```", "").strip()
                        data = json.loads(content)
                        return data.get("percentage", 0), data.get("remaining_minutes", 999)
                except urllib.error.HTTPError as e:
                    err_body = e.read().decode('utf-8', errors='ignore')
                    try:
                        err_json = json.loads(err_body)
                        err_obj = err_json.get("error", {})
                        msg = err_obj.get("message", err_body)
                        code = err_obj.get("code", e.code)
                    except:
                        msg = err_body
                        code = e.code
                    last_err = f"HTTP {code}: {msg}"
                    if code == 429:
                        return None, f"HTTP 429 Quota Exceeded: {msg}"
                    if code in (400, 401, 403):
                        return None, f"HTTP {code} Key Invalid: {msg}"
                except Exception as e:
                    last_err = str(e)
                    
            return None, last_err
        except Exception as e:
            return None, str(e)
        finally:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass

    def setup_tab1(self):
        self.marker_windows = []
        self.show_markers_var = tk.BooleanVar(value=True)
        self.time_mode_var = tk.StringVar(value="duration")

        frame_top = tk.LabelFrame(self.tab1, text="1. Thêm vị trí & Cài đặt thời gian cho từng Số", padx=10, pady=5)
        frame_top.pack(pady=5, padx=10, fill=tk.X)

        frame_mode_select = tk.Frame(frame_top)
        frame_mode_select.pack(fill=tk.X, pady=2)
        
        tk.Radiobutton(frame_mode_select, text="⏱️ Nhập thời lượng bài (Số Phút)", variable=self.time_mode_var, value="duration", command=self.toggle_tab1_mode_ui, font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(frame_mode_select, text="🕒 Nhập mốc giờ cố định (HH:MM:SS)", variable=self.time_mode_var, value="clock", command=self.toggle_tab1_mode_ui, font=("Arial", 9)).pack(side=tk.LEFT, padx=5)

        self.frame_input_inputs = tk.Frame(frame_top)
        self.frame_input_inputs.pack(fill=tk.X, pady=5)

        self.lbl_time_input = tk.Label(self.frame_input_inputs, text="Thời lượng bài (Phút):", font=("Arial", 10))
        self.lbl_time_input.pack(side=tk.LEFT, padx=5)
        
        self.entry_duration = tk.Entry(self.frame_input_inputs, justify="center", font=("Arial", 10), width=10)
        self.entry_duration.insert(0, "45")
        self.entry_duration.pack(side=tk.LEFT, padx=5)

        self.entry_time = tk.Entry(self.frame_input_inputs, justify="center", font=("Arial", 10), width=12)
        now = datetime.now()
        example_time = f"{now.hour:02d}:{(now.minute + 1) % 60:02d}:00"
        self.entry_time.insert(0, example_time)

        self.btn_hook = tk.Button(self.frame_input_inputs, text="📍 Bấm F8 để gán vị trí Số", command=self.start_hook, bg="#2196F3", fg="white", font=("Arial", 9, "bold"))
        self.btn_hook.pack(side=tk.LEFT, padx=10)

        # Khung cài giờ bắt đầu chạy bài 1
        self.frame_start_time = tk.Frame(frame_top)
        self.frame_start_time.pack(fill=tk.X, pady=2)
        
        tk.Label(self.frame_start_time, text="⏰ Giờ bắt đầu chạy Số 1 (HH:MM:SS):", font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=5)
        self.entry_start_time = tk.Entry(self.frame_start_time, justify="center", font=("Arial", 9), width=12)
        self.entry_start_time.pack(side=tk.LEFT, padx=2)
        tk.Label(self.frame_start_time, text="(Để trống = Bấm ▶ là chạy luôn)", font=("Arial", 8, "italic"), fg="gray").pack(side=tk.LEFT, padx=2)

        # Marker display toggle
        tk.Checkbutton(frame_top, text="👁️ Hiện bong bóng Số [1], [2], [3] trên màn hình", variable=self.show_markers_var, command=self.refresh_markers, font=("Arial", 9, "bold"), fg="#D32F2F").pack(anchor=tk.W, padx=5, pady=2)

        frame_list = tk.LabelFrame(self.tab1, text="2. Danh sách các vị trí Số đã cài đặt", padx=5, pady=5)
        frame_list.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)
        
        columns = ("check", "id", "duration", "time", "x", "y", "status")
        self.tree = ttk.Treeview(frame_list, columns=columns, show="headings", height=7)
        
        self.tree.heading("check", text="Chọn")
        self.tree.heading("id", text="Số TT")
        self.tree.heading("duration", text="Thời lượng")
        self.tree.heading("time", text="Giờ Click dự kiến")
        self.tree.heading("x", text="Tọa độ X")
        self.tree.heading("y", text="Tọa độ Y")
        self.tree.heading("status", text="Trạng thái")
        
        self.tree.column("check", width=40, anchor=tk.CENTER)
        self.tree.column("id", width=50, anchor=tk.CENTER)
        self.tree.column("duration", width=80, anchor=tk.CENTER)
        self.tree.column("time", width=110, anchor=tk.CENTER)
        self.tree.column("x", width=65, anchor=tk.CENTER)
        self.tree.column("y", width=65, anchor=tk.CENTER)
        self.tree.column("status", width=110, anchor=tk.CENTER)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree.bind("<ButtonRelease-1>", self.on_tree_click)
        
        scrollbar = ttk.Scrollbar(frame_list, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        frame_action_btn = tk.Frame(self.tab1)
        frame_action_btn.pack(pady=3)
        self.btn_delete = tk.Button(frame_action_btn, text="❌ Xóa ô đã chọn (☑)", command=self.delete_selected_task)
        self.btn_delete.pack(side=tk.LEFT, padx=5)
        self.btn_clear_all = tk.Button(frame_action_btn, text="🔄 Reset lại từ Số 1", command=self.reset_all_tasks)
        self.btn_clear_all.pack(side=tk.LEFT, padx=5)

        # Thêm khung chọn ảnh popup
        frame_popup = tk.Frame(self.tab1)
        frame_popup.pack(pady=3, padx=10, fill=tk.X)
        tk.Label(frame_popup, text="Ảnh nút Đồng ý (Auto click khi hiện):").pack(side=tk.LEFT)
        self.entry_popup = tk.Entry(frame_popup, width=25)
        self.entry_popup.pack(side=tk.LEFT, padx=5)
        tk.Button(frame_popup, text="Chọn", command=lambda: self.browse_image(self.entry_popup)).pack(side=tk.LEFT)

        frame_btn = tk.Frame(self.tab1)
        frame_btn.pack(pady=10)
        
        self.btn_start = tk.Button(frame_btn, text="▶ Bắt đầu Hẹn giờ", command=self.start_timer, bg="#4CAF50", fg="white", width=15, font=("Arial", 10, "bold"))
        self.btn_start.pack(side=tk.LEFT, padx=10)
        
        self.btn_stop = tk.Button(frame_btn, text="⏹ Dừng", command=self.stop_timer, bg="#f44336", fg="white", state=tk.DISABLED, width=12, font=("Arial", 10, "bold"))
        self.btn_stop.pack(side=tk.LEFT, padx=10)

    def toggle_tab1_mode_ui(self):
        mode = self.time_mode_var.get()
        if mode == "duration":
            self.lbl_time_input.config(text="Thời lượng bài (Phút):")
            self.entry_time.pack_forget()
            self.entry_duration.pack(side=tk.LEFT, padx=5, before=self.btn_hook)
        else:
            self.lbl_time_input.config(text="Mốc giờ click (HH:MM:SS):")
            self.entry_duration.pack_forget()
            self.entry_time.pack(side=tk.LEFT, padx=5, before=self.btn_hook)

    def create_marker_overlay(self, num, x, y):
        try:
            win = tk.Toplevel(self.root)
            win.overrideredirect(True)
            win.attributes('-topmost', True)
            win.attributes('-alpha', 0.88)
            # Tự động định kích thước ô bóng bóng chứa Số
            win.geometry(f"+{x+5}+{y-28}")
            
            lbl = tk.Label(win, text=f" #{num} ", bg="#FF3D00", fg="white", font=("Arial", 10, "bold"), bd=1, relief="solid")
            lbl.pack(fill=tk.BOTH, expand=True)
            
            # Cấu hình xuyên thấu click trên Windows
            make_click_through(win)
            return win
        except Exception:
            return None

    def refresh_markers(self):
        self.clear_markers()
        if hasattr(self, 'show_markers_var') and self.show_markers_var.get():
            for task in self.tasks:
                win = self.create_marker_overlay(task['id'], task['x'], task['y'])
                if win:
                    self.marker_windows.append(win)

    def clear_markers(self):
        for win in getattr(self, 'marker_windows', []):
            try:
                win.destroy()
            except Exception:
                pass
        self.marker_windows = []

    def setup_tab2(self):
        lbl_inst = tk.Label(self.tab2, text="Cắt sẵn các ảnh (Snipping Tool) và lưu vào máy tính.\n1. Ảnh điều kiện (VD: thanh 100%)\n2. Ảnh mục tiêu (VD: nút 'Bài tiếp' / Tích xanh / Icon bài)", justify=tk.LEFT, font=("Arial", 10))
        lbl_inst.pack(pady=10, padx=10, anchor=tk.W)
        
        # AI Mode settings
        self.frame_ai = tk.LabelFrame(self.tab2, text="Chế độ AI (Đọc tiến độ thông minh Gemini)", padx=5, pady=5)
        self.frame_ai.pack(fill=tk.X, padx=10, pady=5)
        
        self.use_ai_var = tk.BooleanVar(value=False)
        tk.Checkbutton(self.frame_ai, text="Bật dùng Gemini AI (Không cần Ảnh điều kiện 100%)", variable=self.use_ai_var, command=self.toggle_ai_ui).pack(anchor=tk.W)
        
        frame_api = tk.Frame(self.frame_ai)
        frame_api.pack(fill=tk.X, pady=2)
        tk.Label(frame_api, text="Gemini API Key:").pack(side=tk.LEFT)
        self.entry_api = tk.Entry(frame_api, width=35, show="*")
        self.entry_api.pack(side=tk.LEFT, padx=5)
        
        lbl_link = tk.Label(frame_api, text="(Lấy Key Miễn Phí)", font=("Arial", 9, "underline"), fg="blue", cursor="hand2")
        lbl_link.pack(side=tk.LEFT, padx=5)
        lbl_link.bind("<Button-1>", lambda e: webbrowser.open("https://aistudio.google.com/app/apikey"))
        
        frame_roi = tk.Frame(self.frame_ai)
        frame_roi.pack(fill=tk.X, pady=2)
        self.btn_select_roi = tk.Button(frame_roi, text="Chọn Vùng Tiến Độ", command=self.select_roi)
        self.btn_select_roi.pack(side=tk.LEFT)
        self.lbl_roi = tk.Label(frame_roi, text="Chưa chọn", fg="red")
        self.lbl_roi.pack(side=tk.LEFT, padx=5)
        
        tk.Label(frame_roi, text="Check mỗi (s):").pack(side=tk.LEFT, padx=5)
        self.entry_interval = tk.Entry(frame_roi, width=5)
        self.entry_interval.insert(0, "300")
        self.entry_interval.pack(side=tk.LEFT)

        # Condition Image
        self.frame_cond = tk.Frame(self.tab2)
        self.frame_cond.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(self.frame_cond, text="Ảnh điều kiện:", width=13, anchor=tk.W).pack(side=tk.LEFT)
        self.entry_cond = tk.Entry(self.frame_cond, width=40)
        self.entry_cond.pack(side=tk.LEFT, padx=5)
        self.btn_cond = tk.Button(self.frame_cond, text="Chọn ảnh", command=lambda: self.browse_image(self.entry_cond))
        self.btn_cond.pack(side=tk.LEFT)
        
        # Target Image
        frame_target = tk.Frame(self.tab2)
        frame_target.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(frame_target, text="Ảnh mục tiêu:", width=13, anchor=tk.W).pack(side=tk.LEFT)
        self.entry_target = tk.Entry(frame_target, width=40)
        self.entry_target.pack(side=tk.LEFT, padx=5)
        tk.Button(frame_target, text="Chọn ảnh", command=lambda: self.browse_image(self.entry_target)).pack(side=tk.LEFT)
        
        # Target Mode (Chế độ click ảnh mục tiêu)
        frame_mode = tk.Frame(self.tab2)
        frame_mode.pack(fill=tk.X, padx=10, pady=5)
        self.target_mode = tk.StringVar(value="direct")
        tk.Radiobutton(frame_mode, text="1. Click trực tiếp vào Ảnh mục tiêu (Có Nút Bài Tiếp)", variable=self.target_mode, value="direct", command=self.toggle_mode_ui).pack(anchor=tk.W)
        tk.Radiobutton(frame_mode, text="2. Ảnh MT là Tích Xanh -> Nhảy Y xuống bài dưới", variable=self.target_mode, value="checkmark", command=self.toggle_mode_ui).pack(anchor=tk.W)
        tk.Radiobutton(frame_mode, text="3. Ảnh MT là Icon bài -> Quét đối chiếu với Tích Xanh", variable=self.target_mode, value="list_scan", command=self.toggle_mode_ui).pack(anchor=tk.W)
        
        # Advanced Settings Frame
        self.frame_adv_settings = tk.LabelFrame(self.tab2, text="Cài đặt Mở Rộng", padx=5, pady=5)
        self.frame_adv_settings.pack(fill=tk.X, padx=10, pady=5)
        
        # Mode 2 Settings
        self.frame_mode2 = tk.Frame(self.frame_adv_settings)
        self.frame_mode2.pack(fill=tk.X, pady=2)
        tk.Label(self.frame_mode2, text="[Mode 2] Khoảng cách nhảy Y (px):").pack(side=tk.LEFT)
        self.entry_offset = tk.Entry(self.frame_mode2, width=5)
        self.entry_offset.insert(0, "40")
        self.entry_offset.pack(side=tk.LEFT, padx=5)
        
        tk.Label(self.frame_mode2, text="Skip N bài:").pack(side=tk.LEFT, padx=5)
        self.entry_skip = tk.Entry(self.frame_mode2, width=3)
        self.entry_skip.insert(0, "0")
        self.entry_skip.pack(side=tk.LEFT, padx=2)

        # Mode 3 Settings
        self.frame_mode3 = tk.Frame(self.frame_adv_settings)
        self.frame_mode3.pack(fill=tk.X, pady=2)
        tk.Label(self.frame_mode3, text="[Mode 3] Ảnh Tích Xanh (Để so sánh):", width=30, anchor=tk.W).pack(side=tk.LEFT)
        self.entry_chk_img = tk.Entry(self.frame_mode3, width=15)
        self.entry_chk_img.pack(side=tk.LEFT, padx=5)
        tk.Button(self.frame_mode3, text="Chọn", command=lambda: self.browse_image(self.entry_chk_img)).pack(side=tk.LEFT)
        
        # Skip Image (Né Mìn)
        frame_skip_img = tk.Frame(self.frame_adv_settings)
        frame_skip_img.pack(fill=tk.X, pady=2)
        tk.Label(frame_skip_img, text="Ảnh bài cần bỏ qua (Tùy chọn):", width=30, anchor=tk.W).pack(side=tk.LEFT)
        self.entry_skip_img = tk.Entry(frame_skip_img, width=15)
        self.entry_skip_img.pack(side=tk.LEFT, padx=5)
        tk.Button(frame_skip_img, text="Chọn", command=lambda: self.browse_image(self.entry_skip_img)).pack(side=tk.LEFT)
        
        self.toggle_mode_ui() # Initialize UI state

        # Replay Image
        frame_replay = tk.Frame(self.tab2)
        frame_replay.pack(fill=tk.X, padx=10, pady=2)
        tk.Label(frame_replay, text="Ảnh nút Bắt đầu xem:", width=18, anchor=tk.W, justify=tk.LEFT).pack(side=tk.LEFT)
        self.entry_replay = tk.Entry(frame_replay, width=35)
        self.entry_replay.pack(side=tk.LEFT, padx=5)
        tk.Button(frame_replay, text="Chọn ảnh", command=lambda: self.browse_image(self.entry_replay)).pack(side=tk.LEFT)

        frame_replay2 = tk.Frame(self.tab2)
        frame_replay2.pack(fill=tk.X, padx=10, pady=2)
        tk.Label(frame_replay2, text="Ảnh nút Xem lại:", width=18, anchor=tk.W, justify=tk.LEFT).pack(side=tk.LEFT)
        self.entry_replay2 = tk.Entry(frame_replay2, width=35)
        self.entry_replay2.pack(side=tk.LEFT, padx=5)
        tk.Button(frame_replay2, text="Chọn ảnh", command=lambda: self.browse_image(self.entry_replay2)).pack(side=tk.LEFT)
        
        # Status Label
        frame_status = tk.LabelFrame(self.tab2, text="Trạng thái Bot", padx=10, pady=5)
        frame_status.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.lbl_bot_status = tk.Label(frame_status, text="Đang chờ...", font=("Arial", 11, "italic"), fg="blue", wraplength=450, justify=tk.CENTER)
        self.lbl_bot_status.pack(expand=True)
        
        # Controls
        frame_btn2 = tk.Frame(self.tab2)
        frame_btn2.pack(pady=10)
        
        self.btn_bot_start = tk.Button(frame_btn2, text="Bắt đầu Bot", command=self.start_bot, bg="#4CAF50", fg="white", width=15, font=("Arial", 10, "bold"))
        self.btn_bot_start.pack(side=tk.LEFT, padx=10)
        
        self.btn_bot_stop = tk.Button(frame_btn2, text="Dừng Bot", command=self.stop_bot, bg="#f44336", fg="white", state=tk.DISABLED, width=15, font=("Arial", 10, "bold"))
        self.btn_bot_stop.pack(side=tk.LEFT, padx=10)
        
    def toggle_mode_ui(self):
        mode = self.target_mode.get()
        
        # Reset all
        for widget in self.frame_mode2.winfo_children() + self.frame_mode3.winfo_children():
            if isinstance(widget, (tk.Entry, tk.Button)):
                widget.config(state=tk.DISABLED)
                
        if mode == "checkmark":
            for widget in self.frame_mode2.winfo_children():
                if isinstance(widget, (tk.Entry, tk.Button)):
                    widget.config(state=tk.NORMAL)
        elif mode == "list_scan":
            for widget in self.frame_mode3.winfo_children():
                if isinstance(widget, (tk.Entry, tk.Button)):
                    widget.config(state=tk.NORMAL)

    def browse_image(self, entry_widget):
        filepath = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")])
        if filepath:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, filepath)
            
    def update_bot_status(self, text, color="blue"):
        self.lbl_bot_status.config(text=text, fg=color)
        
    def start_bot(self):
        self.save_config()
        use_ai = self.use_ai_var.get()
        cond_img = self.entry_cond.get().strip()
        target_img = self.entry_target.get().strip()
        replay_img = self.entry_replay.get().strip()
        replay_img2 = self.entry_replay2.get().strip()
        skip_img = self.entry_skip_img.get().strip()
        chk_img = self.entry_chk_img.get().strip()
        
        if use_ai:
            if not self.entry_api.get().strip():
                messagebox.showerror("Lỗi", "Vui lòng nhập Gemini API Key!")
                return
            if not self.roi:
                messagebox.showerror("Lỗi", "Vui lòng chọn Vùng tiến độ!")
                return
            try:
                val = int(self.entry_interval.get())
                if val < 300:
                    self.entry_interval.delete(0, tk.END)
                    self.entry_interval.insert(0, "300")
            except ValueError:
                self.entry_interval.delete(0, tk.END)
                self.entry_interval.insert(0, "300")
        else:
            if not cond_img or not os.path.exists(cond_img):
                messagebox.showerror("Lỗi", "Đường dẫn Ảnh điều kiện không hợp lệ!")
                return
        if not target_img or not os.path.exists(target_img):
            messagebox.showerror("Lỗi", "Đường dẫn Ảnh mục tiêu không hợp lệ!")
            return
        if replay_img and not os.path.exists(replay_img):
            messagebox.showerror("Lỗi", "Đường dẫn Ảnh nút Bắt đầu xem không hợp lệ!")
            return
        if replay_img2 and not os.path.exists(replay_img2):
            messagebox.showerror("Lỗi", "Đường dẫn Ảnh nút Xem lại không hợp lệ!")
            return
            
        if self.target_mode.get() == "checkmark":
            try:
                int(self.entry_offset.get())
                int(self.entry_skip.get())
            except ValueError:
                messagebox.showerror("Lỗi", "Khoảng cách Y và số bài Skip phải là số nguyên!")
                return
        elif self.target_mode.get() == "list_scan":
            if not chk_img or not os.path.exists(chk_img):
                messagebox.showerror("Lỗi", "Chế độ 3 yêu cầu phải có Ảnh Tích Xanh để đối chiếu!")
                return
                
        if skip_img and not os.path.exists(skip_img):
            messagebox.showerror("Lỗi", "Đường dẫn Ảnh bài cần bỏ qua không hợp lệ!")
            return

        self.is_bot_running = True
        self.btn_bot_start.config(state=tk.DISABLED)
        self.btn_bot_stop.config(state=tk.NORMAL)
        self.update_bot_status("Khởi động Bot...\nĐang quét ảnh điều kiện trên màn hình...", "blue")
        
        threading.Thread(target=self.run_bot_logic, args=(cond_img, target_img, replay_img, skip_img, chk_img), daemon=True).start()
        
    def stop_bot(self):
        self.is_bot_running = False
        self.btn_bot_start.config(state=tk.NORMAL)
        self.btn_bot_stop.config(state=tk.DISABLED)
        self.update_bot_status("Đã dừng Bot.", "red")
        
    def run_bot_logic(self, cond_img, target_img, replay_img, skip_img, chk_img):
        while self.is_bot_running:
            try:
                condition_met = False
                
                if self.use_ai_var.get():
                    api_key = self.entry_api.get().strip()
                    try:
                        interval = int(self.entry_interval.get())
                        if interval < 300:
                            interval = 300  # Ép cứng tối thiểu 300s (5 phút) để an toàn Quota API
                    except:
                        interval = 300
                        
                    self.root.after(0, self.update_bot_status, f"Đang nhờ AI đọc tiến độ...", "blue")
                    percent, rem_mins_or_error = self.check_progress_ai(api_key, self.roi)
                    
                    if percent is None:
                        err_str = str(rem_mins_or_error)
                        if "Key Invalid" in err_str or "API_KEY_INVALID" in err_str or "API key not valid" in err_str or "HTTP 400" in err_str or "HTTP 403" in err_str or "HTTP 401" in err_str:
                            status_msg = (
                                f"Lỗi Gemini API Key không hợp lệ!\n"
                                f"Vui lòng lấy lại API Key mới tại: aistudio.google.com\n"
                                f"(Tự động thử lại sau 300s / 5 phút...)"
                            )
                        elif "timed out" in err_str.lower() or "timeout" in err_str.lower():
                            status_msg = (
                                f"Mạng chậm (Timeout phản hồi từ Gemini API)\n"
                                f"Đang chờ 300s (5 phút) để AI quét lại..."
                            )
                        elif "429" in err_str or "Quota Exceeded" in err_str or "quota" in err_str.lower() or "RESOURCE_EXHAUSTED" in err_str:
                            status_msg = (
                                f"Lỗi API 429 (Hết lượt gọi Quota Gemini)\n"
                                f"Đang chờ 300s (5 phút) để AI quét lại..."
                            )
                        else:
                            err_text = err_str[:80]
                            status_msg = (
                                f"Lỗi API: {err_text}\n"
                                f"Đang chờ 300s (5 phút) để AI quét lại..."
                            )
                        self.root.after(0, self.update_bot_status, status_msg, "red")
                        for _ in range(300):
                            if not self.is_bot_running: break
                            time.sleep(1)
                        continue
                        
                    self.root.after(0, self.update_bot_status, f"AI thấy: {percent}%", "purple")
                    if percent >= 100:
                        condition_met = True
                        self.root.after(0, self.update_bot_status, "AI xác nhận ĐÃ HOÀN THÀNH 100%!\nĐang xử lý click mục tiêu...", "green")
                    else:
                        self.root.after(0, self.update_bot_status, f"Chưa hoàn thành ({percent}%). Đợi 300s (5 phút)...", "orange")
                        for _ in range(300):
                            if not self.is_bot_running: break
                            time.sleep(1)
                                
                            if replay_img and os.path.exists(replay_img):
                                try:
                                    replay_loc = pyautogui.locateCenterOnScreen(replay_img, confidence=0.8)
                                    if replay_loc is not None:
                                        pyautogui.click(replay_loc)
                                        self.root.after(0, self.update_bot_status, "Đã tự động bấm Bắt đầu xem video!", "purple")
                                        time.sleep(2)
                                except Exception:
                                    pass
                                if replay_img2 and os.path.exists(replay_img2):
                                    try:
                                        replay_loc = pyautogui.locateCenterOnScreen(replay_img2, confidence=0.8)
                                        if replay_loc is not None:
                                            pyautogui.click(replay_loc)
                                            self.root.after(0, self.update_bot_status, "Đã tự động bấm Xem Lại (Replay) video!", "purple")
                                            time.sleep(2)
                                    except Exception:
                                        pass
                                
                                time.sleep(1)
                            continue
                else:
                    try:
                        cond_loc = pyautogui.locateOnScreen(cond_img, confidence=0.8)
                    except Exception:
                        cond_loc = None
                    
                    if cond_loc is not None:
                        condition_met = True
                        self.root.after(0, self.update_bot_status, "Phát hiện Ảnh Điều Kiện!\nĐang xử lý click mục tiêu...", "green")
                        time.sleep(0.5) 
                
                if condition_met:
                    if self.target_mode.get() == "direct":
                        # Mode 1: Click trực tiếp
                        try:
                            target_loc = pyautogui.locateCenterOnScreen(target_img, confidence=0.8)
                        except Exception:
                            target_loc = None
                        if target_loc is not None:
                            pyautogui.click(target_loc)
                            self.root.after(0, self.update_bot_status, "Đã click chuyển bài trực tiếp!\nTạm nghỉ 10 giây...", "green")
                            time.sleep(10)
                            self.root.after(0, self.update_bot_status, "Tiếp tục quét màn hình tìm 100%...", "blue")
                        else:
                            self.root.after(0, self.update_bot_status, "Thấy 100% nhưng KHÔNG tìm thấy Ảnh mục tiêu!", "orange")
                            time.sleep(2)
                            
                    elif self.target_mode.get() == "checkmark":
                        # Mode 2: Dựa vào Tích xanh nhảy Y
                        try:
                            checks = list(pyautogui.locateAllOnScreen(target_img, confidence=0.8))
                        except Exception:
                            checks = []
                            
                        if checks:
                            lowest_check = max(checks, key=lambda loc: loc.top)
                            
                            offset = int(self.entry_offset.get())
                            skip = int(self.entry_skip.get())
                            
                            center_x = lowest_check.left + lowest_check.width / 2
                            center_y = lowest_check.top + lowest_check.height / 2
                            
                            target_y = center_y + offset * (skip + 1)
                            
                            # NE MIN (SKIP BY IMAGE)
                            if skip_img:
                                try:
                                    skip_locs = list(pyautogui.locateAllOnScreen(skip_img, confidence=0.7, grayscale=True))
                                    collision = True
                                    while collision:
                                        collision = False
                                        for loc in skip_locs:
                                            skip_y = loc.top + loc.height / 2
                                            if abs(target_y - skip_y) < max(30, offset * 0.8):
                                                target_y += offset
                                                collision = True
                                                self.root.after(0, self.update_bot_status, "Phát hiện Bài bị cấm!\nĐã tự động cộng dồn Y để né mìn an toàn.", "purple")
                                                time.sleep(1.5)
                                                break
                                except Exception:
                                    pass
                            
                            pyautogui.click(x=center_x, y=target_y)
                            
                            self.root.after(0, self.update_bot_status, f"Đã click bài mới!\nTạm nghỉ 10 giây...", "green")
                            time.sleep(10)
                            self.root.after(0, self.update_bot_status, "Tiếp tục quét màn hình tìm 100%...", "blue")
                        else:
                            self.root.after(0, self.update_bot_status, "Thấy 100% nhưng KHÔNG tìm thấy Tích xanh nào!", "orange")
                            time.sleep(2)
                            
                    elif self.target_mode.get() == "list_scan":
                        # Mode 3: Quét danh sách so khớp Icon Chung & Tích Xanh
                        try:
                            icons = list(pyautogui.locateAllOnScreen(target_img, confidence=0.7, grayscale=True))
                        except Exception:
                            icons = []
                            
                        if not icons:
                            self.root.after(0, self.update_bot_status, "Chưa tìm thấy Icon bài học chung nào!", "orange")
                            time.sleep(2)
                            continue
                            
                        # Sort icons top to bottom
                        icons = sorted(icons, key=lambda loc: loc.top)
                        
                        try:
                            checks = list(pyautogui.locateAllOnScreen(chk_img, confidence=0.7, grayscale=True))
                        except Exception:
                            checks = []
                            
                        clicked = False
                        for icon in icons:
                            icon_x = icon.left + icon.width / 2
                            icon_y = icon.top + icon.height / 2
                            
                            has_check = False
                            for chk in checks:
                                chk_y = chk.top + chk.height / 2
                                # Nếu tích xanh nằm ngang hàng với icon (lệch Y dưới 20px)
                                if abs(icon_y - chk_y) < 20:
                                    has_check = True
                                    break
                                    
                            if not has_check:
                                # Đây là bài CHƯA HỌC!
                                # Check xem có trùng Ảnh bài cấm không
                                is_skipped = False
                                if skip_img:
                                    try:
                                        skip_locs = list(pyautogui.locateAllOnScreen(skip_img, confidence=0.7, grayscale=True))
                                        for skip_loc in skip_locs:
                                            skip_y = skip_loc.top + skip_loc.height / 2
                                            if abs(icon_y - skip_y) < 30:
                                                is_skipped = True
                                                break
                                    except Exception:
                                        pass
                                        
                                if is_skipped:
                                    self.root.after(0, self.update_bot_status, "Đã né 1 bài bị cấm, quét bài tiếp theo...", "purple")
                                    continue # Chuyển sang icon bài học tiếp theo bên dưới
                                    
                                # An toàn -> CLICK!
                                pyautogui.click(x=icon_x, y=icon_y)
                                clicked = True
                                self.root.after(0, self.update_bot_status, "Đã click bài thiếu Tích xanh!\nTạm nghỉ 10 giây...", "green")
                                time.sleep(10)
                                self.root.after(0, self.update_bot_status, "Tiếp tục quét màn hình tìm 100%...", "blue")
                                break # Xong việc, dừng quét icon list
                                
                        if not clicked:
                            self.root.after(0, self.update_bot_status, "Tất cả các bài trên màn hình đều đã có Tích xanh!", "orange")
                            time.sleep(2)
                            
                else:
                    # Chưa đạt 100%, check auto replay
                    if replay_img:
                        try:
                            replay_loc = pyautogui.locateCenterOnScreen(replay_img, confidence=0.8)
                            if replay_loc is not None:
                                pyautogui.click(replay_loc)
                                self.root.after(0, self.update_bot_status, "Đã bấm nút Bắt đầu xem!\nTiếp tục chờ đạt 100%...", "purple")
                                time.sleep(5)
                                continue
                        except Exception:
                            pass
                            
                    if replay_img2:
                        try:
                            replay_loc = pyautogui.locateCenterOnScreen(replay_img2, confidence=0.8)
                            if replay_loc is not None:
                                pyautogui.click(replay_loc)
                                self.root.after(0, self.update_bot_status, "Đã bấm nút Xem Lại (Replay)!\nTiếp tục chờ đạt 100%...", "purple")
                                time.sleep(5)
                                continue
                        except Exception:
                            pass
                            
                    time.sleep(1)
                    
            except Exception:
                time.sleep(1)
            except Exception as e:
                err_str = str(e)
                if "Could not locate" in err_str or "ImageNotFound" in err_str:
                    time.sleep(1)
                else:
                    self.root.after(0, self.update_bot_status, f"Lỗi: {err_str}", "red")
                    time.sleep(2)
                
        self.root.after(0, self.update_bot_status, "Bot đã dừng.", "red")

    # === TAB 1 LOGIC (OLD CODE) ===
    def on_tree_click(self, event):
        region = self.tree.identify_region(event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x)
            if column == '#1':
                item = self.tree.identify_row(event.y)
                if item:
                    values = list(self.tree.item(item, "values"))
                    if values[0] == "☐":
                        values[0] = "☑"
                    else:
                        values[0] = "☐"
                    self.tree.item(item, values=values)
        
    def start_hook(self):
        mode = self.time_mode_var.get()
        val_str = ""
        if mode == "duration":
            val_str = self.entry_duration.get().strip()
            try:
                mins = float(val_str)
                if mins <= 0: raise ValueError()
            except ValueError:
                messagebox.showerror("Lỗi", "Số phút học phải là số lớn hơn 0 (ví dụ: 45 hoặc 30.5)!")
                return
        else:
            val_str = self.entry_time.get().strip()
            try:
                datetime.strptime(val_str, "%H:%M:%S")
            except ValueError:
                messagebox.showerror("Lỗi", "Sai định dạng thời gian.\nVui lòng nhập theo định dạng HH:MM:SS (ví dụ: 15:30:00)")
                return
            
        self.btn_hook.config(text="Đang chờ bấm F8...", state=tk.DISABLED)
        threading.Thread(target=self.wait_for_hotkey, args=(mode, val_str), daemon=True).start()
        
    def wait_for_hotkey(self, mode, val_str):
        keyboard.wait("F8")
        x, y = pyautogui.position()
        self.root.after(0, self.add_task_to_ui, mode, val_str, x, y)
        
    def add_task_to_ui(self, mode, val_str, x, y):
        self.task_counter += 1
        if mode == "duration":
            mins = float(val_str)
            duration_text = f"{mins:g} phút"
            time_text = "Tự cộng dồn"
        else:
            mins = 0
            duration_text = "--"
            time_text = val_str

        task = {
            'id': self.task_counter,
            'mode': mode,
            'duration_mins': mins,
            'duration_text': duration_text,
            'time': time_text,
            'x': x,
            'y': y,
            'status': "Chờ"
        }
        self.tasks.append(task)
        self.tree.insert("", tk.END, values=("☐", task['id'], task['duration_text'], task['time'], task['x'], task['y'], task['status']))
        self.btn_hook.config(text="📍 Bấm F8 để gán vị trí Số", state=tk.NORMAL)
        self.refresh_markers()
        
    def delete_selected_task(self):
        items_to_delete = []
        for item in self.tree.get_children():
            values = self.tree.item(item, "values")
            if values[0] == "☑":
                items_to_delete.append(item)
                
        if not items_to_delete:
            messagebox.showinfo("Thông báo", "Vui lòng tích (☑) vào các dòng bạn muốn xóa ở cột Chọn!")
            return
            
        for item in items_to_delete:
            item_values = self.tree.item(item, "values")
            task_id = int(item_values[1])
            self.tasks = [t for t in self.tasks if t['id'] != task_id]
            self.tree.delete(item)

        # Đánh lại số thứ tự 1, 2, 3...
        self.task_counter = len(self.tasks)
        for i, task in enumerate(self.tasks, start=1):
            task['id'] = i
            
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for task in self.tasks:
            self.tree.insert("", tk.END, values=("☐", task['id'], task['duration_text'], task['time'], task['x'], task['y'], task['status']))
            
        self.refresh_markers()

    def reset_all_tasks(self):
        self.tasks = []
        self.task_counter = 0
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.refresh_markers()

    def start_timer(self):
        popup_img = self.entry_popup.get().strip()
        if not self.tasks and not popup_img:
            messagebox.showerror("Lỗi", "Vui lòng thêm ít nhất 1 tọa độ HOẶC 1 ảnh nút Đồng ý!")
            return
            
        if self.tasks and all(t['status'] == "Đã click" for t in self.tasks) and not popup_img:
            messagebox.showinfo("Thông báo", "Tất cả các mốc thời gian đã được xử lý. Hãy thêm mới hoặc cập nhật!")
            return
            
        now = datetime.now()
        start_time_str = self.entry_start_time.get().strip()
        ref_time = now
        
        if start_time_str:
            try:
                parts = start_time_str.split(':')
                if len(parts) == 2:
                    start_time_str += ":00"
                parsed_time = datetime.strptime(start_time_str, "%H:%M:%S")
                target_start = now.replace(hour=parsed_time.hour, minute=parsed_time.minute, second=parsed_time.second, microsecond=0)
                if target_start < now - timedelta(seconds=60):
                    target_start += timedelta(days=1)
                ref_time = target_start
            except ValueError:
                messagebox.showerror("Lỗi", "Giờ bắt đầu không đúng định dạng HH:MM:SS (ví dụ 01:05:00 hoặc 13:05)!")
                return

        for index, task in enumerate(self.tasks):
            if task['status'] != "Đã click":
                if task.get('mode') == 'duration':
                    mins = task.get('duration_mins', 0)
                    target = ref_time + timedelta(minutes=mins)
                    task['target_dt'] = target
                    ref_time = target
                    task['time'] = target.strftime("%H:%M:%S")
                else:
                    t = datetime.strptime(task['time'], "%H:%M:%S")
                    target = now.replace(hour=t.hour, minute=t.minute, second=t.second, microsecond=0)
                    if target < now:
                        target += timedelta(days=1)
                    task['target_dt'] = target
                    ref_time = target
                # Cập nhật hiển thị giờ click dự kiến trên bảng
                self.update_task_time_ui(index, task['time'])
                task['status'] = "Chờ"
                
        self.is_running_tab1 = True
        self.btn_start.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self.btn_hook.config(state=tk.DISABLED)
        self.btn_delete.config(state=tk.DISABLED)
        
        threading.Thread(target=self.wait_and_click, daemon=True).start()
        
    def stop_timer(self):
        self.is_running_tab1 = False
        self.btn_start.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self.btn_hook.config(state=tk.NORMAL)
        self.btn_delete.config(state=tk.NORMAL)
        
    def wait_and_click(self):
        popup_img = self.entry_popup.get().strip()
        while self.is_running_tab1:
            now = datetime.now()
            for index, task in enumerate(self.tasks):
                if task['status'] != "Đã click":
                    rem_sec = (task['target_dt'] - now).total_seconds()
                    if rem_sec <= 0 and task['status'] != "Đã click":
                        # Ẩn bong bóng tạm thời để đảm bảo click lọt xuống cửa sổ web/ứng dụng bên dưới 100%
                        self.root.after(0, self.clear_markers)
                        time.sleep(0.05)
                        pyautogui.click(x=task['x'], y=task['y'])
                        task['status'] = "Đã click"
                        self.root.after(0, self.update_task_status_ui, index, "Đã click")
                        time.sleep(0.1)
                        self.root.after(0, self.refresh_markers)
                    elif task['status'] != "Đã click":
                        rem_m = int(rem_sec // 60)
                        rem_s = int(rem_sec % 60)
                        if rem_m > 0:
                            status_str = f"Còn {rem_m}m {rem_s:02d}s"
                        else:
                            status_str = f"Còn {rem_s:02d}s"
                        self.root.after(0, self.update_task_status_ui, index, status_str)
                        
            if popup_img and os.path.exists(popup_img):
                try:
                    popup_loc = pyautogui.locateCenterOnScreen(popup_img, confidence=0.8)
                    if popup_loc is not None:
                        pyautogui.click(popup_loc)
                        time.sleep(1)
                except Exception:
                    pass

            time.sleep(0.5)
            
            if self.tasks:
                all_finished = all(t['status'] == "Đã click" for t in self.tasks)
                if all_finished and not popup_img:
                    self.root.after(0, self.on_all_tasks_done)
                    break

    def update_task_time_ui(self, index, new_time_str):
        children = self.tree.get_children()
        if index < len(children):
            item = children[index]
            values = list(self.tree.item(item, "values"))
            values[3] = new_time_str
            self.tree.item(item, values=values)
                
    def update_task_status_ui(self, index, new_status):
        children = self.tree.get_children()
        if index < len(children):
            item = children[index]
            values = list(self.tree.item(item, "values"))
            if len(values) > 6:
                values[6] = new_status
                self.tree.item(item, values=values)
            
    def on_all_tasks_done(self):
        self.stop_timer()
        messagebox.showinfo("Hoàn tất", "Đã thực hiện xong (hoặc bỏ qua) toàn bộ danh sách click!")

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoClickerApp(root)
    root.mainloop()
