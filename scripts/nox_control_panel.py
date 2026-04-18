import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import argparse
import csv
import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

from action_executor import execute_action
from entity_extractor import extract_entities
from intent_router import route_intent
from model import get_model_path
from predict import predict_intent


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "intent_dataset.csv"
NOX100_CATALOG_PATH = PROJECT_ROOT / "data" / "raw" / "nox_100_intents_catalog.csv"
NOX250_CATALOG_PATH = PROJECT_ROOT / "data" / "raw" / "nox_250_intents_catalog.csv"
DEFAULT_FEEDBACK_PATH = PROJECT_ROOT / "data" / "raw" / "nox_feedback.csv"


SAMPLE_ACTIONS = [
    ("Modo foco", "activa modo foco"),
    ("Modo gaming", "activa modo gaming"),
    ("Video YouTube", "abri un video de rocket league"),
    ("Foto camara", "sacame una foto"),
    ("Volumen 70", "pon el volumen al 70"),
    ("Brillo max", "brillo al maximo"),
    ("Abrir Steam", "abre steam"),
    ("Abrir Discord", "abre discord"),
    ("Buscar en web", "busca en la web setup dual monitor"),
    ("Timer 25m", "pon un timer de 25 minutos"),
    ("Alarma 07:30", "pon una alarma a las 7:30"),
    ("Estado CPU", "uso de cpu"),
]


def load_known_intents(version: str) -> list[str]:
    intents: set[str] = set()
    source_path = RAW_DATA_PATH

    if version in {"nox", "nox250", "best"} and NOX250_CATALOG_PATH.exists():
        source_path = NOX250_CATALOG_PATH
    elif version == "nox100" and NOX100_CATALOG_PATH.exists():
        source_path = NOX100_CATALOG_PATH

    with source_path.open("r", encoding="utf-8", newline="") as file_handle:
        reader = csv.DictReader(file_handle)
        for row in reader:
            intent = (row.get("intent") or "").strip()
            target_intent = (row.get("target_intent") or "").strip()
            if intent:
                intents.add(intent)
            if target_intent:
                intents.add(target_intent)
    return sorted(intents)


def append_feedback(
    feedback_path: Path,
    text: str,
    predicted_intent: str,
    correct_intent: str,
) -> None:
    feedback_path.parent.mkdir(parents=True, exist_ok=True)
    file_exists = feedback_path.exists()

    with feedback_path.open("a", encoding="utf-8", newline="") as file_handle:
        writer = csv.DictWriter(
            file_handle,
            fieldnames=["text", "predicted_intent", "correct_intent"],
        )
        if not file_exists:
            writer.writeheader()
        writer.writerow(
            {
                "text": text,
                "predicted_intent": predicted_intent,
                "correct_intent": correct_intent,
            }
        )


