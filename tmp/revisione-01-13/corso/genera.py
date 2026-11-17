# Genera la cartella del corso (slide, indice, schede da stampare) a partire da:
#   programma.py             il programma settimana per settimana
#   contenuti/sNN-*.md       il testo delle slide: sNN-spiegazione.md e sNN-attivita.md
#   schede/settimana-NN      le schede da stampare, in .md (quelle che iniziano con
#                            "soluzione" o "docente" vanno nella cartella del docente)
#   assets/                  stile e motore delle slide
#
# Uso: python genera.py [cartella di destinazione]
#
# Formato dei file .md delle slide
#   ---                  separa le slide
#   ???                  da qui in poi, note per il docente
#   <!-- docente -->     slide visibile solo al docente (soluzioni, criteri)
#   # Titolo / ## Sottotitolo, elenchi con - o 1., > riquadro (> !attenzione, > !prova)
#   ||                   divide la slide in colonne
#   | a | b |            tabelle
#   <svg ...> ... </svg> disegno, senza righe vuote in mezzo
#   @file percorso       collegamento a una scheda (es. settimana-03/scheda-annuncio.md)
#
# Nelle schede valgono le stesse regole, piu':
#   @righe N             N righe vuote per scrivere
#   @riquadro H [testo]  riquadro alto H millimetri per disegnare, con un'etichetta
#   @griglia N L         griglia di N x N quadretti, larga L millimetri
#   @pagina              salto pagina
#   @alto N              (in una cella di tabella) cella vuota alta N millimetri
#   @colonne ... || ... @fine   colonne affiancate (dentro si possono usare le macro)
# In cima a ogni scheda per gli studenti compare la riga Nome / Classe / Data
# (non nelle schede che iniziano con "carte", che sono da ritagliare).

import html
import importlib.util
import os
import re
import shutil
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
DEST = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(os.path.dirname(QUI), "Corso Tecnologie applicate seconda")
SCHEDE = os.path.join(QUI, "schede")
TITOLO_CORSO = "Scienze e tecnologie applicate · seconda"


