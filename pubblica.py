#!/usr/bin/env python3
"""Rigenera i corsi dai repo su GitHub, li cifra e pubblica il sito.

Uso: .venv/bin/python pubblica.py [--password NUOVA] [--no-push] [-m MESSAGGIO]
La password sta in ~/.config/corsi-sito/password, mai nel repo.
"""
import argparse
import base64
import hashlib
import hmac
import html
import io
import os
import re
import secrets
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

QUI = Path(__file__).resolve().parent
SORGENTI = QUI / ".cache" / "sorgenti"
USCITA = QUI / "docs"
FILE_PASSWORD = Path.home() / ".config" / "corsi-sito" / "password"
FILE_SALE = QUI / "sale.txt"
ITERAZIONI = 600_000

CORSI = [
    {"slug": "elettronica", "repo": "FondamentiElettronicaElettrotecnica",
     "cartella": "Corso Fondamenti di elettronica ed elettrotecnica",
     "titolo": "Fondamenti di elettronica ed elettrotecnica",
     "classe": "Prima, indirizzo tecnico tecnologico", "extra": {}},
    {"slug": "tecnologie", "repo": "TecnologieApplicateSeconda",
     "cartella": "Corso Tecnologie applicate seconda",
     "titolo": "Scienze e tecnologie applicate",
     "classe": "Seconda, grafica e comunicazione", "extra": {}},
    {"slug": "python", "repo": "Python3Superiore",
     "cartella": "Corso Python terza",
     "titolo": "Python",
     "classe": "Terza superiore",
     "extra": {"correttore-voti": "Correttore dei voti", "kit": "Script del kit Thonny"}},
]

PAROLE = """lavagna quaderno circuito resistore diodo pila lampada ponte banco matita
righello gesso aula campana compasso squadra libro zaino finestra corrente
tensione bobina filo morsetto saldatore tastiera schermo stampante colore carta
inchiostro manifesto lettera pennello cartella gomma foglio tabella grafico formula""".split()


def password():
    FILE_PASSWORD.parent.mkdir(parents=True, exist_ok=True)
    if not FILE_PASSWORD.exists():
        p = "-".join(secrets.choice(PAROLE) for _ in range(4)) + "-" + str(secrets.randbelow(9000) + 1000)
        scrivi_password(p)
    return FILE_PASSWORD.read_text(encoding="utf-8").strip()


def scrivi_password(p):
    FILE_PASSWORD.parent.mkdir(parents=True, exist_ok=True)
    FILE_PASSWORD.write_text(p + "\n", encoding="utf-8")
    FILE_PASSWORD.chmod(0o600)


def sale():
    if not FILE_SALE.exists():
        FILE_SALE.write_text(secrets.token_hex(16) + "\n", encoding="utf-8")
    return FILE_SALE.read_text(encoding="utf-8").strip()


def deriva(p, s):
    return PBKDF2HMAC(hashes.SHA256(), 32, bytes.fromhex(s), ITERAZIONI).derive(p.encode("utf-8"))


def cifra(chiave, percorso, dati):
    # nonce legato a percorso e contenuto: un file non cambiato resta identico nel repo
    nonce = hmac.new(chiave, percorso.encode("utf-8") + b"\0" + dati, hashlib.sha256).digest()[:12]
    return nonce + AESGCM(chiave).encrypt(nonce, dati, None)


def prepara_sorgente(corso):
    dest = SORGENTI / corso["repo"]
    if dest.exists():
        subprocess.run(["git", "-C", str(dest), "pull", "-q", "--ff-only"], check=True)
    else:
        dest.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["gh", "repo", "clone", f"steb6/{corso['repo']}", str(dest), "--", "-q"], check=True)
    generato = dest / corso["cartella"]
    shutil.rmtree(generato, ignore_errors=True)
    r = subprocess.run([sys.executable, "corso/genera.py"], cwd=dest, capture_output=True, text=True)
    if r.returncode or not (generato / "INDICE.html").exists():
        sys.exit(f"genera.py di {corso['repo']} non riuscito:\n{r.stdout}\n{r.stderr}")
    return dest, generato


def incorpora_risorse(testo, cartella):
    def css(m):
        return "<style>" + (cartella / m.group(1)).read_text(encoding="utf-8") + "</style>"

    def js(m):
        codice = (cartella / m.group(1)).read_text(encoding="utf-8").replace("</script", "<\\/script")
        return "<script>" + codice + "</script>"

    testo = re.sub(r'<link rel="stylesheet" href="([^"]+\.css)">', css, testo)
    return re.sub(r'<script src="([^"]+\.js)"></script>', js, testo)