class NoxControlPanel:
    def __init__(self, root: tk.Tk, version: str, no_execute: bool, no_feedback: bool, feedback_file: str) -> None:
        self.root = root
        self.version = version
        self.no_execute = no_execute
        self.no_feedback = no_feedback
        self.feedback_path = Path(feedback_file)
        self.model_path = get_model_path(version)
        self.known_intents = set(load_known_intents(version))

        self.root.title("NOX Control Panel")
        self.root.geometry("1120x760")
        self.root.minsize(920, 620)

        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("TLabel", background="#0D0D0D", foreground="#FFFFFF")
        style.configure("TFrame", background="#0D0D0D")
        style.configure("TLabelframe", background="#0D0D0D", foreground="#8B0000")
        style.configure("TLabelframe.Label", background="#0D0D0D", foreground="#8B0000")
        style.configure("TButton", background="#7F1D1D", foreground="#FFFFFF", padding=6)
        style.map("TButton", background=[("active", "#991B1B")])

        self.root.configure(bg="#0D0D0D")

        self.status_var = tk.StringVar(
            value=(
                f"Modelo: {self.version} | Ejecutar acciones: {'No' if self.no_execute else 'Si'}"
                f" | Feedback: {'No' if self.no_feedback else 'Si'}"
            )
        )
        self.placeholder_text = "Escribe aqui tu instruccion libre. Ejemplo: pon una alarma a las 7:30"

        self._build_ui()
        self._set_input_placeholder()
        self.input_box.focus_set()
        self._append_trace(f"Panel iniciado con modelo {self.version}")
        self._append_trace(f"Archivo de modelo: {self.model_path}")
        if self.no_feedback:
            self._append_trace("Captura de feedback desactivada")
        else:
            self._append_trace(f"Captura de feedback activada en: {self.feedback_path}")
        self._append_console("NOX", "Listo. Puedes escribir una instruccion o usar un boton de accion.")

    def _build_ui(self) -> None:
        self.root.grid_rowconfigure(0, weight=0)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(2, weight=2)
        self.root.grid_rowconfigure(3, weight=0)
        self.root.grid_columnconfigure(0, weight=1)

        header = ttk.Frame(self.root, padding=8)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        ttk.Label(
            header,
            text="NOX - Panel de Acciones",
            font=("Segoe UI", 15, "bold"),
        ).grid(row=0, column=0, sticky="w")

        ttk.Label(
            header,
            textvariable=self.status_var,
            foreground="#9CA3AF",
        ).grid(row=1, column=0, sticky="w", pady=(2, 0))

        trace_frame = ttk.LabelFrame(self.root, text="Proceso interno del pipeline", padding=8)
        trace_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 8))
        trace_frame.grid_rowconfigure(0, weight=1)
        trace_frame.grid_columnconfigure(0, weight=1)

        self.trace_box = ScrolledText(trace_frame, wrap="word", height=10, font=("Consolas", 10))
        self.trace_box.grid(row=0, column=0, sticky="nsew")
        self.trace_box.configure(state="disabled", background="#0D0D0D", foreground="#FFFFFF", insertbackground="#FF3333")

        center = ttk.Frame(self.root)
        center.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 8))
        center.grid_rowconfigure(0, weight=1)
        center.grid_columnconfigure(0, weight=1)
        center.grid_columnconfigure(1, weight=2)

        actions_frame = ttk.LabelFrame(center, text="Acciones rapidas", padding=8)
        actions_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        actions_frame.grid_columnconfigure(0, weight=1)
        actions_frame.grid_columnconfigure(1, weight=1)

        for i, (label, command_text) in enumerate(SAMPLE_ACTIONS):
            btn = ttk.Button(
                actions_frame,
                text=label,
                command=lambda text=command_text: self._run_from_button(text),
            )
            btn.grid(row=i // 2, column=i % 2, padx=4, pady=4, sticky="ew")

        console_frame = ttk.LabelFrame(center, text="Consola", padding=8)
        console_frame.grid(row=0, column=1, sticky="nsew")
        console_frame.grid_rowconfigure(0, weight=1)
        console_frame.grid_columnconfigure(0, weight=1)

        self.console_box = ScrolledText(console_frame, wrap="word", font=("Consolas", 10))
        self.console_box.grid(row=0, column=0, sticky="nsew")
        self.console_box.configure(state="disabled", background="#0D0D0D", foreground="#FFFFFF", insertbackground="#FF3333")

        input_wrapper = ttk.LabelFrame(self.root, text="Entrada libre", padding=(10, 6, 10, 10))
        input_wrapper.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 10))
        input_wrapper.grid_columnconfigure(0, weight=1)

        hint = ttk.Label(
            input_wrapper,
            text="NOX: escribe instrucciones libres para trabajo, gaming o anti-procrastinacion. Enter = enviar, Shift+Enter = nueva linea.",
            foreground="#9CA3AF",
        )
        hint.grid(row=0, column=0, sticky="w", pady=(0, 6))

        input_frame = ttk.Frame(input_wrapper)
        input_frame.grid(row=3, column=0, sticky="ew")
        input_frame.grid_columnconfigure(0, weight=1)

        self.input_box = tk.Text(input_frame, height=3, wrap="word", font=("Segoe UI", 10))
        self.input_box.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.input_box.configure(background="#180000", foreground="#FFFFFF", insertbackground="#FF3333")
        self.input_box.bind("<Return>", self._on_submit)
        self.input_box.bind("<Shift-Return>", self._on_shift_enter)
        self.input_box.bind("<FocusIn>", self._on_input_focus_in)

        send_btn = ttk.Button(input_frame, text="Enviar", command=self._submit)
        send_btn.grid(row=0, column=1)

        clear_btn = ttk.Button(input_frame, text="Limpiar panel", command=self._clear_panels)
        clear_btn.grid(row=0, column=2, padx=(8, 0))

    def _set_input_placeholder(self) -> None:
        self.input_box.delete("1.0", "end")
        self.input_box.insert("1.0", self.placeholder_text)
        self.input_box.configure(fg="#6b7280")

    def _on_input_focus_in(self, _event: tk.Event) -> None:
        current = self.input_box.get("1.0", "end").strip()
        if current == self.placeholder_text:
            self.input_box.delete("1.0", "end")
            self.input_box.configure(fg="#FFFFFF")

    def _append_trace(self, message: str) -> None:
        self.trace_box.configure(state="normal")
        self.trace_box.insert("end", f"{message}\n")
        self.trace_box.see("end")
        self.trace_box.configure(state="disabled")

    def _append_console(self, speaker: str, message: str) -> None:
        self.console_box.configure(state="normal")
        self.console_box.insert("end", f"[{speaker}] {message}\n")
        self.console_box.see("end")
        self.console_box.configure(state="disabled")

    def _clear_panels(self) -> None:
        self.trace_box.configure(state="normal")
        self.trace_box.delete("1.0", "end")
        self.trace_box.configure(state="disabled")

        self.console_box.configure(state="normal")
        self.console_box.delete("1.0", "end")
        self.console_box.configure(state="disabled")

        self._append_trace("Panel limpiado")

    def _on_submit(self, _event: tk.Event) -> None:
        self._submit()
        return "break"

    def _on_shift_enter(self, _event: tk.Event) -> str:
        self.input_box.insert("insert", "\n")
        return "break"

    def _run_from_button(self, command_text: str) -> None:
        self.input_box.delete("1.0", "end")
        self.input_box.configure(fg="#111827")
        self.input_box.insert("1.0", command_text)
        self.input_box.focus_set()
        self._submit()

    def _capture_feedback(self, text: str, predicted_intent: str, final_intent: str) -> None:
        if self.no_feedback:
            return

        is_correct = messagebox.askyesno(
            "Feedback",
            f"¿La intent detectada fue correcta?\n\nIntent: {final_intent}",
        )
        if is_correct:
            self._append_trace("5) Feedback: correcta")
            return

        correct_intent = simpledialog.askstring(
            "Feedback",
            "Escribe la intent correcta:",
            parent=self.root,
        )
        if correct_intent is None:
            self._append_trace("5) Feedback cancelado por el usuario")
            return

        correct_intent = correct_intent.strip()
        if not correct_intent:
            messagebox.showwarning("Feedback", "La intent correcta no puede estar vacia.")
            self._append_trace("5) Feedback rechazado: intent vacia")
            return

        if correct_intent not in self.known_intents:
            create_new = messagebox.askyesno(
                "Feedback",
                f"La intent '{correct_intent}' no existe. ¿Quieres crearla en feedback?",
            )
            if not create_new:
                self._append_trace("5) Feedback no guardado: intent nueva no confirmada")
                return
            self.known_intents.add(correct_intent)

        append_feedback(self.feedback_path, text, predicted_intent, correct_intent)
        self._append_trace(
            f"5) Feedback guardado: predicted={predicted_intent}, correct={correct_intent}"
        )
        self._append_console("NOX", "Feedback guardado para reentrenar.")

    def _submit(self) -> None:
        user_text = self.input_box.get("1.0", "end").strip()
        if not user_text or user_text == self.placeholder_text:
            return

        self.input_box.delete("1.0", "end")
        self._set_input_placeholder()
        self._append_console("Tu", user_text)

        self._append_trace("---")
        self._append_trace(f"1) Texto recibido: {user_text}")

        predicted_intent = predict_intent(user_text, version=self.version)
        intent, routing_reason = route_intent(user_text, predicted_intent)
        if routing_reason:
            self._append_trace(f"2) Intent clasificada: {predicted_intent} -> corregida a {intent}")
            self._append_trace(f"   Motivo: {routing_reason}")
        else:
            self._append_trace(f"2) Intent clasificada: {intent}")

        entities = extract_entities(user_text, intent)
        self._append_trace(f"3) Entidades extraidas: {entities if entities else '{}'}")

        if self.no_execute:
            result = {
                "status": "ok",
                "message": "Modo prueba activo: no se ejecuto accion real.",
            }
            self._append_trace("4) Ejecucion omitida por modo prueba")
        else:
            result = execute_action(intent, entities)
            if result["status"] == "confirm_required":
                confirm = messagebox.askyesno("Confirmacion requerida", result["message"])
                if confirm:
                    result = execute_action(intent, entities, force=True)
                    self._append_trace("4) Confirmacion aprobada por usuario")
                else:
                    result = {"status": "ok", "message": "Accion cancelada por el usuario."}
                    self._append_trace("4) Accion cancelada por el usuario")
            else:
                self._append_trace(f"4) Resultado de ejecucion: {result['status']}")

        entity_str = ", ".join(f"{k}={v}" for k, v in entities.items()) if entities else "sin entidades"
        self._append_console("NOX", f"Intent: {intent} | Entidades: {entity_str}")
        self._append_console("NOX", result["message"])
        self._capture_feedback(user_text, predicted_intent, intent)


def main() -> None:
    parser = argparse.ArgumentParser(description="UI desktop para NOX")
    parser.add_argument(
        "--version",
        default="nox250",
        help="Version del modelo: v1, v2, v3 o alias nox/nox100/nox250/best",
    )
    parser.add_argument(
        "--no-execute",
        action="store_true",
        help="No ejecuta acciones reales; solo muestra pipeline",
    )
    parser.add_argument(
        "--feedback-file",
        default=str(DEFAULT_FEEDBACK_PATH),
        help="Archivo CSV donde se guardan correcciones de intents",
    )
    parser.add_argument(
        "--no-feedback",
        action="store_true",
        help="Desactiva la captura de feedback",
    )
    args = parser.parse_args()

    root = tk.Tk()
    app = NoxControlPanel(
        root=root,
        version=args.version,
        no_execute=args.no_execute,
        no_feedback=args.no_feedback,
        feedback_file=args.feedback_file,
    )
    _ = app
    root.mainloop()


if __name__ == "__main__":
    main()
