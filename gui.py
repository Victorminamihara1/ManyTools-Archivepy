import PySimpleGUI as sg
from pathlib import Path
import traceback
import os
import sys
import subprocess
import webbrowser
import threading

# módulos do projeto
from gmail_client import baixar_anexos_xlsx_google
from ler_e_preparar import ler_e_preparar, init_db, gravar_sqlite, gerar_relatorio
from enviar_confirmacao import enviar_confirmacao
from organizer import FileOrganizer   # NOVO

sg.theme("SystemDefault")

# --------- CONFIG BÁSICA ---------
REMETENTE = "robsonzambrotti69@gmail.com"
DESTINATARIOS = ["julianoferreira2078@edu.unifil.br"]
QUERY_XLSX_PADRAO = "newer_than:7d has:attachment filename:xlsx"


# --------- Helpers ---------
def abrir_arquivo(path_str: str):
    p = Path(path_str)
    if not p.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {p}")
    try:
        if sys.platform.startswith("win"):
            os.startfile(str(p))  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.run(["open", str(p)], check=False)
        else:
            subprocess.run(["xdg-open", str(p)], check=False)
    except Exception:
        webbrowser.open(p.as_uri())


# --------- PIPELINE ---------
def pipeline(raiz_str: str, query: str):
    p_sel = Path(raiz_str)
    if p_sel.name.lower() == "planilha":
        p_raiz = p_sel.parent
        p_plan = p_sel
    else:
        p_raiz = p_sel
        p_plan = p_raiz / "planilha"
    p_plan.mkdir(parents=True, exist_ok=True)

    logs = []
    def log(msg): logs.append(msg)

    try:
        log(f"[GMAIL] Buscando anexos com query: {query}")
        baixados = baixar_anexos_xlsx_google(query=query, destino_planilha_dir=str(p_plan), max_results=100)
        log(f"[GMAIL] Anexos .xlsx baixados: {baixados}")

        xlsx = list(p_plan.glob("*.xlsx"))
        if not xlsx:
            return {"ok": False, "logs": logs, "erro": "Sem planilhas para processar."}

        log(f"[ETL] Lendo e validando {len(xlsx)} arquivo(s) de {p_plan} ...")
        df, avisos = ler_e_preparar(str(p_raiz))
        for a in avisos: log("[AVISO] " + a)

        db_path = str(p_raiz / "data" / "fechamento.db")
        log(f"[DB] Inicializando DB: {db_path}")
        init_db(db_path)

        inseridas = gravar_sqlite(db_path, df)
        log(f"[DB] Linhas inseridas: {inseridas}")

        rel_path = gerar_relatorio(str(p_raiz), db_path, df, avisos)
        log(f"[REL] Relatório: {rel_path}")

        try:
            enviar_confirmacao(relatorio_txt=rel_path, remetente=REMETENTE, destinatarios=DESTINATARIOS)
            log("[GMAIL] Confirmação enviada")
        except Exception as e:
            log("[GMAIL] Falha ao enviar confirmação: " + str(e))

        return {"ok": True, "logs": logs, "raiz": str(p_raiz),
                "planilha": str(p_plan), "db": db_path,
                "rel": rel_path, "inseridas": int(inseridas)}

    except Exception as e:
        log("ERRO: " + str(e))
        log(traceback.format_exc())
        return {"ok": False, "logs": logs, "erro": str(e)}


