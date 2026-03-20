from __future__ import annotations

import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk

from config.settings import AppSettings
from core.reasoning_engine import ReasoningEngine
from core.profile_manager import ProfileManager
from core.memory_manager import MemoryManager


class MISApp(tk.Tk):
    def __init__(
        self,
        settings: AppSettings,
        reasoning_engine: ReasoningEngine,
        profile_manager: ProfileManager,
        memory_manager: MemoryManager,
    ) -> None:
        super().__init__()
        self.settings = settings
        self.reasoning_engine = reasoning_engine
        self.profile_manager = profile_manager
        self.memory_manager = memory_manager
        self.external_user_id = settings.user_id

        self.title(settings.app_name)
        self.geometry("1180x760")
        self.minsize(980, 650)

        self.status_var = tk.StringVar(value="Ready")

        self._build_layout()
        self._load_profile_view()
        self._load_chat_history()
        self._run_onboarding_if_needed()

    def _build_layout(self) -> None:
        container = ttk.Frame(self, padding=10)
        container.pack(fill=tk.BOTH, expand=True)

        container.columnconfigure(0, weight=3)
        container.columnconfigure(1, weight=2)
        container.rowconfigure(0, weight=1)

        self.chat_frame = ttk.LabelFrame(container, text="Conversation")
        self.chat_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        self.chat_text = scrolledtext.ScrolledText(self.chat_frame, wrap=tk.WORD, font=("Segoe UI", 10))
        self.chat_text.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        self.chat_text.configure(state=tk.DISABLED)

        entry_row = ttk.Frame(self.chat_frame)
        entry_row.pack(fill=tk.X, padx=8, pady=(0, 8))

        self.input_var = tk.StringVar()
        self.input_entry = ttk.Entry(entry_row, textvariable=self.input_var)
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.input_entry.bind("<Return>", self._send_message)

        send_btn = ttk.Button(entry_row, text="Send", command=self._send_message)
        send_btn.pack(side=tk.LEFT, padx=(6, 0))

        right_panel = ttk.Frame(container)
        right_panel.grid(row=0, column=1, sticky="nsew")
        right_panel.rowconfigure(1, weight=1)

        self.profile_frame = ttk.LabelFrame(right_panel, text="Identity Profile")
        self.profile_frame.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        memory_frame = ttk.LabelFrame(right_panel, text="Memory Viewer")
        memory_frame.grid(row=1, column=0, sticky="nsew")
        memory_frame.rowconfigure(1, weight=1)

        controls = ttk.Frame(memory_frame)
        controls.grid(row=0, column=0, sticky="ew", padx=8, pady=8)
        self.search_var = tk.StringVar()
        ttk.Entry(controls, textvariable=self.search_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(controls, text="Search", command=self._search_memory).pack(side=tk.LEFT, padx=(6, 0))

        self.memory_text = scrolledtext.ScrolledText(memory_frame, wrap=tk.WORD, height=16, font=("Consolas", 9))
        self.memory_text.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        self.memory_text.configure(state=tk.DISABLED)

        footer = ttk.Frame(self)
        footer.pack(fill=tk.X, padx=10, pady=(0, 8))
        ttk.Label(footer, text="Status:").pack(side=tk.LEFT)
        ttk.Label(footer, textvariable=self.status_var).pack(side=tk.LEFT, padx=(6, 0))

    def _load_profile_view(self) -> None:
        for child in self.profile_frame.winfo_children():
            child.destroy()

        profile = self.profile_manager.get_profile(self.external_user_id)
        rows = [
            ("Name", profile.display_name),
            ("Risk Tolerance", f"{profile.risk_tolerance:.2f}"),
            ("Communication", profile.communication_style),
            ("Tone", profile.emotional_tone_preference),
            ("Ambition", f"{profile.ambition_level:.2f}"),
            ("Goals", profile.goals or "Not set"),
        ]
        for i, (k, v) in enumerate(rows):
            ttk.Label(self.profile_frame, text=f"{k}:", font=("Segoe UI", 9, "bold")).grid(row=i, column=0, sticky="w", padx=8, pady=2)
            ttk.Label(self.profile_frame, text=v, wraplength=280).grid(row=i, column=1, sticky="w", padx=8, pady=2)

        ttk.Button(self.profile_frame, text="Edit Profile", command=self._open_onboarding_dialog).grid(
            row=len(rows), column=0, columnspan=2, padx=8, pady=(6, 8), sticky="ew"
        )

    def _run_onboarding_if_needed(self) -> None:
        profile = self.profile_manager.get_profile(self.external_user_id)
        if profile.goals.strip():
            return
        self.after(250, self._open_onboarding_dialog)

    def _open_onboarding_dialog(self) -> None:
        profile = self.profile_manager.get_profile(self.external_user_id)

        top = tk.Toplevel(self)
        top.title("Personality Onboarding")
        top.geometry("420x380")
        top.transient(self)
        top.grab_set()

        risk = tk.DoubleVar(value=profile.risk_tolerance)
        ambition = tk.DoubleVar(value=profile.ambition_level)
        communication = tk.StringVar(value=profile.communication_style)
        tone = tk.StringVar(value=profile.emotional_tone_preference)
        goals = tk.StringVar(value=profile.goals)

        ttk.Label(top, text="Risk tolerance").pack(anchor="w", padx=12, pady=(12, 0))
        ttk.Scale(top, from_=0, to=1, variable=risk).pack(fill=tk.X, padx=12)

        ttk.Label(top, text="Ambition level").pack(anchor="w", padx=12, pady=(12, 0))
        ttk.Scale(top, from_=0, to=1, variable=ambition).pack(fill=tk.X, padx=12)

        ttk.Label(top, text="Communication style").pack(anchor="w", padx=12, pady=(12, 0))
        ttk.Combobox(top, textvariable=communication, values=["simple", "balanced", "detailed"], state="readonly").pack(fill=tk.X, padx=12)

        ttk.Label(top, text="Preferred emotional tone").pack(anchor="w", padx=12, pady=(12, 0))
        ttk.Combobox(top, textvariable=tone, values=["calm", "balanced", "motivational"], state="readonly").pack(fill=tk.X, padx=12)

        ttk.Label(top, text="Current goals").pack(anchor="w", padx=12, pady=(12, 0))
        ttk.Entry(top, textvariable=goals).pack(fill=tk.X, padx=12)

        def save_profile() -> None:
            p = self.profile_manager.get_profile(self.external_user_id)
            self.profile_manager.upsert_profile_from_onboarding(
                user_row_id=p.user_row_id,
                risk_tolerance=float(risk.get()),
                communication_style=communication.get(),
                emotional_tone_preference=tone.get(),
                ambition_level=float(ambition.get()),
                goals=goals.get().strip(),
            )
            top.destroy()
            self._load_profile_view()

        ttk.Button(top, text="Save", command=save_profile).pack(fill=tk.X, padx=12, pady=14)

    def _append_chat(self, speaker: str, text: str) -> None:
        self.chat_text.configure(state=tk.NORMAL)
        self.chat_text.insert(tk.END, f"{speaker}: {text}\n\n")
        self.chat_text.see(tk.END)
        self.chat_text.configure(state=tk.DISABLED)

    def _set_status(self, status: str) -> None:
        self.status_var.set(status)

    def _send_message(self, _event=None) -> None:
        message = self.input_var.get().strip()
        if not message:
            return
        self.input_var.set("")
        self._append_chat("You", message)
        self._set_status("Thinking...")

        thread = threading.Thread(target=self._handle_ai_response, args=(message,), daemon=True)
        thread.start()

    def _handle_ai_response(self, message: str) -> None:
        try:
            response = self.reasoning_engine.process_user_message(self.external_user_id, message)
            self.after(0, lambda: self._append_chat("MIS", response))
            self.after(0, self._load_profile_view)
            self.after(0, self._search_memory)
            self.after(0, lambda: self._set_status("Ready"))
        except Exception as exc:
            self.after(0, lambda: self._set_status("Error"))
            self.after(0, lambda: messagebox.showerror("MIS Error", str(exc)))

    def _load_chat_history(self) -> None:
        profile = self.profile_manager.get_profile(self.external_user_id)
        self.memory_manager.load_recent_to_short_term(profile.user_row_id)
        messages = self.memory_manager.fetch_recent_messages(profile.user_row_id, limit=30)
        for msg in reversed(messages):
            who = "You" if msg["role"] == "user" else "MIS"
            self._append_chat(who, msg["content"])

    def _search_memory(self) -> None:
        profile = self.profile_manager.get_profile(self.external_user_id)
        query = self.search_var.get().strip()
        if query:
            results = self.memory_manager.search_long_term_memory(profile.user_row_id, query=query, limit=40)
        else:
            results = self.memory_manager.fetch_recent_messages(profile.user_row_id, limit=40)

        self.memory_text.configure(state=tk.NORMAL)
        self.memory_text.delete("1.0", tk.END)
        for item in results:
            self.memory_text.insert(
                tk.END,
                f"[{item['created_at']}] {item['role']} | {item.get('category', 'general')} | important={item.get('is_important', 0)}\n"
                f"{item['content']}\n\n",
            )
        self.memory_text.configure(state=tk.DISABLED)
