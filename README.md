Projeto RPA — Gmail → Planilhas → SQLite → Relatórios
Este projeto implementa um RPA (Robotic Process Automation) para automatizar o fluxo de fechamento de caixa diário em uma rede de lojas de autopeças.

O sistema é composto por uma interface gráfica (GUI) e integra as seguintes etapas:
📥 Receber planilhas de vendas via Gmail (baixando anexos .xlsx automaticamente).


🧹 ETL simples: ler planilhas, validar colunas e calcular valores.


💾 Gravar no banco SQLite (fechamento.db).


📝 Gerar relatório de fechamento em .txt.


📧 Enviar e-mail de confirmação para a gerência (com o relatório em anexo).



🚀 Tecnologias usadas
Python 3.11+


PySimpleGUI — interface gráfica


Pandas — ETL de planilhas


SQLite — banco de dados local


Google Gmail API — baixar e enviar e-mails


Google OAuth 2.0 — autenticação segura





📂 Estrutura do projeto
projeto_rpa_gui/
│
├── gui.py                # Interface gráfica principal
├── main.py               # Execução em linha de comando
├── gmail_client.py       # Integração com Gmail API (baixar/enviar emails)
├── google_auth.py        # Função utilitária para OAuth2
├── ler_e_preparar.py     # ETL das planilhas (ler, validar, calcular)
├── enviar_confirmacao.py # Função para mandar email de confirmação
├── core.py               # Funções compartilhadas
│
├── planilha/             # Pasta onde as planilhas .xlsx ficam
├── data/                 # Banco SQLite (`fechamento.db`)
├── relatorios/           # Relatórios gerados em .txt
│
├── requirements.txt      # Dependências do projeto
└── README.md             # Este arquivo


⚙️ Instalação
Copie os arquivos .rar no anexo


Crie e ative um ambiente virtual:

 python -m venv venv
venv\Scripts\activate   # Windows
source venv/bin/activate # Linux/Mac

Instale as dependências:

 pip install -r requirements.txt




🔑 Configuração do Gmail API
Acesse Google Cloud Console.


Crie um projeto e ative a Gmail API.


Crie credenciais OAuth Client ID (Desktop App).


Baixe o arquivo credentials.json e coloque na raiz do projeto.


Na primeira execução, o navegador abrirá pedindo login → autorize com sua conta Google.


Isso vai gerar o arquivo token.json automaticamente.


O token.json será usado nas próximas execuções.



▶️ Como usar
GUI
python gui.py

Selecione a pasta RAIZ (que contém planilha/).


Ajuste a query do Gmail (ex.: newer_than:7d has:attachment filename:xlsx).


Clique em Processar TUDO.


Acompanhe os logs.


Use o botão Abrir relatório para abrir o último relatório gerado.


Linha de comando
python main.py



📑 Relatórios
Os relatórios são salvos na pasta relatorios/ com nome no formato:
relatorio_YYYY-MM-DD_HHMMSS.txt

Exemplo de conteúdo:
Relatório de Processamento - 2025-09-18_14:30:07

Avisos/Anotações:
- PlanilhaNovoPadrao_01.xlsx: colunas ausentes ['preco_unitario'] — ignorado

Linhas válidas inseridas: 106

Totais por dia e loja:
- 2025-09-17 | Loja 101: R$ 12.345,67
- 2025-09-17 | Loja 102: R$  8.910,11

Banco de dados: C:\...\data\fechamento.db
Pasta de origem: C:\...\projeto_rpa_gui

