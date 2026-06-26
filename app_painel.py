"""
SCADA Portos RS - Painel de Monitoramento Elétrico Empresarial
Desenvolvido em Python/Streamlit com injeção avançada de UI/UX.
"""
import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime, timedelta, timezone # <-- Atualizado
import plotly.graph_objects as go

# --- NOVA FUNÇÃO DE FUSO HORÁRIO ---
def obter_hora_brasil():
    """Força o servidor da nuvem a usar a hora de Brasília (UTC-3)"""
    return datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=3)
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
        
        .stApp { background-color: #021a2f !important; }
        .stMarkdown, p, label, .stText { color: #e2e8f0 !important; }

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
        
        .bottom-bar { position: fixed; bottom: 0; left: 0; right: 0; height: 32px; background-color: #011223; border-top: 1px solid #003052; color: white; display: flex; align-items: center; padding: 0 24px; font-size: 11px; font-weight: 600; z-index: 99999; gap: 16px; }

        .info-card {
            background-color: #003b63;
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
        .metric-sub { font-size: 11px; font-weight: 600; margin-top: 4px; }

        [data-testid="stExpander"] { border: 1px solid #004b7a !important; border-radius: 8px !important; background: #002b49 !important; margin-top: 8px !important; margin-bottom: 24px !important; }
        [data-testid="stExpander"] details summary { padding: 10px 15px !important; }
        [data-testid="stExpander"] details summary p { font-size: 12px !important; color: #94a3b8 !important; font-weight: 600 !important; }
        [data-testid="stExpander"] details { border: none !important; }

        .mini-cards-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(130px, 1fr)); gap: 10px; padding: 10px 0; }
        .mini-card { background-color: #00395d; border: 1px solid #005387; border-radius: 6px; padding: 12px 8px; text-align: center; }
        .mc-label { font-size: 9px; color: #94a3b8; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; display: block;}
        .mc-value { font-size: 14px; font-weight: 700; display: block; }

        div[data-testid="stTabs"] button { color: #94a3b8 !important; background-color: transparent !important; font-weight: 600 !important; border-bottom: 2px solid transparent !important;}
        div[data-testid="stTabs"] button[aria-selected="true"] { color: #ffffff !important; border-bottom: 2px solid #00aeef !important; }
        div[data-testid="stTabs"] button:hover { color: #00aeef !important; }
        
        .logout-container { position: fixed; top: 14px; right: 24px; z-index: 999999; }
        .logout-container button { background: rgba(0,0,0,0.2) !important; border: 1px solid rgba(255,255,255,0.3) !important; color: white !important; padding: 2px 12px !important; height: 32px !important; font-size: 12px !important; }
        .logout-container button:hover { background: #ef4444 !important; border-color: #ef4444 !important; }
                /* =========================================
           PLOTLY DARK THEME CUSTOMIZATION
           ========================================= */
        [data-testid="stPlotlyChart"] > div {
            border-radius: 10px !important;
            overflow: hidden !important;
            border: 1px solid rgba(255,255,255,0.07) !important;
        }
        iframe[title="plotly"] {
            background: transparent !important;
        }
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
    """Regra de Cores: Branco (Normal) | Vermelho (Fora do Parâmetro)"""
    try: v = float(valor)
    except: return "#ffffff"

    if tipo == 'V': return "#ef4444" if (v < 195 or v > 245) else "#ffffff"
    elif tipo == 'A': return "#ef4444" if v > 100 else "#ffffff"
    elif tipo == 'Hz': return "#ef4444" if (v < 59.5 or v > 60.5) else "#ffffff"
    elif tipo == 'PF': return "#ef4444" if v < 0.92 else "#ffffff"
    elif tipo == 'THD': return "#ef4444" if v > 10 else "#ffffff"
    
    return "#ffffff" # Padrão para os demais (Potências, etc)

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
    agora = obter_hora_brasil()
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
        dt_agora = obter_hora_brasil()
        diferenca_segundos = (dt_agora - dt_leitura).total_seconds()
        
        # Se a diferença for menor ou igual a 120 segundos, está ONLINE
        return diferenca_segundos <= 120
    except:
        return False
# ==============================================================================
# MOTOR DE GRÁFICOS PLOTLY (DARK THEME INDUSTRIAL)
# ==============================================================================
def hex_to_rgb(hex_color: str) -> str:
    hex_color = hex_color.lstrip('#')
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return f'{r},{g},{b}'

def renderizar_grafico_profissional(
    df: pd.DataFrame, coluna_y: str, coluna_x: str = 'Data_Hora_Obj',
    titulo: str = '', unidade: str = '',
    limite_min_ok: float = None, limite_max_ok: float = None,
    limite_min_atencao: float = None, limite_max_atencao: float = None,
    limite_critico_min: float = None, limite_critico_max: float = None,
    cor_linha: str = '#00aeef', mostrar_media: bool = True, mostrar_min_max: bool = True
) -> go.Figure:
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df[coluna_x], y=df[coluna_y], mode='lines', name=titulo,
        line=dict(color=cor_linha, width=2, shape='spline', smoothing=0.4),
        fill='tozeroy', fillcolor=f'rgba({hex_to_rgb(cor_linha)}, 0.15)',
        hovertemplate=f'<b>%{{x|%d/%m/%Y %H:%M}}</b><br>{titulo}: <b>%{{y:,.2f}} {unidade}</b><extra></extra>'
    ))

    if limite_min_ok is not None and limite_max_ok is not None:
        fig.add_hrect(y0=limite_min_ok, y1=limite_max_ok, fillcolor='rgba(34,197,94,0.08)', layer='below', line_width=0,
                      annotation_text='▶ Faixa Adequada', annotation_position='top right', annotation_font=dict(size=10, color='rgba(34,197,94,0.9)'))
        for y_val in [limite_min_ok, limite_max_ok]:
            fig.add_hline(y=y_val, line=dict(color='rgba(34,197,94,0.6)', width=1, dash='dot'))

    if limite_min_atencao is not None and limite_min_ok is not None:
        fig.add_hrect(y0=limite_min_atencao, y1=limite_min_ok, fillcolor='rgba(245,158,11,0.07)', layer='below', line_width=0)
        fig.add_hline(y=limite_min_atencao, line=dict(color='rgba(245,158,11,0.5)', width=1, dash='dash'),
                      annotation_text='⚠ Zona de Atenção', annotation_position='bottom right', annotation_font=dict(size=10, color='rgba(245,158,11,0.9)'))

    if limite_max_atencao is not None and limite_max_ok is not None:
        fig.add_hrect(y0=limite_max_ok, y1=limite_max_atencao, fillcolor='rgba(245,158,11,0.07)', layer='below', line_width=0)

    if limite_critico_min is not None:
        fig.add_hrect(y0=df[coluna_y].min() * 0.95, y1=limite_critico_min, fillcolor='rgba(239,68,68,0.08)', layer='below', line_width=0)
        fig.add_hline(y=limite_critico_min, line=dict(color='rgba(239,68,68,0.6)', width=1, dash='dash'),
                      annotation_text='✕ Limite Crítico', annotation_position='top right', annotation_font=dict(size=10, color='rgba(239,68,68,0.9)'))

    if limite_critico_max is not None:
        fig.add_hrect(y0=limite_critico_max, y1=df[coluna_y].max() * 1.05 if df[coluna_y].max() > limite_critico_max else limite_critico_max * 1.05,
                      fillcolor='rgba(239,68,68,0.08)', layer='below', line_width=0)
        fig.add_hline(y=limite_critico_max, line=dict(color='rgba(239,68,68,0.6)', width=1, dash='dash'),
                      annotation_text='✕ Limite Crítico', annotation_position='bottom right', annotation_font=dict(size=10, color='rgba(239,68,68,0.9)'))

    if mostrar_min_max and not df.empty:
        idx_max, idx_min = df[coluna_y].idxmax(), df[coluna_y].idxmin()
        val_max, val_min = df[coluna_y].max(), df[coluna_y].min()
        x_max, x_min = df[coluna_x].iloc[idx_max], df[coluna_x].iloc[idx_min]

        fig.add_trace(go.Scatter(x=[x_max], y=[val_max], mode='markers+text', name='Máximo',
            marker=dict(symbol='triangle-up', size=12, color='#ef4444', line=dict(color='#fff', width=1)),
            text=[f'▲ Máx: {val_max:,.2f} {unidade}'], textposition='top center', textfont=dict(size=11, color='#ff6b6b'),
            hovertemplate=f'Máximo: <b>{val_max:,.2f} {unidade}</b><br>%{{x|%d/%m %H:%M}}<extra></extra>'))

        fig.add_trace(go.Scatter(x=[x_min], y=[val_min], mode='markers+text', name='Mínimo',
            marker=dict(symbol='triangle-down', size=12, color='#22c55e', line=dict(color='#fff', width=1)),
            text=[f'▼ Mín: {val_min:,.2f} {unidade}'], textposition='bottom center', textfont=dict(size=11, color='#4ade80'),
            hovertemplate=f'Mínimo: <b>{val_min:,.2f} {unidade}</b><br>%{{x|%d/%m %H:%M}}<extra></extra>'))

    if mostrar_media and not df.empty:
        media = df[coluna_y].mean()
        fig.add_hline(y=media, line=dict(color='rgba(255,255,255,0.4)', width=1.2, dash='longdash'),
                      annotation_text=f'Média: {media:,.2f} {unidade}', annotation_position='top left', annotation_font=dict(size=11, color='rgba(255,255,255,0.8)'))

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.15)',
        font=dict(family='Inter, sans-serif', color='#e2e8f0', size=12),
        title=dict(text=titulo, font=dict(color='#ffffff', size=16), x=0.01, xanchor='left', pad=dict(b=12)),
        xaxis=dict(gridcolor='rgba(255,255,255,0.15)', linecolor='rgba(255,255,255,0.2)', tickcolor='rgba(255,255,255,0.3)', tickformat='%H:%M\n%d/%m', nticks=12, showgrid=True),
        yaxis=dict(gridcolor='rgba(255,255,255,0.15)', linecolor='rgba(255,255,255,0.2)', ticksuffix=f' {unidade}', showgrid=True),
        margin=dict(l=60, r=40, t=50, b=40), hovermode='x unified',
        # AQUI ESTÁ A CORREÇÃO: font=dict(color='#ffffff') força a legenda a ficar branca
        legend=dict(bgcolor='rgba(0,43,73,0.9)', bordercolor='rgba(255,255,255,0.3)', borderwidth=1, orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1, font=dict(color='#ffffff')),
        hoverlabel=dict(bgcolor='#003b63', bordercolor='#00aeef', font=dict(size=13, color='#ffffff'))
    )
    return fig
    
    fig = go.Figure()
    
    # Trace Principal
    fig.add_trace(go.Scatter(
        x=df[coluna_x], y=df[coluna_y], mode='lines', name=titulo,
        line=dict(color=cor_linha, width=2, shape='spline', smoothing=0.4),
        fill='tozeroy', fillcolor=f'rgba({hex_to_rgb(cor_linha)}, 0.15)',
        hovertemplate=f'<b>%{{x|%d/%m/%Y %H:%M}}</b><br>{titulo}: <b>%{{y:,.2f}} {unidade}</b><extra></extra>'
    ))

    # Faixa ADEQUADA (Verde)
    if limite_min_ok is not None and limite_max_ok is not None:
        fig.add_hrect(y0=limite_min_ok, y1=limite_max_ok, fillcolor='rgba(34,197,94,0.08)', layer='below', line_width=0,
                      annotation_text='▶ Faixa Adequada', annotation_position='top right', annotation_font=dict(size=10, color='rgba(34,197,94,0.9)'))
        for y_val in [limite_min_ok, limite_max_ok]:
            fig.add_hline(y=y_val, line=dict(color='rgba(34,197,94,0.6)', width=1, dash='dot'))

    # Faixa ATENÇÃO Inferior (Âmbar)
    if limite_min_atencao is not None and limite_min_ok is not None:
        fig.add_hrect(y0=limite_min_atencao, y1=limite_min_ok, fillcolor='rgba(245,158,11,0.07)', layer='below', line_width=0)
        fig.add_hline(y=limite_min_atencao, line=dict(color='rgba(245,158,11,0.5)', width=1, dash='dash'),
                      annotation_text='⚠ Zona de Atenção', annotation_position='bottom right', annotation_font=dict(size=10, color='rgba(245,158,11,0.9)'))

    # Faixa ATENÇÃO Superior (Âmbar)
    if limite_max_atencao is not None and limite_max_ok is not None:
        fig.add_hrect(y0=limite_max_ok, y1=limite_max_atencao, fillcolor='rgba(245,158,11,0.07)', layer='below', line_width=0)

    # Zona CRÍTICA Inferior (Vermelha)
    if limite_critico_min is not None:
        fig.add_hrect(y0=df[coluna_y].min() * 0.95, y1=limite_critico_min, fillcolor='rgba(239,68,68,0.08)', layer='below', line_width=0)
        fig.add_hline(y=limite_critico_min, line=dict(color='rgba(239,68,68,0.6)', width=1, dash='dash'),
                      annotation_text='✕ Limite Crítico', annotation_position='top right', annotation_font=dict(size=10, color='rgba(239,68,68,0.9)'))

    # Zona CRÍTICA Superior (Vermelha)
    if limite_critico_max is not None:
        fig.add_hrect(y0=limite_critico_max, y1=df[coluna_y].max() * 1.05 if df[coluna_y].max() > limite_critico_max else limite_critico_max * 1.05,
                      fillcolor='rgba(239,68,68,0.08)', layer='below', line_width=0)
        fig.add_hline(y=limite_critico_max, line=dict(color='rgba(239,68,68,0.6)', width=1, dash='dash'),
                      annotation_text='✕ Limite Crítico', annotation_position='bottom right', annotation_font=dict(size=10, color='rgba(239,68,68,0.9)'))

    # Marcadores Min/Max
    if mostrar_min_max and not df.empty:
        idx_max, idx_min = df[coluna_y].idxmax(), df[coluna_y].idxmin()
        val_max, val_min = df[coluna_y].max(), df[coluna_y].min()
        x_max, x_min = df[coluna_x].iloc[idx_max], df[coluna_x].iloc[idx_min]

        fig.add_trace(go.Scatter(x=[x_max], y=[val_max], mode='markers+text', name='Máximo',
            marker=dict(symbol='triangle-up', size=12, color='#ef4444', line=dict(color='#fff', width=1)),
            text=[f'▲ Máx: {val_max:,.2f} {unidade}'], textposition='top center', textfont=dict(size=11, color='#ff6b6b'),
            hovertemplate=f'Máximo: <b>{val_max:,.2f} {unidade}</b><br>%{{x|%d/%m %H:%M}}<extra></extra>'))

        fig.add_trace(go.Scatter(x=[x_min], y=[val_min], mode='markers+text', name='Mínimo',
            marker=dict(symbol='triangle-down', size=12, color='#22c55e', line=dict(color='#fff', width=1)),
            text=[f'▼ Mín: {val_min:,.2f} {unidade}'], textposition='bottom center', textfont=dict(size=11, color='#4ade80'),
            hovertemplate=f'Mínimo: <b>{val_min:,.2f} {unidade}</b><br>%{{x|%d/%m %H:%M}}<extra></extra>'))

    # Linha de Média
    if mostrar_media and not df.empty:
        media = df[coluna_y].mean()
        fig.add_hline(y=media, line=dict(color='rgba(255,255,255,0.4)', width=1.2, dash='longdash'),
                      annotation_text=f'Média: {media:,.2f} {unidade}', annotation_position='top left', annotation_font=dict(size=11, color='rgba(255,255,255,0.8)'))

    # Layout Dark Theme de Alto Contraste
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.15)',
        font=dict(family='Inter, sans-serif', color='#e2e8f0', size=12),
        title=dict(text=titulo, font=dict(color='#ffffff', size=16), x=0.01, xanchor='left', pad=dict(b=12)),
        xaxis=dict(gridcolor='rgba(255,255,255,0.15)', linecolor='rgba(255,255,255,0.2)', tickcolor='rgba(255,255,255,0.3)', tickformat='%H:%M\n%d/%m', nticks=12, showgrid=True),
        yaxis=dict(gridcolor='rgba(255,255,255,0.15)', linecolor='rgba(255,255,255,0.2)', ticksuffix=f' {unidade}', showgrid=True),
        margin=dict(l=60, r=40, t=50, b=40), hovermode='x unified',
        legend=dict(bgcolor='rgba(0,43,73,0.9)', bordercolor='rgba(255,255,255,0.3)', borderwidth=1, orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        hoverlabel=dict(bgcolor='#003b63', bordercolor='#00aeef', font=dict(size=13, color='#ffffff'))
    )
    return fig
    
    fig = go.Figure()
    
    # Trace Principal
    fig.add_trace(go.Scatter(
        x=df[coluna_x], y=df[coluna_y], mode='lines', name=titulo,
        line=dict(color=cor_linha, width=1.8, shape='spline', smoothing=0.4),
        fill='tozeroy', fillcolor=f'rgba({hex_to_rgb(cor_linha)}, 0.08)',
        hovertemplate=f'<b>%{{x|%d/%m/%Y %H:%M}}</b><br>{titulo}: <b>%{{y:,.2f}} {unidade}</b><extra></extra>'
    ))

    # Faixa ADEQUADA (Verde)
    if limite_min_ok is not None and limite_max_ok is not None:
        fig.add_hrect(y0=limite_min_ok, y1=limite_max_ok, fillcolor='rgba(34,197,94,0.08)', layer='below', line_width=0,
                      annotation_text='▶ Faixa Adequada', annotation_position='top right', annotation_font=dict(size=9, color='rgba(34,197,94,0.7)'))
        for y_val in [limite_min_ok, limite_max_ok]:
            fig.add_hline(y=y_val, line=dict(color='rgba(34,197,94,0.5)', width=1, dash='dot'))

    # Faixa ATENÇÃO Inferior (Âmbar)
    if limite_min_atencao is not None and limite_min_ok is not None:
        fig.add_hrect(y0=limite_min_atencao, y1=limite_min_ok, fillcolor='rgba(245,158,11,0.07)', layer='below', line_width=0)
        fig.add_hline(y=limite_min_atencao, line=dict(color='rgba(245,158,11,0.4)', width=1, dash='dash'),
                      annotation_text='⚠ Zona de Atenção', annotation_position='bottom right', annotation_font=dict(size=9, color='rgba(245,158,11,0.7)'))

    # Faixa ATENÇÃO Superior (Âmbar)
    if limite_max_atencao is not None and limite_max_ok is not None:
        fig.add_hrect(y0=limite_max_ok, y1=limite_max_atencao, fillcolor='rgba(245,158,11,0.07)', layer='below', line_width=0)

    # Zona CRÍTICA Inferior (Vermelha)
    if limite_critico_min is not None:
        fig.add_hrect(y0=df[coluna_y].min() * 0.95, y1=limite_critico_min, fillcolor='rgba(239,68,68,0.06)', layer='below', line_width=0)
        fig.add_hline(y=limite_critico_min, line=dict(color='rgba(239,68,68,0.5)', width=1, dash='dash'),
                      annotation_text='✕ Limite Crítico', annotation_position='top right', annotation_font=dict(size=9, color='rgba(239,68,68,0.7)'))

    # Zona CRÍTICA Superior (Vermelha)
    if limite_critico_max is not None:
        fig.add_hrect(y0=limite_critico_max, y1=df[coluna_y].max() * 1.05 if df[coluna_y].max() > limite_critico_max else limite_critico_max * 1.05,
                      fillcolor='rgba(239,68,68,0.06)', layer='below', line_width=0)
        fig.add_hline(y=limite_critico_max, line=dict(color='rgba(239,68,68,0.5)', width=1, dash='dash'),
                      annotation_text='✕ Limite Crítico', annotation_position='bottom right', annotation_font=dict(size=9, color='rgba(239,68,68,0.7)'))

    # Marcadores Min/Max
    if mostrar_min_max and not df.empty:
        idx_max, idx_min = df[coluna_y].idxmax(), df[coluna_y].idxmin()
        val_max, val_min = df[coluna_y].max(), df[coluna_y].min()
        x_max, x_min = df[coluna_x].iloc[idx_max], df[coluna_x].iloc[idx_min]

        fig.add_trace(go.Scatter(x=[x_max], y=[val_max], mode='markers+text', name='Máximo',
            marker=dict(symbol='triangle-up', size=10, color='#ef4444', line=dict(color='#fff', width=1)),
            text=[f'▲ Máx: {val_max:,.2f} {unidade}'], textposition='top center', textfont=dict(size=10, color='#ef4444'),
            hovertemplate=f'Máximo: <b>{val_max:,.2f} {unidade}</b><br>%{{x|%d/%m %H:%M}}<extra></extra>'))

        fig.add_trace(go.Scatter(x=[x_min], y=[val_min], mode='markers+text', name='Mínimo',
            marker=dict(symbol='triangle-down', size=10, color='#22c55e', line=dict(color='#fff', width=1)),
            text=[f'▼ Mín: {val_min:,.2f} {unidade}'], textposition='bottom center', textfont=dict(size=10, color='#22c55e'),
            hovertemplate=f'Mínimo: <b>{val_min:,.2f} {unidade}</b><br>%{{x|%d/%m %H:%M}}<extra></extra>'))

    # Linha de Média
    if mostrar_media and not df.empty:
        media = df[coluna_y].mean()
        fig.add_hline(y=media, line=dict(color='rgba(255,255,255,0.25)', width=1.2, dash='longdash'),
                      annotation_text=f'Média: {media:,.2f} {unidade}', annotation_position='top left', annotation_font=dict(size=10, color='rgba(255,255,255,0.5)'))

    # Layout Dark Theme
    fig.update_layout(
        paper_bgcolor='#021a2f', plot_bgcolor='#021a2f',
        font=dict(family='Inter, sans-serif', color='#94a3b8', size=11),
        title=dict(text=titulo, font=dict(color='#e2e8f0', size=14), x=0.01, xanchor='left', pad=dict(b=12)),
        xaxis=dict(gridcolor='rgba(255,255,255,0.05)', linecolor='rgba(255,255,255,0.1)', tickcolor='rgba(255,255,255,0.2)', tickformat='%H:%M\n%d/%m', nticks=12, showgrid=True),
        yaxis=dict(gridcolor='rgba(255,255,255,0.05)', linecolor='rgba(255,255,255,0.1)', ticksuffix=f' {unidade}', showgrid=True),
        margin=dict(l=60, r=40, t=50, b=40), hovermode='x unified',
        legend=dict(bgcolor='rgba(2,26,47,0.8)', bordercolor='rgba(255,255,255,0.1)', borderwidth=1, orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        hoverlabel=dict(bgcolor='#003b63', bordercolor='#00aeef', font=dict(size=12, color='#e2e8f0'))
    )
    return fig

def estatisticas_grafico(df, coluna_y, unidade):
    if df.empty: return
    v_max, v_min, v_med, v_atu = df[coluna_y].max(), df[coluna_y].min(), df[coluna_y].mean(), df[coluna_y].iloc[-1]
    v_std = df[coluna_y].std() if len(df) > 1 else 0.0

    st.markdown(f"""
    <div style="display:grid; grid-template-columns:repeat(5,1fr); gap:8px; margin-top:8px;">
        <div style="background:rgba(255,255,255,0.04); border-radius:8px; padding:10px 12px; border:1px solid rgba(255,255,255,0.07); text-align:center;">
            <div style="font-size:10px;color:#64748b;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:4px;">Atual</div>
            <div style="font-size:16px;font-weight:700;color:#00aeef;">{v_atu:,.2f} <span style='font-size:11px;font-weight:400;'>{unidade}</span></div>
        </div>
        <div style="background:rgba(255,255,255,0.04); border-radius:8px; padding:10px 12px; border:1px solid rgba(255,255,255,0.07); text-align:center;">
            <div style="font-size:10px;color:#64748b;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:4px;">Máximo</div>
            <div style="font-size:16px;font-weight:700;color:#ef4444;">{v_max:,.2f} <span style='font-size:11px;font-weight:400;'>{unidade}</span></div>
        </div>
        <div style="background:rgba(255,255,255,0.04); border-radius:8px; padding:10px 12px; border:1px solid rgba(255,255,255,0.07); text-align:center;">
            <div style="font-size:10px;color:#64748b;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:4px;">Mínimo</div>
            <div style="font-size:16px;font-weight:700;color:#22c55e;">{v_min:,.2f} <span style='font-size:11px;font-weight:400;'>{unidade}</span></div>
        </div>
        <div style="background:rgba(255,255,255,0.04); border-radius:8px; padding:10px 12px; border:1px solid rgba(255,255,255,0.07); text-align:center;">
            <div style="font-size:10px;color:#64748b;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:4px;">Média</div>
            <div style="font-size:16px;font-weight:700;color:#e2e8f0;">{v_med:,.2f} <span style='font-size:11px;font-weight:400;'>{unidade}</span></div>
        </div>
        <div style="background:rgba(255,255,255,0.04); border-radius:8px; padding:10px 12px; border:1px solid rgba(255,255,255,0.07); text-align:center;">
            <div style="font-size:10px;color:#64748b;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:4px;">Desvio Padrão</div>
            <div style="font-size:16px;font-weight:700;color:#94a3b8;">{v_std:,.2f} <span style='font-size:11px;font-weight:400;'>{unidade}</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def seletor_fase(prefixo_key: str) -> str:
    st.markdown("""
    <style>
    div[data-testid="stRadio"] > label { display: none; }
    div[data-testid="stRadio"] > div { display: flex; gap: 6px; flex-wrap: wrap; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 6px; width: fit-content; }
    div[data-testid="stRadio"] > div > label { background: transparent; border: 1px solid rgba(255,255,255,0.12); border-radius: 6px; padding: 5px 14px; font-size: 12px; font-weight: 600; color: #64748b; cursor: pointer; transition: all 0.2s ease; display: block; }
    div[data-testid="stRadio"] > div > label:hover { border-color: #00aeef; color: #00aeef; background: rgba(0,174,239,0.08); }
    div[data-testid="stRadio"] > div > label[data-checked="true"] { background: #005387; border-color: #005387; color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)
    return st.radio('Selecione a Fase', options=['Total', 'Fase A', 'Fase B', 'Fase C', 'Todas as Fases'], index=0, horizontal=True, key=prefixo_key, label_visibility="collapsed")
def renderizar_grafico_potencia(df, tipo, key_suffix, kva_nom):
    unidade = 'W' if tipo == 'ativa' else 'VA'
    colunas = {
        'ativa': {'Total': 'Potencia_Total_W', 'Fase A': 'P_Fase_A_W', 'Fase B': 'P_Fase_B_W', 'Fase C': 'P_Fase_C_W'},
        'aparente': {'Total': 'Potencia_Aparente_Total_VA', 'Fase A': 'S_Fase_A_VA', 'Fase B': 'S_Fase_B_VA', 'Fase C': 'S_Fase_C_VA'}
    }
    cores_fases = {'Fase A': '#00aeef', 'Fase B': '#22c55e', 'Fase C': '#a78bfa'}

    st.markdown(f"<div style='font-size:11px;color:#94a3b8;font-weight:600;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:8px;'>Filtro de Visualização — Potência {'Ativa' if tipo=='ativa' else 'Aparente'}</div>", unsafe_allow_html=True)
    opcao = seletor_fase(f'fase_{tipo}_{key_suffix}')

    max_total = (kva_nom * 0.92) if tipo == 'ativa' else kva_nom
    max_fase = max_total / 3

    if opcao == 'Todas as Fases':
        fig = go.Figure()
        for fase in ['Fase A', 'Fase B', 'Fase C']:
            col = colunas[tipo].get(fase)
            if col in df.columns:
                fig.add_trace(go.Scatter(x=df['Data_Hora_Obj'], y=df[col], mode='lines', name=fase, line=dict(color=cores_fases[fase], width=2, shape='spline', smoothing=0.3), hovertemplate=f'<b>{fase}</b><br>%{{x|%d/%m %H:%M}}: <b>%{{y:,.2f}} {unidade}</b><extra></extra>'))
        
        fig.add_hline(y=max_fase*0.8, line=dict(color='rgba(34,197,94,0.6)', width=1, dash='dot'), annotation_text='80% (Fase)', annotation_position='top right', annotation_font=dict(size=10, color='rgba(34,197,94,0.9)'))
        fig.add_hline(y=max_fase, line=dict(color='rgba(239,68,68,0.6)', width=1, dash='dash'), annotation_text='100% (Fase)', annotation_position='bottom right', annotation_font=dict(size=10, color='rgba(239,68,68,0.9)'))
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.15)', 
            font=dict(family='Inter, sans-serif', color='#e2e8f0', size=12), 
            title=dict(text=f'Potência {"Ativa" if tipo=="ativa" else "Aparente"} por Fase', font=dict(color='#ffffff', size=16), x=0.01, pad=dict(b=12)), 
            xaxis=dict(gridcolor='rgba(255,255,255,0.15)', linecolor='rgba(255,255,255,0.2)', tickformat='%H:%M\n%d/%m', nticks=12, showgrid=True),
            yaxis=dict(gridcolor='rgba(255,255,255,0.15)', linecolor='rgba(255,255,255,0.2)', ticksuffix=f' {unidade}', showgrid=True),
            margin=dict(l=60, r=40, t=50, b=40), hovermode='x unified',
            # AQUI ESTÁ A CORREÇÃO DA LEGENDA
            legend=dict(bgcolor='rgba(0,43,73,0.9)', bordercolor='rgba(255,255,255,0.3)', borderwidth=1, orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1, font=dict(color='#ffffff')),
            hoverlabel=dict(bgcolor='#003b63', bordercolor='#00aeef', font=dict(size=13, color='#ffffff'))
        )
        
        # AQUI ESTÁ A CORREÇÃO THEME=NONE
        st.plotly_chart(fig, width="stretch", config={'displayModeBar': True, 'displaylogo': False}, theme=None)
    else:
        col_selecionada = colunas[tipo].get(opcao)
        cor = cores_fases.get(opcao, '#c084fc')
        lim_ok = (max_total * 0.8) if opcao == 'Total' else (max_fase * 0.8)
        lim_crit = max_total if opcao == 'Total' else max_fase

        fig = renderizar_grafico_profissional(df=df, coluna_y=col_selecionada, titulo=f'Potência {"Ativa" if tipo=="ativa" else "Aparente"} — {opcao}', unidade=unidade, cor_linha=cor, limite_min_ok=0, limite_max_ok=lim_ok, limite_max_atencao=lim_crit*0.95, limite_critico_max=lim_crit)
        
        # AQUI ESTÁ A CORREÇÃO THEME=NONE
        st.plotly_chart(fig, width="stretch", config={'displayModeBar': True, 'displaylogo': False}, theme=None)
        estatisticas_grafico(df, col_selecionada, unidade)

def separador_grafico(titulo_secao: str):
    st.markdown(f"""<div style="display:flex; align-items:center; gap:12px; margin: 28px 0 16px;"><div style="width:3px; height:20px; background:#005387; border-radius:2px; flex-shrink:0;"></div><div style="font-size:13px; font-weight:700; color:#e2e8f0; text-transform:uppercase; letter-spacing:0.8px;">{titulo_secao}</div><div style="flex:1; height:1px; background:rgba(255,255,255,0.06);"></div></div>""", unsafe_allow_html=True)

def cabecalho_historico(nome_subestacao, df):
    periodo_inicio, periodo_fim = df['Data_Hora_Obj'].min().strftime('%d/%m/%Y %H:%M'), df['Data_Hora_Obj'].max().strftime('%d/%m/%Y %H:%M')
    st.markdown(f"""<div style="background:rgba(0,83,135,0.15); border:1px solid rgba(0,83,135,0.3); border-left:4px solid #005387; border-radius:8px; padding:14px 18px; margin-bottom:20px; display:flex; gap:24px; align-items:center; flex-wrap:wrap;"><div><div style="font-size:10px;color:#64748b;text-transform:uppercase;letter-spacing:0.8px;">Subestação</div><div style="font-size:16px;font-weight:700;color:#e2e8f0;margin-top:2px;">⚡ {nome_subestacao}</div></div><div style="width:1px;height:36px;background:rgba(255,255,255,0.1);"></div><div><div style="font-size:10px;color:#64748b;text-transform:uppercase;letter-spacing:0.8px;">Período</div><div style="font-size:13px;font-weight:600;color:#94a3b8;margin-top:2px;">{periodo_inicio} → {periodo_fim}</div></div><div style="width:1px;height:36px;background:rgba(255,255,255,0.1);"></div><div><div style="font-size:10px;color:#64748b;text-transform:uppercase;letter-spacing:0.8px;">Leituras</div><div style="font-size:16px;font-weight:700;color:#00aeef;margin-top:2px;">{len(df):,}</div></div></div>""", unsafe_allow_html=True)

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
                if (obter_hora_brasil() - dt_leitura).total_seconds() <= 240:
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
        if st.button("Gerar Gráficos e Relatório", type="primary", width="stretch", key="btn_grafico"):
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
                    
                    # 1. Tensão (Variação e Cor)
                    v_diff_perc = ((v_avg - v_nom) / v_nom) * 100 if v_nom > 0 else 0
                    v_is_bad = v_diff_perc < -8.0 or v_diff_perc > 5.0
                    cV = "#ef4444" if v_is_bad else "#ffffff"
                    c_sub_V = "#ef4444" if v_is_bad else "#4ade80" # Verde se OK, Vermelho se Ruim
                    v_seta = "▲" if v_diff_perc > 0 else ("▼" if v_diff_perc < 0 else "")
                    v_sub_text = f"{v_seta} {abs(v_diff_perc):.1f}% (Ref: {v_nom}V)"

                    # 2. Corrente (Uso e Cor)
                    i_perc = (i_avg / i_nom) * 100 if i_nom > 0 else 0
                    i_is_bad = i_perc > 100
                    cA = "#ef4444" if i_is_bad else "#ffffff"
                    c_sub_A = "#ef4444" if i_is_bad else "#4ade80"
                    i_sub_text = f"Uso: {i_perc:.1f}% (Max: {i_nom}A)"

                    # 3. Potência Aparente (Uso e Cor)
                    s_perc = (s_total / kva_nom) * 100 if kva_nom > 0 else 0
                    s_is_bad = s_perc > 100
                    cS = "#ef4444" if s_is_bad else "#ffffff"
                    c_sub_S = "#ef4444" if s_is_bad else "#4ade80"
                    s_sub_text = f"Uso: {s_perc:.1f}% (Max: {kva_nom/1000:.0f}kVA)"

                    if v_is_bad or i_is_bad or s_is_bad:
                        atencoes += 1

                    card_html = f"""
                    <div class="info-card">
                        <div class="card-header-row">
                            <div class="status-badge"><div class="status-dot"></div> ONLINE</div>
                            <div style="font-size:10px; color:#94a3b8; font-weight:600;">{data_hora}</div>
                        </div>
                        <div class="card-title">🔌 {nome_bonito}</div>
                        <div class="card-metrics-row">
                            <div class="metric-item">
                                <span class="metric-label">Tensão Média</span>
                                <span class="metric-value" style="color:{cV}">{v_avg} V</span>
                                <span class="metric-sub" style="color:{c_sub_V}">{v_sub_text}</span>
                            </div>
                            <div class="metric-item">
                                <span class="metric-label">Corr. Média</span>
                                <span class="metric-value" style="color:{cA}">{i_avg} A</span>
                                <span class="metric-sub" style="color:{c_sub_A}">{i_sub_text}</span>
                            </div>
                            <div class="metric-item">
                                <span class="metric-label">Pot. Ativa</span>
                                <span class="metric-value" style="color:#ffffff">{p_tot} W</span>
                                <span class="metric-sub" style="color:transparent">.</span>
                            </div>
                            <div class="metric-item">
                                <span class="metric-label">Pot. Aparente</span>
                                <span class="metric-value" style="color:{cS}">{s_total/1000:.1f} kVA</span>
                                <span class="metric-sub" style="color:{c_sub_S}">{s_sub_text}</span>
                            </div>
                        </div>
                    </div>
                    """
                    st.markdown(card_html, unsafe_allow_html=True)
                    
                    with st.expander("⚙️ Ver detalhamento técnico"):
                        html_metricas = '<div class="mini-cards-grid">'
                        for chave, valor in dados.items():
                            if chave in ['Data_Hora', 'Tensao_Media_V', 'Corrente_Media_A', 'Potencia_Total_W', 'Potencia_Aparente_Total_VA']: continue
                            
                            # Usa a função para definir Branco ou Vermelho
                            cor_mc = obter_cor_semantica(chave.split('_')[0], valor)
                            
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
                            segundos = int((obter_hora_brasil() - dt_leitura).total_seconds())
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
                        <div class="card-title" style="color:#ef4444;">🔌 {nome_bonito}</div>
                        <div style="text-align:center; padding: 10px 0;">
                            <div style="font-weight:600; color:#ef4444; font-size:14px;">Falha de Comunicação</div>
                            <div style="font-size:12px; color:#cbd5e1; margin-top:4px;">{mensagem_tempo}</div>
                        </div>
                    </div>
                    """
                    st.markdown(card_html, unsafe_allow_html=True)

    renderizar_footer(onlines, offlines, atencoes)

    # ---------------------------------------------------------------------
    # ABA 2: HISTÓRICO E RELATÓRIOS (NUVEM)
    # ---------------------------------------------------------------------
    with aba_historico:
        st.markdown("<br>", unsafe_allow_html=True)
        
        # --- CABEÇALHO DA ABA HISTÓRICO ---
        st.markdown("<h3 style='color:#ffffff; font-size:18px;'>Análise de Dados Históricos (Nuvem)</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color:#94a3b8; font-size:13px;'>Gere gráficos e exporte dados a partir do histórico armazenado no servidor Firebase.</p>", unsafe_allow_html=True)
        
        # --- FILTROS DE BUSCA E BOTÃO DE E-MAIL ---
        # Organizamos os filtros e o botão de e-mail na mesma linha
        col_f1, col_f2, col_f3, col_email = st.columns([2, 1, 1, 1.5])
        
        nomes_bonitos = list(DICIONARIO_NOMES.values())
        sub_escolhida = col_f1.selectbox("Selecione a Subestação", nomes_bonitos, key="sel_subestacao")
        nome_banco = [k for k, v in DICIONARIO_NOMES.items() if v == sub_escolhida][0]
        
        data_inicio = col_f2.date_input("Data Inicial", key="data_ini")
        data_fim = col_f3.date_input("Data Final", key="data_fim")
        
        # Botão de E-mail com Validação de Usuário
        with col_email:
            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True) # Alinha o botão com os inputs
            with st.popover("📧 Enviar Relatório por E-mail", use_container_width=True):
                st.markdown("<p style='color:#005387; font-weight:bold; margin-bottom:5px;'>Autorização de Envio</p>", unsafe_allow_html=True)
                email_solicitante = st.text_input("Seu E-mail Corporativo", placeholder="exemplo@gmail.com")
                
                if st.button("Solicitar Envio", type="primary", use_container_width=True, key="btn_confirma_email"):
                    # Lista de e-mails autorizados a pedir o relatório
                    emails_autorizados = ["gabrielbranco2002@gmail.com", "natan25cmartins@gmail.com", "lucasmeurercardoso@gmail.com", "marcost04@gmail.com"]
                    
                    if not email_solicitante:
                        st.error("Preencha o e-mail!")
                    elif email_solicitante.strip().lower() not in emails_autorizados:
                        st.error("Acesso Negado. Este e-mail não está cadastrado no sistema SCADA.")
                    else:
                        with st.spinner("Autenticado. Gerando gráficos e enviando..."):
                            try:
                                from relatorio_email import compilar_enviar_relatorio
                                # O botão agora chama a função SEM passar senha. 
                                # A função vai usar a senha que está salva no Cofre (Secrets) do Streamlit.
                                sucesso = compilar_enviar_relatorio()
                                if sucesso:
                                    st.success(f"Relatório enviado com sucesso para toda a equipe!")
                                else:
                                    st.error("Falha interna ao enviar o e-mail.")
                            except Exception as e:
                                st.error(f"Erro: {e}")

        # --- MEMÓRIA DO GRÁFICO ---
        if 'df_historico' not in st.session_state:
            st.session_state['df_historico'] = None
            st.session_state['nome_hist'] = ""
        
        # --- BOTÃO ÚNICO DE GERAR GRÁFICOS ---
        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        if st.button("Gerar Gráficos na Tela", type="primary", width="stretch", key="btn_gerar_unico"):
            with st.spinner("Baixando histórico da nuvem... Isso pode levar alguns segundos."):
                datas_selecionadas = pd.date_range(data_inicio, data_fim).strftime('%Y-%m-%d').tolist()
                dados_historico = []
                
                for dia in datas_selecionadas:
                    url_busca = f"{FIREBASE_URL}/historico/{nome_banco}/{dia}.json"
                    try:
                        import requests
                        res = requests.get(url_busca, timeout=10)
                        if res.status_code == 200 and res.json() is not None:
                            for hora, valores in res.json().items(): dados_historico.append(valores)
                    except: continue
                
                if dados_historico:
                    df_filtrado = pd.DataFrame(dados_historico)
                    df_filtrado['Data_Hora_Obj'] = pd.to_datetime(df_filtrado['Data_Hora'], format='%d/%m/%Y %H:%M:%S')
                    
                    df_filtrado = df_filtrado.sort_values('Data_Hora_Obj').drop_duplicates(subset=['Data_Hora_Obj'])
                    df_filtrado = df_filtrado.set_index('Data_Hora_Obj').resample('1min').asfreq().fillna(0).reset_index()
                    df_filtrado['Data_Hora'] = df_filtrado['Data_Hora_Obj'].dt.strftime('%d/%m/%Y %H:%M:%S')
                    
                    st.session_state['df_historico'] = df_filtrado
                    st.session_state['nome_hist'] = sub_escolhida
                else:
                    st.session_state['df_historico'] = None
                    st.warning("Nenhum dado encontrado na nuvem para este período.")
        
        # --- RENDERIZAÇÃO DOS GRÁFICOS PLOTLY ---
        if st.session_state.get('df_historico') is not None:
            df_plot = st.session_state['df_historico']
            nome_sub = st.session_state['nome_hist']
            kva_nom, v_nom, i_nom = extrair_dados_placa(nome_sub)
            
            cabecalho_historico(nome_sub, df_plot)

            separador_grafico("⚡ Tensão Média")
            fig_tensao = renderizar_grafico_profissional(df_plot, 'Tensao_Media_V', titulo=f'Curva de Tensão Média — {nome_sub}', unidade='V', cor_linha='#38bdf8', limite_min_ok=117, limite_max_ok=133, limite_min_atencao=108, limite_max_atencao=140, limite_critico_min=108, limite_critico_max=140)
            st.plotly_chart(fig_tensao, width="stretch", config={'displayModeBar': True, 'displaylogo': False}, theme=None)
            estatisticas_grafico(df_plot, 'Tensao_Media_V', 'V')

            separador_grafico("⚡ Corrente Média")
            fig_corrente = renderizar_grafico_profissional(df_plot, 'Corrente_Media_A', titulo=f'Curva de Corrente Média — {nome_sub}', unidade='A', cor_linha='#fbbf24', limite_min_ok=0, limite_max_ok=i_nom*0.8, limite_max_atencao=i_nom*0.9, limite_critico_max=i_nom)
            st.plotly_chart(fig_corrente, width="stretch", config={'displayModeBar': True, 'displaylogo': False}, theme=None)
            estatisticas_grafico(df_plot, 'Corrente_Media_A', 'A')

            separador_grafico("⚡ Potência Ativa (W)")
            renderizar_grafico_potencia(df_plot, 'ativa', nome_banco, kva_nom)

            separador_grafico("⚡ Potência Aparente (VA)")
            renderizar_grafico_potencia(df_plot, 'aparente', nome_banco, kva_nom)

            separador_grafico("⚡ Fator de Potência")
            fig_fp = renderizar_grafico_profissional(df_plot, 'Fator_Potencia', titulo=f'Curva de Fator de Potência — {nome_sub}', unidade='', cor_linha='#a78bfa', limite_min_ok=0.92, limite_max_ok=1.0, limite_min_atencao=0.85, limite_critico_min=0.85)
            fig_fp.update_yaxes(range=[0.7, 1.05], tickformat='.2f')
            st.plotly_chart(fig_fp, width="stretch", config={'displayModeBar': True, 'displaylogo': False}, theme=None)
            estatisticas_grafico(df_plot, 'Fator_Potencia', '')

            separador_grafico("📋 Tabela de Dados Brutos")
            st.dataframe(df_plot.drop(columns=['Data_Hora_Obj']).tail(200), width="stretch", height=320)
            
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
