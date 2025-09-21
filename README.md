📌 README – Sistema de Automação com Google API e Organização de Arquivos
📖 Descrição

Este projeto é uma aplicação em Python com interface gráfica em PySimpleGUI, que integra serviços do Google (Gmail, Drive, Sheets) e adiciona funções de organização automática de arquivos locais.

Ele foi desenvolvido para automatizar processos repetitivos, como:

Coletar anexos de e-mails e processá-los.

Gerar relatórios em Excel.

Organizar arquivos em pastas específicas do computador (por extensão, nome ou tipo definido pelo usuário).

Assim, o software atua como uma central de automação pessoal, unindo e-mails, planilhas e gestão de arquivos de forma simples e intuitiva.

🚀 Funcionalidades

📧 Automação de E-mails

Busca automática de anexos em contas Gmail.

Filtragem por período, extensão ou remetente.

Confirmação automática para a gerência após processar dados.

📊 Manipulação de Dados

Leitura de planilhas .xlsx com pandas e openpyxl.

Tratamento e análise de dados.

Exportação de relatórios organizados.

🗂️ Organização de Arquivos Locais

Permite escolher uma pasta do computador.

Reorganiza arquivos automaticamente em subpastas de acordo com:

Extensão (.pdf, .jpg, .xlsx etc.).

Tipo de documento (imagens, textos, planilhas).

Configuração personalizada definida pelo usuário.

🖥️ Interface Gráfica

Desenvolvida em PySimpleGUI, simples e amigável.

Menu intuitivo com botões de ação para cada função.

⚙️ Instalação e Configuração
1. Pré-requisitos

Python 3.11+ instalado.

Conta Google com permissões na API desejada (Gmail/Drive/Sheets).

Dependências listadas no requirements.txt.

2. Clonando o Repositório
git clone (https://github.com/Victorminamihara1/ManyTools-Archivepy.git)
cd SEU-REPO

3. Criando Ambiente Virtual
python -m venv .venv
.venv\Scripts\activate    # Windows
source .venv/bin/activate # Linux/Mac

4. Instalando Dependências
pip install -r requirements.txt

⚠️ Nunca compartilhe .env, token.json ou credenciais no GitHub.

▶️ Uso
Rodar o sistema
python gui.py

Fluxo do Usuário

Fazer login no Google (apenas na primeira vez).

Escolher entre os módulos:

E-mail → baixar anexos, processar planilhas, enviar confirmações.

Arquivos → organizar a pasta selecionada automaticamente.

Exportar relatórios e salvar no formato Excel.

Encerrar pelo botão Sair.

📂 Estrutura de Pastas (sugestão)
projeto/
│-- main.py
│-- auth_google.py
│-- file_organizer.py
│-- requirements.txt
│-- .env.example
│-- /src
│   │-- gui.py
│   │-- email_module.py
│   │-- excel_module.py
│   │-- organizer_module.py
│-- /output
│   │-- relatorios/
│   │-- organizados/

👨‍💻 Tecnologias Utilizadas

Python 3.11+

PySimpleGUI 5.x (interface gráfica)

pandas + openpyxl (planilhas)

google-api-python-client + google-auth (integração Google)

python-dotenv (gestão de credenciais seguras)

🔒 Segurança

Arquivo .env deve ser usado para variáveis sensíveis.

Tokens e credenciais não devem ser versionados no Git.

Repositórios públicos devem usar GitHub Secrets no CI/CD.

📜 Licença

Este projeto é distribuído sob a licença MIT, podendo ser usado e modificado livremente, desde que mantidos os créditos originais.
