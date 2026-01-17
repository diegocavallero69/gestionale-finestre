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

# --- FUNZIONI DI UTILITÀ (PDF) ---

def genera_pdf(dati_testata, df_misure):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    
    # 1. INTESTAZIONE
    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, 800, "SCHEDA RILIEVI - PRODUZIONE")
    c.setFont("Helvetica", 10)
    c.drawString(450, 800, f"Data: {datetime.now().strftime('%d/%m/%Y')}")
    
    # Riquadro Cliente
    c.setStrokeColor(colors.black)
    c.rect(40, 715, 515, 75, fill=0)
    c.drawString(50, 775, f"CLIENTE: {dati_testata['cliente']}")
    c.drawString(50, 760, f"INDIRIZZO: {dati_testata['indirizzo']}")
    c.drawString(50, 745, f"COMMESSA: {dati_testata['commessa']}")
    c.drawString(300, 775, f"TELEFONO: {dati_testata['telefono']}")
    c.drawString(300, 760, f"EMAIL: {dati_testata['email']}")
    
    # TIPO MISURE
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, 725, f"TIPO MISURE RILIEVATE:  >>>  {dati_testata['tipo_misura'].upper()}  <<<")

    # 2. DATI TECNICI
    c.setFillColor(colors.lightgrey)
    c.rect(40, 630, 515, 80, fill=1, stroke=1)
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 9)
    
    # Riga 1
    c.drawString(50, 695, f"MAT: {dati_testata['tipo_mat']}")
    c.drawString(250, 695, f"COL. ALL: {dati_testata['colore_alluminio']}")
    c.drawString(400, 695, f"MANIGLIA: {dati_testata['maniglia']} ({dati_testata['colore_maniglia']})")
    
    # Riga 2
    c.drawString(50, 680, f"ESSENZA: {dati_testata['essenza_legno']}")
    c.drawString(250, 680, f"FIN. EST: {dati_testata['finitura_legno']}")
    c.drawString(400, 680, f"FIN. INT: {dati_testata['finitura_interna_legno']}")
    
    # Riga 3
    c.drawString(50, 665, f"COPERTURE: {dati_testata['coperture']}")
    c.drawString(250, 665, f"VETRO: {dati_testata['vetro']}")
    c.drawString(400, 665, f"OSCURANTE GEN: {dati_testata['oscurante']}")
    
    # Riga 4
    info_extra = ""
    if dati_testata['zoccolo']: info_extra += f"ZOCCOLO: {dati_testata['zoccolo']} | CENTRALI: {dati_testata['nrCentrali']} "
    if dati_testata['HCentrale1']: info_extra += f"(H1: {dati_testata['HCentrale1']}) "
    if dati_testata['HCentrale2']: info_extra += f"(H2: {dati_testata['HCentrale2']}) "
    c.drawString(50, 650, info_extra)

    # 3. TABELLA MISURE
    y = 600
    c.setFont("Helvetica-Bold", 8)
    
    # Intestazioni
    c.drawString(40, y, "POS")
    c.drawString(100, y, "QTÀ")
    c.drawString(130, y, "L x H (mm)")
    c.drawString(190, y, "APERTURA")
    c.drawString(250, y, "BATTUTA")
    c.drawString(320, y, "FORMA / ANTE")
    c.drawString(400, y, "NOTE E ACCESSORI")
    c.line(40, y-5, 555, y-5)
    
    y -= 20
    c.setFont("Helvetica", 9)
    
    for index, row in df_misure.iterrows():
        if pd.notna(row["Posizione"]) and str(row["Posizione"]).strip() != "":
            
            # --- RIGA PRINCIPALE ---
            c.setFont("Helvetica-Bold", 9)
            c.drawString(40, y, str(row["Posizione"])[:12])
            c.setFont("Helvetica", 9)
            
            c.drawString(100, y, str(row["Qtà"]))
            
            dims = f"{row['Larghezza (L)']} x {row['Altezza (H)']}"
            if row.get("Altezza (arco trapezio) (H1)"):
                 dims += f" (H1:{row['Altezza (arco trapezio) (H1)']})"
            c.drawString(130, y, dims)
            
            c.drawString(190, y, str(row["Apertura"])[:12])
            c.drawString(250, y, str(row.get("Battuta", ""))[:12])
            
            forma_ante = f"{row.get('Forma','')} ({row.get('Nr ante','')}A)"
            c.drawString(320, y, forma_ante)
            
            c.drawString(400, y, str(row.get("Note", ""))[:30])
            
            # --- RIGA DETTAGLI ---
            dettagli = []
            
            # Accessori
            acc = []
            if row.get("Porta"): acc.append("PORTA")
            if row.get("Serratura"): acc.append("SERR.")
            if row.get("Altezza maniglia"): acc.append(f"H.Man:{row['Altezza maniglia']}")
            if acc: dettagli.append(" ".join(acc))
            
            # Coprifili (Stampiamo solo se hanno valori > 0)
            cop = []
            keys_cop = {
                "coprifilo interno": "Int", "coprifilo esterno": "Est",
                "coprifilo interno INF": "Int.Inf", "coprifilo esterno INF": "Est.Inf",
                "coprifilo interno DX": "Int.Dx", "coprifilo esterno DX": "Est.Dx",
                "coprifilo aggiuntivo L": "Agg.L", "coprifilo aggiuntivo H": "Agg.H"
            }
            for k, v in keys_cop.items():
                val = row.get(k)
                if val and val != 0:
                    cop.append(f"{v}:{val}")
            
            if cop: dettagli.append(f"COP: {', '.join(cop)}")
            
            # Oscuranti
            osc = []
            if row.get("zanzariera incasso"): osc.append("ZANZ.INC")
            if row.get("L_Zanzariera") or row.get("H_Zanzariera"): 
                osc.append(f"Zanz:{row.get('L_Zanzariera','')}x{row.get('H_Zanzariera','')}")
            if row.get("L_Oscurante") or row.get("H_Oscurante"):
                osc.append(f"Osc:{row.get('L_Oscurante','')}x{row.get('H_Oscurante','')}")
            
            if osc: dettagli.append(" ".join(osc))
            
            if dettagli:
                y -= 10
                c.setFont("Helvetica", 7)
                c.drawString(130, y, " // ".join(dettagli))
                c.setFont("Helvetica", 9)

            c.line(40, y-5, 555, y-5)
            y -= 20
            
            if y < 60:
                c.showPage()
                y = 800

    c.drawString(50, 50, f"NOTE GENERALI: {dati_testata['note_generali']}")
    c.save()
    buffer.seek(0)
    return buffer

