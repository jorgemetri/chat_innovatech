import gspread
from oauth2client.service_account import ServiceAccountCredentials # Ou gspread.service_account se tiver gspread >= 5.0.0
from datetime import datetime

# --- Configurações do Google Sheets ---
SERVICE_ACCOUNT_FILE = "ardent-curve-460514-b2-d89c379c10cf.json"
# Tente primeiro com open_by_id se você atualizar o gspread.
# Se não, use SPREADSHEET_TITLE.
SPREADSHEET_ID = "1cUTbptS5QzFNMC3ClFIkupeyyxAfLIJ8HGkPSMCUq3Q" # Mantenha o ID
SPREADSHEET_TITLE = "BaseDadosChat" # Use se open_by_id não funcionar devido à versão do gspread
WORKSHEET_NAME = "Página1"

SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

# --- Dados de Teste para Enviar ---
# Lista completa de colunas esperadas (conforme sua definição anterior)
colunas_esperadas = [
    "Data e Hora do Envio",
    "1 - Como você se identifica / Você é:",
    "1.1 (Colaborador) - Qual é a sua empresa?",
    "1.2 (Colaborador) Em qual setor você atua?",
    "1.2.1 (Colaborador) Por favor, especifique o outro setor:",
    "2. (Colaborador) Você gostaria de informar o seu nome?",
    "2.1 (Colaborador) Me diga o seu nome:",
    "2.2 (Colaborador) Você quer receber o retorno do seu comunicado?",
    "2.3 (Colaborador) Me informe o seu contato (WhatsApp ou E-mail):",
    "3 (Colaborador) O que você gostaria de comunicar?",
    "3.1 (Colaborador) Sua comunicação é algo recorrente?",
    "3.2 (Colaborador) Chegou a comunicar seu superior imediato?",
    "S1.1 - A qual parte interessada você pertence?",
    "S1.2 - Digite o Nome da Comunidade/Localidade que você pertence:",
    "S1.3 - A qual órgão do poder público você pertence?",
    "S2. - Você gostaria de informar seu nome?",
    "S2.1 - Me diga seu nome:",
    "S2.2 - Você quer receber retorno do seu comunicado?",
    "S2.3 - Me informe seu contato (WhatsApp ou E-mail):",
    "S3. - O que você gostaria de comunicar?",
    "S3.1 - Se Reclamação, qual o tipo?",
    "S3.1.1 - Se Outro tipo de reclamação, por favor especifique:",
    "S3.2 - Descreva sua comunicação (detalhes):",
    "S3.2.1 - Seu comunicado é recorrente?",
    "S3.2.2 - A quem comunicou/informou anteriormente?",
    "S3.2.3 - Há quanto tempo ocorreu o fato ou o último contato?",
    "S3.3 - Como você identifica a empresa ou o fato relacionado à empresa?",
    "S3.3.1 - Se Outro modo de identificação, por favor especifique:"
]

# Simular dados para uma linha (AGORA COM 28 ITENS)
dados_da_linha_teste = [
    datetime.now().strftime("%d/%m/%Y às %H:%M:%S"), # Data e Hora do Envio
    "Morador Comunidade",                            # 1 - Como você se identifica
    "",                                              # 1.1 (Colaborador) - Qual é a sua empresa?
    "",                                              # 1.2 (Colaborador) Em qual setor você atua?
    "",                                              # 1.2.1 (Colaborador) Por favor, especifique o outro setor:
    "",                                              # 2. (Colaborador) Você gostaria de informar o seu nome?
    "",                                              # 2.1 (Colaborador) Me diga o seu nome:
    "",                                              # 2.2 (Colaborador) Você quer receber o retorno do seu comunicado?
    "",                                              # 2.3 (Colaborador) Me informe o seu contato
    "",                                              # 3 (Colaborador) O que você gostaria de comunicar?
    "",                                              # 3.1 (Colaborador) Sua comunicação é algo recorrente?
    "",                                              # 3.2 (Colaborador) Chegou a comunicar seu superior imediato?
    "Local (vizinho)",                               # S1.1 - A qual parte interessada você pertence?
    "Vila Esperança Teste Script",                   # S1.2 - Digite o Nome da Comunidade/Localidade
    "",                                              # S1.3 - A qual órgão do poder público você pertence?
    "Sim",                                           # S2. - Você gostaria de informar seu nome?
    "Testador Python",                               # S2.1 - Me diga seu nome:
    "Sim",                                           # S2.2 - Você quer receber retorno do seu comunicado?
    "script.teste@example.com",                      # S2.3 - Me informe seu contato
    "Reclamação",                                    # S3. - O que você gostaria de comunicar?
    "Poeira",                                        # S3.1 - Se Reclamação, qual o tipo?
    "",                                              # S3.1.1 - Se Outro tipo de reclamação, especifique:
    "Muita poeira na estrada principal durante a seca.", # S3.2 - Descreva sua comunicação
    "Sim",                                           # S3.2.1 - Seu comunicado é recorrente?
    "Prefeitura local (sem sucesso)",                # S3.2.2 - A quem comunicou/informou anteriormente?
    "Há 2 semanas",                                  # S3.2.3 - Há quanto tempo ocorreu o fato
    "Adesivo Veículo",                               # S3.3 - Como você identifica a empresa
    ""                                               # S3.3.1 - Se Outro modo de identificação, especifique:
]

