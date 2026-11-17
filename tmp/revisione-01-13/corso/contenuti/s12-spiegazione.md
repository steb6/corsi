???
Parte 1 (10 minuti): come si stampa a colori con quattro inchiostri, il retino. Prima fase: analizzare tre ricette CMYK descritte nella scheda. Parte 2 (10 minuti): Pantone, e perché lo stesso colore cambia da uno schermo all'altro e in stampa. Seconda fase: rappresentare le coperture su quattro griglie a penna.

---

# La quadricromia

Le riviste, i manifesti, le scatole si stampano con **quattro inchiostri**:

| C | M | Y | K |
| --- | --- | --- | --- |
| ciano | magenta | giallo | nero (*key*) |

Perché il nero, se C + M + Y fa già quasi nero?

- C + M + Y fa un **marrone scuro**, non un nero pieno
- tre inchiostri uno sopra l'altro **bagnano** troppo la carta
- il testo nero con tre colori verrebbe **sfocato** se i colori non sono perfettamente allineati

???
Il nero si chiama K da "key", la lastra di riferimento su cui si allineano le altre. Molti pensano che K stia per "black": non è così, ma non è un errore grave.

---

# Il retino

<svg class="fig" viewBox="0 0 900 220" width="900" height="220">
<defs><pattern id="rc" width="14" height="14" patternUnits="userSpaceOnUse" patternTransform="rotate(15)"><circle cx="7" cy="7" r="4" fill="#00aeef"/></pattern><pattern id="rm" width="14" height="14" patternUnits="userSpaceOnUse" patternTransform="rotate(75)"><circle cx="7" cy="7" r="5.5" fill="#ec008c" style="mix-blend-mode:multiply"/></pattern><pattern id="ry" width="14" height="14" patternUnits="userSpaceOnUse"><circle cx="7" cy="7" r="3" fill="#fff200"/></pattern></defs>
<rect x="20" y="20" width="180" height="180" fill="#c1446f"/>
<text x="110" y="215" text-anchor="middle" font-size="18" fill="#1d232b">da lontano</text>
<g transform="translate(320 20)"><rect width="180" height="180" fill="#fff"/><rect width="180" height="180" fill="url(#ry)"/><rect width="180" height="180" fill="url(#rc)" style="mix-blend-mode:multiply"/><rect width="180" height="180" fill="url(#rm)" style="mix-blend-mode:multiply"/></g>
<text x="410" y="215" text-anchor="middle" font-size="18" fill="#1d232b">con la lente</text>
</svg>

Si stampano **puntini** piccolissimi, anche sovrapposti: variano le aree coperte da ciascun inchiostro. Da lontano l’occhio integra il risultato.

???
Usare il disegno ingrandito come esempio; nessuna osservazione di oggetti. Le griglie della scheda semplificano la copertura, senza riprodurre forma e orientamento dei punti.

---

# Al lavoro: prima fase

Tre ricette CMYK da confrontare. La somma delle coperture può superare 100% perché gli inchiostri si sovrappongono.

???
Passare alle slide dell'attività (fase 1). Tornare qui dopo circa un'ora.

---

# Le tinte piatte: Pantone

Per alcuni colori la quadricromia **non basta**: un arancio fluorescente, l'oro, l'argento, il colore esatto di un marchio.

Si usa allora un **inchiostro già pronto**, scelto da un catalogo a ventaglio: il più usato si chiama **Pantone**.

- ogni colore ha un **numero** di riferimento: carta e condizioni di stampa influiscono comunque sul risultato
- costa di più: ogni tinta piatta è **un inchiostro in più** nella macchina

???
Esempi da raccontare: le grandi marche di bibite, i colori delle squadre e delle bandiere sono quasi sempre definiti con un numero Pantone.

---

# Perché il colore cambia

Lo stesso file può venire **diverso**:

| Dove | Perché |
| --- | --- |
| due schermi | ogni schermo ha luci RGB un po' diverse |
| schermo e stampa | lo schermo è luce (RGB), la carta è inchiostro (CMYK) |
| due carte | la carta lucida e la carta da giornale assorbono diversamente |

Per questo si **calibra** lo schermo e si usano i **profili colore**: istruzioni che dicono come tradurre i colori da un mezzo all'altro.

???
Caso da discutere: una ricetta identica appare più spenta su carta assorbente. Il codice da solo non basta: occorre considerare supporto e condizioni di stampa.

---

# Al lavoro: seconda fase

Un campione rappresentato con quattro griglie: i segni indicano quantità, le sigle identificano gli inchiostri.

???
Tornare alle slide dell'attività (fase 2).