# --- GESTIONE STATO ---
if 'dati_caricati' not in st.session_state:
    st.session_state['dati_caricati'] = None

# --- SIDEBAR (CARICAMENTO) ---
with st.sidebar:
    st.header("📂 Gestione Progetto")
    uploaded_file = st.file_uploader("Carica Progetto (.json)", type=["json"])
    if uploaded_file is not None:
        try:
            dati_json = json.load(uploaded_file)
            st.session_state['dati_caricati'] = dati_json
            st.success("Dati caricati!")
        except:
            st.error("File non valido.")

# --- INTERFACCIA PRINCIPALE ---
st.title("🪟 Gestionale Rilievi Serramenti")

d = st.session_state['dati_caricati'] if st.session_state['dati_caricati'] else {}

# === SEZIONE 1: INPUT DATI (COLLASSABILE) ===
# Qui mettiamo tutto dentro un expander per nasconderlo
with st.expander("📝 1. Anagrafica e 2. Specifiche Tecniche (Clicca per Aprire/Chiudere)", expanded=False):
    
    col_anag1, col_anag2 = st.columns(2)
    with col_anag1:
        st.subheader("1. Anagrafica")
        cliente = st.text_input("Cliente", value=d.get("cliente", ""))
        indirizzo = st.text_input("Indirizzo", value=d.get("indirizzo", ""))
        commessa = st.text_input("Commessa", value=d.get("commessa", ""))
    with col_anag2:
        st.write("") # Spaziatore
        st.write("") 
        telefono = st.text_input("Telefono", value=d.get("telefono", ""))
        email = st.text_input("Email", value=d.get("email", ""))

    st.markdown("---")
    
    # Tipo Misura
    tipo_misura_options = ["Misure foro (dare gioco)", "Misure esterno telaio finito", "Misure luce architettonica"]
    saved_tipo_mis = d.get("tipo_misura", tipo_misura_options[0])
    idx_tipo_mis = tipo_misura_options.index(saved_tipo_mis) if saved_tipo_mis in tipo_misura_options else 0
    tipo_misura = st.radio("Seleziona il tipo di misura:", options=tipo_misura_options, index=idx_tipo_mis, horizontal=True)

    st.markdown("---")
    st.subheader("2. Specifiche Tecniche")
    
    c1, c2, c3 = st.columns(3)
    
    with c1:
        # MATERIALE
        mat_options = ["Legno Estia", "Legno Clima80", "Legno alluminio Innova", "Legno alluminio Essential", "Legno alluminio Evo 2.0"]
        saved_mat = d.get("tipo_mat", mat_options[0])
        idx_mat = mat_options.index(saved_mat) if saved_mat in mat_options else 0
        tipo_mat = st.selectbox("Materiale", mat_options, index=idx_mat)
        
        # COLORE ALLUMINIO
        colore_alluminio = ""
        if "alluminio" in tipo_mat.lower():
            opt_alluminio = ["Bianco 9010", "Avorio 1013", "Grigio seta 7044", "Ciliegio", "Ral da definire"]
            saved_alu = d.get("colore_alluminio", opt_alluminio[0])
            idx_alu = opt_alluminio.index(saved_alu) if saved_alu in opt_alluminio else 0
            colore_alluminio = st.selectbox("Colore Alluminio Esterno", opt_alluminio, index=idx_alu)
        
        # VETRO
        opt_vet = ["Doppio", "Triplo"]
        saved_vet = d.get("vetro", opt_vet[0])
        idx_vet = opt_vet.index(saved_vet) if saved_vet in opt_vet else 0
        vetro = st.selectbox("Vetro", opt_vet, index=idx_vet)

    with c2:
        # LEGNO
        opt_legno = ["Pino lista intera", "Pino finger joint", "Red Grandis", "Larice", "Castagno", "Rovere"]
        saved_legno = d.get("essenza_legno", opt_legno[0])
        idx_legno = opt_legno.index(saved_legno) if saved_legno in opt_legno else 0
        essenza_legno = st.selectbox("Essenza Legno", opt_legno, index=idx_legno)
        
        # FINITURE
        opt_finitura = ["Noce", "Noce chiaro", "Noce scuro", "Pino scuro", "Ral 9010", "Ral 1013", "Ral 7044"]
        saved_finitura = d.get("finitura_legno", opt_finitura[0])
        idx_finitura = opt_finitura.index(saved_finitura) if saved_finitura in opt_finitura else 0
        finitura_legno = st.selectbox("Finitura Esterna", opt_finitura, index=idx_finitura)
        
        saved_fin_int = d.get("finitura_interna_legno", opt_finitura[0]) # Default same list
        idx_fin_int = opt_finitura.index(saved_fin_int) if saved_fin_int in opt_finitura else 0
        finitura_interna_legno = st.selectbox("Finitura Interna", opt_finitura, index=idx_fin_int)

    with c3:
        # MANIGLIA E ACCESSORI
        opt_maniglia = ["Glasgow", "Berna", "Bordeaux", "Brera", "Lisbona"]
        saved_maniglia = d.get("maniglia", opt_maniglia[0])
        idx_maniglia = opt_maniglia.index(saved_maniglia) if saved_maniglia in opt_maniglia else 0
        maniglia = st.selectbox("Maniglia", opt_maniglia, index=idx_maniglia)
        
        opt_col_man = ["Cromo satinato", "Cromo lucido", "Ottone", "Ottone satinato", "Nero"]
        saved_col_man = d.get("colore_maniglia", opt_col_man[0])
        idx_col_man = opt_col_man.index(saved_col_man) if saved_col_man in opt_col_man else 0
        colore_maniglia = st.selectbox("Colore Maniglia", opt_col_man, index=idx_col_man)

        opt_osc = ["Nessuno", "Persiana", "Scuro", "Tapparella", "Persiana Monoblocco", "Scuro Monoblocco"]
        saved_osc = d.get("oscurante", opt_osc[0])
        idx_osc = opt_osc.index(saved_osc) if saved_osc in opt_osc else 0
        oscurante = st.selectbox("Oscurante Generale", opt_osc, index=idx_osc)
        
        opt_cop = ["Cromo satinato", "Ottone", "Bianche", "Marroni", "Ral"]
        saved_cop = d.get("coperture", opt_cop[0])
        idx_cop = opt_cop.index(saved_cop) if saved_cop in opt_cop else 0
        coperture = st.selectbox("Coperture", opt_cop, index=idx_cop)

    st.markdown("##### Dettagli Porta")
    c_p1, c_p2 = st.columns(2)
    zoccolo = c_p1.text_input("Zoccolo (mm)", value=d.get("zoccolo", ""))
    nrCentrali = c_p2.text_input("N. Centrali", value=d.get("nrCentrali", ""))
    
    col_h1, col_h2, col_h3 = st.columns(3)
    HCentrale1 = col_h1.text_input("H Centr.1", value=d.get("HCentrale1", ""))
    HCentrale2 = col_h2.text_input("H Centr.2", value=d.get("HCentrale2", ""))
    HCentrale3 = col_h3.text_input("H Centr.3", value=d.get("HCentrale3", ""))
    
    note_generali = st.text_area("Note Generali Commessa", value=d.get("note_generali", ""))


