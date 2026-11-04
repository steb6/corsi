// Apre una pagina cifrata: chiede la password, decifra e mostra il contenuto.
(function () {
  var SALE = "43282287d1bcbd512203c33a0e414d2d", ITERAZIONI = 600000, NOME = "corsi.chiave";
  var dati = document.getElementById("dati").textContent.trim();

  function leggi() {
    try { return sessionStorage.getItem(NOME) || localStorage.getItem(NOME); } catch (e) { return null; }
  }
  function byte(hex) {
    var u = new Uint8Array(hex.length / 2);
    for (var i = 0; i < u.length; i++) u[i] = parseInt(hex.substr(i * 2, 2), 16);
    return u;
  }
  function hex(buf) {
    return Array.from(new Uint8Array(buf)).map(function (b) { return ("0" + b.toString(16)).slice(-2); }).join("");
  }
  function b64(s) {
    var r = atob(s), u = new Uint8Array(r.length);
    for (var i = 0; i < r.length; i++) u[i] = r.charCodeAt(i);
    return u;
  }
  function decifra(chiaveHex, tutto) {
    return crypto.subtle.importKey("raw", byte(chiaveHex), "AES-GCM", false, ["decrypt"]).then(function (k) {
      return crypto.subtle.decrypt({ name: "AES-GCM", iv: tutto.slice(0, 12) }, k, tutto.slice(12));
    });
  }
  function deriva(password) {
    return crypto.subtle.importKey("raw", new TextEncoder().encode(password), "PBKDF2", false, ["deriveBits"]).then(function (k) {
      return crypto.subtle.deriveBits({ name: "PBKDF2", hash: "SHA-256", salt: byte(SALE), iterations: ITERAZIONI }, k, 256);
    }).then(hex);
  }
  function scarica(url, nome, chiave) {
    fetch(url + ".enc").then(function (r) {
      if (!r.ok) throw new Error(r.status);
      return r.arrayBuffer();
    }).then(function (b) {
      return decifra(chiave, new Uint8Array(b));
    }).then(function (chiaro) {
      var a = document.createElement("a");
      a.href = URL.createObjectURL(new Blob([chiaro]));
      a.download = nome;
      document.body.appendChild(a);
      a.click();
      a.remove();
    }).catch(function () { alert("Download non riuscito. Riprova."); });
  }
  function mostra(chiaro, chiave) {
    var html = new TextDecoder().decode(chiaro);
    document.open();
    document.write(html);
    document.close();
    // i file che non sono pagine (.py, .txt, .wav, .zip) sono cifrati a parte
    document.addEventListener("click", function (e) {
      var a = e.target.closest && e.target.closest("a[href]");
      if (!a || a.hasAttribute("download")) return;
      if (a.hasAttribute("data-esci")) {
        e.preventDefault();
        try { sessionStorage.removeItem(NOME); localStorage.removeItem(NOME); } catch (x) {}
        location.reload();
        return;
      }
      var p = new URL(a.href, location.href);
      if (p.origin !== location.origin || /(\.html|\/)$/.test(p.pathname)) return;
      e.preventDefault();
      scarica(p.pathname, decodeURIComponent(p.pathname.split("/").pop()), chiave);
    });
  }
  function form(errore) {
    var f = document.getElementById("accesso");
    f.hidden = false;
    var campo = f.querySelector("input[type=password]"), msg = document.getElementById("errore");
    msg.textContent = errore || "";
    campo.focus();
    f.onsubmit = function (e) {
      e.preventDefault();
      var btn = f.querySelector("button");
      btn.disabled = true;
      msg.textContent = "";
      deriva(campo.value).then(function (chiave) {
        return decifra(chiave, b64(dati)).then(function (chiaro) {
          try {
            if (f.querySelector("input[type=checkbox]").checked) localStorage.setItem(NOME, chiave);
            else sessionStorage.setItem(NOME, chiave);
          } catch (x) {}
          mostra(chiaro, chiave);
        });
      }).catch(function () {
        btn.disabled = false;
        msg.textContent = "Password sbagliata.";
        campo.select();
      });
    };
  }

  if (!window.crypto || !crypto.subtle) { form("Questo browser non può aprire il sito: aggiornalo."); return; }
  var salvata = leggi();
  if (!salvata) { form(); return; }
  decifra(salvata, b64(dati)).then(function (chiaro) { mostra(chiaro, salvata); }).catch(function () {
    try { sessionStorage.removeItem(NOME); localStorage.removeItem(NOME); } catch (x) {}
    form();
  });
})();