if len(dados_da_linha_teste) != len(colunas_esperadas):
    print(f"ERRO DE CONFIGURAÇÃO INTERNA: Número de dados de teste ({len(dados_da_linha_teste)}) não corresponde ao número de colunas esperadas ({len(colunas_esperadas)}).")
    print("Verifique a montagem de 'dados_da_linha_teste' e 'colunas_esperadas' no script.")
    exit()

print(f"Tentando adicionar a seguinte linha com {len(dados_da_linha_teste)} colunas:")
# print(dados_da_linha_teste) # Descomente se quiser ver os dados antes de enviar

try:
    print(f"Autenticando com o arquivo: {SERVICE_ACCOUNT_FILE}...")
    creds = ServiceAccountCredentials.from_json_keyfile_name(filename=SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    print("Autenticação bem-sucedida!")

    # Tentar abrir por ID primeiro (mais robusto)
    spreadsheet = None
    try:
        print(f"Tentando abrir planilha com ID: {SPREADSHEET_ID}...")
        spreadsheet = client.open_by_id(SPREADSHEET_ID)
        print(f"Planilha '{spreadsheet.title}' (ID) aberta com sucesso!")
    except AttributeError:
        print(f"Método 'open_by_id' não encontrado. Tentando abrir pelo título '{SPREADSHEET_TITLE}' (pode ser uma versão mais antiga do gspread)...")
        try:
            spreadsheet = client.open(SPREADSHEET_TITLE)
            print(f"Planilha '{spreadsheet.title}' (Título) aberta com sucesso!")
        except gspread.exceptions.SpreadsheetNotFound:
            print(f"ERRO CRÍTICO: Planilha com TÍTULO '{SPREADSHEET_TITLE}' não encontrada. Verifique o título e o compartilhamento com: {creds.service_account_email}")
            exit()
    except gspread.exceptions.SpreadsheetNotFound:
        print(f"ERRO CRÍTICO: Planilha com ID '{SPREADSHEET_ID}' não encontrada. Verifique o ID e o compartilhamento com: {creds.service_account_email}")
        exit()


    print(f"Selecionando a aba: {WORKSHEET_NAME}...")
    worksheet = spreadsheet.worksheet(WORKSHEET_NAME)
    print(f"Aba '{worksheet.title}' selecionada!")

    # Opcional: Verificar se os cabeçalhos da planilha correspondem ao esperado
    # headers_in_sheet = worksheet.row_values(1) # Pega a primeira linha (cabeçalhos)
    # if headers_in_sheet != colunas_esperadas:
    # print("AVISO: Os cabeçalhos na planilha não correspondem exatamente às colunas esperadas no script.")
    # print(f"Cabeçalhos na Planilha: {headers_in_sheet}")
    # print(f"Colunas Esperadas Script: {colunas_esperadas}")
    # else:
    # print("Cabeçalhos da planilha correspondem ao esperado.")


    print("Tentando adicionar a linha de dados à planilha...")
    worksheet.append_row(dados_da_linha_teste, value_input_option='USER_ENTERED')
    print("🎉 Dados adicionados com sucesso à planilha!")

except FileNotFoundError:
    print(f"ERRO CRÍTICO: Arquivo de credenciais '{SERVICE_ACCOUNT_FILE}' não encontrado.")
except gspread.exceptions.WorksheetNotFound:
    print(f"ERRO CRÍTICO: Aba '{WORKSHEET_NAME}' não encontrada na planilha.")
except Exception as e:
    print(f"Ocorreu um erro inesperado: {e}")
    if 'creds' in locals() and hasattr(creds, 'service_account_email'):
        print(f"Verifique se a planilha foi compartilhada com: {creds.service_account_email}")
    else:
        print("Não foi possível obter o email da conta de serviço das credenciais.")