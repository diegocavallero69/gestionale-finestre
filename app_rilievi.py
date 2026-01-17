import streamlit as st
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
import io
from datetime import datetime

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Rilievi Finestre", page_icon="🪟", layout="wide")

# --- FUNZIONE GENERAZIONE PDF ---
def genera_pdf(dati_testata, df_misure):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # 1. INTESTAZIONE
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 800, "SCHEDA RILIEVI - PRODUZIONE")
    
    c.setFont("Helvetica", 10)
    c.drawString(450, 800, f"Data: {datetime.now().strftime('%d/%m/%Y')}")
    
    # Riquadro Cliente
    c.setStrokeColor(colors.black)
    c.rect(40, 720, 515, 70, fill=0)
    c.drawString(50, 770, f"CLIENTE: {dati_testata['cliente']}")
    c.drawString(50, 755, f"CANTIERE/INDIRIZZO: {dati_testata['indirizzo']}")
    c.drawString(50, 740, f"COMMESSA: {dati_testata['commessa']}")
    c.drawString(300, 770, f"TELEFONO: {dati_testata['telefono']}")
    c.drawString(300, 755, f"EMAIL: {dati_testata['email']}")

    # 2. DATI TECNICI GENERALI (La scelta fatta nel menu)
    c.setFillColor(colors.lightgrey)
    c.rect(40, 680, 515, 30, fill=1, stroke=1)
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, 690, f"SPECIFICHE: {dati_testata['tipo_mat']}  |  Modello: {dati_testata['modello']}  |  Colore: {dati_testata['colore']}")

    # 3. TABELLA MISURE (Loop sulle righe inserite)
    y = 650
    c.setFont("Helvetica-Bold", 9)
    # Intestazione colonna
    c.drawString(45, y, "POSIZIONE")
    c.drawString(150, y, "L (mm)")
    c.drawString(200, y, "H (mm)")
    c.drawString(250, y, "QTÀ")
    c.drawString(290, y, "APERTURA")
    c.drawString(360, y, "NOTE / ACCESSORI")
    c.line(40, y-5, 555, y-5)
    
    y -= 20
    c.setFont("Helvetica", 10)
    
    # Itero su ogni riga della tabella che hai compilato
    for index, row in df_misure.iterrows():
        if row["Posizione"] and row["Posizione"] != "": # Scrivo solo se c'è scritto qualcosa
            c.drawString(45, y, str(row["Posizione"]))
            c.drawString(150, y, str(row["Larghezza (L)"]))
            c.drawString(200, y, str(row["Altezza (H)"]))
            c.drawString(255, y, str(row["Qtà"]))
            c.drawString(290, y, str(row["Apertura"]))
            # Taglio le note se sono troppo lunghe
            nota = str(row["Note"])[:40] 
            c.drawString(360, y, nota)
            
            c.line(40, y-5, 555, y-5) # Riga orizzontale
            y -= 20
            
            # Se finisco la pagina (semplificato)
            if y < 50:
                c.showPage()
                y = 800

    # 4. NOTE FINALI
    c.drawString(50, 100, f"NOTE GENERALI COMMESSA: {dati_testata['note_generali']}")

    c.save()
    buffer.seek(0)
    return buffer

# --- INTERFACCIA UTENTE (STREAMLIT) ---

# Titolo e Logo (puoi mettere un'immagine qui)
st.title("🪟 Gestionale Rilievi Serramenti")
st.markdown("---")

# --- COLONNA SINISTRA: DATI GENERALI ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("1. Anagrafica")
    cliente = st.text_input("Nome Cliente / Ragione Sociale")
    indirizzo = st.text_input("Indirizzo Cantiere")
    commessa = st.text_input("Rif. Commessa")
    telefono = st.text_input("Telefono")
    email = st.text_input("Email")
    
    st.subheader("2. Specifiche Tecniche")
    tipo_mat = st.selectbox("Materiale", ["Legno", "Legno-Alluminio", "PVC", "Alluminio"])
    
    # Logica condizionale semplice
    if "Legno" in tipo_mat:
        modello = st.selectbox("Modello", ["Area", "Classica", "Opera", "Epoca"])
        colore = st.selectbox("Essenza/Finitura", ["Rovere Naturale", "Laccato Bianco", "Noce", "Miele"])
    else:
        modello = st.selectbox("Profilo", ["Standard 70mm", "Minimal", "Scorrevole"])
        colore = st.text_input("Colore RAL/Finitura", "Bianco 9010")

    note_generali = st.text_area("Note Generali Commessa")

# --- COLONNA DESTRA: GRIGLIA MISURE ---
with col2:
    st.subheader("3. Inserimento Misure")
    st.info("Compila la tabella qui sotto come se fosse Excel. Aggiungi righe col tasto +")

    # Creiamo un DataFrame vuoto con le colonne giuste
    df_template = pd.DataFrame(
        [{"Posizione": "Cucina", "Larghezza (L)": 1200, "Altezza (H)": 1400, "Qtà": 1, "Apertura": "A/R DX", "Note": "Vetro satinato"}],
    )

    # L'EDITOR MAGICO DI STREAMLIT
    misure_df = st.data_editor(
        df_template,
        num_rows="dynamic", # Permette di aggiungere righe
        column_config={
            "Qtà": st.column_config.NumberColumn("Q.tà", min_value=1, step=1, width="small"),
            "Larghezza (L)": st.column_config.NumberColumn("L (mm)", min_value=0, format="%d"),
            "Altezza (H)": st.column_config.NumberColumn("H (mm)", min_value=0, format="%d"),
            "Apertura": st.column_config.SelectboxColumn(
                "Tipo Apertura",
                options=["Fisso", "1 Anta DX", "1 Anta SX", "A/R DX", "A/R SX", "2 Ante", "Scorrevole"],
                required=True,
            ),
        },
        hide_index=True,
        use_container_width=True
    )

# --- PULSANTE DI STAMPA ---
st.markdown("---")
col_sx, col_dx = st.columns([3, 1])

with col_dx:
    if st.button("Genera Anteprima PDF", type="primary"):
        st.toast("Generazione PDF in corso...", icon="⏳")
        
        # Raccolta dati testata
        dati_ordine = {
            "cliente": cliente, "indirizzo": indirizzo, "commessa": commessa,
            "telefono": telefono, "email": email,
            "tipo_mat": tipo_mat, "modello": modello, "colore": colore,
            "note_generali": note_generali
        }
        
        # Generazione File
        pdf_file = genera_pdf(dati_ordine, misure_df)
        
        # Download
        st.download_button(
            label="📥 SCARICA PDF DEFINITIVO",
            data=pdf_file,
            file_name=f"Rilievi_{cliente}_{commessa}.pdf",
            mime="application/pdf"
        )
        st.success("PDF Pronto!")