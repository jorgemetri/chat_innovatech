import streamlit as st
import time
import json
from datetime import datetime

# --- Título da Página e Configuração ---
TITLE = "Canal e Comunicação Operacional"

st.set_page_config(page_title=TITLE)
st.title(TITLE)
st.header("Grupo de Certificação Floreslta Colpar Brasil")
# --- Constantes ---
GREETING_MESSAGE = """
Meu nome é Colpi, assitente virtual do Grupo de Certificação Floretal Colpar Brasil, um espaço seguro para que todas as vozes sejam ouvidas.

Antes de começarmos, preciso informar uma coisa importante, este canal é exclusivo para tratar de assuntos operacionais e do dia-a-dia. Caso tenha queira fazer uma denúncia de assédio ou violência sexual, do trabalho, corrupção ou outro tema delicado, temos um canal exclusivo, através de QRcode XXXXXXXXXXXXXX.
"""

QUESTIONS_DATA = [
    # PERGUNTA INICIAL DE BIFURCAÇÃO
    {"text": "1 - Como você se identifica / Você é:",
     "options": ["Colaborador Interno - Colpar; RM ou Greenplac", "Colaborador externo - Prestador de Serviço", "Morador Comunidade", "Poder Público"],
     "key_prefix": "q1_identificacao", 'input_type': 'radio'},

    # --- FLUXO PARA COLABORADOR INTERNO / EXTERNO ---
    {"text": "1.1 (Colaborador) - Qual é a sua empresa?",
     "key_prefix": "c_q1_1_empresa", 'input_type': 'text',
     "condition": {"depends_on_key": "q1_identificacao",
                   "not_expected_values": ["Morador Comunidade", "Poder Público"]}
    },
    {"text": "1.2 (Colaborador) Em qual setor você atua?",
     "options": ["Silvicultura", "Colheita", "Administrativo", "Outro"],
     "key_prefix": "c_q1_2_setor", 
     'input_type': 'radio',
     "condition": {"depends_on_key": "q1_identificacao",
                   "not_expected_values": ["Morador Comunidade", "Poder Público"]}
    },
    {"text": "1.2.1 (Colaborador) Por favor, especifique o outro setor:",
     "key_prefix": "c_q1_2_setor_especificacao",
     'input_type': 'text',
     "condition": {"depends_on_key": "c_q1_2_setor", "expected_value": "Outro"} 
    },
    {"text": "2. (Colaborador) Você gostaria de informar o seu nome?",
     "options": ["Sim", "Não"],
     "key_prefix": "c_q2_informar_nome", 'input_type': 'radio',
     "condition": {"depends_on_key": "q1_identificacao",
                   "not_expected_values": ["Morador Comunidade", "Poder Público"]}
    },
    {"text": "2.1 (Colaborador) Me diga o seu nome:",
     "key_prefix": "c_q2_1_nome", 'input_type': 'text',
     "condition": {"depends_on_key": "c_q2_informar_nome", "expected_value": "Sim"}
    },
    {"text": "2.2 (Colaborador) Você quer receber o retorno do seu comunicado?",
     "options": ["Sim", "Não"],
     "key_prefix": "c_q2_2_retorno", 'input_type': 'radio',
      "condition": {"depends_on_key": "q1_identificacao", # Mantém a condição geral do fluxo
                   "not_expected_values": ["Morador Comunidade", "Poder Público"]}
    },
    {"text": "2.3 (Colaborador) Me informe o seu contato (WhatsApp ou E-mail):",
     "key_prefix": "c_q2_3_contato", 'input_type': 'text',
     # Esta condição já funciona: se c_q2_2_retorno for "Não" ou não for perguntado, esta será pulada.
     "condition": {"depends_on_key": "c_q2_2_retorno", "expected_value": "Sim"} 
    },
    {"text": "3 (Colaborador) O que você gostaria de comunicar?",
     "options": ["Reclamação", "Sugestão", "Elogio", "Engajamento", "Dúvida"],
     "key_prefix": "c_q3_tipo_comunicado", 'input_type': 'radio',
      "condition": {"depends_on_key": "q1_identificacao",
                   "not_expected_values": ["Morador Comunidade", "Poder Público"]}
    },
    {"text": "3.1 (Colaborador) Sua comunicação é algo recorrente?",
     "options": ["Sim", "Não"],
     "key_prefix": "c_q3_1_recorrente", 'input_type': 'radio',
      "condition": {"depends_on_key": "q1_identificacao",
                   "not_expected_values": ["Morador Comunidade", "Poder Público"]}
    },
    {"text": "3.2 (Colaborador) Chegou a comunicar seu superior imediato?",
     "options": ["Sim", "Não"],
     "key_prefix": "c_q3_2_superior", 'input_type': 'radio',
      "condition": {"depends_on_key": "q1_identificacao",
                   "not_expected_values": ["Morador Comunidade", "Poder Público"]}
    },

    # --- FLUXO PARA MORADOR COMUNIDADE / PODER PÚBLICO ---
    {"text": "S1.1 - A qual parte interessada você pertence?",
     "options": ["Local (vizinho)","Local (assentamento)","Local (município/cidade)","Tradicional","Indigena","Poder Público (específico)"],
     "key_prefix": "s_q1_1_parte_interessada", 'input_type': 'radio',
     "condition": {"depends_on_key": "q1_identificacao", "expected_values": ["Morador Comunidade", "Poder Público"]}
    },
    {"text": "S1.2 - Digite o Nome da Comunidade/Localidade que você pertence:",
     "key_prefix": "s_q1_2_nome_comunidade", 'input_type': 'text',
     "condition": {"depends_on_key": "s_q1_1_parte_interessada", 
                   "not_expected_value": "Poder Público (específico)"} 
    },
    {"text": "S1.3 - A qual órgão do poder público você pertence?",
     "key_prefix": "s_q1_3_orgao_publico", 'input_type': 'text',
      "condition": {"depends_on_key": "s_q1_1_parte_interessada", "expected_value": "Poder Público (específico)"}
    },
    {"text": "S2. - Você gostaria de informar seu nome?",
     "options": ["Sim","Não"],
     "key_prefix": "s_q2_informar_nome", 'input_type': 'radio',
     "condition": {"depends_on_key": "q1_identificacao", "expected_values": ["Morador Comunidade", "Poder Público"]}
    },
    {"text": "S2.1 - Me diga seu nome:",
     "key_prefix": "s_q2_1_nome", 'input_type': 'text', 
     "condition": {"depends_on_key": "s_q2_informar_nome", "expected_value": "Sim"}
    },
    {"text": "S2.2 - Você quer receber retorno do seu comunicado?",
     "options": ["Sim","Não"],
     "key_prefix": "s_q2_2_retorno", 'input_type': 'radio',
     # MODIFICAÇÃO AQUI: Esta pergunta só faz sentido se o usuário permitiu informar dados pessoais (nome ou contato)
     # A condição mais forte é se ele disse "Sim" para informar nome. Se disse "Não", não perguntamos sobre retorno.
     "condition": {"depends_on_key": "s_q2_informar_nome", "expected_value": "Sim"}
    },
    {"text": "S2.3 - Me informe seu contato (WhatsApp ou E-mail):",
     "key_prefix": "s_q2_3_contato", 'input_type': 'text', 
     # Esta condição está correta: só pergunta o contato se ele quis receber retorno.
     # E, pela condição anterior, só chega aqui se ele também quis informar o nome.
     "condition": {"depends_on_key": "s_q2_2_retorno", "expected_value": "Sim"}
    },
    {"text": "S3. - O que você gostaria de comunicar?",
     "options": ["Reclamação","Sugestão","Elogio","Engajamento","Dúvida"],
     "key_prefix": "s_q3_tipo_comunicado", 'input_type': 'radio',
     "condition": {"depends_on_key": "q1_identificacao", "expected_values": ["Morador Comunidade", "Poder Público"]}
    },
    {"text": "S3.1 - Se Reclamação, qual o tipo?",
     "options": ["Poeira","Alta Velocidade","Danos Estrada","Outro"],
     "key_prefix": "s_q3_1_tipo_reclamacao", 'input_type': 'radio',
     "condition": {"depends_on_key": "s_q3_tipo_comunicado", "expected_value": "Reclamação"}
    },
    {"text": "S3.1.1 - Se Outro tipo de reclamação, por favor especifique:",
     "key_prefix": "s_q3_1_1_reclamacao_outro", 'input_type': 'text', 
     "condition": {"depends_on_key": "s_q3_1_tipo_reclamacao", "expected_value": "Outro"}
    },
    {"text": "S3.2 - Descreva sua comunicação (detalhes):",
     "key_prefix": "s_q3_2_descricao", 'input_type': 'text', 
     "condition": {"depends_on_key": "q1_identificacao", "expected_values": ["Morador Comunidade", "Poder Público"]}
    },
    {"text": "S3.2.1 - Seu comunicado é recorrente?",
     "options": ["Sim","Não"],
     "key_prefix": "s_q3_2_1_recorrente", 'input_type': 'radio',
     "condition": {"depends_on_key": "q1_identificacao", "expected_values": ["Morador Comunidade", "Poder Público"]}
    },
    {"text": "S3.2.2 - A quem comunicou/informou anteriormente?",
     "key_prefix": "s_q3_2_2_quem_comunicou", 'input_type': 'text', 
     "condition": {"depends_on_key": "q1_identificacao", "expected_values": ["Morador Comunidade", "Poder Público"]}
    },
    {"text": "S3.2.3 - Há quanto tempo ocorreu o fato ou o último contato?",
     "key_prefix": "s_q3_2_3_quanto_tempo", 'input_type': 'text', 
     "condition": {"depends_on_key": "q1_identificacao", "expected_values": ["Morador Comunidade", "Poder Público"]}
    },
    {"text": "S3.3 - Como você identifica a empresa ou o fato relacionado à empresa?",
     "options": ["Adesivo Veículo","Outra pessoa me informou","Conheço o colaborador","Presenciei o fato","Outro"],
     "key_prefix": "s_q3_3_identifica_empresa", 'input_type': 'radio',
     "condition": {"depends_on_key": "q1_identificacao", "expected_values": ["Morador Comunidade", "Poder Público"]}
    },
    {"text": "S3.3.1 - Se Outro modo de identificação, por favor especifique:",
     "key_prefix": "s_q3_3_1_identifica_outro", 'input_type': 'text', 
     "condition": {"depends_on_key": "s_q3_3_identifica_empresa", "expected_value": "Outro"}
    },
]