# --------- GUI ---------
def main():
    # --- aba pipeline ---
    tab_pipeline = [
        [sg.Text("Diretório RAIZ do dia (a pasta que contém 'planilha/'):" )],
        [sg.Input(key="-DIR-", expand_x=True), sg.FolderBrowse("Escolher...")],
        [sg.Text("Query Gmail para anexos .xlsx:" )],
        [sg.Input(QUERY_XLSX_PADRAO, key="-Q-", expand_x=True)],
        [sg.Multiline(size=(100, 20), key="-LOG-", autoscroll=True, disabled=True, font=("Consolas", 9))],
        [sg.Button("Processar TUDO", key="-RUN-"), sg.Button("Abrir relatório", key="-OPENREL-")]
    ]

    # --- aba organizer ---
    tab_organizer = [
        [sg.Text("Pasta para organizar:")],
        [sg.Input(key="-ORGDIR-", expand_x=True), sg.FolderBrowse("Escolher...")],
        [sg.Checkbox("Dry-run (não move arquivos)", default=True, key="-DRY-")],
        [sg.ProgressBar(100, orientation="h", size=(40, 20), key="-ORGPROG-")],
        [sg.Multiline(size=(100, 15), key="-ORGLOG-", autoscroll=True, disabled=True, font=("Consolas", 9))],
        [sg.Button("Organizar", key="-ORGRUN-"), sg.Button("Undo", key="-ORGUNDO-")]
    ]

    layout = [
        [sg.TabGroup([[sg.Tab("Pipeline Gmail", tab_pipeline),
                       sg.Tab("Organizador de Arquivos", tab_organizer)]])],
        [sg.Button("Sair")]
    ]

    win = sg.Window("ManyTools — RPA + Organizer", layout, finalize=True)

    last_result = None
    organizer = FileOrganizer(history_file="organizer_history.json")
    try:
        organizer.load_rules_from_file("rules.json")
    except:
        pass

    # função que roda organizer em thread
    def run_organizer(folder, dry, window):
        def cb(pct, filepath, action, idx, total):
            window.write_event_value("-ORGPROGRESS-", (pct, filepath, action, idx, total))
        result = organizer.organize_folder(folder, dry_run=dry, progress_callback=cb)
        window.write_event_value("-ORGDONE-", result)

    while True:
        ev, vals = win.read()
        if ev in (sg.WIN_CLOSED, "Sair"):
            break

        # --- eventos pipeline ---
        if ev == "-RUN-":
            raiz = vals["-DIR-"]
            query_atual = vals["-Q-"].strip() or QUERY_XLSX_PADRAO
            win["-LOG-"].update("")
            win.perform_long_operation(lambda: pipeline(raiz, query_atual), "-DONE-")

        elif ev == "-DONE-":
            result = vals["-DONE-"]
            last_result = result
            for line in result.get("logs", []):
                win["-LOG-"].print(line)

            if result.get("ok"):
                win["-LOG-"].print("\n[OK] Processo finalizado com sucesso.")
                sg.popup_ok("Processo finalizado com sucesso!", keep_on_top=True)
            else:
                win["-LOG-"].print("\n[FAIL] " + result.get("erro", "Falha desconhecida"))
                sg.popup_error("Falha no processo. Verifique o log.", keep_on_top=True)

        elif ev == "-OPENREL-":
            if last_result and last_result.get("rel"):
                try:
                    abrir_arquivo(last_result["rel"])
                except Exception as e:
                    sg.popup_error(f"Não consegui abrir: {last_result['rel']}\n\n{e}", keep_on_top=True)
            else:
                sg.popup_error("Nenhum relatório gerado nesta sessão.", keep_on_top=True)

        # --- eventos organizer ---
        elif ev == "-ORGRUN-":
            pasta = vals["-ORGDIR-"]
            dry = vals["-DRY-"]
            if not pasta:
                sg.popup_error("Escolha uma pasta para organizar.")
                continue
            win["-ORGLOG-"].update("")
            win["-ORGLOG-"].print("Iniciando organização...")
            t = threading.Thread(target=run_organizer, args=(pasta, dry, win), daemon=True)
            t.start()

        elif ev == "-ORGPROGRESS-":
            pct, filepath, action, idx, total = vals[ev]
            win["-ORGPROG-"].update(pct)
            win["-ORGLOG-"].print(f"{idx}/{total} ({pct}%) {filepath} -> {action.get('action')}")

        elif ev == "-ORGDONE-":
            result = vals["-ORGDONE-"]
            win["-ORGLOG-"].print("Finalizado:", result)

        elif ev == "-ORGUNDO-":
            res = organizer.undo_last()
            win["-ORGLOG-"].print("Undo:", res)

    win.close()


if __name__ == "__main__":
    main()
