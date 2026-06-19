import smtplib
import pandas as pd
import plotly.graph_objects as go
import requests
import io
import zipfile
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
from datetime import datetime, timedelta

# ==============================================================================
# CONFIGURAÇÕES DO RELATÓRIO
# ==============================================================================
FIREBASE_URL = 'https://scada-portos-rs-cb2ab-default-rtdb.firebaseio.com'
EMAIL_DESTINO = "gabrielbranco2002@gmail.com"

# Tenta ler a senha do Cofre da Nuvem (Streamlit Secrets)
try:
    import streamlit as st
    EMAIL_REMETENTE = st.secrets["EMAIL_REMETENTE"]
    SENHA_GMAIL = st.secrets["SENHA_GMAIL"]
except:
    # Se falhar (ex: rodando no PC local às 07:00), usa as credenciais fixas abaixo:
    EMAIL_REMETENTE = "seu_email_que_vai_enviar@gmail.com"
    SENHA_GMAIL = "suasenhadedezeisseisletras"

DICIONARIO_NOMES = {
    'MED_SUB_SE-A': 'Subestação A', 'MED_SUB_SE-B': 'Subestação B', 'MED_SUB_SE-C': 'Subestação C',
    'MED_SUB_SE-D': 'Subestação D', 'MED_SUB_SE-R_E': 'Subestação E', 'MED_SUB_SE-E_F': 'Subestação F',
    'MED_SUB_SE-G': 'Subestação G', 'MED_SUB_SE-T_H': 'Subestação H', 'MED_SUB_SE-01_I': 'Subestação I',
    'MED_SUB_SE-02_J': 'Subestação J'
}

def gerar_grafico_png(df, nome_sub):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Data_Hora_Obj'], y=df['Potencia_Total_W'], mode='lines', 
                             line=dict(color='#00aeef', width=2), fill='tozeroy', fillcolor='rgba(0,174,239,0.1)'))
    
    idx_max, idx_min = df['Potencia_Total_W'].idxmax(), df['Potencia_Total_W'].idxmin()
    fig.add_trace(go.Scatter(x=[df['Data_Hora_Obj'].iloc[idx_max]], y=[df['Potencia_Total_W'].max()], mode='markers+text',
                             marker=dict(color='red', size=10), text=['Máx'], textposition='top center'))
    fig.add_trace(go.Scatter(x=[df['Data_Hora_Obj'].iloc[idx_min]], y=[df['Potencia_Total_W'].min()], mode='markers+text',
                             marker=dict(color='green', size=10), text=['Mín'], textposition='bottom center'))
    
    fig.update_layout(title=f'Curva de Potência (W) - {nome_sub}', paper_bgcolor='white', plot_bgcolor='white',
                      margin=dict(l=20, r=20, t=40, b=20), width=600, height=300, showlegend=False)
    
    img_bytes = fig.to_image(format="png", engine="kaleido")
    return img_bytes

def compilar_enviar_relatorio():
    print("[RELATÓRIO] Iniciando compilação do relatório semanal...")
    
    hoje = datetime.now()
    dias_semana = [(hoje - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
    dias_semana.reverse()
    
    msg = MIMEMultipart('related')
    msg['Subject'] = f"📊 Relatório Executivo SCADA - Portos RS ({dias_semana[0]} a {dias_semana[-1]})"
    msg['From'] = EMAIL_REMETENTE
    msg['To'] = EMAIL_DESTINO

    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f4f7f6; margin: 0; padding: 20px;">
        <div style="max-width: 800px; margin: auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
            <div style="background-color: #005387; padding: 30px; text-align: center; color: white;">
                <h1 style="margin: 0; font-size: 24px;">PAINEL DE MONITORAMENTO ELÉTRICO</h1>
                <p style="margin: 5px 0 0 0; font-size: 14px; color: #00aeef;">Relatório Analítico Semanal</p>
            </div>
            <div style="padding: 30px;">
                <p>Prezado(a) Engenheiro(a),</p>
                <p>Segue o resumo estatístico e os gráficos de desempenho das subestações referentes aos últimos 7 dias.</p>
    """

    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for cod_banco, nome_bonito in DICIONARIO_NOMES.items():
            dados_hist = []
            for dia in dias_semana:
                try:
                    res = requests.get(f"{FIREBASE_URL}/historico/{cod_banco}/{dia}.json", timeout=5)
                    if res.status_code == 200 and res.json():
                        for _, valores in res.json().items(): dados_hist.append(valores)
                except: continue
                
            if not dados_hist: continue
            
            df = pd.DataFrame(dados_hist)
            df['Data_Hora_Obj'] = pd.to_datetime(df['Data_Hora'], format='%d/%m/%Y %H:%M:%S')
            df = df.sort_values('Data_Hora_Obj').reset_index(drop=True)
            
            csv_str = df.drop(columns=['Data_Hora_Obj']).to_csv(sep=';', index=False)
            zip_file.writestr(f"{nome_bonito}_Semana.csv", csv_str)
            
            p_max = df['Potencia_Total_W'].max()
            p_min = df['Potencia_Total_W'].min()
            p_med = df['Potencia_Total_W'].mean()
            p_std = df['Potencia_Total_W'].std()
            
            img_bytes = gerar_grafico_png(df, nome_bonito)
            cid = f"img_{cod_banco}"
            img_mime = MIMEImage(img_bytes)
            img_mime.add_header('Content-ID', f'<{cid}>')
            img_mime.add_header('Content-Disposition', 'inline')
            msg.attach(img_mime)
            
            html_body += f"""
            <div style="border: 1px solid #e0e6ed; border-top: 4px solid #005387; border-radius: 8px; padding: 20px; margin-bottom: 25px;">
                <h2 style="color: #005387; margin-top: 0;">🔌 {nome_bonito}</h2>
                <table style="width: 100%; text-align: center; margin-bottom: 15px; border-collapse: collapse;">
                    <tr style="font-size: 11px; color: #64748b; text-transform: uppercase;">
                        <td>Máxima</td><td>Mínima</td><td>Média</td><td>Desvio Padrão</td>
                    </tr>
                    <tr style="font-size: 18px; font-weight: bold;">
                        <td style="color: #ef4444;">{p_max:,.2f} W</td>
                        <td style="color: #22c55e;">{p_min:,.2f} W</td>
                        <td style="color: #005387;">{p_med:,.2f} W</td>
                        <td style="color: #64748b;">{p_std:,.2f} W</td>
                    </tr>
                </table>
                <div style="text-align: center;">
                    <img src="cid:{cid}" style="max-width: 100%; height: auto; border-radius: 5px;">
                </div>
            </div>
            """

    html_body += """
            </div>
            <div style="background-color: #1e293b; padding: 15px; text-align: center; color: #94a3b8; font-size: 12px;">
                SCADA Portos RS v2.0 - Relatório gerado automaticamente.<br>
                Os dados brutos (.csv) estão em anexo neste e-mail.
            </div>
        </div>
    </body>
    </html>
    """
    
    msg.attach(MIMEText(html_body, 'html'))
    
    zip_buffer.seek(0)
    anexo_zip = MIMEApplication(zip_buffer.read(), _subtype="zip")
    anexo_zip.add_header('Content-Disposition', 'attachment', filename="Backup_Semanal_PortosRS.zip")
    msg.attach(anexo_zip)
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_REMETENTE, SENHA_GMAIL)
        server.send_message(msg)
        server.quit()
        print("[RELATÓRIO] E-mail enviado com sucesso!")
        return True
    except Exception as e:
        print(f"[ERRO RELATÓRIO] Falha ao enviar e-mail: {e}")
        return False