import PySimpleGUI as sg
from pathlib import Path
import traceback
from datetime import datetime

# sua lógica já pronta
from core import ler_e_preparar, init_db, gravar_sqlite, gerar_relatorio

sg.theme("SystemDefault")

# ------------- utilitários -------------
def log_append(win, key, msg: str):
    if not msg.endswith("\n"):
        msg += "\n"
    atual = win[key].get()
    win[key].update(atual + msg, autoscroll=True)

def resolver_raiz_e_planilha(dir_escolhido: str):
    """
    Aceita:
      - RAIZ que contém 'planilha/'
      - a própria pasta 'planilha'
    Retorna (raiz:Path, pasta_planilha:Path)
    """
    p = Path(dir_escolhido).expanduser().resolve()
    if p.name.lower() == "planilha":
        return p.parent, p
    return p, p / "planilha"

def listar_relatorios(dir_escolhido: str):
    """
    Aceita:
      - RAIZ que contém 'relatorios/'
      - a própria 'relatorios'
    Retorna (pasta_relatorios:Path, lista_de_arquivos:list[Path])
    """
    p = Path(dir_escolhido).expanduser().resolve()
    if p.name.lower() == "relatorios" and p.is_dir():
        rel_dir = p
    else:
        rel_dir = p / "relatorios"
    if not rel_dir.exists():
        return rel_dir, []
    return rel_dir, sorted(rel_dir.glob("*.txt"))

# ------------- layout das abas -------------
aba_processar = [
    [sg.Text("Selecione a RAIZ do dia (que contém 'planilha/') ou a própria pasta 'planilha':")],
    [sg.Input(key="-P_DIR-"), sg.FolderBrowse("Escolher...")],
    [sg.Button("Processar", key="-P_RUN-"), sg.Text("", key="-P_INFO-", size=(50,1))],
    [sg.Multiline(size=(100, 20), key="-P_LOG-", autoscroll=True, disabled=True)],
]

aba_relatorios = [
    [sg.Text("Selecione a RAIZ do dia (que contém 'relatorios/') ou a própria pasta 'relatorios':")],
    [sg.Input(key="-R_DIR-"), sg.FolderBrowse("Escolher..."), sg.Button("Carregar", key="-R_LOAD-")],
    [sg.Text("", key="-R_INFO-", size=(60,1))],
    [sg.Listbox(values=[], size=(60, 15), key="-R_FILES-", enable_events=True)],
    [sg.Multiline(size=(100, 25), key="-R_VIEW-", autoscroll=True, disabled=True)],
]

layout = [
    [sg.TabGroup([[
        sg.Tab("Processar", aba_processar),
        sg.Tab("Relatórios", aba_relatorios),
    ]], expand_x=True, expand_y=True)]
]

win = sg.Window("RPA — Processar & Relatórios (Unificado)", layout, finalize=True, resizable=True)

# ------------- loop principal -------------
while True:
    ev, vals = win.read()
    if ev in (sg.WIN_CLOSED, "Sair"):
        break

    # --- Aba Processar ---
    if ev == "-P_RUN-":
        try:
            win["-P_LOG-"].update("")  # limpa log a cada execução
            dir_escolhido = vals["-P_DIR-"].strip()
            if not dir_escolhido:
                sg.popup_error("Escolha a RAIZ (com 'planilha/') ou a própria 'planilha'.", keep_on_top=True)
                continue

            raiz, p_plan = resolver_raiz_e_planilha(dir_escolhido)
            if not p_plan.exists():
                sg.popup_error(f"Não encontrei a pasta: {p_plan}", keep_on_top=True)
                continue

            log_append(win, "-P_LOG-", f"[{datetime.now().strftime('%H:%M:%S')}] > Lendo planilhas de: {p_plan}")
            # A função ler_e_preparar espera a RAIZ
            df, avisos = ler_e_preparar(str(raiz))
            for a in avisos:
                log_append(win, "-P_LOG-", f"AVISO: {a}")
            log_append(win, "-P_LOG-", f"Linhas válidas: {len(df)}")

            db_path = str(raiz / "data" / "fechamento.db")
            log_append(win, "-P_LOG-", f"> Inicializando DB: {db_path}")
            init_db(db_path)

            inseridas = gravar_sqlite(db_path, df)
            log_append(win, "-P_LOG-", f"> Inseridas {inseridas} linha(s) no SQLite.")

            rel_path = gerar_relatorio(str(raiz), db_path, df, avisos)
            log_append(win, "-P_LOG-", f"> Relatório gerado em: {rel_path}")

            win["-P_INFO-"].update("Processo finalizado com sucesso!")
            sg.popup_ok("Processo finalizado com sucesso!", keep_on_top=True)
        except Exception as e:
            log_append(win, "-P_LOG-", "ERRO: " + str(e))
            log_append(win, "-P_LOG-", traceback.format_exc())
            sg.popup_error("Falhou. Veja o log.", keep_on_top=True)

    # --- Aba Relatórios ---
    if ev == "-R_LOAD-":
        dir_rel = vals["-R_DIR-"].strip()
        if not dir_rel:
            win["-R_INFO-"].update("Nenhum diretório selecionado.")
            win["-R_FILES-"].update([])
            win["-R_VIEW-"].update("")
            continue
        rel_dir, arquivos = listar_relatorios(dir_rel)
        if not arquivos:
            win["-R_INFO-"].update(f"Nada encontrado em: {rel_dir}")
            win["-R_FILES-"].update([])
            win["-R_VIEW-"].update("")
        else:
            win["-R_INFO-"].update(f"Listando {len(arquivos)} arquivo(s) em: {rel_dir}")
            win["-R_FILES-"].update([a.name for a in arquivos])

    if ev == "-R_FILES-":
        dir_rel = vals["-R_DIR-"].strip()
        sel = vals["-R_FILES-"]
        if dir_rel and sel:
            rel_dir, _ = listar_relatorios(dir_rel)
            file_path = rel_dir / sel[0]
            try:
                texto = file_path.read_text(encoding="utf-8")
                win["-R_VIEW-"].update(texto)
            except Exception as e:
                sg.popup_error(f"Erro ao abrir: {e}", keep_on_top=True)

win.close()