# === SEZIONE 2: TABELLA MISURE (A TUTTO SCHERMO) ===
st.markdown("---")
st.subheader("3. Misure e Quantità")

# 1. Recupero o Inizializzazione DataFrame
if 'misure' in d:
    df_iniziale = pd.DataFrame(d['misure'])
else:
    df_iniziale = pd.DataFrame(
        [{"Posizione": "Cucina", "Forma": "Rettangolare", "Nr ante": 1, 
          "Larghezza (L)": 1200, "Altezza (H)": 1400, "Qtà": 1, "Apertura": "DKD", 
          "Battuta": "15x40 Lat/sup", "Porta": False, "Serratura": False, "Note": ""}]
    )

# 2. DEFINIZIONE DELLE COLONNE AVANZATE
# Importante: Definisco quali colonne sono "Extra". 
# Se non esistono nel DF, le creo a 0 per evitare che spariscano.
extra_cols_coprifili = [
    "coprifilo interno", "coprifilo esterno",
    "coprifilo interno INF", "coprifilo esterno INF", 
    "coprifilo interno DX", "coprifilo esterno DX",
    "coprifilo aggiuntivo L", "coprifilo aggiuntivo H"
]
extra_cols_oscuranti = [
    "zanzariera incasso", "L_Zanzariera", "H_Zanzariera",
    "L_Oscurante", "H_Oscurante", "note oscurante"
]

