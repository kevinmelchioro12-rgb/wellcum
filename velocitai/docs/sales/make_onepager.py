"""Genera la scheda commerciale di una pagina in PDF (docs/sales/VelociTAI_OnePager.pdf).

    pip install reportlab
    python3 docs/sales/make_onepager.py

Il contenuto rispecchia ONE_PAGER.md. Pensato come leave-behind per i Comandi.
"""

import os
import sys

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable)
except ImportError:
    sys.exit("reportlab non installato. Esegui: pip install reportlab")

NAVY = colors.HexColor("#0b1f3a")
ACCENT = colors.HexColor("#1f6feb")
GREY = colors.HexColor("#555555")


def build(path):
    doc = SimpleDocTemplate(
        path, pagesize=A4,
        leftMargin=18 * mm, rightMargin=18 * mm,
        topMargin=14 * mm, bottomMargin=12 * mm,
        title="VelociTAI - Scheda prodotto", author="VelociTAI")
    ss = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=ss["Title"], textColor=NAVY, fontSize=21,
                        spaceAfter=2, leading=24)
    tag = ParagraphStyle("tag", parent=ss["Normal"], textColor=ACCENT, fontSize=11,
                         spaceAfter=8)
    h2 = ParagraphStyle("h2", parent=ss["Heading2"], textColor=NAVY, fontSize=12,
                        spaceBefore=8, spaceAfter=3)
    body = ParagraphStyle("body", parent=ss["Normal"], fontSize=9.5, leading=13)
    small = ParagraphStyle("small", parent=ss["Normal"], fontSize=8, textColor=GREY)
    bullet = ParagraphStyle("bullet", parent=body, leftIndent=8, bulletIndent=0)

    el = []
    el.append(Paragraph("VelociTAI", h1))
    el.append(Paragraph("Accertamento velocità che regge in giudizio", tag))
    el.append(HRFlowable(width="100%", color=ACCENT, thickness=1.2, spaceAfter=6))

    el.append(Paragraph(
        "Software di accertamento automatico dei limiti di velocità "
        "(<b>Art. 142 CdS</b>) che copre l'intero ciclo — rilevamento → misura → "
        "lettura targa → <b>prova con catena di custodia</b> → calcolo sanzione → "
        "verbale → notifica PEC — e produce <b>verbali difendibili</b>, riducendo "
        "annullamenti e ricorsi.", body))

    el.append(Paragraph("Perché VelociTAI", h2))
    for b in [
        "<b>Verbale difendibile</b>: tolleranza di legge, riferimenti normativi, "
        "termini perentori, <b>prova firmata (HMAC) verificabile</b> e audit-log "
        "a prova di manomissione.",
        "<b>Sicurezza &amp; GDPR by-design</b>: PII protette e redatte, accessi "
        "controllati, segreti fuori dal codice.",
        "<b>Affidabilità</b>: isolamento guasti, auto-riparazione, niente doppie "
        "multe (idempotenza), auto-diagnosi integrata.",
        "<b>Nessun lock-in</b>: backend e gestionali intercambiabili, API aperte.",
    ]:
        el.append(Paragraph(b, bullet, bulletText="•"))

    el.append(Paragraph("Prezzo (indicativo, IVA esclusa)", h2))
    price = Table([
        ["SaaS tutto incluso", "€ 6.000 / postazione / anno"],
        ["Pay-per-verbale (a risultato)", "€ 1,20 / verbale notificato"],
        ["Chiavi in mano (con partner hardware)", "€ 2.400–2.900 / mese"],
    ], colWidths=[95 * mm, 79 * mm])
    price.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("TEXTCOLOR", (1, 0), (1, -1), NAVY),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica-Bold"),
        ("LINEBELOW", (0, 0), (-1, -2), 0.3, colors.HexColor("#dddddd")),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    el.append(price)
    el.append(Paragraph("Sconti volume e accordi quadro. Acquisto via MEPA/CONSIP "
                        "o gara.", small))

    el.append(Paragraph("Come iniziare (basso rischio)", h2))
    el.append(Paragraph(
        "1) <b>Demo</b> dal vivo (10 min, anche su laptop) &nbsp;·&nbsp; "
        "2) <b>Pilota</b> retribuito su una postazione &nbsp;·&nbsp; "
        "3) Avvio in parallelo dell'<b>omologazione</b> (con partner) e della "
        "pratica GDPR.", body))

    el.append(Spacer(1, 4))
    el.append(HRFlowable(width="100%", color=colors.HexColor("#dddddd"), thickness=0.6))
    el.append(Paragraph(
        "Nota: l'uso per emettere sanzioni richiede strumento <b>omologato MIT</b> "
        "e <b>tarato</b>; VelociTAI si integra nella catena di misura omologata. Da "
        "subito impiegabile come motore di calcolo, prova e gestione verbali su "
        "strumenti già omologati. &nbsp;|&nbsp; 105 test automatici, fuzzing di "
        "sicurezza.", small))
    el.append(Spacer(1, 6))
    el.append(Paragraph("Contatto: ____________________   ·   ______________________"
                        "   ·   ________________", body))

    doc.build(el)
    return path


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "VelociTAI_OnePager.pdf")
    build(out)
    print("Generato:", out)