FINAL_PROMPT_TEXT = "Obrigado por suas respostas! Deseja enviar a pesquisa?"
TYPING_SPEED = 0.02

# --- Funções Auxiliares ---
def initialize_state():
    default_values = {
        "messages": [],
        "current_question_index": 0,
        "answers": {},
        "stage": "greeting",
        "widget_key_suffix": 0
    }
    for key, value in default_values.items():
        if key not in st.session_state:
            st.session_state[key] = value

def reset_chat():
    st.session_state.messages = []
    st.session_state.current_question_index = 0
    st.session_state.answers = {} 
    st.session_state.stage = "greeting"
    st.session_state.widget_key_suffix += 1
    st.rerun()

def type_assistant_message(text_content):
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        for chunk in text_content:
            full_response += chunk
            time.sleep(TYPING_SPEED)
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": text_content})

def add_user_message_and_store_answer(response_content, question_original_key_prefix):
    st.session_state.messages.append({"role": "user", "content": str(response_content)})
    st.session_state.answers[question_original_key_prefix] = str(response_content)

def check_and_skip_question():
    while st.session_state.current_question_index < len(QUESTIONS_DATA):
        question_info = QUESTIONS_DATA[st.session_state.current_question_index]
        should_skip = False
        if "condition" in question_info:
            cond = question_info["condition"]
            previous_answer = st.session_state.answers.get(cond["depends_on_key"])

            if previous_answer is None: 
                should_skip = True
            else:
                if "expected_value" in cond:
                    if previous_answer != cond["expected_value"]:
                        should_skip = True
                elif "expected_values" in cond: 
                    if previous_answer not in cond["expected_values"]:
                        should_skip = True
                elif "not_expected_value" in cond: 
                    if previous_answer == cond["not_expected_value"]:
                        should_skip = True
                elif "not_expected_values" in cond: 
                    if previous_answer in cond["not_expected_values"]:
                        should_skip = True
        
        if should_skip:
            if question_info["key_prefix"] not in st.session_state.answers or \
               st.session_state.answers[question_info["key_prefix"]] == "Não respondida":
                 st.session_state.answers[question_info["key_prefix"]] = "Não Aplicável (pulada)"
            st.session_state.current_question_index += 1
        else:
            return False 
    return True 

