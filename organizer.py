import os
import shutil
import json
from pathlib import Path
from typing import Callable, Dict, List, Optional

class FileOrganizer:
    def __init__(self, rules: Optional[Dict[str, List[str]]] = None, history_file: str = None):
        # regras padrão se não passar nenhuma
        self.rules = rules or {
            "Imagens": [".jpg", ".jpeg", ".png", ".gif"],
            "Documentos": [".pdf", ".docx", ".txt"],
            "Planilhas": [".xls", ".xlsx", ".csv"],
            "Compactados": [".zip", ".rar"],
        }
        self.history_file = history_file
        self.last_moves = []  # para undo

    def save_rules_to_file(self, path="rules.json"):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.rules, f, indent=2, ensure_ascii=False)

    def load_rules_from_file(self, path="rules.json"):
        with open(path, "r", encoding="utf-8") as f:
            self.rules = json.load(f)

    def categorize(self, filename: str) -> str:
        ext = Path(filename).suffix.lower()
        for categoria, extensoes in self.rules.items():
            if ext in extensoes:
                return categoria
        return "Outros"

    def organize_folder(self, folder: str, dry_run: bool = True,
                        progress_callback: Optional[Callable] = None):
        """
        Organiza arquivos em 'folder' conforme as regras.
        Se dry_run=True, só simula (não move nada).
        """
        folder = Path(folder)
        if not folder.exists():
            raise FileNotFoundError(f"Pasta não encontrada: {folder}")

        arquivos = [f for f in folder.iterdir() if f.is_file()]
        total = len(arquivos)
        self.last_moves = []

        for idx, file in enumerate(arquivos, start=1):
            categoria = self.categorize(file.name)
            destino = folder / categoria
            destino.mkdir(exist_ok=True)

            if not dry_run:
                novo_path = destino / file.name
                shutil.move(str(file), str(novo_path))
                self.last_moves.append((str(novo_path), str(file)))  # salvar origem pra undo

            if progress_callback:
                pct = int(idx / total * 100)
                progress_callback(pct, str(file), {"action": "move" if not dry_run else "simulado"}, idx, total)

        return {"total": total, "movidos": len(self.last_moves), "dry_run": dry_run}

    def undo_last(self):
        """
        Reverte o último organize_folder (se não for dry_run).
        """
        if not self.last_moves:
            return {"ok": False, "msg": "Nada para desfazer."}

        for novo, antigo in reversed(self.last_moves):
            if os.path.exists(novo):
                shutil.move(novo, antigo)

        moves = len(self.last_moves)
        self.last_moves = []
        return {"ok": True, "desfeitos": moves}
