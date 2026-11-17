# Scienze e tecnologie applicate · seconda

Un anno di Scienze e tecnologie applicate per la seconda dell'istituto tecnico grafico, 25 settimane da 3 ore. Ogni settimana ha due spiegazioni brevi (circa 10 minuti l'una), ciascuna seguita da un'attività pratica su carta. Non servono computer né telefoni. Il libro di riferimento è "Immaginando" (Hoepli).

## I moduli

| Settimane | Modulo | Verifica pratica |
| --- | --- | --- |
| 1-5 | Comunicazione e pubblicità | |
| 6-8 | Percezione e composizione | settimana 8 (moduli 1 e 2) |
| 9-13 | Luce e colore | settimana 13 |
| 14-17 | Il lettering | settimana 17 |
| 18-21 | Immagine e ottica | settimana 21 |
| 22-25 | Stampa e progetto finale | il manifesto A3, presentato in una mostra in classe |

## Cosa c'è

| Cartella | Contenuto |
| --- | --- |
| `Corso Tecnologie applicate seconda/` | il corso pronto da usare: si apre `INDICE.html` |
| `corso/` | i sorgenti e il generatore, per modificare il corso |

### Corso Tecnologie applicate seconda/

- `INDICE.html`: la tabella delle 25 settimane, con i link alle slide e alle schede
- `slides/`: due lezioni per settimana (spiegazione e attività), con le note per il docente
- `materiale-studenti/`: le schede da stampare in A4, una cartella per settimana
- `soluzioni-docente/`: soluzioni delle verifiche e griglia di valutazione

Nelle slide: frecce o spazio per andare avanti, `F` schermo intero, `N` note, `S` slide per il docente (soluzioni e criteri di voto), `L` tutte le slide in colonna. Dal browser si possono stampare sia le slide (con le note) sia le schede.

### corso/

- `programma.py`: il programma settimana per settimana
- `contenuti/sNN-spiegazione.md`, `contenuti/sNN-attivita.md`: il testo delle 50 lezioni. Il formato è descritto in cima a `genera.py`
- `schede/settimana-NN/`: le schede in `.md`. Quelle che iniziano con `docente` o `soluzione` finiscono solo nel materiale del docente
- `assets/`: stile e motore delle slide (HTML, funzionano offline)
- `genera.py`: costruisce il corso completo

## Rigenerare il corso

Basta Python 3, senza librerie aggiuntive:

```
python corso\genera.py
```

Ricrea la cartella `Corso Tecnologie applicate seconda/` accanto a `corso/`.