def involucro(dati_cifrati, profondita):
    su = "../" * profondita
    return f"""<!doctype html>
<html lang="it"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>Corsi · accesso</title>
<link rel="stylesheet" href="{su}porta.css">
</head><body>
<form id="accesso" hidden>
<h1>Corsi</h1>
<p>Materiale riservato ai docenti.</p>
<label>Password <input type="password" autocomplete="current-password" required></label>
<label class="ricorda"><input type="checkbox"> Ricordami su questo computer</label>
<p class="nota">Non spuntare sui computer della scuola: chiunque vedrebbe anche le soluzioni.</p>
<button>Entra</button>
<p id="errore" role="alert"></p>
</form>
<script id="dati" type="text/plain">{base64.b64encode(dati_cifrati).decode()}</script>
<script src="{su}porta.js"></script>
<noscript>Per aprire il sito serve JavaScript.</noscript>
</body></html>
"""


def pubblica_pagina(chiave, rel, testo):
    dest = USCITA / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(involucro(cifra(chiave, rel, testo.encode("utf-8")), rel.count("/")), encoding="utf-8")


def pubblica_file(chiave, rel, dati):
    dest = USCITA / (rel + ".enc")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(cifra(chiave, rel, dati))


def comprimi(radice, nome_in_zip):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(radice.rglob("*")):
            if f.is_file() and "__pycache__" not in f.parts:
                # data fissa: lo zip cambia solo se cambia il contenuto
                info = zipfile.ZipInfo(str(Path(nome_in_zip) / f.relative_to(radice)), (2020, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                z.writestr(info, f.read_bytes())
    return buf.getvalue()


def pubblica_corso(chiave, corso, dest, generato):
    slug = corso["slug"]
    for f in sorted(generato.rglob("*")):
        if not f.is_file():
            continue
        rel = f.relative_to(generato).as_posix()
        if "_assets" in f.parts:
            continue
        if f.suffix == ".html":
            testo = incorpora_risorse(f.read_text(encoding="utf-8"), f.parent)
            if rel == "INDICE.html":
                testo = re.sub(r"(<body[^>]*>)", r'\1<a href="../index.html" style="display:inline-block;margin:12px 16px;font:15px sans-serif">← Tutti i corsi</a>', testo, count=1)
            pubblica_pagina(chiave, f"{slug}/{rel}", testo)
        else:
            pubblica_file(chiave, f"{slug}/{rel}", f.read_bytes())
    pubblica_file(chiave, f"{slug}/corso-{slug}.zip", comprimi(generato, f"corso-{slug}"))
    for cartella in corso["extra"]:
        pubblica_file(chiave, f"{slug}/{cartella}.zip", comprimi(dest / cartella, cartella))


def pagina_iniziale():
    schede = ""
    for c in CORSI:
        extra = "".join(f'<a href="{c["slug"]}/{k}.zip">{html.escape(v)} (zip)</a>' for k, v in c["extra"].items())
        schede += f"""<section><h2>{html.escape(c["titolo"])}</h2><p>{html.escape(c["classe"])}</p>
<div class="azioni"><a class="primario" href="{c["slug"]}/INDICE.html">Apri il corso</a>
<a href="{c["slug"]}/corso-{c["slug"]}.zip">Scarica tutto (zip)</a>{extra}</div></section>\n"""
    return f"""<!doctype html>
<html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow"><title>Corsi</title><link rel="stylesheet" href="porta.css"></head>
<body class="casa"><header><h1>Corsi</h1><a href="#" data-esci>Esci</a></header>
<p>25 settimane per ogni corso: slide, schede da stampare, soluzioni per il docente.</p>
{schede}</body></html>
"""


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--password")
    a.add_argument("--no-push", action="store_true")
    a.add_argument("-m", dest="messaggio", default="Aggiorna il sito")
    o = a.parse_args()
    if o.password:
        scrivi_password(o.password)
    s = sale()
    chiave = deriva(password(), s)

    prodotti = [(c, *prepara_sorgente(c)) for c in CORSI]
    shutil.rmtree(USCITA, ignore_errors=True)
    USCITA.mkdir()
    for c, dest, generato in prodotti:
        pubblica_corso(chiave, c, dest, generato)

    testo = pagina_iniziale()
    pubblica_pagina(chiave, "index.html", testo)
    (USCITA / "porta.js").write_text(
        (QUI / "porta.js").read_text(encoding="utf-8").replace("%%SALE%%", s).replace("%%ITER%%", str(ITERAZIONI)),
        encoding="utf-8")
    shutil.copy(QUI / "porta.css", USCITA / "porta.css")
    (USCITA / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")
    (USCITA / ".nojekyll").write_text("", encoding="utf-8")
    print("pagine:", sum(1 for _ in USCITA.rglob("*.html")), "· file cifrati:", sum(1 for _ in USCITA.rglob("*.enc")))

    if o.no_push:
        return
    subprocess.run(["git", "add", "-A"], cwd=QUI, check=True)
    if subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=QUI).returncode == 0:
        print("Niente da pubblicare.")
        return
    subprocess.run(["git", "commit", "-q", "-m", o.messaggio], cwd=QUI, check=True)
    subprocess.run(["git", "push", "-q", "origin", "main"], cwd=QUI, check=True)
    print("Pubblicato.")


if __name__ == "__main__":
    main()