# --- Inicialização do Estado ---
initialize_state()

# --- Exibir histórico de mensagens ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Lógica Principal do Chat por Estágio ---

if st.session_state.stage == "greeting":
    type_assistant_message(GREETING_MESSAGE)
    if QUESTIONS_DATA:
        st.session_state.stage = "questioning"
    else:
        type_assistant_message("Nenhuma pergunta configurada para esta pesquisa.")
        st.session_state.stage = "finished"
    st.rerun()

elif st.session_state.stage == "questioning":
    if check_and_skip_question(): 
        st.session_state.stage = "final_prompt"
        st.rerun()

    current_q_index = st.session_state.current_question_index
    if current_q_index >= len(QUESTIONS_DATA): 
        st.session_state.stage = "final_prompt"
        st.rerun()
    
    question_info = QUESTIONS_DATA[current_q_index]

    if not st.session_state.messages or st.session_state.messages[-1]["content"] != question_info["text"]:
        type_assistant_message(question_info["text"])
        st.rerun() 

    widget_key_prefix = question_info['key_prefix']
    unique_widget_suffix = st.session_state.widget_key_suffix
    
    response_submitted = False
    user_response = None
    input_label = "Sua resposta:"

    if question_info['input_type'] == 'radio':
        radio_widget_key = f"radio_{widget_key_prefix}_{unique_widget_suffix}"
        selected_option = st.radio(
            label=input_label,
            options=question_info["options"],
            key=radio_widget_key,
            index=None
        )
        if st.button("Confirmar Resposta", key=f"confirm_btn_{radio_widget_key}"):
            if selected_option is not None:
                user_response = selected_option
                response_submitted = True
            else:
                st.warning("Por favor, selecione uma opção.")
    
    elif question_info['input_type'] == 'text':
        text_input_widget_key = f"text_input_{widget_key_prefix}_{unique_widget_suffix}"

        if text_input_widget_key not in st.session_state:
            st.session_state[text_input_widget_key] = ""
        
        st.text_input(
            label=input_label,
            key=text_input_widget_key 
        )

        if st.button("Confirmar Resposta", key=f"confirm_btn_{text_input_widget_key}"):
            current_text_value = st.session_state.get(text_input_widget_key, "").strip()
            if current_text_value:
                user_response = current_text_value
                response_submitted = True
            else:
                st.warning("Por favor, digite sua resposta.")

    if response_submitted and user_response is not None:
        add_user_message_and_store_answer(user_response, question_info["key_prefix"])
        st.session_state.current_question_index += 1
        
        if check_and_skip_question() or st.session_state.current_question_index >= len(QUESTIONS_DATA):
            st.session_state.stage = "final_prompt"
        st.rerun()

