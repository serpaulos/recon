import json
import tkinter as tk
from datetime import date
from pathlib import Path
from tkinter import ttk

from src.config.app_config import ENVS
from .controllers import (
    Ctx,
    on_run_bat, on_run_excel, on_validate_excel, on_prepare_email,
    on_mark_excel_done, on_retry_jira_upload,
    update_button_states, refresh_bat_status_label, populate_jobs_tree,
    on_job_double_click,
)
from .persistence import prune_job_state
from .state import AppState

STATE_FILE = Path("jobs_state.json")
APP_STATE_FILE = Path("app_state.json")

legacy_jobs = {
    "PROD": [("ACCTERR", "P201767A"), ("HOLDERR", "P201769A"), ("ISINERR", "P201766A"), ("PARTERR", "P201765A"),
             ("PENDERR", "P201770A"), ("SETTERR", "P201773A")],
    "DEMO": [("ACCTERR", "X201767A"), ("HOLDERR", "X201769A"), ("ISINERR", "X201766A"), ("PARTERR", "X201765A"),
             ("PENDERR", "X201770A"), ("SETTERR", "X201773A")],
    "FUNK": [("ACCTERR", "F201767A"), ("HOLDERR", "F201769A"), ("ISINERR", "F201766A"), ("PARTERR", "F201765A"),
             ("PENDERR", "F201770A"), ("SETTERR", "F201773A")],
}


def rollover_if_new_day(state: AppState) -> bool:
    today = date.today().strftime("%Y-%m-%d")
    if state.run_date_key != today:
        state.run_date_key = today

        # reset “rodada”
        state.bat_done = False
        state.bat_last_run = None
        state.operating_date_ddmmyyyy = None
        state.operating_date_key = None
        state.draft_jobs_by_env = {}

        for env in ("PROD", "DEMO", "FUNK"):
            state.last_jira_key[env] = None
            state.excel_done[env] = False
            state.validate_done[env] = False

        return True
    return False


class ReconApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Reconciliation Automation GUI")
        self.root.geometry("950x720")

        self.state = AppState()
        self.job_state_by_date = {}

        self._load_states()

        # rollover diário
        if rollover_if_new_day(self.state):
            self._save_app_state(self.state)

        self.widgets = {}
        self._build_ui()

        self.ctx = Ctx(
            root=self.root,
            widgets=self.widgets,
            state=self.state,
            legacy_jobs=legacy_jobs,
            job_state_by_date=self.job_state_by_date,
            save_job_state=self._save_job_state,
            app_state_save=self._save_app_state,
            log=self.log,
        )

        # bind double click
        self.widgets["tree_jobs"].bind("<Double-1>", lambda e: on_job_double_click(self.ctx, e))

        update_button_states(self.ctx)
        refresh_bat_status_label(self.ctx)

    def run(self):
        self.root.mainloop()

    # -------- persistence --------
    def _load_states(self):
        if STATE_FILE.exists():
            self.job_state_by_date = json.loads(STATE_FILE.read_text(encoding="utf-8"))

        if prune_job_state(self.job_state_by_date, keep_days=60):
            self._save_job_state()

        if APP_STATE_FILE.exists():
            data = json.loads(APP_STATE_FILE.read_text(encoding="utf-8"))
            self.state = AppState.from_dict(data)

    def _save_job_state(self):
        STATE_FILE.write_text(json.dumps(self.job_state_by_date, indent=2), encoding="utf-8")

    def _save_app_state(self, state: AppState):
        APP_STATE_FILE.write_text(json.dumps(state.to_dict(), indent=2), encoding="utf-8")

    # -------- logging --------
    def log(self, msg: str):
        box = self.widgets["status_box"]
        box.config(state="normal")
        box.insert(tk.END, msg + "\n")
        box.config(state="disabled")
        box.see(tk.END)

    # -------- UI --------
    def _build_ui(self):
        top = ttk.Frame(self.root)
        top.pack(fill="x", padx=10, pady=6)

        ttk.Label(top, text="Select environment:").pack(side="left", padx=5)
        env_var = tk.StringVar(value="PROD")
        self.widgets["env_var"] = env_var

        env_combo = ttk.Combobox(top, textvariable=env_var, values=list(ENVS.keys()), state="readonly", width=10)
        env_combo.pack(side="left", padx=5)

        load_jobs_btn = ttk.Button(top, text="Load Jobs", command=lambda: populate_jobs_tree(self.ctx))
        load_jobs_btn.pack(side="left", padx=5)
        self.widgets["load_jobs_btn"] = load_jobs_btn

        bat_status_var = tk.StringVar(value="BAT: NOT RUN")
        self.widgets["bat_status_var"] = bat_status_var
        ttk.Label(top, textvariable=bat_status_var).pack(side="left", padx=12)

        # ---- Jobs tree ----
        tree_frame = ttk.LabelFrame(self.root, text="Legacy Jobs")
        tree_frame.pack(fill="x", padx=10, pady=6)

        tree_jobs = ttk.Treeview(tree_frame, columns=["Job", "Job ID", "Status", "RC"], show="headings", height=6)
        for col in ["Job", "Job ID", "Status", "RC"]:
            tree_jobs.heading(col, text=col)
            tree_jobs.column(col, width=160, anchor="center")
        tree_jobs.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        self.widgets["tree_jobs"] = tree_jobs

        sb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree_jobs.yview)
        sb.pack(side="right", fill="y")
        tree_jobs.configure(yscrollcommand=sb.set)

        # ---- Summary ----
        summary = ttk.LabelFrame(self.root, text="Environment Summary")
        summary.pack(fill="x", padx=10, pady=6)

        summary_box = tk.Text(summary, height=5, state="disabled")
        summary_box.pack(fill="x", padx=5, pady=4)
        self.widgets["summary_box"] = summary_box

        # ---- Actions ----
        actions = ttk.LabelFrame(self.root, text="Actions")
        actions.pack(fill="x", padx=10, pady=6)

        run_bat_btn = tk.Button(actions, text="Run BAT", width=15, command=lambda: on_run_bat(self.ctx))
        run_excel_btn = tk.Button(actions, text="Run Excel Macro", width=15, command=lambda: on_run_excel(self.ctx))
        mark_excel_done_btn = tk.Button(actions, text="Excel Already Ran", width=15,
                                        command=lambda: on_mark_excel_done(self.ctx))
        validate_excel_btn = tk.Button(actions, text="Validate Excel", width=15,
                                       command=lambda: on_validate_excel(self.ctx))
        retry_jira_btn = tk.Button(actions, text="Retry Jira Upload", width=16,
                                   command=lambda: on_retry_jira_upload(self.ctx))
        prepare_email_btn = tk.Button(actions, text="Prepare Email", width=15,
                                      command=lambda: on_prepare_email(self.ctx))

        run_bat_btn.pack(side="left", padx=5, pady=5)
        run_excel_btn.pack(side="left", padx=5, pady=5)
        mark_excel_done_btn.pack(side="left", padx=5, pady=5)
        validate_excel_btn.pack(side="left", padx=5, pady=5)
        retry_jira_btn.pack(side="left", padx=5, pady=5)
        prepare_email_btn.pack(side="left", padx=5, pady=5)

        self.widgets.update({
            "run_bat_btn": run_bat_btn,
            "run_excel_btn": run_excel_btn,
            "mark_excel_done_btn": mark_excel_done_btn,
            "validate_excel_btn": validate_excel_btn,
            "retry_jira_btn": retry_jira_btn,
            "prepare_email_btn": prepare_email_btn,
        })

        # ---- Preview ----
        preview = ttk.LabelFrame(self.root, text="Overview Preview")
        preview.pack(fill="both", expand=True, padx=10, pady=6)

        table_frame = ttk.Frame(preview)
        table_frame.pack(fill="both", expand=True)

        overview_tree = ttk.Treeview(table_frame, show="headings", height=8)
        overview_tree.pack(side="left", fill="both", expand=True)
        self.widgets["overview_tree"] = overview_tree

        sb2 = ttk.Scrollbar(table_frame, orient="vertical", command=overview_tree.yview)
        sb2.pack(side="right", fill="y")
        overview_tree.configure(yscrollcommand=sb2.set)

        # ---- Logs ----
        logs = ttk.LabelFrame(self.root, text="Status / Logs")
        logs.pack(fill="both", expand=False, padx=10, pady=6)

        status_box = tk.Text(logs, height=8, state="disabled")
        status_box.pack(fill="both", expand=True, padx=5, pady=4)
        self.widgets["status_box"] = status_box
