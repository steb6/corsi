// Motore delle slide: navigazione, note, lettura, soluzioni nascoste.
(function () {
  "use strict";
  var items = Array.prototype.slice.call(document.querySelectorAll(".item"));
  var vista = document.getElementById("vista");
  var pannelloNote = document.getElementById("note");
  var barra = document.getElementById("barra");
  var conta = document.getElementById("conta");
  var progresso = document.getElementById("progresso");
  var cur = 0;
  var stato = { note: false, lettura: false, soluzioni: false };

  function leggi(chiave) { try { return localStorage.getItem(chiave); } catch (e) { return null; } }
  function scrivi(chiave, v) { try { localStorage.setItem(chiave, v); } catch (e) {} }
  stato.note = leggi("corso-note") === "1";

  // ---- dimensioni ----
  function scala() {
    var s;
    if (stato.lettura) {
      s = Math.min(1000, window.innerWidth - 32) / 1280;
    } else {
      var w = vista.clientWidth, h = vista.clientHeight;
      s = Math.min((w - 16) / 1280, (h - 16) / 720);
    }
    document.documentElement.style.setProperty("--s", Math.max(s, 0.1));
  }

  // Riduce il testo delle slide troppo piene finche' ci stanno.
  var rapporto = [];
  function adatta() {
    rapporto = [];
    items.forEach(function (it, i) {
      var body = it.querySelector(".body");
      var f = 1;
      body.style.fontSize = "";
      function trabocca() {
        if (body.scrollHeight > body.clientHeight + 1) return true;
        var pres = body.querySelectorAll("pre, table, .cols");
        for (var j = 0; j < pres.length; j++) if (pres[j].scrollWidth > pres[j].clientWidth + 1) return true;
        return false;
      }
      while (trabocca() && f > 0.6) { f -= 0.04; body.style.fontSize = f + "em"; }
      if (f < 1) rapporto.push({ slide: i + 1, scala: Math.round(f * 100) / 100, ancora: trabocca() });
    });
    window.rapportoAdattamento = rapporto;
  }

  // ---- navigazione ----
  function visibile(i) {
    return stato.note || stato.soluzioni || !items[i].classList.contains("docente");
  }
  function vai(i, dalHash) {
    if (i < 0) i = 0;
    if (i >= items.length) i = items.length - 1;
    items[cur].classList.remove("cur");
    cur = i;
    items[cur].classList.add("cur");
    conta.textContent = (cur + 1) + " / " + items.length;
    progresso.style.width = ((cur + 1) / items.length * 100) + "%";
    if (stato.note) {
      var n = items[cur].querySelector(".note");
      pannelloNote.innerHTML = "<h3>Note · slide " + (cur + 1) + "</h3>" +
        (n && n.innerHTML.trim() ? n.innerHTML : '<p class="vuote">Nessuna nota per questa slide.</p>');
      pannelloNote.scrollTop = 0;
    }
    if (!dalHash) history.replaceState(null, "", "#" + (cur + 1));
  }
  function avanti() {
    for (var i = cur + 1; i < items.length; i++) if (visibile(i)) return vai(i);
  }
  function indietro() {
    for (var i = cur - 1; i >= 0; i--) if (visibile(i)) return vai(i);
  }
  function primaVisibile(da, passo) {
    for (var i = da; i >= 0 && i < items.length; i += passo) if (visibile(i)) return i;
    return da;
  }

  // ---- modalita' ----
  function aggiorna() {
    document.body.classList.toggle("con-note", stato.note && !stato.lettura);
    document.body.classList.toggle("lettura", stato.lettura);
    items.forEach(function (it) {
      it.classList.toggle("nascosta-docente", it.classList.contains("docente") && !visibile(items.indexOf(it)));
    });
    document.getElementById("b-note").classList.toggle("attivo", stato.note);
    document.getElementById("b-lettura").classList.toggle("attivo", stato.lettura);
    document.getElementById("b-soluzioni").classList.toggle("attivo", stato.soluzioni);
    scala();
    if (!visibile(cur)) cur = primaVisibile(cur, -1);
    vai(cur);
    if (stato.lettura) items[cur].scrollIntoView();
  }
  function commuta(chiave) {
    stato[chiave] = !stato[chiave];
    if (chiave === "note") scrivi("corso-note", stato.note ? "1" : "0");
    aggiorna();
  }
  function schermoIntero() {
    if (document.fullscreenElement) document.exitFullscreen();
    else if (document.documentElement.requestFullscreen) document.documentElement.requestFullscreen();
  }

  // ---- copia del codice ----
  function copia(testo, bottone) {
    function fatto() { bottone.textContent = "Copiato"; setTimeout(function () { bottone.textContent = "Copia"; }, 1500); }
    function riserva() {
      var t = document.createElement("textarea");
      t.value = testo; document.body.appendChild(t); t.select();
      try { document.execCommand("copy"); fatto(); } catch (e) {}
      document.body.removeChild(t);
    }
    if (navigator.clipboard && window.isSecureContext) navigator.clipboard.writeText(testo).then(fatto, riserva);
    else riserva();
  }
  document.querySelectorAll(".slide pre:not(.shell)").forEach(function (pre) {
    var b = document.createElement("button");
    b.className = "copia"; b.type = "button"; b.textContent = "Copia";
    b.addEventListener("click", function (e) { e.stopPropagation(); copia(pre.querySelector("code").textContent, b); });
    pre.appendChild(b);
  });

  // ---- eventi ----
  document.addEventListener("keydown", function (e) {
    if (e.ctrlKey || e.altKey || e.metaKey) return;
    var k = e.key;
    if (stato.lettura && ["ArrowDown", "ArrowUp", "PageDown", "PageUp", " ", "Home", "End"].indexOf(k) >= 0) return;
    if (k === "ArrowRight" || k === "ArrowDown" || k === "PageDown" || k === " " || k === "Enter") { e.preventDefault(); avanti(); }
    else if (k === "ArrowLeft" || k === "ArrowUp" || k === "PageUp" || k === "Backspace") { e.preventDefault(); indietro(); }
    else if (k === "Home") vai(primaVisibile(0, 1));
    else if (k === "End") vai(primaVisibile(items.length - 1, -1));
    else if (k === "f" || k === "F") schermoIntero();
    else if (k === "n" || k === "N") commuta("note");
    else if (k === "l" || k === "L") commuta("lettura");
    else if (k === "s" || k === "S") commuta("soluzioni");
    else if (k === "Escape" && (stato.lettura || stato.note)) { stato.lettura = false; stato.note = false; scrivi("corso-note", "0"); aggiorna(); }
  });
  vista.addEventListener("click", function (e) {
    if (stato.lettura) return;
    if (e.target.closest("a, button, pre, input, textarea, table")) return;
    if (String(window.getSelection()).length) return;
    var r = vista.getBoundingClientRect();
    if (e.clientX - r.left < r.width * 0.25) indietro(); else avanti();
  });
  var tx = null;
  vista.addEventListener("touchstart", function (e) { tx = e.touches[0].clientX; }, { passive: true });
  vista.addEventListener("touchend", function (e) {
    if (tx === null || stato.lettura) return;
    var dx = e.changedTouches[0].clientX - tx; tx = null;
    if (dx < -50) avanti(); else if (dx > 50) indietro();
  });
  document.getElementById("b-avanti").addEventListener("click", avanti);
  document.getElementById("b-indietro").addEventListener("click", indietro);
  document.getElementById("b-note").addEventListener("click", function () { commuta("note"); });
  document.getElementById("b-lettura").addEventListener("click", function () { commuta("lettura"); });
  document.getElementById("b-soluzioni").addEventListener("click", function () { commuta("soluzioni"); });
  document.getElementById("b-schermo").addEventListener("click", schermoIntero);

  // la barra sparisce quando il mouse sta fermo durante la presentazione
  var timer = null;
  function mostraBarra() {
    barra.classList.remove("nascosta");
    clearTimeout(timer);
    timer = setTimeout(function () { if (!stato.lettura && !stato.note) barra.classList.add("nascosta"); }, 2500);
  }
  document.addEventListener("mousemove", mostraBarra);
  window.addEventListener("resize", scala);
  window.addEventListener("hashchange", function () {
    var n = parseInt(location.hash.slice(1), 10);
    if (n >= 1 && n <= items.length && n - 1 !== cur) vai(n - 1, true);
  });

  // ---- avvio ----
  var iniziale = parseInt(location.hash.slice(1), 10);
  cur = (iniziale >= 1 && iniziale <= items.length) ? iniziale - 1 : 0;
  items[cur].classList.add("cur");
  scala();
  adatta();
  if (location.search.indexOf("lettura") >= 0) stato.lettura = true;
  aggiorna();
  mostraBarra();
})();
