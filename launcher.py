#!/usr/bin/env python3
"""DiligenceBinder graphical launcher."""
import json
import os
import sys
import threading
import time
import traceback
import webbrowser
from pathlib import Path
from tkinter import Tk, Frame, Label, Button, Entry, Text, Scrollbar, filedialog, messagebox, ttk

# PyInstaller 路径适配
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys._MEIPASS)
else:
    BASE_DIR = Path(__file__).parent


def load_env():
    env = {}
    env_file = BASE_DIR / ".env"
    if env_file.exists():
        for line in open(env_file, encoding="utf-8").readlines():
            line = line.strip()
            if line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    return env


ENV = load_env()
os.environ.setdefault("TEXTIN_APP_ID", ENV.get("TEXTIN_APP_ID", ""))
os.environ.setdefault("TEXTIN_SECRET_CODE", ENV.get("TEXTIN_SECRET_CODE", ""))
os.environ.setdefault("DEEPSEEK_API_KEY", ENV.get("DEEPSEEK_API_KEY", ""))


class App:
    def __init__(self):
        self.root = Tk()
        self.root.title("DiligenceBinder — IBD 底稿凭证智能提取")
        self.root.geometry("680x520")
        self.root.resizable(True, True)
        self.root.configure(bg="#f0f2f5")

        # 标题
        header = Frame(self.root, bg="#1a1a2e", height=60)
        header.pack(fill="x")
        Label(header, text="DiligenceBinder", font=("Microsoft YaHei", 20, "bold"),
              fg="white", bg="#1a1a2e").pack(pady=10)
        Label(header, text="非标准扫描凭证 PDF → 结构化底稿 Excel", font=("Microsoft YaHei", 10),
              fg="#aaa", bg="#1a1a2e").pack()

        # 文件夹选择
        f1 = Frame(self.root, bg="#f0f2f5")
        f1.pack(fill="x", padx=20, pady=(20, 5))
        Label(f1, text="📁 PDF 文件夹:", font=("Microsoft YaHei", 12), bg="#f0f2f5").pack(side="left")
        self.folder_var = ""
        self.folder_label = Label(f1, text="未选择", font=("Microsoft YaHei", 12),
                                  fg="#888", bg="white", relief="sunken", anchor="w", width=35)
        self.folder_label.pack(side="left", padx=(8, 8), fill="x", expand=True)
        Button(f1, text="浏览...", font=("Microsoft YaHei", 11),
               command=self.choose_folder, padx=12).pack(side="right")

        # 输出目录
        f2 = Frame(self.root, bg="#f0f2f5")
        f2.pack(fill="x", padx=20, pady=5)
        Label(f2, text="📤 输出目录:", font=("Microsoft YaHei", 12), bg="#f0f2f5").pack(side="left")
        self.out_var = ""
        self.out_label = Label(f2, text="(同 PDF 文件夹)", font=("Microsoft YaHei", 12),
                               fg="#888", bg="white", relief="sunken", anchor="w", width=35)
        self.out_label.pack(side="left", padx=(8, 8), fill="x", expand=True)
        Button(f2, text="浏览...", font=("Microsoft YaHei", 11),
               command=self.choose_output, padx=12).pack(side="right")

        # 按钮
        f3 = Frame(self.root, bg="#f0f2f5")
        f3.pack(fill="x", padx=20, pady=15)
        self.start_btn = Button(f3, text="▶ 开始提取", font=("Microsoft YaHei", 14, "bold"),
                                bg="#e94560", fg="white", padx=30, pady=6,
                                command=self.start)
        self.start_btn.pack()

        # 进度条
        f4 = Frame(self.root, bg="#f0f2f5")
        f4.pack(fill="x", padx=20, pady=(0, 5))
        self.progress = ttk.Progressbar(f4, mode="determinate", length=620)
        self.progress.pack()
        self.progress_label = Label(f4, text="", font=("Microsoft YaHei", 9),
                                    bg="#f0f2f5", fg="#888")
        self.progress_label.pack()

        # 日志
        f5 = Frame(self.root, bg="#f0f2f5")
        f5.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        Label(f5, text="处理日志:", font=("Microsoft YaHei", 9), bg="#f0f2f5", fg="#666").pack(anchor="w")
        log_frame = Frame(f5, bg="white")
        log_frame.pack(fill="both", expand=True)
        self.log_text = Text(log_frame, font=("Consolas", 9), wrap="word",
                             bg="#1a1a2e", fg="#0f0", relief="flat", padx=8, pady=8)
        self.log_text.pack(side="left", fill="both", expand=True)
        scroll = Scrollbar(log_frame, command=self.log_text.yview)
        scroll.pack(side="right", fill="y")
        self.log_text.config(yscrollcommand=scroll.set)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def log(self, msg):
        self.log_text.insert("end", msg + "\n")
        self.log_text.see("end")
        self.root.update_idletasks()

    def choose_folder(self):
        path = filedialog.askdirectory(title="选择包含 PDF 的文件夹")
        if path:
            self.folder_var = path
            self.folder_label.config(text=path, fg="black")
            if not self.out_var:
                self.out_var = path
                self.out_label.config(text=path, fg="black")

    def choose_output(self):
        path = filedialog.askdirectory(title="选择输出目录")
        if path:
            self.out_var = path
            self.out_label.config(text=path, fg="black")

    def start(self):
        if not self.folder_var:
            messagebox.showwarning("提示", "请先选择包含 PDF 的文件夹")
            return

        self.start_btn.config(state="disabled", text="处理中...")
        self.progress["value"] = 0
        self.progress_label.config(text="")
        self.log_text.delete("1.0", "end")
        threading.Thread(target=self.run_pipeline, daemon=True).start()

    def run_pipeline(self):
        try:
            # Import pipeline modules from BASE_DIR
            sys.path.insert(0, str(BASE_DIR))

            self.log("=" * 50)
            self.log("  DiligenceBinder — 开始处理")
            self.log("=" * 50)
            self.log(f"  PDF 文件夹: {self.folder_var}")
            self.log(f"  输出目录: {self.out_var or self.folder_var}")

            # Step 1: Collect PDFs
            pdf_dir = Path(self.folder_var)
            pdf_files = list(pdf_dir.rglob("*.pdf"))
            if not pdf_files:
                self.log("❌ 未找到 PDF 文件!")
                self.root.after(0, lambda: self.start_btn.config(
                    state="normal", text="▶ 开始提取"))
                return
            self.log(f"  找到 {len(pdf_files)} 份 PDF")

            # Step 2: Process each PDF
            from pipeline_items import process_pdf
            output_base = Path(self.out_var or self.folder_var) / "DiligenceBinder_Output"
            output_base.mkdir(parents=True, exist_ok=True)

            all_items = []
            total = len(pdf_files)
            for i, pdf_path in enumerate(pdf_files):
                pdf_name = pdf_path.stem
                self.log(f"  [{i+1}/{total}] {pdf_name} ...")
                self.progress["value"] = (i / total) * 50  # First half: extraction
                self.progress_label.config(text=f"提取: {i+1}/{total}")
                self.root.update_idletasks()

                try:
                    items = process_pdf(str(pdf_path), output_base, verbose=False)
                    all_items.extend(items)
                    self.log(f"    ✅ {len(items)} 个单据")
                except Exception as e:
                    self.log(f"    ❌ 错误: {e}")

            # Step 3: Generate review HTML
            self.log("")
            self.log("  生成审核页面...")
            self.progress["value"] = 60
            self.progress_label.config(text="生成审核页面...")
            self.root.update_idletasks()

            from build_review_html import build_html as gen_html
            # Convert intermediate.json data to build_html format
            pdfs_data = []
            for d in sorted(output_base.iterdir()):
                if d.is_dir():
                    ij = d / "intermediate.json"
                    if ij.exists():
                        raw = json.loads(ij.read_text(encoding="utf-8"))
                        items = []
                        for item in raw.get("items", []):
                            items.append({
                                "页码": item.get("页码", 0),
                                "单据序号": item.get("单据序号", 1),
                                "单据类型": item.get("单据类型", ""),
                                "文件路径": item.get("文件路径", ""),
                                "凭证编号": item.get("凭证编号", ""),
                                "记账日期": item.get("记账日期", ""),
                                "公司名称": item.get("公司名称", ""),
                                "摘要": item.get("摘要", ""),
                                "金额": item.get("金额", ""),
                                "发票号码": item.get("发票号码", ""),
                                "开票日期": item.get("开票日期", ""),
                                "销售方名称": item.get("销售方名称", ""),
                                "价税合计": item.get("价税合计", ""),
                                "回单编号": item.get("回单编号", ""),
                                "交易日期": item.get("交易日期", ""),
                                "交易金额": item.get("交易金额", ""),
                            })
                        # Load page texts from markdown files
                        import re as _re
                        texts = {}
                        pages_dir = d / "pages"
                        if pages_dir.exists():
                            for md_file in sorted(pages_dir.glob("p*_markdown.md")):
                                try:
                                    pn = int(md_file.stem.split("_")[0][1:])
                                    raw_md = md_file.read_text(encoding="utf-8")
                                    txt = _re.sub(r'<[^>]+>', ' ', raw_md)
                                    txt = _re.sub(r'\s+', ' ', txt).strip()
                                    texts[str(pn)] = txt
                                except:
                                    pass
                        pdfs_data.append({
                            "pdf_name": raw["pdf_name"],
                            "total_pages": raw.get("total_pages", 0),
                            "items": items,
                            "texts": texts,
                        })

            if pdfs_data:
                # Render page images for the HTML
                self.log("  渲染页面图片...")
                self.progress["value"] = 70
                self.progress_label.config(text="渲染页面图片...")
                self.root.update_idletasks()

                import fitz
                img_dir = output_base / "page_images"
                img_dir.mkdir(exist_ok=True)
                img_count = 0
                for pdf_data in pdfs_data:
                    pdf_name = pdf_data["pdf_name"]
                    # Find PDF file: try stored path first, then search in folder
                    pdf_path = None
                    for item in pdf_data.get("items", []):
                        fp = item.get("文件路径", "")
                        if fp:
                            candidate = Path(fp)
                            if candidate.exists():
                                pdf_path = candidate; break
                    if not pdf_path:
                        # Search by filename in the PDF folder
                        for f in pdf_dir.rglob(f"{pdf_name}.pdf"):
                            pdf_path = f; break
                    if not pdf_path:
                        self.log(f"    ⚠️ 找不到 PDF: {pdf_name}")
                        continue
                    doc = fitz.open(pdf_path)
                    for pn in range(1, pdf_data.get("total_pages", 0) + 1):
                        img_file = img_dir / f"{pdf_name}_p{pn}.jpg"
                        if not img_file.exists() and pn <= len(doc):
                            doc[pn-1].get_pixmap(dpi=120).save(str(img_file))
                            img_count += 1
                    doc.close()
                self.log(f"    ✅ {img_count} 张页面图片")

                html = gen_html(pdfs_data)
                html_path = output_base / "审核页面.html"
                html_path.write_text(html, encoding="utf-8")
                self.log(f"  ✅ 审核页面: {html_path}")
                self.progress["value"] = 100
                self.progress_label.config(text="完成!")
                self.root.update_idletasks()

                # Open in browser
                webbrowser.open(f"file:///{html_path}")
            else:
                self.log("  ⚠️ 无数据可生成审核页面")
                self.progress["value"] = 100

            self.log("")
            self.log("=" * 50)
            self.log("  处理完成!")
            self.log(f"  输出目录: {output_base}")
            self.log(f"  审核页面: {output_base / '审核页面.html'}")
            self.log("=" * 50)

        except Exception as e:
            self.log(f"❌ 严重错误: {e}")
            self.log(traceback.format_exc())

        self.root.after(0, lambda: self.start_btn.config(
            state="normal", text="▶ 开始提取"))

    def on_close(self):
        self.root.destroy()


def main():
    app = App()
    app.root.mainloop()


if __name__ == "__main__":
    main()