elif st.session_state.stage == "final_prompt":
    if not st.session_state.messages or st.session_state.messages[-1]["content"] != FINAL_PROMPT_TEXT:
        type_assistant_message(FINAL_PROMPT_TEXT)
        st.rerun()

    final_choice_radio_key = f"final_choice_radio_{st.session_state.widget_key_suffix}"
    final_choice = st.radio(
        label="Sua decisão:",
        options=("Sim", "Não"),
        key=final_choice_radio_key,
        index=None
    )

    finalize_button_key = f"finalize_btn_{final_choice_radio_key}"
    if st.button("Finalizar Pesquisa", key=finalize_button_key):
        if final_choice is not None:
            st.session_state.messages.append({"role": "user", "content": final_choice})

            if final_choice == "Sim":
                submission_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                survey_results_obj = {"Data e Hora do Envio": submission_time}
                
                results_display_str_parts = [
                    "Pesquisa enviada com sucesso! Obrigado pela sua participação.",
                    f"**Enviada em:** {submission_time}\n",
                    "**Resumo das Respostas:**"
                ]
                
                for q_data in QUESTIONS_DATA: 
                    question_text = q_data['text']
                    answer = st.session_state.answers.get(q_data["key_prefix"], "Não respondida")
                    survey_results_obj[question_text] = answer
                    if answer != "Não Aplicável (pulada)": 
                        results_display_str_parts.append(f"- **{question_text}**: {answer}")
                    elif st.session_state.answers.get(q_data["key_prefix"]): 
                         results_display_str_parts.append(f"- **{question_text}**: {answer}")


                final_summary_message = "\n".join(results_display_str_parts)
                type_assistant_message(final_summary_message)
                
                st.success("Dados da pesquisa (também exibidos no chat e abaixo):")
                st.json(survey_results_obj)
            else:
                type_assistant_message("Entendido. A pesquisa não foi enviada. O chat será reiniciado para uma nova tentativa, se desejar.")
                st.info("Pesquisa não enviada.")

            st.session_state.stage = "finished"
            st.rerun()
        else:
            st.warning("Por favor, escolha Sim ou Não para finalizar.")

elif st.session_state.stage == "finished":
    if st.button("Iniciar Nova Pesquisa", key=f"restart_btn_{st.session_state.widget_key_suffix}"):
        reset_chat()