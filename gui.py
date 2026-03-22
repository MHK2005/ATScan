import os
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
from project import extract_text, score_resume, build_resume


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

ACCENT = "#3B82F6"
ACCENT_HOVER = "#2563EB"
SUCCESS = "#22C55E"
WARNING = "#F59E0B"
DANGER = "#EF4444"
BG_CARD = "#1E293B"
BG_INPUT = "#0F172A"
TEXT_DIM = "#94A3B8"


def score_color(score):
    if score >= 70:
        return SUCCESS
    elif score >= 40:
        return WARNING
    return DANGER


class ATScanApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("ATScan — ATS Resume Scanner")
        self.geometry("900x720")
        self.minsize(820, 640)
        self.configure(fg_color="#0F172A")

        header = ctk.CTkFrame(self, fg_color="#0F172A", height=60)
        header.pack(fill="x", padx=24, pady=(18, 0))
        ctk.CTkLabel(
            header, text="ATScan",
            font=("Segoe UI", 28, "bold"), text_color="white",
        ).pack(side="left")
        ctk.CTkLabel(
            header, text="ATS Resume Scanner",
            font=("Segoe UI", 14), text_color=TEXT_DIM,
        ).pack(side="left", padx=(12, 0), pady=(8, 0))

        self.tabs = ctk.CTkTabview(
            self, fg_color=BG_CARD,
            segmented_button_fg_color=BG_INPUT,
            segmented_button_selected_color=ACCENT,
            segmented_button_unselected_color="#1E293B",
            corner_radius=12,
        )
        self.tabs.pack(fill="both", expand=True, padx=24, pady=18)

        self._build_analyze_tab()
        self._build_build_tab()

    def _build_analyze_tab(self):
        tab = self.tabs.add("  Analyze Resume  ")

        picker = ctk.CTkFrame(tab, fg_color="transparent")
        picker.pack(fill="x", padx=16, pady=(16, 8))

        self.file_entry = ctk.CTkEntry(
            picker,
            placeholder_text="Select a resume file (.txt / .pdf / .docx)",
            font=("Segoe UI", 13), fg_color=BG_INPUT,
            border_color="#334155", height=42,
        )
        self.file_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        ctk.CTkButton(
            picker, text="Browse", width=100, height=42,
            fg_color=ACCENT, hover_color=ACCENT_HOVER,
            font=("Segoe UI", 13, "bold"),
            command=self._browse_file,
        ).pack(side="left")

        self.analyze_btn = ctk.CTkButton(
            tab, text="Analyze", height=44, corner_radius=10,
            fg_color=ACCENT, hover_color=ACCENT_HOVER,
            font=("Segoe UI", 15, "bold"),
            command=self._analyze,
        )
        self.analyze_btn.pack(fill="x", padx=16, pady=(4, 12))

        self.result_frame = ctk.CTkScrollableFrame(
            tab, fg_color=BG_INPUT, corner_radius=10,
        )
        self.result_frame.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        self.result_widgets = []

    def _browse_file(self):
        path = filedialog.askopenfilename(
            filetypes=[
                ("Resume Files", "*.txt *.pdf *.docx"),
                ("All Files", "*.*"),
            ]
        )
        if path:
            self.file_entry.delete(0, "end")
            self.file_entry.insert(0, path)

    def _analyze(self):
        filepath = self.file_entry.get().strip().strip("\"' ")
        if not filepath:
            messagebox.showwarning("No File", "Please select a resume file first.")
            return

        for widget in self.result_widgets:
            widget.destroy()
        self.result_widgets.clear()

        try:
            text = extract_text(filepath)
        except (FileNotFoundError, ValueError) as e:
            messagebox.showerror("Error", str(e))
            return

        if not text.strip():
            messagebox.showwarning("Empty", "The file appears to be empty.")
            return

        result = score_resume(text)
        self._show_results(result)

    def _show_results(self, result):
        parent = self.result_frame
        score = result["total_score"]
        color = score_color(score)

        score_label = ctk.CTkLabel(
            parent, text=f"{score} / 100",
            font=("Segoe UI", 48, "bold"), text_color=color,
        )
        score_label.pack(pady=(20, 4))
        self.result_widgets.append(score_label)

        if score >= 80:
            grade_text = "Excellent"
        elif score >= 60:
            grade_text = "Good"
        elif score >= 40:
            grade_text = "Needs Work"
        else:
            grade_text = "Poor"

        grade = ctk.CTkLabel(
            parent, text=grade_text,
            font=("Segoe UI", 16), text_color=TEXT_DIM,
        )
        grade.pack(pady=(0, 16))
        self.result_widgets.append(grade)

        breakdown = result["breakdown"]
        categories = [
            ("Sections",     breakdown["sections"],     30),
            ("Keywords",     breakdown["keywords"],     25),
            ("Action Verbs", breakdown["action_verbs"], 20),
            ("Word Count",   breakdown["word_count"],   15),
            ("Formatting",   breakdown["formatting"],   10),
        ]

        for label_text, val, max_val in categories:
            row = ctk.CTkFrame(parent, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=3)
            self.result_widgets.append(row)

            ctk.CTkLabel(
                row, text=label_text, width=110, anchor="w",
                font=("Segoe UI", 13), text_color="#CBD5E1",
            ).pack(side="left")

            pct = val / max_val if max_val else 0
            bar_color = SUCCESS if pct >= 0.7 else WARNING if pct >= 0.4 else DANGER

            bar = ctk.CTkProgressBar(
                row, height=14, corner_radius=6,
                progress_color=bar_color, fg_color="#1E293B",
            )
            bar.set(pct)
            bar.pack(side="left", fill="x", expand=True, padx=8)

            ctk.CTkLabel(
                row, text=f"{val}/{max_val}", width=50,
                font=("Segoe UI", 12), text_color=TEXT_DIM,
            ).pack(side="left")

        sep = ctk.CTkFrame(parent, fg_color="#334155", height=1)
        sep.pack(fill="x", padx=20, pady=12)
        self.result_widgets.append(sep)

        fb_title = ctk.CTkLabel(
            parent, text="Feedback",
            font=("Segoe UI", 15, "bold"), text_color="white", anchor="w",
        )
        fb_title.pack(fill="x", padx=20, pady=(0, 6))
        self.result_widgets.append(fb_title)

        for line in result["feedback"]:
            fb = ctk.CTkLabel(
                parent, text=f"  •  {line}",
                font=("Segoe UI", 13), text_color="#CBD5E1",
                anchor="w", wraplength=660, justify="left",
            )
            fb.pack(fill="x", padx=20, pady=1)
            self.result_widgets.append(fb)

    def _build_build_tab(self):
        tab = self.tabs.add("  Build Resume  ")

        form = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=16, pady=16)

        self.build_fields = {}

        simple_fields = [
            ("name",     "Full Name",     ""),
            ("email",    "Email",          "you@email.com"),
            ("phone",    "Phone",          "+92 300 1234567"),
            ("linkedin", "LinkedIn URL",   "linkedin.com/in/yourprofile  (optional)"),
            ("github",   "GitHub URL",     "github.com/yourusername  (optional)"),
        ]

        for key, label, placeholder in simple_fields:
            self._add_label(form, label)
            widget = ctk.CTkEntry(
                form, height=40, font=("Segoe UI", 13),
                fg_color=BG_INPUT, border_color="#334155",
                corner_radius=8, placeholder_text=placeholder,
            )
            widget.pack(fill="x", pady=(0, 6))
            self.build_fields[key] = (widget, False)

        multiline_fields = [
            ("summary",        "Professional Summary",  70),
            ("skills",         "Skills",                80),
            ("experience",     "Work Experience",       160),
            ("education",      "Education",             100),
            ("projects",       "Projects",              140),
            ("certifications", "Certifications",         60),
        ]

        for key, label, height in multiline_fields:
            self._add_label(form, label)
            widget = ctk.CTkTextbox(
                form, height=height, font=("Segoe UI", 13),
                fg_color=BG_INPUT, border_color="#334155", corner_radius=8,
            )
            widget.pack(fill="x", pady=(0, 6))
            self.build_fields[key] = (widget, True)

        self.gen_btn = ctk.CTkButton(
            form, text="Generate Resume", height=46, corner_radius=10,
            fg_color=ACCENT, hover_color=ACCENT_HOVER,
            font=("Segoe UI", 15, "bold"),
            command=self._generate,
        )
        self.gen_btn.pack(fill="x", pady=(20, 4))

        self.build_status = ctk.CTkLabel(
            form, text="",
            font=("Segoe UI", 13), text_color=TEXT_DIM,
        )
        self.build_status.pack(pady=(4, 0))

    def _add_label(self, parent, text):
        ctk.CTkLabel(
            parent, text=text,
            font=("Segoe UI", 13, "bold"),
            text_color="#CBD5E1", anchor="w",
        ).pack(fill="x", pady=(12, 2))

    def _get_field(self, key):
        widget, multiline = self.build_fields[key]
        if multiline:
            return widget.get("1.0", "end").strip()
        return widget.get().strip()

    def _generate(self):
        name = self._get_field("name")
        if not name:
            messagebox.showwarning("Missing", "Please enter a name.")
            return

        self.gen_btn.configure(state="disabled", text="Generating...")
        self.build_status.configure(text="")

        data = {key: self._get_field(key) for key in self.build_fields}

        def run():
            try:
                result = build_resume(data)
                score = result["score_result"]["total_score"]
                path = os.path.abspath(result["filepath"])
                color = score_color(score)
                self.after(0, lambda: self._on_generate_done(path, score, color))
            except Exception as e:
                self.after(0, lambda: self._on_generate_error(str(e)))

        threading.Thread(target=run, daemon=True).start()

    def _on_generate_done(self, path, score, color):
        self.gen_btn.configure(state="normal", text="Generate Resume")
        self.build_status.configure(
            text=f"Resume saved!   ATS Score: {score}/100",
            text_color=color,
        )
        if messagebox.askyesno("Done", f"Resume generated with ATS score {score}/100.\n\nOpen the file?"):
            os.startfile(path)

    def _on_generate_error(self, msg):
        self.gen_btn.configure(state="normal", text="Generate Resume")
        messagebox.showerror("Error", msg)


def launch():
    app = ATScanApp()
    app.mainloop()


if __name__ == "__main__":
    launch()

