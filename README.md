# Corsi

Sito con i corsi di `FondamentiElettronicaElettrotecnica`, `TecnologieApplicateSeconda` e `Python3Superiore`, protetto da password.

GitHub Pages è pubblico anche con un repo privato, quindi la protezione è la cifratura: ogni pagina e ogni file in `docs/` è cifrato con AES-256-GCM, con una chiave derivata dalla password (PBKDF2, 600.000 iterazioni). Il browser decifra dopo aver ricevuto la password.

## Aggiornare il sito

```
.venv/bin/python pubblica.py -m "Cosa è cambiato"
```

Scarica l'ultima versione dei tre repo da GitHub (quindi le modifiche vanno prima pushate lì), rigenera i corsi, cifra e pubblica.

## Cambiare la password

```
.venv/bin/python pubblica.py --password "nuova-password" -m "Cambia la password"
```

La password sta in `~/.config/corsi-sito/password`, mai nel repo. Dopo il cambio, chi aveva "Ricordami" la deve inserire di nuovo. Vale per le versioni nuove delle pagine: chi aveva già scaricato quelle vecchie le può ancora leggere con la vecchia password, e la cronologia del repo le conserva.

## Installazione su una macchina nuova

```
python3 -m venv --without-pip .venv
python3 -m pip install --target "$(.venv/bin/python -c 'import site;print(site.getsitepackages()[0])')" pygame-ce cryptography
```

Serve `gh` autenticato. Python deve avere `pygame-ce` nel suo ambiente perché il corso di Python genera le schermate dei giochi.