def carica_programma():
    spec = importlib.util.spec_from_file_location("programma", os.path.join(QUI, "programma.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.MODULI, mod.SETTIMANE


# ---------------------------------------------------------------- testo in linea

def in_linea(testo):
    pezzi = re.split(r"(`[^`]+`)", testo)
    out = []
    for p in pezzi:
        if len(p) > 1 and p.startswith("`") and p.endswith("`"):
            out.append(f"<code>{html.escape(p[1:-1])}</code>")
            continue
        e = html.escape(p, quote=False)
        e = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", e)
        e = re.sub(r"(?<![\w*])\*([^*\s][^*]*?)\*(?![\w*])", r"<em>\1</em>", e)
        e = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', e)
        out.append(e)
    return "".join(out)


def senza_markup(testo):
    return re.sub(r"[`*]", "", testo)


# ---------------------------------------------------------------- schede

def file_scheda(rel):
    p = os.path.join(SCHEDE, rel.replace("/", os.sep))
    if not os.path.exists(p):
        raise FileNotFoundError(f"manca la scheda schede/{rel}")
    return p


def cartella_di(rel):
    nome = os.path.basename(rel)
    return "soluzioni-docente" if nome.startswith(("soluzione", "docente")) else "materiale-studenti"


def pagina_scheda(rel):
    """Percorso della scheda stampabile, relativo alla radice del corso."""
    return f"{cartella_di(rel)}/{rel.rsplit('.', 1)[0]}.html"


def griglia_svg(n, lato_mm):
    ve = 'vector-effect="non-scaling-stroke"'
    linee = "".join(f'<line x1="{i}" y1="0" x2="{i}" y2="{n}" {ve}/><line x1="0" y1="{i}" x2="{n}" y2="{i}" {ve}/>'
                    for i in range(n + 1))
    return (f'<svg class="griglia" viewBox="-0.05 -0.05 {n + .1} {n + .1}" style="width:{lato_mm}mm;height:{lato_mm}mm">'
            f'<g stroke="#777" stroke-width="1" fill="none">{linee}</g></svg>')


# ---------------------------------------------------------------- blocchi di testo

def blocchi(righe, contesto):
    """Converte una lista di righe di testo in HTML."""
    out = []
    i = 0
    para = []

    def chiudi_para():
        if para:
            out.append("<p>" + in_linea(" ".join(para)) + "</p>")
            para.clear()

    while i < len(righe):
        r = righe[i]
        s = r.strip()
        if not s:
            chiudi_para()
            i += 1
            continue
        if s.startswith("# "):
            chiudi_para()
            out.append(f"<h1>{in_linea(s[2:])}</h1>")
        elif s.startswith("## "):
            chiudi_para()
            out.append(f"<h2>{in_linea(s[3:])}</h2>")
        elif s.startswith("@file "):
            chiudi_para()
            rel = s.split()[1]
            file_scheda(rel)
            cart = cartella_di(rel) + "\\" + os.path.dirname(rel).replace("/", "\\")
            titolo = titolo_scheda(rel)
            out.append(f'<p class="piccolo">Scheda: <a href="../{pagina_scheda(rel)}">{html.escape(titolo)}</a>'
                       f' &nbsp;·&nbsp; nella cartella <code>{html.escape(cart)}</code></p>')
        elif s.startswith("@righe"):
            chiudi_para()
            n = int(s.split()[1])
            out.append('<div class="righe">' + '<div></div>' * n + '</div>')
        elif s.startswith("@riquadro"):
            chiudi_para()
            parti = s.split(maxsplit=2)
            etichetta = f"<span>{in_linea(parti[2])}</span>" if len(parti) > 2 else ""
            out.append(f'<div class="riquadro" style="height:{int(parti[1])}mm">{etichetta}</div>')
        elif s.startswith("@griglia"):
            chiudi_para()
            _, n, lato = s.split()
            out.append(f'<div class="fig-box">{griglia_svg(int(n), int(lato))}</div>')
        elif s == "@pagina":
            chiudi_para()
            out.append('<div class="salto"></div>')
        elif s == "@colonne":
            chiudi_para()
            j = i + 1
            colonne = [[]]
            while j < len(righe) and righe[j].strip() != "@fine":
                if righe[j].strip() == "||":
                    colonne.append([])
                else:
                    colonne[-1].append(righe[j])
                j += 1
            out.append('<div class="cols">' + "".join(
                f'<div class="col">{blocchi(c, contesto)}</div>' for c in colonne) + "</div>")
            i = j + 1
            continue
        elif s.startswith("<"):
            chiudi_para()
            j = i
            grezzo = []
            while j < len(righe) and righe[j].strip():
                grezzo.append(righe[j])
                j += 1
            out.append("\n".join(grezzo))
            i = j
            continue
        elif s.startswith(">"):
            chiudi_para()
            j = i
            dentro = []
            while j < len(righe) and righe[j].strip().startswith(">"):
                dentro.append(righe[j].strip()[1:].lstrip() if righe[j].strip() != ">" else "")
                j += 1
            classe = ""
            if dentro and dentro[0].startswith("!"):
                classe = f' class="{dentro[0][1:].strip()}"'
                dentro = dentro[1:]
            out.append(f"<blockquote{classe}>" + blocchi(dentro, contesto) + "</blockquote>")
            i = j
            continue
        elif re.match(r"^(-|\d+\.) ", s):
            chiudi_para()
            j, html_lista = elenco(righe, i, contesto)
            out.append(html_lista)
            i = j
            continue
        elif s.startswith("|") and s != "||":
            chiudi_para()
            j = i
            tab = []
            while j < len(righe) and righe[j].strip().startswith("|"):
                tab.append(righe[j].strip())
                j += 1
            out.append(tabella(tab))
            i = j
            continue
        else:
            para.append(s)
        i += 1
    chiudi_para()
    return "\n".join(out)


def rientro(r):
    return len(r) - len(r.lstrip(" "))


def elenco(righe, i, contesto):
    base = rientro(righe[i])
    ordinato = bool(re.match(r"^\d+\. ", righe[i].strip()))
    voci = []
    while i < len(righe):
        r = righe[i]
        s = r.strip()
        if not s:
            # un elenco continua dopo una riga vuota solo se segue un'altra voce
            if i + 1 < len(righe) and re.match(r"^(-|\d+\.) ", righe[i + 1].strip()) and rientro(righe[i + 1]) >= base:
                i += 1
                continue
            break
        ind = rientro(r)
        m = re.match(r"^(-|\d+\.) (.*)$", s)
        if m and ind == base:
            voci.append([m.group(2)])
        elif ind > base and voci:
            voci[-1].append(r[base + 2:] if len(r) > base + 2 else s)
        else:
            break
        i += 1
    tag = "ol" if ordinato else "ul"
    parti = []
    for v in voci:
        if len(v) == 1:
            parti.append(f"<li>{in_linea(v[0])}</li>")
        else:
            prima = v[0]
            resto = v[1:]
            if resto and re.match(r"^(-|\d+\.) |^>|^@", resto[0].strip()):
                parti.append(f"<li>{in_linea(prima)}{blocchi(resto, contesto)}</li>")
            else:
                parti.append(f"<li>{in_linea(' '.join([prima] + [x.strip() for x in resto]))}</li>")
    return i, f"<{tag}>" + "".join(parti) + f"</{tag}>"


def cella(c):
    # "@alto N" in una cella la rende alta N millimetri, vuota (per scriverci o disegnarci)
    m = re.match(r"^@alto (\d+)$", c)
    return f'<div style="height:{m.group(1)}mm"></div>' if m else in_linea(c)


def tabella(righe):
    celle = [[c.strip() for c in r.strip("|").split("|")] for r in righe]
    corpo = [c for c in celle if not all(re.match(r"^:?-+:?$", x) for x in c)]
    h = "<table><thead><tr>" + "".join(f"<th>{in_linea(c)}</th>" for c in corpo[0]) + "</tr></thead><tbody>"
    for riga in corpo[1:]:
        h += "<tr>" + "".join(f"<td>{cella(c)}</td>" for c in riga) + "</tr>"
    return h + "</tbody></table>"


# ---------------------------------------------------------------- slide

def slide_html(testo, contesto):
    righe = testo.split("\n")
    docente = any(r.strip() == "<!-- docente -->" for r in righe)
    righe = [r for r in righe if r.strip() != "<!-- docente -->"]
    note = []
    if any(r.strip() == "???" for r in righe):
        k = [r.strip() for r in righe].index("???")
        righe, note = righe[:k], righe[k + 1:]
    colonne = [[]]
    for r in righe:
        if r.strip() == "||":
            colonne.append([])
        else:
            colonne[-1].append(r)
    if len(colonne) == 1:
        corpo = blocchi(colonne[0], contesto)
    else:
        # il titolo (se c'e') resta sopra le colonne
        testa = []
        prima = colonne[0]
        while prima and (not prima[0].strip() or prima[0].startswith("# ")):
            testa.append(prima.pop(0))
        colonne = [c for c in colonne if any(r.strip() for r in c)]
        corpo = blocchi(testa, contesto) + '<div class="cols">' + "".join(
            f'<div class="col">{blocchi(c, contesto)}</div>' for c in colonne) + "</div>"
    return docente, corpo, blocchi(note, contesto)


def dividi_slide(testo):
    pezzi, cur = [], []
    for r in testo.split("\n"):
        if r.strip() == "---":
            pezzi.append("\n".join(cur))
            cur = []
        else:
            cur.append(r)
    pezzi.append("\n".join(cur))
    return [p for p in pezzi if p.strip()]


BARRA = """<div id="progresso"></div>
<div id="barra">
  <a href="../INDICE.html" title="Torna all'indice">Indice</a>
  <button id="b-indietro" title="Indietro (freccia sinistra)">&#9664;</button>
  <span class="conta" id="conta"></span>
  <button id="b-avanti" title="Avanti (freccia destra o spazio)">&#9654;</button>
  <button id="b-note" title="Note per il docente (N)">Note</button>
  <button id="b-soluzioni" title="Mostra anche le slide del docente (S)">Soluzioni</button>
  <button id="b-lettura" title="Tutte le slide in colonna, con le note; si puo' stampare (L)">Lettura</button>
  <button id="b-schermo" title="Schermo intero (F)">Schermo intero</button>
</div>"""

ETICHETTA = {"spiegazione": "Spiegazione", "attivita": "Attività"}


def genera_lezione(sett, modulo, nome_modulo, tipo, titolo, testo):
    contesto = f"s{sett:02d}-{tipo}"
    etichetta = ETICHETTA[tipo]
    piede = f"Settimana {sett} · {etichetta}"
    slides = dividi_slide(testo) if testo else ["# In preparazione\n\nLe slide di questa lezione non sono ancora pronte."]
    note_titolo = ""
    if slides and slides[0].lstrip().startswith("???"):
        note_titolo = blocchi(slides[0].lstrip()[3:].split("\n"), contesto)
        slides = slides[1:]
    classe_tipo = "tipo" if tipo == "spiegazione" else "tipo lab"
    elementi = [(False, "titolo",
                 f'<div class="sopra">Modulo {modulo} · {html.escape(nome_modulo)} · Settimana {sett}</div>'
                 f'<h1>{in_linea(titolo)}</h1><div class="{classe_tipo}">{etichetta}</div>', note_titolo)]
    for s in slides:
        docente, corpo, note = slide_html(s, contesto)
        elementi.append((docente, "", corpo, note))
    parti = []
    for n, (docente, classe, corpo, note) in enumerate(elementi, 1):
        classi = " ".join(x for x in ("slide", classe, "docente" if docente else "") if x)
        parti.append(f'<div class="item{" docente" if docente else ""}"><div class="frame"><section class="{classi}">'
                     f'<div class="body">{corpo}</div><footer class="sfoot"><span>{piede}</span><span>{n}</span></footer>'
                     f'</section></div><aside class="note">{note}</aside></div>')
    pagina = f"""<!doctype html>
<html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sett. {sett} · {etichetta} · {html.escape(senza_markup(titolo))}</title>
<link rel="stylesheet" href="_assets/slides.css"></head>
<body>
<div id="vista">
{chr(10).join(parti)}
</div>
<div id="note"></div>
{BARRA}
<script src="_assets/slides.js"></script>
</body></html>
"""
    with open(os.path.join(DEST, "slides", contesto + ".html"), "w", encoding="utf-8") as f:
        f.write(pagina)
    return len(elementi), sum(1 for e in elementi if e[0])


# ---------------------------------------------------------------- schede da stampare

PAGINA_SCHEDA = """<!doctype html>
<html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titolo}</title>
<style>
@page {{ size: A4 portrait; margin: 14mm; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: #e9ecef; color: #1d232b; font: 12pt/1.45 "Segoe UI", system-ui, Arial, sans-serif; }}
.comandi {{ max-width: 210mm; margin: 0 auto; padding: 12px 0; display: flex; gap: 10px; align-items: center; }}
.comandi a, .comandi button {{ font: 15px "Segoe UI", sans-serif; padding: 6px 14px; border: 1px solid #c5ccd3; border-radius: 5px; background: #fff; color: #1d232b; text-decoration: none; cursor: pointer; }}
.comandi span {{ color: #5b6672; font-size: 14px; }}
.foglio {{ max-width: 210mm; margin: 0 auto 30px; background: #fff; padding: 14mm; box-shadow: 0 1px 6px rgba(0,0,0,.2); }}
.intesta {{ display: flex; gap: 6mm; font-size: 11pt; margin-bottom: 5mm; }}
.intesta span {{ flex: 1; border-bottom: 1px solid #555; padding-bottom: 1mm; white-space: nowrap; }}
.intesta span.corto {{ flex: 0 0 32mm; }}
.avviso {{ background: #fbe9e7; color: #b3261e; padding: 2mm 4mm; font-weight: 600; margin-bottom: 4mm; border-radius: 3px; }}
h1 {{ font-size: 18pt; margin: 0 0 3mm; color: #9a2f68; }}
h2 {{ font-size: 13pt; margin: 5mm 0 1.5mm; }}
p {{ margin: 0 0 2mm; }}
ul, ol {{ margin: 0 0 2mm; padding-left: 6mm; }}
li {{ margin: .5mm 0; }}
table {{ border-collapse: collapse; width: 100%; margin: 1mm 0 3mm; font-size: 11pt; }}
th, td {{ border: 1px solid #888; padding: 1.5mm 2.5mm; text-align: left; vertical-align: top; }}
th {{ background: #f3f3f3; }}
td:empty::after {{ content: ""; display: inline-block; height: 7mm; }}
blockquote {{ margin: 0 0 3mm; padding: 2mm 4mm; border-left: 3px solid #9a2f68; background: #f7e9f1; }}
blockquote.attenzione {{ border-left-color: #b3261e; background: #fbe9e7; }}
blockquote p:last-child {{ margin: 0; }}
.righe {{ margin: 1mm 0 3mm; }}
.righe div {{ height: 9mm; border-bottom: 1px solid #999; }}
.riquadro {{ border: 1px solid #555; margin: 1mm 0 3mm; position: relative; }}
.riquadro span {{ position: absolute; left: 2mm; top: 1mm; font-size: 9pt; color: #666; }}
.fig-box {{ display: flex; justify-content: center; margin: 2mm 0; }}
.cols {{ display: flex; gap: 6mm; }}
.cols > .col {{ flex: 1; min-width: 0; }}
svg {{ max-width: 100%; }}
.salto {{ break-after: page; height: 0; }}
@media screen {{ .salto {{ border-top: 2px dashed #c5ccd3; margin: 10mm -14mm; }} }}
@media print {{
  body {{ background: #fff; }}
  .comandi {{ display: none; }}
  .foglio {{ max-width: none; margin: 0; padding: 0; box-shadow: none; }}
  * {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
}}
</style></head><body>
<div class="comandi"><a href="{indice}">Indice</a><button onclick="window.print()">Stampa</button><span>{dove}</span></div>
<div class="foglio">
{testa}
{corpo}
</div>
</body></html>
"""

_titoli = {}


def titolo_scheda(rel):
    if rel not in _titoli:
        testo = open(file_scheda(rel), encoding="utf-8").read()
        m = re.search(r"^# (.+)$", testo, re.M)
        _titoli[rel] = senza_markup(m.group(1)) if m else os.path.basename(rel)
    return _titoli[rel]


def genera_schede():
    elenco_file = {}
    if not os.path.isdir(SCHEDE):
        return elenco_file
    for cartella in sorted(os.listdir(SCHEDE)):
        sorg = os.path.join(SCHEDE, cartella)
        if not os.path.isdir(sorg) or not cartella.startswith("settimana-"):
            continue
        sett = int(cartella.split("-")[1])
        for nome in sorted(os.listdir(sorg)):
            if not nome.endswith(".md") or nome.startswith("_"):
                continue
            rel = f"{cartella}/{nome}"
            docente = cartella_di(rel) == "soluzioni-docente"
            testo = open(os.path.join(sorg, nome), encoding="utf-8").read()
            if docente:
                testa = '<div class="avviso">Solo per il docente: non distribuire agli studenti.</div>'
            elif nome.startswith("carte"):
                testa = ""
            else:
                testa = ('<div class="intesta"><span>Nome e cognome</span>'
                         '<span class="corto">Classe</span><span class="corto">Data</span></div>')
            dest = os.path.join(DEST, pagina_scheda(rel).replace("/", os.sep))
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, "w", encoding="utf-8") as f:
                f.write(PAGINA_SCHEDA.format(titolo=html.escape(titolo_scheda(rel)), indice="../../INDICE.html",
                                             dove=html.escape(pagina_scheda(rel).replace("/", "\\")),
                                             testa=testa, corpo=blocchi(testo.split("\n"), "scheda")))
            elenco_file.setdefault(sett, []).append(rel)
    return elenco_file


# ---------------------------------------------------------------- indice

def genera_indice(moduli, settimane, elenco_file, conteggi):
    sezioni = []
    for m, nome_m in moduli.items():
        righe_m = [s for s in settimane if s[1] == m]
        da, a = righe_m[0][0], righe_m[-1][0]
        tr = []
        for sett, _, spieg, att in righe_m:
            file_html = []
            for rel in elenco_file.get(sett, []):
                cl = ' class="sol"' if cartella_di(rel) == "soluzioni-docente" else ""
                file_html.append(f'<a{cl} href="{pagina_scheda(rel)}">{html.escape(titolo_scheda(rel))}</a>')
            ns, _ = conteggi[(sett, "spiegazione")]
            na, da_doc = conteggi[(sett, "attivita")]
            tr.append(f"""<tr><td class="num">{sett}</td>
<td><a class="lez" href="slides/s{sett:02d}-spiegazione.html">{in_linea(spieg)}</a><span class="quante">{ns} slide</span></td>
<td><a class="lez" href="slides/s{sett:02d}-attivita.html">{in_linea(att)}</a><span class="quante">{na} slide{f" · {da_doc} solo docente" if da_doc else ""}</span></td>
<td class="file">{"<br>".join(file_html)}</td></tr>""")
        sezioni.append(f"""<section><h2>Modulo {m} · {html.escape(nome_m)} <span>settimane {da}-{a}</span></h2>
<div class="tab"><table><thead><tr><th>Sett.</th><th>Spiegazione (circa 20 min)</th><th>Attività (il resto delle 3 ore)</th><th>Schede da stampare</th></tr></thead>
<tbody>{"".join(tr)}</tbody></table></div></section>""")
    materiali = "materiale-studenti/settimana-01/scheda-materiali.html"
    griglia = "soluzioni-docente/settimana-01/docente-valutazione.html"
    pagina = f"""<!doctype html>
<html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{TITOLO_CORSO}</title>
<style>
:root {{ --testo:#1d232b; --tenue:#5b6672; --accento:#9a2f68; --chiaro:#f7e9f1; --bordo:#d5dbe1; --verde:#1e7a3c; --rosso:#b3261e; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: #f4f6f8; color: var(--testo); font: 16px/1.5 "Segoe UI", system-ui, -apple-system, Roboto, Arial, sans-serif; }}
main {{ max-width: 1180px; margin: 0 auto; padding: 28px 16px 60px; }}
h1 {{ font-size: 30px; margin: 0 0 4px; }}
.sotto {{ color: var(--tenue); margin: 0 0 24px; }}
.guida {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 14px; margin-bottom: 30px; }}
.guida div {{ background: #fff; border: 1px solid var(--bordo); border-radius: 8px; padding: 14px 18px; }}
.guida h3 {{ margin: 0 0 6px; font-size: 16px; }}
.guida ul, .guida ol {{ margin: 0; padding-left: 1.2em; }}
.guida p {{ margin: 0 0 6px; }}
.guida a {{ color: var(--accento); }}
kbd {{ font: 13px Consolas, monospace; border: 1px solid #b9c1c9; border-bottom-width: 2px; border-radius: 4px; padding: 0 5px; background: #fff; }}
section {{ margin-bottom: 30px; }}
h2 {{ font-size: 21px; margin: 0 0 8px; color: var(--accento); }}
h2 span {{ font-size: 15px; color: var(--tenue); font-weight: 400; margin-left: 6px; }}
.tab {{ overflow-x: auto; background: #fff; border: 1px solid var(--bordo); border-radius: 8px; }}
table {{ border-collapse: collapse; width: 100%; min-width: 720px; }}
th, td {{ text-align: left; vertical-align: top; padding: 9px 12px; border-bottom: 1px solid #e6e9ed; }}
th {{ font-size: 13px; text-transform: uppercase; letter-spacing: .04em; color: var(--tenue); background: #fafbfc; }}
tr:last-child td {{ border-bottom: 0; }}
td.num {{ font-weight: 700; color: var(--tenue); width: 50px; }}
a.lez {{ color: var(--testo); text-decoration: none; font-weight: 600; display: block; }}
a.lez:hover {{ color: var(--accento); text-decoration: underline; }}
.quante {{ display: block; font-size: 13px; color: var(--tenue); }}
td.file {{ font-size: 14px; width: 230px; }}
td.file a {{ color: var(--accento); }}
td.file a.sol {{ color: var(--rosso); }}
code {{ font: .92em Consolas, monospace; background: #eef1f4; padding: 0 .25em; border-radius: 3px; }}
</style></head><body><main>
<h1>{TITOLO_CORSO}</h1>
<p class="sotto">Istituto tecnico, indirizzo grafica e comunicazione · 25 settimane, 3 ore a settimana · tutto in classe, senza computer e senza telefono. Clic su un titolo per aprire le slide.</p>
<div class="guida">
  <div><h3>Come va una lezione di 3 ore</h3><ol>
    <li>Spiegazione, parte 1 (10 minuti)</li>
    <li>Attività, prima fase (circa un'ora)</li>
    <li>Spiegazione, parte 2 (10 minuti)</li>
    <li>Attività, seconda fase (circa un'ora e un quarto)</li>
    <li>Consegna e riordino (10 minuti)</li></ol>
    <p>Il punto in cui fermarsi è segnato nelle slide.</p></div>
  <div><h3>Le slide</h3><ul>
    <li><kbd>→</kbd> o <kbd>Spazio</kbd> avanti, <kbd>←</kbd> indietro</li>
    <li><kbd>F</kbd> schermo intero, <kbd>N</kbd> note per il docente</li>
    <li><kbd>S</kbd> mostra le slide <b>SOLO DOCENTE</b> (criteri, soluzioni)</li>
    <li><kbd>L</kbd> tutte le slide in colonna con le note, da leggere prima o da stampare</li></ul></div>
  <div><h3>Schede e materiali</h3>
    <p><code>materiale-studenti</code>: le schede da stampare per la classe (pulsante Stampa in alto, formato A4).</p>
    <p><code>soluzioni-docente</code>: soluzioni e griglie, in rosso nella tabella. Non vanno distribuite.</p>
    <p><a href="{materiali}">Elenco dei materiali</a> da chiedere a inizio anno · <a href="{griglia}">Griglia di valutazione</a></p></div>
</div>
{"".join(sezioni)}
</main></body></html>
"""
    with open(os.path.join(DEST, "INDICE.html"), "w", encoding="utf-8") as f:
        f.write(pagina)


# ---------------------------------------------------------------- tutto insieme

def main():
    moduli, settimane = carica_programma()
    # si cancellano i file vecchi ma non le cartelle, che su OneDrive restano a volte bloccate
    for sotto in ("slides", "materiale-studenti", "soluzioni-docente"):
        for radice, _, nomi in os.walk(os.path.join(DEST, sotto)):
            for nome in nomi:
                os.remove(os.path.join(radice, nome))
    os.makedirs(os.path.join(DEST, "slides"), exist_ok=True)
    shutil.copytree(os.path.join(QUI, "assets"), os.path.join(DEST, "slides", "_assets"), dirs_exist_ok=True)
    elenco_file = genera_schede()
    conteggi = {}
    mancanti = []
    for sett, mod, spieg, att in settimane:
        for tipo, titolo in (("spiegazione", spieg), ("attivita", att)):
            md = os.path.join(QUI, "contenuti", f"s{sett:02d}-{tipo}.md")
            testo = open(md, encoding="utf-8").read() if os.path.exists(md) else ""
            if not testo:
                mancanti.append(f"s{sett:02d}-{tipo}")
            conteggi[(sett, tipo)] = genera_lezione(sett, mod, moduli[mod], tipo, titolo, testo)
    genera_indice(moduli, settimane, elenco_file, conteggi)
    totale = sum(v[0] for v in conteggi.values())
    print(f"Fatto: {DEST}")
    print(f"{len(conteggi)} lezioni, {totale} slide, {sum(len(v) for v in elenco_file.values())} schede")
    if mancanti:
        print("Ancora da scrivere:", ", ".join(mancanti))


if __name__ == "__main__":
    main()