# Inizializzo le colonne a 0/None se mancano (così l'editor non si rompe)
for col in extra_cols_coprifili + extra_cols_oscuranti:
    if col not in df_iniziale.columns:
        if "zanzariera incasso" in col:
            df_iniziale[col] = False
        elif "note" in col:
            df_iniziale[col] = ""
        else:
            df_iniziale[col] = 0

# 3. INTERRUTTORI VISIBILITÀ
c_check1, c_check2 = st.columns(2)
show_coprifili = c_check1.checkbox("Mostra Varianti Coprifili", value=False)
show_oscuranti = c_check2.checkbox("Mostra Dettagli Oscuranti/Zanz", value=False)

# 4. DEFINIZIONE ORDINE COLONNE (Questo fa la magia del nascondi/mostra)
column_order = [
    "Posizione", "Forma", "Nr ante", "Larghezza (L)", "Altezza (H)", "Altezza (arco trapezio) (H1)",
    "Qtà", "Apertura", "Battuta", "Porta", "Serratura", "Altezza maniglia", "Note"
]

if show_coprifili:
    # Aggiungo i coprifili all'ordine visualizzato
    column_order.extend(extra_cols_coprifili)

if show_oscuranti:
    # Aggiungo oscuranti all'ordine visualizzato
    column_order.extend(extra_cols_oscuranti)

