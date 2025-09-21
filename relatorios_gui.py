import PySimpleGUI as sg
from pathlib import Path

sg.theme("SystemDefault")

def listar_relatorios(dir_escolhido: str):
    """
    Retorna (pasta_relatorios: Path, lista_de_arquivos: list[Path])
    Aceita:
      - dir_escolhido = raiz do dia (com subpasta 'relatorios')
      - dir_escolhido = a própria pasta 'relatorios'
    """
    p = Path(dir_escolhido).expanduser().resolve()

    # Se usuário apontar direto pra 'relatorios', usa ela.
    if p.name.lower() == "relatorios" and p.is_dir():
        rel_dir = p
    else:
        # Caso contrário, supõe que é a RAIZ e procura a subpasta 'relatorios'
        rel_dir = p / "relatorios"

    if not rel_dir.exists():
        return rel_dir, []

    # Filtra .txt; ajuste aqui se quiser ver outros formatos
    arquivos = sorted(rel_dir.glob("*.txt"))
    return rel_dir, arquivos

def main():
    layout = [
        [sg.Text("Selecione a RAIZ do dia (que contém 'relatorios/') ou a própria pasta 'relatorios':")],
        [sg.Input(key="-DIR-", enable_events=True), sg.FolderBrowse("Escolher...")],
        [sg.Button("Carregar"), sg.Text("", key="-INFO-", size=(60,1))],
        [sg.Listbox(values=[], size=(60, 15), key="-FILES-", enable_events=True)],
        [sg.Multiline(size=(100, 25), key="-CONTENT-", disabled=True)],
        [sg.Button("Sair")]
    ]
    win = sg.Window("Visualizar Relatórios", layout, finalize=True)

    def atualizar_lista():
        dir_sel = win["-DIR-"].get().strip()
        if not dir_sel:
            win["-INFO-"].update("Nenhum diretório selecionado.")
            win["-FILES-"].update([])
            win["-CONTENT-"].update("")
            return

        rel_dir, arquivos = listar_relatorios(dir_sel)
        if not arquivos:
            win["-INFO-"].update(f"Nada encontrado em: {rel_dir}")
            win["-FILES-"].update([])
            win["-CONTENT-"].update("")
        else:
            win["-INFO-"].update(f"Listando {len(arquivos)} arquivo(s) em: {rel_dir}")
            win["-FILES-"].update([a.name for a in arquivos])

    while True:
        ev, vals = win.read()
        if ev in (sg.WIN_CLOSED, "Sair"):
            break

        if ev in ("Carregar", "-DIR-"):  # carrega tanto ao clicar quanto ao editar o caminho
            atualizar_lista()

        if ev == "-FILES-":
            dir_sel = vals["-DIR-"].strip()
            sel = vals["-FILES-"]
            if dir_sel and sel:
                rel_dir, _ = listar_relatorios(dir_sel)
                file_path = rel_dir / sel[0]
                try:
                    texto = file_path.read_text(encoding="utf-8")
                    win["-CONTENT-"].update(texto)
                except Exception as e:
                    sg.popup_error(f"Erro ao abrir: {e}", keep_on_top=True)

    win.close()

if __name__ == "__main__":
    main()
