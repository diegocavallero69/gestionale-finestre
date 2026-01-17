import streamlit as st
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
import io
import json
from datetime import datetime

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Rilievi Finestre", page_icon="🪟", layout="wide")

# --- FUNZIONI DI UTILITÀ ---

def genera_pdf(dati_testata, df_misure):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    
    # 1. INTESTAZIONE
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 800, "SCHEDA RILIEVI - PRODUZIONE")
    c.setFont("Helvetica", 10)
    c.drawString(450, 800, f"Data: {datetime.now().strftime('%d/%m/%Y')}")
    
    # Riquadro Cliente
    c.setStrokeColor(colors.black)
    c.rect(40, 720, 515, 70, fill=0)
    c.drawString(50, 770, f"CLIENTE: {dati_testata['cliente']}")
    c.drawString(50, 755, f"INDIRIZZO: {dati_testata['indirizzo']}")
    c.drawString(50, 740, f"COMMESSA: {dati_testata['commessa']}")
    c.drawString(300, 770, f"TELEFONO: {dati_testata['telefono']}")
    c.drawString(300, 755, f"EMAIL: {dati_testata['email']}")

    # 2. DATI TECNICI
    c.setFillColor(colors.lightgrey)
    c.rect(40, 680, 515, 30, fill=1, stroke=1)
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, 690, f"SPECIFICHE: {dati_testata['tipo_mat']}  |  Modello: {dati_testata['modello']}  |  Colore: {dati_testata['colore']}")

    # 3. TABELLA MISURE
    y = 650
    c.setFont("Helvetica-Bold", 9)
    c.drawString(45, y, "POS")
    c.drawString(100, y, "L (mm)")
    c.drawString(150, y, "H (mm)")
    c.drawString(200, y, "QTÀ")
    c.drawString(240, y, "APERTURA")
    c.drawString(310, y, "NOTE / ACCESSORI")
    c.line(40, y-5, 555, y-5)
    
    y -= 20
    c.setFont("Helvetica", 10)
    
    for index, row in df_misure.iterrows():
        # Scrivo solo se la riga non è vuota o ha almeno una posizione
        if pd.notna(row["Posizione"]) and str(row["Posizione"]).strip() != "":
            c.drawString(45, y, str(row["Posizione"]))
            c.drawString(100, y, str(row["Larghezza (L)"]))
            c.drawString(150, y, str(row["Altezza (H)"]))
            c.drawString(205, y, str(row["Qtà"]))
            c.drawString(240, y, str(row["Apertura"]))
            nota = str(row["Note"])[:45] 
            c.drawString(310, y, nota)
            
            c.line(40, y-5, 555, y-5)
            y -= 20
            
            if y < 50:
                c.showPage()
                y = 800

    c.drawString(50, 100, f"NOTE GENERALI: {dati_testata['note_generali']}")
    c.save()
    buffer.seek(0)
    return buffer

# --- GESTIONE STATO (Serve per caricare i dati) ---
if 'dati_caricati' not in st.session_state:
    st.session_state['dati_caricati'] = None

# --- SIDEBAR: GESTIONE FILE ---
with st.sidebar:
    st.header("📂 Gestione Progetto")
    st.write("Salva il tuo lavoro per continuarlo dopo.")
    
    # CARICA FILE
    uploaded_file = st.file_uploader("Carica Progetto (.json)", type=["json"])
    if uploaded_file is not None:
        try:
            dati_json = json.load(uploaded_file)
            st.session_state['dati_caricati'] = dati_json
            st.success("Dati caricati! La pagina si aggiornerà.")
        except:
            st.error("File non valido.")

# --- INTERFACCIA PRINCIPALE ---
st.title("🪟 Gestionale Rilievi Serramenti")

# Recupero dati se caricati, altrimenti vuoti
d = st.session_state['dati_caricati'] if st.session_state['dati_caricati'] else {}

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("1. Anagrafica")
    cliente = st.text_input("Cliente", value=d.get("cliente", ""))
    indirizzo = st.text_input("Indirizzo", value=d.get("indirizzo", ""))
    commessa = st.text_input("Commessa", value=d.get("commessa", ""))
    telefono = st.text_input("Telefono", value=d.get("telefono", ""))
    email = st.text_input("Email", value=d.get("email", ""))
    
    st.subheader("2. Specifiche")
    # Indici per i selectbox (per selezionare il valore salvato)
    mat_options = ["Legno", "Legno-Alluminio", "PVC", "Alluminio"]
    mat_idx = mat_options.index(d.get("tipo_mat", "Legno")) if d.get("tipo_mat") in mat_options else 0
    tipo_mat = st.selectbox("Materiale", mat_options, index=mat_idx)
    
    modello = st.text_input("Modello/Profilo", value=d.get("modello", ""))
    colore = st.text_input("Colore/Finitura", value=d.get("colore", ""))
    note_generali = st.text_area("Note Generali", value=d.get("note_generali", ""))

with col2:
    st.subheader("3. Misure")
    
    # Preparo i dati della tabella
    if 'misure' in d:
        df_iniziale = pd.DataFrame(d['misure'])
    else:
        df_iniziale = pd.DataFrame(
            [{"Posizione": "Sala", "Larghezza (L)": 1000, "Altezza (H)": 1400, "Qtà": 1, "Apertura": "A/R DX", "Note": ""}]
        )

    misure_df = st.data_editor(
        df_iniziale,
        num_rows="dynamic",
        column_config={
            "Qtà": st.column_config.NumberColumn("Q.tà", min_value=1, step=1, width="small"),
            "Larghezza (L)": st.column_config.NumberColumn("L", format="%d"),
            "Altezza (H)": st.column_config.NumberColumn("H", format="%d"),
            "Apertura": st.column_config.SelectboxColumn(
                "Apertura",
                options=["Fisso", "1 Anta DX", "1 Anta SX", "A/R DX", "A/R SX", "2 Ante", "Scorrevole"],
                required=True,
            ),
        },
        use_container_width=True
    )

st.markdown("---")

# --- PULSANTI SALVATAGGIO E STAMPA ---
c_sx, c_cnt, c_dx = st.columns(3)

# 1. SALVA PROGETTO (JSON)
dati_completi = {
    "cliente": cliente, "indirizzo": indirizzo, "commessa": commessa,
    "telefono": telefono, "email": email,
    "tipo_mat": tipo_mat, "modello": modello, "colore": colore,
    "note_generali": note_generali,
    "misure": misure_df.to_dict('records') # Converte la tabella in dati salvabili
}

json_str = json.dumps(dati_completi, indent=4)

with c_sx:
    # Nome file intelligente
    nome_file_json = f"Progetto_{cliente if cliente else 'Nuovo'}.json"
    st.download_button(
        label="💾 SALVA PROGETTO (Modificabile)",
        data=json_str,
        file_name=nome_file_json,
        mime="application/json",
    )

# 2. GENERA PDF
with c_dx:
    if st.button("Genera PDF", type="primary"):
        pdf_file = genera_pdf(dati_completi, misure_df)
        st.download_button(
            label="📥 SCARICA PDF",
            data=pdf_file,
            file_name=f"Rilievi_{cliente}.pdf",
            mime="application/pdf"
        )