# 5. CONFIGURAZIONE EDITOR
col_config = {
    "Posizione": st.column_config.TextColumn("Posizione", width="medium"),
    "Forma": st.column_config.SelectboxColumn("Forma", options=["Rettangolare", "Arco", "Trapezio", "3 centri"], required=True, width="small"),
    "Nr ante": st.column_config.NumberColumn("Ante", min_value=1, max_value=4, step=1, format="%d", width="small"),
    "Larghezza (L)": st.column_config.NumberColumn("L", format="%d", width="small"),
    "Altezza (H)": st.column_config.NumberColumn("H", format="%d", width="small"),
    "Altezza (arco trapezio) (H1)": st.column_config.NumberColumn("H1", format="%d", width="small"),
    "Qtà": st.column_config.NumberColumn("Qtà", min_value=1, step=1, width="small"),
    "Apertura": st.column_config.SelectboxColumn("Apertura", options=["Fisso", "DX", "SX", "DKD", "DKS", "DX Centrale", "SX Centrale"], required=True, width="medium"),
    "Battuta": st.column_config.SelectboxColumn("Battuta", options=["15x40 Lat/sup", "15x50 Lat/sup", "15x70 Lat/sup","15x40 Lat/sup/inf", "15x50 Lat/sup/inf", "15x70 Lat/sup/inf"], required=True, width="medium"),
    "Porta": st.column_config.CheckboxColumn("Porta", default=False, width="small"),
    "Serratura": st.column_config.CheckboxColumn("Serratura", default=False, width="small"),
    "Altezza maniglia": st.column_config.NumberColumn("H.Man", format="%d", width="small"),
    "Note": st.column_config.TextColumn("Note", width="large"),
    
    # Colonne Extra (Configurate ma visibili solo se in column_order)
    "coprifilo interno": st.column_config.NumberColumn("Cop.Int", format="%d"),
    "coprifilo esterno": st.column_config.NumberColumn("Cop.Est", format="%d"),
    "coprifilo interno INF": st.column_config.NumberColumn("C.Int.INF", format="%d"),
    "coprifilo esterno INF": st.column_config.NumberColumn("C.Est.INF", format="%d"),
    "coprifilo interno DX": st.column_config.NumberColumn("C.Int.DX", format="%d"),
    "coprifilo esterno DX": st.column_config.NumberColumn("C.Est.DX", format="%d"),
    "coprifilo aggiuntivo L": st.column_config.NumberColumn("C.Agg.L", format="%d"),
    "coprifilo aggiuntivo H": st.column_config.NumberColumn("C.Agg.H", format="%d"),
    
    "zanzariera incasso": st.column_config.CheckboxColumn("Zanz.Inc", default=False),
    "L_Zanzariera": st.column_config.NumberColumn("L.Zanz", format="%d"),
    "H_Zanzariera": st.column_config.NumberColumn("H.Zanz", format="%d"),
    "L_Oscurante": st.column_config.NumberColumn("L.Osc", format="%d"),
    "H_Oscurante": st.column_config.NumberColumn("H.Osc", format="%d"),
    "note oscurante": st.column_config.TextColumn("Note Osc"),
}

# 6. VISUALIZZAZIONE EDITOR
misure_df = st.data_editor(
    df_iniziale,
    column_order=column_order, # <--- QUESTO è il trucco per nascondere/mostrare
    column_config=col_config,
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True
)

# Validazione errori
errori = []
for index, row in misure_df.iterrows():
    ante = row.get("Nr ante", 1)
    apertura = row.get("Apertura", "")
    if pd.notna(ante) and ante < 3 and "Centrale" in str(apertura):
        errori.append(f"Riga {index+1}: Apertura '{apertura}' non valida per {ante} ante!")

if errori:
    for e in errori:
        st.error(e)
    st.stop()

st.markdown("---")

# === BOTTONI (ZONA BASSA) ===
c_sx, c_cnt, c_dx = st.columns(3)

dati_completi = {
    "cliente": cliente, "indirizzo": indirizzo, "commessa": commessa,
    "telefono": telefono, "email": email,
    "tipo_misura": tipo_misura,
    "tipo_mat": tipo_mat,
    "colore_alluminio": colore_alluminio,
    "essenza_legno": essenza_legno,
    "finitura_legno": finitura_legno,
    "finitura_interna_legno": finitura_interna_legno,
    "maniglia": maniglia,
    "colore_maniglia": colore_maniglia,
    "coperture": coperture,
    "vetro": vetro,
    "oscurante": oscurante,
    "zoccolo": zoccolo,
    "nrCentrali": nrCentrali,
    "HCentrale1": HCentrale1, "HCentrale2": HCentrale2, "HCentrale3": HCentrale3,
    "note_generali": note_generali,
    "misure": misure_df.to_dict('records')
}

json_str = json.dumps(dati_completi, indent=4)

with c_sx:
    nome_file_json = f"Progetto_{cliente if cliente else 'Nuovo'}.json"
    st.download_button("💾 SALVA PROGETTO", json_str, file_name=nome_file_json, mime="application/json")

with c_dx:
    if st.button("Genera PDF", type="primary"):
        pdf_file = genera_pdf(dati_completi, misure_df)
        st.download_button("📥 SCARICA PDF", pdf_file, file_name=f"Rilievi_{cliente}.pdf", mime="application/pdf")