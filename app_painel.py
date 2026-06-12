"""
SCADA Portos RS - Painel de Monitoramento Elétrico Empresarial
Desenvolvido em Python/Streamlit com injeção avançada de UI/UX.
"""

import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime
from streamlit_autorefresh import st_autorefresh # <-- NOVA LINHA AQUI
# ==============================================================================
# 1. CONFIGURAÇÃO DA PÁGINA E DIRETÓRIOS
# ==============================================================================
st.set_page_config(
    page_title="SCADA Portos RS", 
    page_icon="⚡", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

DIRETORIO_ATUAL = os.path.dirname(os.path.abspath(__file__))
CAMINHO_LOGO = os.path.join(DIRETORIO_ATUAL, "logo.png")

# ==============================================================================
# 2. INJEÇÃO DE CSS CUSTOMIZADO GLOBAL
# ==============================================================================
def injetar_css_global():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
        
        /* 3. PROFUNDIDADE E HIERARQUIA VISUAL */
        .stApp { background-color: #021a2f !important; } /* Fundo da página mais escuro */
        .stMarkdown, p, label, .stText { color: #e2e8f0 !important; }

        /* 1. CORREÇÃO DO ESPAÇO VAZIO E HEADER */
        header[data-testid="stHeader"] { display: none !important; }
        .block-container { padding-top: 5rem !important; padding-bottom: 4rem !important; }

        .scada-header {
            position: fixed; top: 0; left: 0; right: 0;
            background-color: #003052; height: 60px; z-index: 99999;
            display: flex; justify-content: space-between; align-items: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.4); padding: 0 24px;
        }
        .header-title-box { display: flex; align-items: center; gap: 15px; }
        .h-title { color: #ffffff !important; font-weight: 700; font-size: 16px; margin:0; line-height: 1;}
        .h-subtitle { color: #94a3b8 !important; font-weight: 500; font-size: 11px; margin:0;}
        
        /* 9. RODAPÉ FIXO */
        .bottom-bar { position: fixed; bottom: 0; left: 0; right: 0; height: 32px; background-color: #011223; border-top: 1px solid #003052; color: white; display: flex; align-items: center; padding: 0 24px; font-size: 11px; font-weight: 600; z-index: 99999; gap: 16px; }

        /* 3. CARDS PRINCIPAIS COM CONTRASTE */
        .info-card {
            background-color: #003b63; /* Fundo do card mais claro que a página */
            border: 1px solid #004b7a;
            border-top: 4px solid #4ade80;
            border-radius: 12px; padding: 20px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.3);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .info-card:hover { transform: translateY(-3px); box-shadow: 0 12px 32px rgba(0,0,0,0.4); border-color: #00609a; }
        .info-card.offline { border-top: 4px solid #ef4444; background-color: #3b0a0a; border-color: #5c1010;}
        
        .card-header-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
        .status-badge { display: flex; align-items: center; gap: 8px; font-size: 12px; font-weight: 700; color: #4ade80; letter-spacing: 0.5px;}
        .status-badge.offline { color: #ef4444; }
        
        .status-dot { width: 10px; height: 10px; border-radius: 50%; background-color: #4ade80; animation: pulse-green 1.5s infinite; box-shadow: 0 0 8px #4ade80;}
        .status-dot.offline { background-color: #ef4444; animation: none; box-shadow: 0 0 8px #ef4444;}
        @keyframes pulse-green { 0%, 100% { transform: scale(1); opacity: 1; } 50% { transform: scale(1.6); opacity: 0.4; } }
        
        .card-title { font-size: 14px; font-weight: 700; color: #ffffff; margin-bottom: 20px; display: flex; align-items: center; gap: 8px; }
        .card-metrics-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; align-items: start; }
        .metric-item { display: flex; flex-direction: column; gap: 4px; }
        .metric-label { font-size: 10px; color: #94a3b8; text-transform: uppercase; font-weight: 600; letter-spacing: 0.5px; }
        .metric-value { font-size: 18px; font-weight: 700; white-space: nowrap;}
        
        /* 5. GAUGE DE CAPACIDADE NA TELA PRINCIPAL */
        .cap-bar-bg { width: 100%; height: 4px; background: rgba(255,255,255,0.1); border-radius: 2px; margin-top: 4px; overflow: hidden;}
        .cap-bar-fill { height: 100%; border-radius: 2px; transition: width 0.5s ease; }

        /* 8. EXPANDER E MINI-CARDS */
        [data-testid="stExpander"] { border: 1px solid #004b7a !important; border-radius: 8px !important; background: #002b49 !important; margin-top: 8px !important; margin-bottom: 24px !important; }
        [data-testid="stExpander"] details summary { padding: 10px 15px !important; }
        [data-testid="stExpander"] details summary p { font-size: 12px !important; color: #94a3b8 !important; font-weight: 600 !important; }
        [data-testid="stExpander"] details { border: none !important; }

        .mini-cards-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(130px, 1fr)); gap: 10px; padding: 10px 0; }
        .mini-card { background-color: #00395d; border: 1px solid #005387; border-radius: 6px; padding: 12px 8px; text-align: center; }
        .mc-label { font-size: 9px; color: #94a3b8; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; display: block;}
        .mc-value { font-size: 14px; font-weight: 700; display: block; }
        .section-title { font-size: 11px; font-weight: 700; color: #94a3b8; letter-spacing: 1px; margin-top: 16px; margin-bottom: 8px; border-bottom: 1px solid #004b7a; padding-bottom: 4px;}

        /* 6. HEALTH BARS COM ZONAS DE ALERTA */
        .health-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; margin-top: 10px; margin-bottom: 20px;}
        .health-card { background: #00223e; border: 1px solid #004b7a; border-radius: 8px; padding: 15px; }
        .h-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
        .h-title { font-size: 10px; color: #94a3b8; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
        .h-delta { font-size: 13px; font-weight: 700; }
        .progress-bg { position: relative; width: 100%; height: 8px; background: #011223; border-radius: 4px; margin-bottom: 8px; overflow: hidden; border: 1px solid #003052;}
        .progress-fill { height: 100%; border-radius: 4px; transition: width 0.5s ease, background-color 0.3s ease; }
        /* Marcadores de Threshold (Limites) */
        .marker-warn { position: absolute; left: 80%; top: 0; bottom: 0; width: 2px; background: #fbbf24; z-index: 2; opacity: 0.7;}
        .marker-danger { position: absolute; left: 95%; top: 0; bottom: 0; width: 2px; background: #ef4444; z-index: 2; opacity: 0.7;}
        .h-footer { font-size: 11px; color: #64748b; display: flex; justify-content: space-between; }
        .h-val-medido { font-weight: 700; color: #ffffff; }

        /* 7. ESTILIZAÇÃO NATIVA DAS ABAS STREAMLIT */
        div[data-testid="stTabs"] button { color: #94a3b8 !important; background-color: transparent !important; font-weight: 600 !important; border-bottom: 2px solid transparent !important;}
        div[data-testid="stTabs"] button[aria-selected="true"] { color: #ffffff !important; border-bottom: 2px solid #00aeef !important; }
        div[data-testid="stTabs"] button:hover { color: #00aeef !important; }
        </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 3. VARIÁVEIS E REGRAS DE NEGÓCIO (Cores Semânticas e Dados de Placa)
# ==============================================================================
# Dicionário com o Título Completo de Engenharia (Nome - kVA - Tensão - Disjuntor)
DICIONARIO_NOMES = {
    'MED_SUB_SE-A': 'Subestação A — 225 kVA — 220/127V (600A)', 
    'MED_SUB_SE-B': 'Subestação B — 225 kVA — 220/127V (600A)',
    'MED_SUB_SE-C': 'Subestação C — 225 kVA — 220/127V (600A)', 
    'MED_SUB_SE-D': 'Subestação D — 45 kVA — 380/220V (100A)',
    'MED_SUB_SE-R_E': 'Subestação E — 225 kVA — 220/127V (600A)', 
    'MED_SUB_SE-E_F': 'Subestação F — 225 kVA — 220/127V (600A)',
    'MED_SUB_SE-G': 'Subestação G — 225 kVA — 220/127V (600A)', 
    'MED_SUB_SE-T_H': 'Subestação H — 45 kVA — 380/220V (70A)',
    'MED_SUB_SE-01_I': 'Subestação I — 45 kVA — 380/220V (100A)', 
    'MED_SUB_SE-02_J': 'Subestação J — 45 kVA — 380/220V (100A)'
}

def obter_cor_semantica(tipo, valor):
    """Hierarquia semântica rígida para o Dark Mode"""
    try: v = float(valor)
    except: return "#e2e8f0"

    if tipo == 'V': return "#ef4444" if (v < 195 or v > 245) else "#38bdf8" # Ciano
    elif tipo == 'A': return "#ef4444" if v > 100 else "#fbbf24" # Amarelo/Âmbar
    elif tipo == 'Hz': return "#ef4444" if (v < 59.5 or v > 60.5) else "#a78bfa" # Roxo claro
    elif tipo == 'PF':
        if v >= 0.92: return "#4ade80" # Verde
        if v >= 0.85: return "#fbbf24" # Amarelo
        return "#ef4444" # Vermelho
    elif tipo == 'THD':
        if v > 10: return "#ef4444"
        if v > 5: return "#fbbf24"
        return "#4ade80"
    elif tipo == 'MC_V': return "#38bdf8"
    elif tipo == 'MC_A': return "#fbbf24"
    elif tipo == 'MC_W': return "#c084fc" # Roxo
    return "#e2e8f0"

def extrair_dados_placa(nome_completo):
    """Lê a string do nome da subestação e extrai os valores nominais matemáticos."""
    # Extrai kVA (Transformador)
    if '225 kVA' in nome_completo: kva_nom = 225000
    elif '45 kVA' in nome_completo: kva_nom = 45000
    else: kva_nom = 100000
    
    # Extrai Tensão Nominal de Fase (Fase-Neutro)
    if '220/127V' in nome_completo: v_nom = 127.0
    elif '380/220V' in nome_completo: v_nom = 220.0
    else: v_nom = 127.0
    
    # Extrai Corrente do Disjuntor Geral (Amperes)
    if '600A' in nome_completo: i_nom = 600.0
    elif '100A' in nome_completo: i_nom = 100.0
    elif '70A' in nome_completo: i_nom = 70.0
    else: i_nom = 100.0
    
    return kva_nom, v_nom, i_nom

def ler_ultimos_dados(nome_arquivo_csv):
    caminho = os.path.join(DIRETORIO_ATUAL, f"{nome_arquivo_csv}.csv")
    if os.path.exists(caminho):
        try:
            df = pd.read_csv(caminho, sep=';')
            if not df.empty: return df.iloc[-1].to_dict()
        except: return None
    return None

def ler_ultimos_dados(nome_arquivo_csv):
    caminho = os.path.join(DIRETORIO_ATUAL, f"{nome_arquivo_csv}.csv")
    if os.path.exists(caminho):
        try:
            df = pd.read_csv(caminho, sep=';')
            if not df.empty: return df.iloc[-1].to_dict()
        except: return None
    return None

# ==============================================================================
# 4. COMPONENTES VISUAIS (HTML INJECTORS)
# ==============================================================================
def renderizar_header(onlines, totais):
    agora = datetime.now()
    hora_str = agora.strftime('%H:%M:%S')
    data_str = agora.strftime('%d %b %Y')
    
    import base64
    logo_html = ""
    if os.path.exists(CAMINHO_LOGO):
        with open(CAMINHO_LOGO, "rb") as f:
            encoded_string = base64.b64encode(f.read()).decode()
            logo_html = f'<img src="data:image/png;base64,{encoded_string}" style="height:35px;">'
    else:
        logo_html = '<span style="font-weight:900; font-size:20px; color:white;">⚡ PORTOS RS</span>'

    header_html = f"""
    <div class="scada-header">
        <div class="header-top">
            <div style="display:flex;align-items:center;gap:16px;">
                {logo_html}
                <div>
                    <p class="h-title">PAINEL DE MONITORAMENTO ELÉTRICO</p>
                    <p class="h-subtitle">Portos do Rio Grande — Infraestrutura SCADA</p>
                </div>
            </div>
            <div class="clock">{hora_str} &nbsp;|&nbsp; {data_str}</div>
        </div>
        <div class="header-status-bar">
            <span style="color:white;font-size:12px;font-weight:600;display:flex;align-items:center;">
                <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background-color:#22c55e; margin-right:6px; animation: pulse-green 2s infinite;"></span> REDE ONLINE
            </span>
            <span class="pill">{onlines} / {totais} Ativas</span>
        </div>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)

def renderizar_footer(onlines, offlines, atencoes):
    footer_html = f"""
    <div class="bottom-bar">
        <span style="display:flex;align-items:center;gap:6px;">
            <span style="width:8px;height:8px;border-radius:50%;background:#4ade80;display:inline-block;"></span>
            {onlines} Online
        </span>
        <span style="display:flex;align-items:center;gap:6px; color:#fbbf24;">
            <span style="width:8px;height:8px;border-radius:50%;background:#fbbf24;display:inline-block;"></span>
            {atencoes} Atenção
        </span>
        <span style="display:flex;align-items:center;gap:6px; color:#f87171;">
            <span style="width:8px;height:8px;border-radius:50%;background:#ef4444;display:inline-block;"></span>
            {offlines} Offline
        </span>
        <span style="margin-left:auto; color:#94a3b8; display:flex; align-items:center; gap:12px;">
            <span>SCADA Portos RS v2.1</span>
            <span>|</span>
            <span id="footer-clock" style="font-family:monospace; color:#ffffff;">--:--:--</span>
        </span>
    </div>
    <script>
        (function() {{
            function tickFooter() {{
                var el = document.getElementById('footer-clock');
                if(el) el.textContent = new Date().toLocaleTimeString('pt-BR');
            }}
            tickFooter(); setInterval(tickFooter, 1000);
        }})();
    </script>
    """
    st.markdown(footer_html, unsafe_allow_html=True)

# ==============================================================================
# 5. TELAS DO SISTEMA
# ==============================================================================
def css_tela_login(shake=False):
    animacao_shake = """
        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
            20%, 40%, 60%, 80% { transform: translateX(5px); }
        }
        [data-testid="stForm"] { 
            animation: shake 0.5s !important; 
            border: 2px solid #ef4444 !important; 
        }
    """ if shake else ""
    
    animacao_entrada = "" if shake else "animation: loginEntrada 0.45s cubic-bezier(0.16, 1, 0.3, 1) both;"

    st.markdown(f"""
        <style>
        @keyframes loginEntrada {{
            from {{ opacity: 0; transform: translateY(24px); }}
            to   {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .stApp {{
            background-color: #005387 !important;
            background-image: radial-gradient(circle, rgba(255,255,255,0.06) 1px, transparent 1px);
            background-size: 20px 20px;
        }}
        
        /* 2. Limitar a largura do formulário e centralizar no card */
        [data-testid="stForm"] {{
            background-color: #ffffff !important;
            padding: 40px 30px 50px 30px !important; /* Padding bottom extra para respiro do autocomplete */
            border-radius: 16px !important;
            box-shadow: 0 24px 48px rgba(0,0,0,0.25) !important;
            border: none !important; /* Reset de borda */
            max-width: 380px !important; /* Constrição de largura */
            margin: 8vh auto 0 auto !important; /* Centraliza horizontalmente na tela */
            {animacao_entrada}
        }}
        
        {animacao_shake}
        
        [data-testid="stForm"] p, [data-testid="stForm"] label {{
            color: #64748b !important;
        }}
        
        /* 1. Sumir com o "Press Enter to submit form" e labels fantasmas do Streamlit */
        [data-testid="stTextInput"] label, 
        [data-testid="stTextInput"] div[data-testid="InputInstructions"] {{
            display: none !important;
        }}
        
        /* 3. Ajustar o input de senha para não sobrepor o ícone do olho e o cadeado */
        [data-testid="stTextInput"] input {{
            border: 1.5px solid #e0e6ed !important;
            border-radius: 10px !important;
            height: 48px !important;
            font-size: 16px !important;
            text-align: center !important;
            color: #005387 !important;
            background-color: #f8fafc !important;
            transition: border-color 0.2s ease !important;
            letter-spacing: 4px !important; /* Melhora estética dos pontos da senha */
            padding-right: 45px !important; /* Garante espaço para o olho nativo */
            padding-left: 45px !important; /* Garante espaço para o cadeado SVG */
            background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="%2394a3b8" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>') !important;
            background-repeat: no-repeat !important;
            background-position: 16px center !important;
        }}
        
        /* 4. Corrigir o foco e eliminar a borda vermelha indesejada */
        [data-testid="stTextInput"] input:focus {{
            border-color: #00aeef !important;
            box-shadow: 0 0 0 3px rgba(0, 174, 239, 0.15) !important;
            background-color: #ffffff !important;
            outline: none !important;
        }}

        /* Espaçamento extra do botão para evitar a oclusão pelo menu do navegador */
        [data-testid="stFormSubmitButton"] > button {{
            background: #005387 !important;
            color: #ffffff !important;
            height: 48px !important;
            border-radius: 10px !important;
            font-size: 14px !important;
            font-weight: 700 !important;
            letter-spacing: 0.5px;
            margin-top: 25px !important; /* Aumentado para dar respiro */
            width: 100%;
            border: none !important;
            transition: all 0.3s ease !important;
        }}
        [data-testid="stFormSubmitButton"] > button:hover {{
            background: #00aeef !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 12px rgba(0, 174, 239, 0.4) !important;
        }}
        </style>
    """, unsafe_allow_html=True)
def tela_login():
    if 'login_erro' not in st.session_state: st.session_state['login_erro'] = False
    
    css_tela_login(shake=st.session_state['login_erro'])
    
    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    with col2:
        with st.form("form_login", clear_on_submit=False):
            
            if os.path.exists(CAMINHO_LOGO):
                import base64
                with open(CAMINHO_LOGO, "rb") as f:
                    encoded_string = base64.b64encode(f.read()).decode()
                st.markdown(f'<div style="text-align: center; margin-bottom: 15px;"><img src="data:image/png;base64,{encoded_string}" width="220"></div>', unsafe_allow_html=True)
            else:
                st.markdown('<h1 style="text-align: center; color: #005387;">⚡ SCADA</h1>', unsafe_allow_html=True)
                
            st.markdown("<h3 style='text-align: center; color: #005387; margin-bottom: 0px;'>SISTEMA SCADA</h3>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; font-size: 14px; margin-top: 0px;'>Monitoramento de Infraestrutura Elétrica</p>", unsafe_allow_html=True)
            
            st.write("")
            
            # Input nativo do Streamlit
            senha_digitada = st.text_input("Senha", type="password", placeholder="••••••••", label_visibility="collapsed")
            
            submit = st.form_submit_button("ACESSAR SISTEMA")
            
            if submit:
                if senha_digitada == "dinfraportosrs":
                    st.session_state['logado'] = True
                    st.session_state['login_erro'] = False
                    st.rerun()
                else:
                    st.session_state['login_erro'] = True
                    st.rerun()
            
            if st.session_state['login_erro']:
                st.markdown("<p style='color:#ef4444; font-size:13px; text-align: center; font-weight:600; margin-top: 10px;'>Credenciais inválidas. Tente novamente.</p>", unsafe_allow_html=True)
            
            st.markdown("<p style='text-align: center; font-size: 11px; margin-top: 25px; color: #94a3b8;'>v2.0 · Portos RS © 2025</p>", unsafe_allow_html=True)
def verificar_status_online(data_hora_str):
    """Retorna True se a última leitura ocorreu nos últimos 2 minutos (120 segundos)."""
    if not data_hora_str or data_hora_str == 'N/A':
        return False
    try:
        # Converte a string do CSV para um objeto de tempo do Python
        dt_leitura = datetime.strptime(data_hora_str, '%d/%m/%Y %H:%M:%S')
        dt_agora = datetime.now()
        diferenca_segundos = (dt_agora - dt_leitura).total_seconds()
        
        # Se a diferença for menor ou igual a 120 segundos, está ONLINE
        return diferenca_segundos <= 120
    except:
        return False

def tela_dashboard():
    injetar_css_global()
    
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=10000, key="data_refresh")
    
    import requests
    FIREBASE_URL = 'https://scada-portos-rs-cb2ab-default-rtdb.firebaseio.com'
    
    banco_de_dados = {}
    try:
        resposta = requests.get(f"{FIREBASE_URL}/tempo_real.json", timeout=5)
        if resposta.status_code == 200 and resposta.json() is not None:
            banco_de_dados = resposta.json()
    except: pass
    
    dados_gerais = []
    onlines = 0
    atencoes = 0
    for nome_banco, nome_bonito in DICIONARIO_NOMES.items():
        dados = banco_de_dados.get(nome_banco, None)
        is_online = False
        
        if dados is not None:
            try:
                dt_leitura = datetime.strptime(dados.get('Data_Hora', ''), '%d/%m/%Y %H:%M:%S')
                if (datetime.now() - dt_leitura).total_seconds() <= 120:
                    is_online = True
                    onlines += 1
            except: pass
            
        dados_gerais.append((nome_banco, nome_bonito, dados, is_online))
        
    offlines = len(DICIONARIO_NOMES) - onlines
    
    import base64
    logo_html = ""
    if os.path.exists(CAMINHO_LOGO):
        with open(CAMINHO_LOGO, "rb") as f:
            encoded_string = base64.b64encode(f.read()).decode()
            logo_html = f'<img src="data:image/png;base64,{encoded_string}" style="height:35px;">'
    
    st.markdown(f"""
    <div class="scada-header">
        <div class="header-title-box">
            {logo_html}
            <div>
                <p class="h-title">MONITORAMENTO ELÉTRICO</p>
                <p class="h-subtitle">Infraestrutura SCADA</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_vazia, col_sair = st.columns([8, 1])
    with col_sair:
        if st.button("🚪 Sair do Sistema", width="stretch"):
            st.session_state['logado'] = False
            st.rerun()

    aba_tempo_real, aba_historico = st.tabs(["⚡ Monitoramento em Tempo Real", "📈 Histórico e Backup (Nuvem)"])

    with aba_tempo_real:
        colunas_grid = st.columns(3)
        
        for i, (nome_banco, nome_bonito, dados, is_online) in enumerate(dados_gerais):
            coluna_atual = colunas_grid[i % 3]
            
            with coluna_atual:
                if is_online and dados is not None:
                    kva_nom, v_nom, i_nom = extrair_dados_placa(nome_bonito)
                    
                    data_hora = dados.get('Data_Hora', 'N/A')
                    v_avg = dados.get('Tensao_Media_V', 0.0)
                    i_avg = dados.get('Corrente_Media_A', 0.0)
                    p_tot = dados.get('Potencia_Total_W', 0.0)
                    s_total = dados.get('Potencia_Aparente_Total_VA', 0.0)
                    
                    cV = obter_cor_semantica('V', v_avg)
                    cA = obter_cor_semantica('A', i_avg)
                    
                    # CÁLCULOS DO GAUGE DE POTÊNCIA (Fator de Carregamento do Trafo)
                    s_perc = (s_total / kva_nom) * 100 if kva_nom > 0 else 0
                    s_color = "#4ade80" # Verde
                    if s_perc > 75: s_color = "#fbbf24" # Amarelo
                    if s_perc > 90: s_color = "#ef4444" # Vermelho
                    s_bar_width = min(s_perc, 100) # Garante que a barra não passe de 100%

                    # CÁLCULOS DA TENSÃO
                    v_diff_perc = ((v_avg - v_nom) / v_nom) * 100 if v_nom > 0 else 0
                    v_color = "#4ade80"
                    if v_diff_perc < -8.0 or v_diff_perc > 5.0: v_color = "#ef4444"
                    v_seta = "▲" if v_diff_perc > 0 else ("▼" if v_diff_perc < 0 else "")
                    v_bar_width = min(max(50 + (v_diff_perc * 2), 0), 100) 

                    # CÁLCULOS DA CORRENTE (Disjuntor)
                    i_perc = (i_avg / i_nom) * 100 if i_nom > 0 else 0
                    i_color = "#4ade80"
                    if i_perc > 80: i_color = "#fbbf24"
                    if i_perc > 95: i_color = "#ef4444"
                    i_bar_width = min(i_perc, 100)

                    if cV == "#ef4444" or cA == "#ef4444" or s_color == "#ef4444":
                        atencoes += 1

                    card_html = f"""
                    <div class="info-card">
                        <div class="card-header-row">
                            <div class="status-badge"><div class="status-dot"></div> ONLINE</div>
                            <div style="font-size:10px; color:#64748b; font-weight:600;">{data_hora}</div>
                        </div>
                        <div class="card-title">🔌 {nome_bonito}</div>
                        <div class="card-metrics-row">
                            <div class="metric-item">
                                <span class="metric-label">Tensão Média</span>
                                <span class="metric-value" style="color:{cV}">{v_avg} V</span>
                            </div>
                            <div class="metric-item">
                                <span class="metric-label">Corr. Média</span>
                                <span class="metric-value" style="color:{cA}">{i_avg} A</span>
                            </div>
                            <div class="metric-item">
                                <span class="metric-label">Pot. Ativa</span>
                                <span class="metric-value" style="color:#c084fc">{p_tot} W</span>
                            </div>
                            <div class="metric-item">
                                <span class="metric-label">Pot. Aparente</span>
                                <span class="metric-value" style="color:#c084fc">{s_total/1000:.1f} kVA</span>
                                <div class="cap-bar-bg">
                                    <div class="cap-bar-fill" style="width:{s_bar_width}%; background-color:{s_color};"></div>
                                </div>
                                <span style="font-size:9px; color:{s_color}; font-weight:600; margin-top:2px;">Uso: {s_perc:.1f}%</span>
                            </div>
                        </div>
                    </div>
                    """
                    st.markdown(card_html, unsafe_allow_html=True)
                    
                    with st.expander("⚙️ Ver detalhamento técnico"):
                        html_health = f"""
                        <div class="health-grid">
                            <div class="health-card">
                                <div class="h-header"><span class="h-title">Variação da Tensão</span><span class="h-delta" style="color:{v_color}">{v_seta} {abs(v_diff_perc):.1f}%</span></div>
                                <div class="progress-bg">
                                    <div class="progress-fill" style="width: {v_bar_width}%; background-color: {v_color};"></div>
                                </div>
                                <div class="h-footer"><span>Ref: {v_nom}V</span><span class="h-val-medido">{v_avg:.1f} V</span></div>
                            </div>
                            <div class="health-card">
                                <div class="h-header"><span class="h-title">Carga do Disjuntor</span><span class="h-delta" style="color:{i_color}">{i_perc:.1f}%</span></div>
                                <div class="progress-bg">
                                    <div class="progress-fill" style="width: {i_bar_width}%; background-color: {i_color};"></div>
                                    <div class="marker-warn"></div><div class="marker-danger"></div>
                                </div>
                                <div class="h-footer"><span>Max: {i_nom}A</span><span class="h-val-medido">{i_avg:.1f} A</span></div>
                            </div>
                        </div>
                        """
                        st.markdown(html_health, unsafe_allow_html=True)
                        
                        st.markdown("<div class='section-title'>DADOS BRUTOS POR FASE</div>", unsafe_allow_html=True)
                        html_metricas = '<div class="mini-cards-grid">'
                        for chave, valor in dados.items():
                            if chave in ['Data_Hora', 'Tensao_Media_V', 'Corrente_Media_A', 'Potencia_Total_W', 'Potencia_Aparente_Total_VA']: continue
                            cor_mc = "#e2e8f0"
                            if '_V' in chave: cor_mc = obter_cor_semantica('MC_V', valor)
                            elif '_A' in chave: cor_mc = obter_cor_semantica('MC_A', valor)
                            elif '_W' in chave or '_VA' in chave: cor_mc = obter_cor_semantica('MC_W', valor)
                            elif 'Fator_Potencia' in chave: cor_mc = obter_cor_semantica('PF', valor)
                            
                            nome_exibicao = chave.replace('_W', ' (W)').replace('_VA', ' (VA)').replace('_', ' ').upper()
                            html_metricas += f'<div class="mini-card"><span class="mc-label">{nome_exibicao}</span><span class="mc-value" style="color:{cor_mc}">{valor}</span></div>'
                        html_metricas += "</div>"
                        st.markdown(html_metricas, unsafe_allow_html=True)
                        
                else:
                    ultima_tentativa = dados.get('Data_Hora', 'Desconhecida') if dados else 'Desconhecida'
                    if ultima_tentativa == 'Desconhecida': mensagem_tempo = "Aguardando leitura..."
                    else:
                        try:
                            dt_leitura = datetime.strptime(ultima_tentativa, '%d/%m/%Y %H:%M:%S')
                            segundos = int((datetime.now() - dt_leitura).total_seconds())
                            dias, horas, minutos = segundos // 86400, (segundos % 86400) // 3600, (segundos % 3600) // 60
                            partes = []
                            if dias > 0: partes.append(f"{dias} d")
                            if horas > 0: partes.append(f"{horas} h")
                            if minutos > 0: partes.append(f"{minutos} min")
                            tempo_str = " e ".join([", ".join(partes[:-1]), partes[-1]]) if len(partes) > 1 else partes[0] if partes else "segundos"
                            mensagem_tempo = f"Não responde há <b>{tempo_str}</b>."
                        except: mensagem_tempo = "Desconectado."

                    card_html = f"""
                    <div class="info-card offline">
                        <div class="card-header-row">
                            <div class="status-badge offline"><div class="status-dot offline"></div> OFFLINE</div>
                            <div style="font-size:11px; color:#94a3b8; font-weight:500;">{ultima_tentativa}</div>
                        </div>
                        <div class="card-title" style="color:#f87171;">🔌 {nome_bonito}</div>
                        <div style="text-align:center; padding: 10px 0;">
                            <div style="font-weight:600; color:#f87171; font-size:14px;">Falha de Comunicação</div>
                            <div style="font-size:12px; color:#94a3b8; margin-top:4px;">{mensagem_tempo}</div>
                        </div>
                    </div>
                    """
                    st.markdown(card_html, unsafe_allow_html=True)

    renderizar_footer(onlines, offlines, atencoes)

    with aba_historico:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<h3 style='color:#ffffff; font-size:18px;'>Análise de Dados Históricos (Nuvem)</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color:#94a3b8; font-size:13px;'>Gere gráficos e exporte dados a partir do histórico armazenado no servidor Firebase.</p>", unsafe_allow_html=True)
        
        col_filtro1, col_filtro2, col_filtro3 = st.columns([2, 1, 1])
        nomes_bonitos = list(DICIONARIO_NOMES.values())
        sub_escolhida = col_filtro1.selectbox("Selecione a Subestação", nomes_bonitos)
        nome_banco = [k for k, v in DICIONARIO_NOMES.items() if v == sub_escolhida][0]
        
        data_inicio = col_filtro2.date_input("Data Inicial")
        data_fim = col_filtro3.date_input("Data Final")
        
        if st.button("Gerar Gráfico e Tabela", type="primary", width="stretch"):
            with st.spinner("Baixando histórico da nuvem..."):
                datas_selecionadas = pd.date_range(data_inicio, data_fim).strftime('%Y-%m-%d').tolist()
                dados_historico = []
                for dia in datas_selecionadas:
                    url_busca = f"{FIREBASE_URL}/historico/{nome_banco}/{dia}.json"
                    try:
                        res = requests.get(url_busca, timeout=10)
                        if res.status_code == 200 and res.json() is not None:
                            for hora, valores in res.json().items(): dados_historico.append(valores)
                    except: continue
                
                if dados_historico:
                    df_filtrado = pd.DataFrame(dados_historico)
                    df_filtrado['Data_Hora_Obj'] = pd.to_datetime(df_filtrado['Data_Hora'], format='%d/%m/%Y %H:%M:%S')
                    df_filtrado = df_filtrado.sort_values('Data_Hora_Obj').reset_index(drop=True)
                    
                    st.markdown(f"<h4 style='color:#38bdf8; font-size:14px; margin-top:20px;'>📈 Curva de Potência Total (W)</h4>", unsafe_allow_html=True)
                    st.line_chart(df_filtrado, x='Data_Hora', y='Potencia_Total_W', color="#00aeef")
                    
                    st.markdown("<h4 style='color:#38bdf8; font-size:14px; margin-top:20px;'>📋 Dados Brutos</h4>", unsafe_allow_html=True)
                    st.dataframe(df_filtrado.drop(columns=['Data_Hora_Obj']), width="stretch")
                else:
                    st.warning("Nenhum dado encontrado na nuvem para este período.")
                                     
# MAIN ROUTER
# ==============================================================================
def main():
    if 'logado' not in st.session_state: st.session_state['logado'] = False
    
    if not st.session_state['logado']:
        tela_login()
    else:
        tela_dashboard()

if __name__ == "__main__":
    main()