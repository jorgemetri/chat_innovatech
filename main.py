import streamlit as st
import time
import json
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials # Ou gspread.service_account para gspread >= 5.0.0

# --- INÍCIO DAS CONFIGURAÇÕES DO GOOGLE SHEETS (COPIE SUAS CONSTANTES AQUI) ---
SERVICE_ACCOUNT_FILE = "ardent-curve-460514-b2-d89c379c10cf.json"
SPREADSHEET_TITLE = "BaseDadosChat" # Confirmado que funciona com client.open()
WORKSHEET_IDENTIFIER = "Página1" 
SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]
# --- FIM DAS CONFIGURAÇÕES DO GOOGLE SHEETS ---


# --- INÍCIO DAS FUNÇÕES DO GOOGLE SHEETS (COPIE SUAS FUNÇÕES AQUI) ---
@st.cache_resource 
def get_gspread_client():
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name(filename=SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        client = gspread.authorize(creds)
        st.session_state['gspread_client_initialized'] = True 
        return client
    except FileNotFoundError:
        st.error(f"⚠️ Arquivo de credenciais '{SERVICE_ACCOUNT_FILE}' não encontrado. Verifique o caminho.")
        st.session_state['gspread_client_initialized'] = False
        return None
    except Exception as e:
        st.error(f"⚠️ Erro ao autenticar com Google API: {e}")
        st.session_state['gspread_client_initialized'] = False
        return None

@st.cache_resource 
def get_worksheet_cached(_client, spreadsheet_title, worksheet_identifier):
    if not st.session_state.get('gspread_client_initialized', False) or _client is None:
        return None
    try:
        spreadsheet = _client.open(spreadsheet_title) # Usar open() pelo título
        if isinstance(worksheet_identifier, int):
            worksheet = spreadsheet.get_worksheet(worksheet_identifier)
        else:
            worksheet = spreadsheet.worksheet(worksheet_identifier)
        st.session_state['worksheet_loaded'] = True
        return worksheet
    except gspread.exceptions.SpreadsheetNotFound:
        st.error(f"⚠️ Planilha com título '{spreadsheet_title}' não encontrada. Verifique o título e o compartilhamento.")
        st.session_state['worksheet_loaded'] = False
        return None
    except gspread.exceptions.WorksheetNotFound:
        st.error(f"⚠️ Aba '{worksheet_identifier}' não encontrada na planilha.")
        st.session_state['worksheet_loaded'] = False
        return None
    except Exception as e:
        st.error(f"⚠️ Erro ao abrir planilha/aba '{worksheet_identifier}': {e}")
        st.session_state['worksheet_loaded'] = False
        return None

def append_data_to_sheet(worksheet, data_row):
    if not st.session_state.get('worksheet_loaded', False) or worksheet is None :
        st.error("⚠️ Conexão com a aba da planilha não estabelecida. Dados não enviados.")
        return False
    try:
        worksheet.append_row(data_row, value_input_option='USER_ENTERED')
        return True
    except Exception as e:
        st.error(f"⚠️ Erro ao enviar dados para a planilha: {e}")
        return False
# --- FIM DAS FUNÇÕES DO GOOGLE SHEETS ---


# --- Título da Página e Configuração ---
PAGE_TITLE = "Canal de Comunicação Operacional"
st.set_page_config(page_title=PAGE_TITLE, layout="centered") 

# --- CSS Customizado ---
custom_css = """
<style>
    .stApp > header { background-color: transparent; }
    h1#page-title { color: #00447c; text-align: center; font-family: 'Arial', sans-serif; padding-top: 15px; margin-bottom: 0px; }
    h2#page-subtitle { color: #006847; text-align: center; font-family: 'Arial', sans-serif; font-size: 1.3em; margin-top: 5px; margin-bottom: 25px; }
    .stChatMessage { border-radius: 12px; padding: 12px 18px; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
    [data-testid="chatAvatarIcon-assistant"] + div .stChatMessage { background-color: #e9eff7; border-left: 4px solid #007bff; }
    [data-testid="chatAvatarIcon-user"] + div .stChatMessage { background-color: #f0fdf4; border-right: 4px solid #28a745; }
    .stButton>button { border-radius: 8px; padding: 8px 16px; font-weight: 500; }
    .typing-cursor { display: inline-block; width: 2px; height: 1.1em; background-color: #333; animation: blink 0.7s step-end infinite; vertical-align: text-bottom; margin-left: 1px; }
    @keyframes blink { 0%, 100% { background-color: #333; } 50% { background-color: transparent; } }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

st.markdown(f"<h1 id='page-title'>{PAGE_TITLE}</h1>", unsafe_allow_html=True)
st.markdown(f"<h2 id='page-subtitle'>Grupo de Certificação Florestal Colpar Brasil</h2>", unsafe_allow_html=True)
st.divider()

# --- Constantes ---
GREETING_MESSAGE = """
Olá! 👋 Meu nome é **Colpi**, seu assistente virtual do Grupo de Certificação Florestal Colpar Brasil. 
Este é um espaço seguro e confidencial para que todas as vozes sejam ouvidas.

🚨 **Atenção:** Este canal é dedicado a assuntos operacionais e do dia a dia. 
Para denúncias (assédio, corrupção, etc.), utilize nosso canal de denúncias exclusivo: 📲 `QRcode XXXXXXXXXXXXXX`.
"""

# --- INÍCIO DO QUESTIONS_DATA (COPIE SEU QUESTIONS_DATA ORIGINAL E COMPLETO AQUI) ---
QUESTIONS_DATA = [
    {"text": "1 - Como você se identifica / Você é:", "options": ["Colaborador Interno - Colpar; RM ou Greenplac", "Colaborador externo - Prestador de Serviço", "Morador Comunidade", "Poder Público"], "key_prefix": "q1_identificacao", 'input_type': 'radio'},
    {"text": "1.1 (Colaborador) - Qual é a sua empresa?", "key_prefix": "c_q1_1_empresa", 'input_type': 'text', "condition": {"depends_on_key": "q1_identificacao", "not_expected_values": ["Morador Comunidade", "Poder Público"]}},
    {"text": "1.2 (Colaborador) Em qual setor você atua?", "options": ["Silvicultura", "Colheita", "Administrativo", "Outro"], "key_prefix": "c_q1_2_setor", 'input_type': 'radio', "condition": {"depends_on_key": "q1_identificacao", "not_expected_values": ["Morador Comunidade", "Poder Público"]}},
    {"text": "1.2.1 (Colaborador) Por favor, especifique o outro setor:", "key_prefix": "c_q1_2_setor_especificacao", 'input_type': 'text', "condition": {"depends_on_key": "c_q1_2_setor", "expected_value": "Outro"} },
    {"text": "2. (Colaborador) Você gostaria de informar o seu nome?", "options": ["Sim", "Não"], "key_prefix": "c_q2_informar_nome", 'input_type': 'radio', "condition": {"depends_on_key": "q1_identificacao", "not_expected_values": ["Morador Comunidade", "Poder Público"]}},
    {"text": "2.1 (Colaborador) Me diga o seu nome:", "key_prefix": "c_q2_1_nome", 'input_type': 'text', "condition": {"depends_on_key": "c_q2_informar_nome", "expected_value": "Sim"}},
    {"text": "2.2 (Colaborador) Você quer receber o retorno do seu comunicado?", "options": ["Sim", "Não"], "key_prefix": "c_q2_2_retorno", 'input_type': 'radio', "condition": {"depends_on_key": "q1_identificacao", "not_expected_values": ["Morador Comunidade", "Poder Público"]}},
    {"text": "2.3 (Colaborador) Me informe o seu contato (WhatsApp ou E-mail):", "key_prefix": "c_q2_3_contato", 'input_type': 'text', "condition": {"depends_on_key": "c_q2_2_retorno", "expected_value": "Sim"} },
    {"text": "3 (Colaborador) O que você gostaria de comunicar?", "options": ["Reclamação", "Sugestão", "Elogio", "Engajamento", "Dúvida"], "key_prefix": "c_q3_tipo_comunicado", 'input_type': 'radio', "condition": {"depends_on_key": "q1_identificacao", "not_expected_values": ["Morador Comunidade", "Poder Público"]}},
    {"text": "3.1 (Colaborador) Sua comunicação é algo recorrente?", "options": ["Sim", "Não"], "key_prefix": "c_q3_1_recorrente", 'input_type': 'radio', "condition": {"depends_on_key": "q1_identificacao", "not_expected_values": ["Morador Comunidade", "Poder Público"]}},
    {"text": "3.2 (Colaborador) Chegou a comunicar seu superior imediato?", "options": ["Sim", "Não"], "key_prefix": "c_q3_2_superior", 'input_type': 'radio', "condition": {"depends_on_key": "q1_identificacao", "not_expected_values": ["Morador Comunidade", "Poder Público"]}},
    {"text": "S1.1 - A qual parte interessada você pertence?", "options": ["Local (vizinho)","Local (assentamento)","Local (município/cidade)","Tradicional","Indigena","Poder Público (específico)"], "key_prefix": "s_q1_1_parte_interessada", 'input_type': 'radio', "condition": {"depends_on_key": "q1_identificacao", "expected_values": ["Morador Comunidade", "Poder Público"]}},
    {"text": "S1.2 - Digite o Nome da Comunidade/Localidade que você pertence:", "key_prefix": "s_q1_2_nome_comunidade", 'input_type': 'text', "condition": {"depends_on_key": "s_q1_1_parte_interessada", "not_expected_value": "Poder Público (específico)"} },
    {"text": "S1.3 - A qual órgão do poder público você pertence?", "key_prefix": "s_q1_3_orgao_publico", 'input_type': 'text', "condition": {"depends_on_key": "s_q1_1_parte_interessada", "expected_value": "Poder Público (específico)"}},
    {"text": "S2. - Você gostaria de informar seu nome?", "options": ["Sim","Não"], "key_prefix": "s_q2_informar_nome", 'input_type': 'radio', "condition": {"depends_on_key": "q1_identificacao", "expected_values": ["Morador Comunidade", "Poder Público"]}},
    {"text": "S2.1 - Me diga seu nome:", "key_prefix": "s_q2_1_nome", 'input_type': 'text', "condition": {"depends_on_key": "s_q2_informar_nome", "expected_value": "Sim"}},
    {"text": "S2.2 - Você quer receber retorno do seu comunicado?", "options": ["Sim","Não"], "key_prefix": "s_q2_2_retorno", 'input_type': 'radio', "condition": {"depends_on_key": "s_q2_informar_nome", "expected_value": "Sim"}},
    {"text": "S2.3 - Me informe seu contato (WhatsApp ou E-mail):", "key_prefix": "s_q2_3_contato", 'input_type': 'text', "condition": {"depends_on_key": "s_q2_2_retorno", "expected_value": "Sim"}},
    {"text": "S3. - O que você gostaria de comunicar?", "options": ["Reclamação","Sugestão","Elogio","Engajamento","Dúvida"], "key_prefix": "s_q3_tipo_comunicado", 'input_type': 'radio', "condition": {"depends_on_key": "q1_identificacao", "expected_values": ["Morador Comunidade", "Poder Público"]}},
    {"text": "S3.1 - Se Reclamação, qual o tipo?", "options": ["Poeira","Alta Velocidade","Danos Estrada","Outro"], "key_prefix": "s_q3_1_tipo_reclamacao", 'input_type': 'radio', "condition": {"depends_on_key": "s_q3_tipo_comunicado", "expected_value": "Reclamação"}},
    {"text": "S3.1.1 - Se Outro tipo de reclamação, por favor especifique:", "key_prefix": "s_q3_1_1_reclamacao_outro", 'input_type': 'text', "condition": {"depends_on_key": "s_q3_1_tipo_reclamacao", "expected_value": "Outro"}},
    {"text": "S3.2 - Descreva sua comunicação (detalhes):", "key_prefix": "s_q3_2_descricao", 'input_type': 'text', "condition": {"depends_on_key": "q1_identificacao", "expected_values": ["Morador Comunidade", "Poder Público"]}},
    {"text": "S3.2.1 - Seu comunicado é recorrente?", "options": ["Sim","Não"], "key_prefix": "s_q3_2_1_recorrente", 'input_type': 'radio', "condition": {"depends_on_key": "q1_identificacao", "expected_values": ["Morador Comunidade", "Poder Público"]}},
    {"text": "S3.2.2 - A quem comunicou/informou anteriormente?", "key_prefix": "s_q3_2_2_quem_comunicou", 'input_type': 'text', "condition": {"depends_on_key": "q1_identificacao", "expected_values": ["Morador Comunidade", "Poder Público"]}},
    {"text": "S3.2.3 - Há quanto tempo ocorreu o fato ou o último contato?", "key_prefix": "s_q3_2_3_quanto_tempo", 'input_type': 'text', "condition": {"depends_on_key": "q1_identificacao", "expected_values": ["Morador Comunidade", "Poder Público"]}},
    {"text": "S3.3 - Como você identifica a empresa ou o fato relacionado à empresa?", "options": ["Adesivo Veículo","Outra pessoa me informou","Conheço o colaborador","Presenciei o fato","Outro"], "key_prefix": "s_q3_3_identifica_empresa", 'input_type': 'radio', "condition": {"depends_on_key": "q1_identificacao", "expected_values": ["Morador Comunidade", "Poder Público"]}},
    {"text": "S3.3.1 - Se Outro modo de identificação, por favor especifique:", "key_prefix": "s_q3_3_1_identifica_outro", 'input_type': 'text', "condition": {"depends_on_key": "s_q3_3_identifica_empresa", "expected_value": "Outro"}},
]
# --- FIM DO QUESTIONS_DATA ---

FINAL_PROMPT_TEXT = "✅ Pesquisa quase concluída! Você deseja enviar suas respostas?"
TYPING_SPEED = 0.02 
CURSOR_HTML = '<span class="typing-cursor"></span>'

# --- INÍCIO DAS FUNÇÕES AUXILIARES DO CHATBOT (COPIE AS SUAS AQUI) ---
def initialize_state():
    default_values = {"messages": [], "current_question_index": 0, "answers": {}, "stage": "greeting", "widget_key_suffix": 0}
    for key, value in default_values.items():
        if key not in st.session_state: st.session_state[key] = value

def reset_chat():
    st.session_state.messages, st.session_state.current_question_index, st.session_state.answers, st.session_state.stage = [], 0, {}, "greeting"
    st.session_state.widget_key_suffix += 1
    st.rerun()

def type_assistant_message(text_content):
    with st.chat_message("assistant", avatar="🤖"): 
        message_placeholder = st.empty()
        full_response = ""
        words = text_content.split(' ')
        for i, word in enumerate(words):
            full_response += word
            if i < len(words) - 1: full_response += " "
            time.sleep(TYPING_SPEED)
            message_placeholder.markdown(full_response + CURSOR_HTML, unsafe_allow_html=True)
        message_placeholder.markdown(full_response, unsafe_allow_html=True) 
    st.session_state.messages.append({"role": "assistant", "content": text_content})

def add_user_message_and_store_answer(response_content, question_original_key_prefix):
    with st.chat_message("user", avatar="👤"): st.markdown(str(response_content))
    st.session_state.messages.append({"role": "user", "content": str(response_content)})
    st.session_state.answers[question_original_key_prefix] = str(response_content)

def check_and_skip_question():
    while st.session_state.current_question_index < len(QUESTIONS_DATA):
        question_info = QUESTIONS_DATA[st.session_state.current_question_index]
        should_skip = False
        if "condition" in question_info:
            cond = question_info["condition"]
            previous_answer = st.session_state.answers.get(cond["depends_on_key"])
            if previous_answer is None: should_skip = True
            else:
                if "expected_value" in cond and previous_answer != cond["expected_value"]: should_skip = True
                elif "expected_values" in cond and previous_answer not in cond["expected_values"]: should_skip = True
                elif "not_expected_value" in cond and previous_answer == cond["not_expected_value"]: should_skip = True
                elif "not_expected_values" in cond and previous_answer in cond["not_expected_values"]: should_skip = True
        if should_skip:
            if question_info["key_prefix"] not in st.session_state.answers or st.session_state.answers[question_info["key_prefix"]] == "Não respondida":
                 st.session_state.answers[question_info["key_prefix"]] = "Não Aplicável (pulada)"
            st.session_state.current_question_index += 1
        else: return False 
    return True 
# --- FIM DAS FUNÇÕES AUXILIARES DO CHATBOT ---


# --- INÍCIO DA LÓGICA PRINCIPAL DO STREAMLIT (COPIE O RESTANTE DO SEU CÓDIGO AQUI) ---
initialize_state()
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="🤖" if message["role"] == "assistant" else "👤"):
        st.markdown(message["content"], unsafe_allow_html=True)

if st.session_state.stage == "greeting":
    if not st.session_state.messages: type_assistant_message(GREETING_MESSAGE)
    if QUESTIONS_DATA: st.session_state.stage = "questioning"; st.rerun()
    else: 
        if not st.session_state.messages or st.session_state.messages[-1]['content'] != "Nenhuma pergunta configurada.":
            type_assistant_message("Nenhuma pergunta configurada.")
        st.session_state.stage = "finished"; st.rerun()

elif st.session_state.stage == "questioning":
    if check_and_skip_question(): st.session_state.stage = "final_prompt"; st.rerun()
    current_q_index = st.session_state.current_question_index
    if current_q_index >= len(QUESTIONS_DATA): st.session_state.stage = "final_prompt"; st.rerun()
    
    question_info = QUESTIONS_DATA[current_q_index]

    if not st.session_state.messages or \
       st.session_state.messages[-1]["role"] != "assistant" or \
       st.session_state.messages[-1]["content"] != question_info["text"]:
        type_assistant_message(question_info["text"])
    
    with st.container():
        widget_key_prefix, unique_widget_suffix = question_info['key_prefix'], st.session_state.widget_key_suffix
        response_submitted, user_response = False, None
        input_label = "💬 Sua resposta:"

        if question_info['input_type'] == 'radio':
            radio_widget_key = f"radio_{widget_key_prefix}_{unique_widget_suffix}"
            selected_option = st.radio(label=input_label, options=question_info["options"], key=radio_widget_key, index=None, horizontal=True)
            if st.button("✔️ Enviar Resposta", key=f"confirm_btn_{radio_widget_key}"):
                if selected_option is not None: user_response, response_submitted = selected_option, True
                else: st.warning("⚠️ Por favor, selecione uma opção.")
        
        elif question_info['input_type'] == 'text':
            text_input_widget_key = f"text_input_{widget_key_prefix}_{unique_widget_suffix}"
            if text_input_widget_key not in st.session_state: st.session_state[text_input_widget_key] = ""
            
            current_text_value_for_input = st.session_state.get(text_input_widget_key, "")
            user_typed_text = st.text_input(label=input_label, key=text_input_widget_key, value=current_text_value_for_input, placeholder="Digite aqui...")
            if user_typed_text != current_text_value_for_input: 
                st.session_state[text_input_widget_key] = user_typed_text

            if st.button("✔️ Enviar Resposta", key=f"confirm_btn_{text_input_widget_key}"):
                final_text_value = st.session_state.get(text_input_widget_key, "").strip()
                if final_text_value: user_response, response_submitted = final_text_value, True
                else: st.warning("⚠️ Por favor, digite sua resposta.")

        if response_submitted and user_response is not None:
            add_user_message_and_store_answer(user_response, question_info["key_prefix"])
            
            force_final_prompt = False
            if question_info["key_prefix"] == "c_q3_2_superior": force_final_prompt = True
            elif question_info["key_prefix"] == "s_q3_3_identifica_empresa" and user_response != "Outro": force_final_prompt = True
            elif question_info["key_prefix"] == "s_q3_3_1_identifica_outro": force_final_prompt = True

            if force_final_prompt: st.session_state.stage = "final_prompt"
            else:
                st.session_state.current_question_index += 1
                if check_and_skip_question() or st.session_state.current_question_index >= len(QUESTIONS_DATA):
                    st.session_state.stage = "final_prompt"
            st.rerun()

elif st.session_state.stage == "final_prompt":
    if not st.session_state.messages or \
       st.session_state.messages[-1]["role"] != "assistant" or \
       st.session_state.messages[-1]["content"] != FINAL_PROMPT_TEXT:
        type_assistant_message(FINAL_PROMPT_TEXT)
    
    with st.container():
        final_choice_radio_key = f"final_choice_radio_{st.session_state.widget_key_suffix}"
        final_choice = st.radio(label="Sua decisão:", options=("👍 Sim, enviar", "👎 Não, descartar"), key=final_choice_radio_key, index=None, horizontal=True)
        
        if st.button("📤 Finalizar", key=f"finalize_btn_{final_choice_radio_key}"):
            if final_choice is not None:
                add_user_message_and_store_answer(final_choice, "final_survey_decision")
                
                if final_choice == "👍 Sim, enviar":
                    submission_time = datetime.now().strftime("%d/%m/%Y às %H:%M:%S") 
                    
                    row_to_append_to_sheet = [submission_time] 
                    for q_info in QUESTIONS_DATA:
                        answer = st.session_state.answers.get(q_info["key_prefix"], "") 
                        row_to_append_to_sheet.append("" if answer == "Não Aplicável (pulada)" else str(answer))
                    
                    gspread_client = get_gspread_client()
                    worksheet = None 
                    if gspread_client: 
                        worksheet = get_worksheet_cached(gspread_client, SPREADSHEET_TITLE, WORKSHEET_IDENTIFIER) 
                    
                    sheet_update_successful = False
                    if worksheet:
                        if append_data_to_sheet(worksheet, row_to_append_to_sheet):
                            sheet_update_successful = True
                    
                    chat_summary_parts = ["✅ Pesquisa concluída! Obrigado pela sua participação."]
                    if sheet_update_successful:
                        chat_summary_parts.append("Os dados foram enviados para nossa planilha.")
                    elif gspread_client is not None:
                         chat_summary_parts.append("Houve um problema ao enviar os dados para a planilha, mas suas respostas foram registradas localmente.")
                    else:
                        chat_summary_parts.append("Não foi possível conectar ao Google Sheets. Suas respostas foram registradas apenas localmente.")
                    
                    chat_summary_parts.append(f"📅 **Enviada em:** {submission_time}\n")
                    chat_summary_parts.append("📋 **Resumo das Suas Respostas:**")

                    survey_results_obj_local = {"🆔 Data e Hora do Envio": submission_time}
                    for q_data in QUESTIONS_DATA:
                        question_key, question_text = q_data["key_prefix"], q_data['text']
                        if question_key in st.session_state.answers:
                            answer = st.session_state.answers[question_key]
                            if answer != "Não Aplicável (pulada)":
                                survey_results_obj_local[question_text] = answer
                                chat_summary_parts.append(f"- *{question_text}* <br>    ➡️ {answer}")
                    
                    final_summary_message = "\n".join(chat_summary_parts)
                    with st.chat_message("assistant", avatar="🤖"): st.markdown(final_summary_message, unsafe_allow_html=True)
                    st.session_state.messages.append({"role": "assistant", "content": final_summary_message})
                    
                    if sheet_update_successful: st.balloons() 
                    
                    with st.expander("Visualizar dados completos (formato JSON local)", expanded=False): st.json(survey_results_obj_local)
                
                else: 
                    type_assistant_message("❌ Entendido. Suas respostas não foram enviadas e serão descartadas.")
                    st.info("Pesquisa descartada.")
                
                st.session_state.stage = "finished"; st.rerun()
            else: 
                st.warning("⚠️ Por favor, selecione uma opção para finalizar.")

elif st.session_state.stage == "finished":
    st.markdown("---") 
    if st.button("🔄 Iniciar Nova Comunicação", key=f"restart_btn_{st.session_state.widget_key_suffix}"): 
        reset_chat()
# --- FIM DA LÓGICA PRINCIPAL DO STREAMLIT ---