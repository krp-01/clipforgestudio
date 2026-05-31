from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox

from config.settings import (
    DEFAULT_DETAIL_LEVEL,
    DEFAULT_GOALS,
    DEFAULT_RESPONSE_STYLE,
    DEFAULT_USER_NAME,
)
from main import MISSystem


class MISApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("MIS – Memory Identity Stratified")
        self.geometry("1180x760")

        self.system = MISSystem()
        self._build_onboarding()
        self._build_layout()
        self.status_var.set("Gata")

    def _build_onboarding(self) -> None:
        dialog = tk.Toplevel(self)
        dialog.title("Onboarding MIS")
        dialog.transient(self)
        dialog.grab_set()

        fields = {
            "Nume utilizator": tk.StringVar(value=DEFAULT_USER_NAME),
            "Obiective": tk.StringVar(value=DEFAULT_GOALS),
            "Stil răspuns": tk.StringVar(value=DEFAULT_RESPONSE_STYLE),
            "Nivel detaliu": tk.StringVar(value=DEFAULT_DETAIL_LEVEL),
        }

        for idx, (label, var) in enumerate(fields.items()):
            ttk.Label(dialog, text=label).grid(row=idx, column=0, padx=8, pady=6, sticky="w")
            ttk.Entry(dialog, textvariable=var, width=42).grid(row=idx, column=1, padx=8, pady=6)

        def submit() -> None:
            self.system.onboard_user(
                fields["Nume utilizator"].get().strip() or DEFAULT_USER_NAME,
                fields["Obiective"].get().strip(),
                fields["Stil răspuns"].get().strip() or DEFAULT_RESPONSE_STYLE,
                fields["Nivel detaliu"].get().strip() or DEFAULT_DETAIL_LEVEL,
            )
            dialog.destroy()

        ttk.Button(dialog, text="Continuă", command=submit).grid(row=5, column=0, columnspan=2, pady=10)
        self.wait_window(dialog)

    def _build_layout(self) -> None:
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=1)

        left = ttk.Frame(self)
        left.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        left.rowconfigure(0, weight=1)
        left.columnconfigure(0, weight=1)

        self.chat = tk.Text(left, wrap="word", state="disabled", font=("Segoe UI", 10))
        self.chat.grid(row=0, column=0, sticky="nsew")

        input_frame = ttk.Frame(left)
        input_frame.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        input_frame.columnconfigure(0, weight=1)

        self.input_var = tk.StringVar()
        entry = ttk.Entry(input_frame, textvariable=self.input_var)
        entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        entry.bind("<Return>", lambda _: self.send_message())

        ttk.Button(input_frame, text="Trimite", command=self.send_message).grid(row=0, column=1, padx=(0, 6))
        ttk.Button(input_frame, text="Șterge conversația", command=self.clear_chat).grid(row=0, column=2)

        right = ttk.Frame(self)
        right.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=10)
        right.columnconfigure(0, weight=1)

        self.identity_text = self._make_panel(right, "Identitate", 0)
        self.emotions_text = self._make_panel(right, "Emoții", 1)
        self.goals_text = self._make_panel(right, "Scopuri active", 2)
        self.memories_text = self._make_panel(right, "Memorii relevante", 3)

        self.status_var = tk.StringVar(value="Gata")
        ttk.Label(self, textvariable=self.status_var, anchor="w").grid(row=1, column=0, columnspan=2, sticky="ew", padx=10)

    def _make_panel(self, parent: ttk.Frame, title: str, row: int) -> tk.Text:
        frame = ttk.LabelFrame(parent, text=title)
        frame.grid(row=row, column=0, sticky="nsew", pady=(0, 8))
        parent.rowconfigure(row, weight=1)
        text = tk.Text(frame, height=7, wrap="word", state="disabled", font=("Segoe UI", 9))
        text.pack(fill="both", expand=True)
        return text

    def _append_chat(self, speaker: str, message: str) -> None:
        self.chat.configure(state="normal")
        self.chat.insert("end", f"{speaker}: {message}\n\n")
        self.chat.configure(state="disabled")
        self.chat.see("end")

    def _set_text(self, widget: tk.Text, value: str) -> None:
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", value)
        widget.configure(state="disabled")

    def clear_chat(self) -> None:
        self.chat.configure(state="normal")
        self.chat.delete("1.0", "end")
        self.chat.configure(state="disabled")
        self.status_var.set("Gata")

    def send_message(self) -> None:
        user_text = self.input_var.get().strip()
        if not user_text:
            return

        self.input_var.set("")
        self._append_chat("Tu", user_text)
        self.status_var.set("Analizez...")
        self.update_idletasks()

        try:
            result = self.system.process_message(user_text)
            self._append_chat("MIS", result["response"])

            identity = result["identity"]
            identity_view = (
                f"Rezumat: {identity['dynamic_summary']}\n"
                f"Trăsături: {identity['traits']}\n"
                f"Preferințe: {identity['preferences']}\n"
                f"Profil risc: {identity['risk_profile']}"
            )
            self._set_text(self.identity_text, identity_view)

            emotions_view = "\n".join([f"{k}: {v}" for k, v in result["emotions"].items()])
            self._set_text(self.emotions_text, emotions_view)

            goals_view = "\n".join(
                [f"{g['description']} | prioritate={g['priority']} | intensitate={g['intensity']}" for g in result["goals"][:5]]
            )
            self._set_text(self.goals_text, goals_view)

            memories = result["memories"]
            memory_view = "\n".join([f"{m['content']} (r={m['relevance']})" for m in memories]) if memories else "Nicio memorie relevantă încă."
            self._set_text(self.memories_text, memory_view)

            self.status_var.set("Gata")
        except Exception as exc:
            self.status_var.set("Eroare")
            messagebox.showerror("Eroare MIS", f"A apărut o eroare: {exc}")


def run_app() -> None:
    app = MISApp()
    app.mainloop()


if __name__ == "__main__":
    run_app()
