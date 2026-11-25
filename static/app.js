/* Teman Mama - small, dependency-free scripts for the tools.
   Everything a visitor types is kept in localStorage on their own device only. */
(function () {
  "use strict";
  var TM = window.TM || {};
  var S = TM.s || {};
  var LANG = TM.lang || "en";
  var LOCALE = LANG === "ms" ? "ms-MY" : "en-MY";
  var DAY = 864e5;

  // ---------- helpers
  function $(sel, el) { return (el || document).querySelector(sel); }
  function $$(sel, el) { return Array.prototype.slice.call((el || document).querySelectorAll(sel)); }
  function get(key, dflt) {
    try { var v = localStorage.getItem(key); return v === null ? dflt : JSON.parse(v); } catch (e) { return dflt; }
  }
  function set(key, val) { try { localStorage.setItem(key, JSON.stringify(val)); } catch (e) { /* private mode */ } }
  function fill(str, map) { return String(str).replace(/\{(\w+)\}/g, function (_, k) { return map[k] !== undefined ? map[k] : ""; }); }
  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; });
  }
  function parseDate(v) {
    var m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(v || "");
    return m ? new Date(Date.UTC(+m[1], +m[2] - 1, +m[3])) : null;
  }
  function iso(d) { return d.toISOString().slice(0, 10); }
  function today() { var n = new Date(); return new Date(Date.UTC(n.getFullYear(), n.getMonth(), n.getDate())); }
  function addDays(d, n) { return new Date(d.getTime() + n * DAY); }
  function diffDays(a, b) { return Math.round((b - a) / DAY); }
  function fmt(d) { return d.toLocaleDateString(LOCALE, { day: "numeric", month: "short", year: "numeric", timeZone: "UTC" }); }
  function rm(n) { return "RM" + Number(n).toLocaleString("en-MY", { minimumFractionDigits: 2, maximumFractionDigits: 2 }); }
  function slug(s) { return String(s).toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, ""); }

  try { localStorage.setItem("tm_lang", JSON.stringify(LANG).replace(/"/g, "")); } catch (e) { /* ignore */ }

  // ---------- due date (home)
  function dueTool() {
    var box = $("#due-tool"); if (!box) return;
    var input = $("#due-input"), out = $("#due-result"), label = $("#due-label");
    var mode = "due";
    var btns = $$(".seg button", box);
    btns.forEach(function (b) {
      b.addEventListener("click", function () {
        mode = b.getAttribute("data-mode");
        btns.forEach(function (o) { o.setAttribute("aria-pressed", o === b ? "true" : "false"); });
        label.textContent = label.getAttribute("data-" + mode);
        input.value = "";
        out.innerHTML = "";
      });
    });
    function show(due) {
      var left = diffDays(today(), due);
      var ga = 280 - left;
      if (ga < 0 || ga > 44 * 7) { out.innerHTML = '<p class="err">' + esc(S.badDate) + "</p>"; return; }
      if (left < 0) {
        out.innerHTML = '<div class="result"><p>' + esc(S.passed) + '</p><a class="btn" href="pantang.html">' + esc(S.openPantang) + "</a></div>";
        return;
      }
      var w = Math.floor(ga / 7), d = ga % 7;
      var html = '<div class="result"><p class="big">' + esc(fill(S.weeksDays, { w: w, d: d })) + "</p>";
      if (w < 4) {
        html += "<p>" + esc(S.early) + "</p>";
      } else {
        var pw = Math.min(w, 40), info = (TM.weeks || {})[pw];
        var tri = w <= 13 ? 1 : (w <= 27 ? 2 : 3);
        html += '<p class="muted">' + esc(fill(S.tri, { t: tri })) + "</p>";
        if (info) html += "<p>" + info[0] + " " + esc(fill(S.sizeOf, { size: info[1] })) + "</p>";
        html += "<p>" + esc(fill(S.daysToGo, { n: left, date: fmt(due) })) + "</p>";
        html += '<a class="btn" href="weeks/' + pw + '.html">' + esc(fill(S.readWeek, { w: pw })) + " →</a>";
      }
      out.innerHTML = html + "</div>";
    }
    $("#due-go").addEventListener("click", function () {
      var d = parseDate(input.value);
      if (!d) { out.innerHTML = '<p class="err">' + esc(S.pickDate) + "</p>"; return; }
      var due = mode === "lmp" ? addDays(d, 280) : d;
      set("tm_due", iso(due));
      show(due);
    });
    var saved = parseDate(get("tm_due", ""));
    if (saved) { input.value = iso(saved); show(saved); }
  }

  // ---------- current week markers
  function weekMarkers() {
    var due = parseDate(get("tm_due", ""));
    if (!due) return;
    var w = Math.floor((280 - diffDays(today(), due)) / 7);
    if (TM.week && TM.week === w) { var p = $("#you-here"); if (p) p.hidden = false; }
    var li = $('.week-list li[data-week="' + w + '"]');
    if (li) { li.classList.add("current"); li.querySelector(".wk-n").insertAdjacentHTML("beforeend", ' <span class="pill">' + esc(S.youAreHere) + "</span>"); }
  }

  // ---------- pantang planner
  function pantang() {
    var box = $("#pantang-tool"); if (!box) return;
    var trad = $("#p-trad"), daysWrap = $("#p-days-wrap"), days = $("#p-days"), date = $("#p-date"), out = $("#p-result");
    var st = get("tm_pantang", {});
    if (st.trad) trad.value = st.trad;
    if (st.days) days.value = st.days;
    if (st.kind) $$('input[name="p-kind"]').forEach(function (r) { r.checked = r.value === st.kind; });
    date.value = st.date || get("tm_due", "") || "";
    function sync() { daysWrap.hidden = trad.value !== "custom"; }
    trad.addEventListener("change", sync); sync();

    function run() {
      var d = parseDate(date.value);
      if (!d) { out.innerHTML = '<p class="err">' + esc(S.pickDate) + "</p>"; return; }
      var kind = ($('input[name="p-kind"]:checked') || {}).value || "due";
      var n = trad.value === "custom" ? Math.max(7, Math.min(120, parseInt(days.value, 10) || 40)) : parseInt(trad.value, 10);
      set("tm_pantang", { trad: trad.value, days: days.value, kind: kind, date: date.value });
      var t = today();
      var before = [
        [-168, S.pShortlist], [-140, S.pBook], [-42, S.pBuy], [-28, S.pBag]
      ];
      var after = [
        [0, (kind === "birth" ? S.pBirth : S.pDue) + " - " + S.pVacc],
        [3, S.pMilk],
        [6, S.pPat],
        [41, S.pCheck],
        [n - 1, fill(S.pEnd, { n: n })],
        [59, S.pReg],
        [97, S.pMat]
      ].sort(function (a, b) { return a[0] - b[0]; });
      var nextMarked = false;
      function list(items, title) {
        var h = "<h3>" + esc(title) + '</h3><ol class="timeline">';
        items.forEach(function (it) {
          var day = addDays(d, it[0]);
          var cls = day < t ? "past" : "";
          if (!cls && !nextMarked) { cls = "next"; nextMarked = true; }
          var when = fmt(day) + (iso(day) === iso(t) ? " · " + S.pToday : "");
          h += '<li class="' + cls + '"><span class="when">' + esc(when) + "</span>" + esc(it[1]) + "</li>";
        });
        return h + "</ol>";
      }
      var html = kind === "due" ? list(before, S.pBefore) : "";
      html += list(after, S.pAfter);
      if (kind === "due") html += '<p class="hint">' + esc(S.pNoteDue) + "</p>";
      out.innerHTML = html;
    }
    $("#p-go").addEventListener("click", run);
    if (st.date) run();
  }

  // ---------- confinement quotes
  function quotes() {
    var box = $("#quote-tool"); if (!box) return;
    var cards = $$(".quote", box), out = $("#q-result");
    var saved = get("tm_quotes", []);
    cards.forEach(function (c, i) {
      var q = saved[i] || {};
      ["name", "price", "days", "ratio"].forEach(function (k) { if (q[k] !== undefined && q[k] !== "") c.querySelector('[name="' + k + '"]').value = q[k]; });
      $$('input[name="inc"]', c).forEach(function (cb) { cb.checked = (q.inc || []).indexOf(cb.value) >= 0; });
    });
    // Drop-down of typical packages + real centres; picking one fills in the card (still editable).
    var presets = {};
    function showNote(c, p) {
      var note = $(".preset-note", c);
      if (!p) { note.hidden = true; return; }
      if (p.kind === "typical") {
        note.textContent = (LANG === "ms" ? p.note_ms : p.note_en) + " " + S.preTypicalNote;
      } else {
        var price = rm(p.price_from_rm).replace(".00", "") + (p.price_to_rm ? " - " + rm(p.price_to_rm).replace(".00", "") : "");
        var cav = p["caveat_" + LANG] || p.caveat_en || "";
        note.innerHTML = esc(fill(p.days_unstated ? S.preCentreNoteNoDays : S.preCentreNote, { d: p.days, price: price, date: fmt(parseDate(p.checked)) })) +
          (cav ? " <strong>" + esc(cav) + "</strong>" : "") +
          ' <a href="' + esc(p.source_url) + '" target="_blank" rel="noopener">' + esc(S.preSource) + " ↗</a>";
      }
      note.hidden = false;
    }
    function applyPreset(c, p) {
      c.querySelector('[name="name"]').value = p.kind === "typical" ? (LANG === "ms" ? p.ms : p.en) : p.name;
      c.querySelector('[name="price"]').value = p.kind === "typical" ? p.price : p.price_from_rm;
      c.querySelector('[name="days"]').value = p.days || 28;
      var ratio = p.kind === "typical" ? p.ratio : p.babies_per_nurse;
      c.querySelector('[name="ratio"]').value = ratio || "";
      var inc = (p.kind === "typical" ? p.inc : p.includes) || {};
      $$('input[name="inc"]', c).forEach(function (cb) { cb.checked = inc[cb.value] === true; });
      showNote(c, p);
    }
    fetch(TM.root + "data/confinement.json").then(function (r) { return r.ok ? r.json() : null; }).then(function (d) {
      if (!d) return;
      var html = '<optgroup label="' + esc(S.preTypical) + '">' + d.typical.map(function (t) {
        presets[t.id] = Object.assign({ kind: "typical" }, t);
        return '<option value="' + esc(t.id) + '">' + esc(LANG === "ms" ? t.ms : t.en) + "</option>";
      }).join("") + "</optgroup>";
      var byState = {};
      (d.centres || []).forEach(function (c, i) {
        var id = "c" + i;
        presets[id] = Object.assign({ kind: "centre" }, c);
        (byState[c.state] = byState[c.state] || []).push(
          '<option value="' + id + '">' + esc(c.name + " (" + c.area + ") - " + S.qFrom + " " + rm(c.price_from_rm).replace(".00", "")) + "</option>");
      });
      Object.keys(byState).sort().forEach(function (st) {
        html += '<optgroup label="' + esc(fill(S.preCentres, { state: st })) + '">' + byState[st].join("") + "</optgroup>";
      });
      cards.forEach(function (c, i) {
        var sel = c.querySelector('[name="preset"]');
        sel.insertAdjacentHTML("beforeend", html);
        var q = saved[i] || {};
        if (q.preset && presets[q.preset]) { sel.value = q.preset; showNote(c, presets[q.preset]); }
        sel.addEventListener("change", function () {
          if (presets[sel.value]) applyPreset(c, presets[sel.value]); else showNote(c, null);
          render();
        });
      });
    }).catch(function () { /* drop-down is optional */ });
    function read() {
      return cards.map(function (c) {
        return {
          preset: c.querySelector('[name="preset"]').value,
          name: c.querySelector('[name="name"]').value.trim(),
          price: c.querySelector('[name="price"]').value,
          days: c.querySelector('[name="days"]').value,
          ratio: c.querySelector('[name="ratio"]').value,
          inc: $$('input[name="inc"]:checked', c).map(function (cb) { return cb.value; })
        };
      });
    }
    function render() {
      var qs = read();
      set("tm_quotes", qs);
      var rows = [];
      qs.forEach(function (q, i) {
        var p = parseFloat(q.price), d = parseInt(q.days, 10);
        if (p > 0 && d > 0) rows.push({ i: i, name: q.name || fill(S.qQuote, { n: i + 1 }), price: p, days: d, per: p / d, ratio: parseInt(q.ratio, 10), inc: q.inc.length });
      });
      if (!rows.length) { out.innerHTML = '<p class="hint">' + esc(S.qNone) + "</p>"; return; }
      rows.sort(function (a, b) { return a.per - b.per; });
      var H = S.qHead;
      var h = '<div class="table-wrap"><table><thead><tr><th>' + esc(H[0]) + '</th><th class="num">' + esc(H[1]) +
        '</th><th class="num hide-sm">' + esc(H[2]) + '</th><th class="num">' + esc(H[3]) + '</th><th class="num hide-sm">' + esc(H[4]) +
        '</th><th class="num hide-sm">' + esc(H[5]) + "</th></tr></thead><tbody>";
      rows.forEach(function (r, k) {
        var best = k === 0 && rows.length > 1;
        h += '<tr class="' + (best ? "best" : "") + '"><td>' + esc(r.name) +
          (best ? '<span class="flag" style="color:var(--accent)">' + esc(S.qLowest) + "</span>" : "") +
          (r.ratio > 4 ? '<span class="flag">⚠ ' + esc(S.qWarn) + "</span>" : "") +
          '</td><td class="num">' + rm(r.price) + '</td><td class="num hide-sm">' + r.days + '</td><td class="num"><strong>' + rm(r.per) +
          '</strong></td><td class="num hide-sm">' + (r.ratio > 0 ? "1 : " + r.ratio : "-") + '</td><td class="num hide-sm">' + r.inc + "/5</td></tr>";
      });
      out.innerHTML = h + "</tbody></table></div>";
    }
    box.addEventListener("input", render);
    box.addEventListener("change", render);
    $("#q-clear").addEventListener("click", function () {
      cards.forEach(function (c) {
        $$('input[type="text"], input[name="price"], input[name="ratio"]', c).forEach(function (i) { i.value = ""; });
        c.querySelector('[name="days"]').value = 28;
        c.querySelector('[name="preset"]').value = "";
        showNote(c, null);
        $$('input[type="checkbox"]', c).forEach(function (cb) { cb.checked = false; });
      });
      render();
    });
    render();
  }

  // ---------- hospital bag
  function bag() {
    var boxes = $$("input[data-key]"); if (!boxes.length) return;
    var st = get("tm_bag", {}), prog = $("#bag-progress");
    function upd() {
      var n = boxes.filter(function (b) { return b.checked; }).length;
      prog.textContent = n === boxes.length ? S.bagDone : fill(S.bagProgress, { n: n, t: boxes.length });
    }
    boxes.forEach(function (b) {
      b.checked = !!st[b.getAttribute("data-key")];
      b.addEventListener("change", function () { st[b.getAttribute("data-key")] = b.checked; set("tm_bag", st); upd(); });
    });
    $("#bag-reset").addEventListener("click", function () { st = {}; set("tm_bag", st); boxes.forEach(function (b) { b.checked = false; }); upd(); });
    upd();
  }

  // ---------- leave calculator
  function leave() {
    var box = $("#leave-tool"); if (!box) return;
    var birth = $("#lv-birth"), ms = $("#lv-mstart"), ps = $("#lv-pstart"), out = $("#lv-result");
    var st = get("tm_leave", {});
    birth.value = st.birth || get("tm_due", "") || "";
    ms.value = st.ms || ""; ps.value = st.ps || "";
    function run() {
      var b = parseDate(birth.value);
      if (!b) { out.innerHTML = '<p class="err">' + esc(S.lvNeed) + "</p>"; return; }
      set("tm_leave", { birth: birth.value, ms: ms.value, ps: ps.value });
      var m = parseDate(ms.value) || b, p = parseDate(ps.value) || b;
      var h = '<div class="result" style="margin-top:14px">';
      h += '<p class="big">' + esc(S.lvMat) + "</p><p>" + esc(fill(S.lvRange, { a: fmt(m), b: fmt(addDays(m, 97)) })) + "</p>";
      h += '<p class="muted">' + esc(fill(S.lvBack, { d: fmt(addDays(m, 98)) })) + "</p>";
      if (diffDays(m, b) > 30) h += '<p class="err">' + esc(S.lvEarly) + "</p>";
      h += '<p class="big" style="margin-top:12px">' + esc(S.lvPat) + "</p><p>" + esc(fill(S.lvRange, { a: fmt(p), b: fmt(addDays(p, 6)) })) + "</p>";
      out.innerHTML = h + "</div>";
    }
    $("#lv-go").addEventListener("click", run);
    if (birth.value) run();
  }

  // ---------- area pickers (prices + nursery share the saved area)
  function areaPicker(stateSel, distSel, states, onChange) {
    var area = get("tm_area", {});
    stateSel.innerHTML = '<option value="">' + esc(S.allMy) + "</option>" +
      Object.keys(states).sort().map(function (s) { return '<option value="' + esc(s) + '">' + esc(s) + "</option>"; }).join("");
    function fillDist() {
      var s = stateSel.value;
      distSel.disabled = !s;
      distSel.innerHTML = '<option value="">' + esc(S.allDist) + "</option>" +
        (s ? states[s].map(function (d) { return '<option value="' + esc(d) + '">' + esc(d) + "</option>"; }).join("") : "");
    }
    if (area.state && states[area.state]) stateSel.value = area.state;
    fillDist();
    if (area.district && stateSel.value && states[stateSel.value].indexOf(area.district) >= 0) distSel.value = area.district;
    stateSel.addEventListener("change", function () { fillDist(); save(); });
    distSel.addEventListener("change", save);
    function save() { set("tm_area", { state: stateSel.value, district: distSel.value }); onChange(stateSel.value, distSel.value); }
    onChange(stateSel.value, distSel.value);
  }

  // ---------- prices
  function prices() {
    var tables = $("#pr-tables"); if (!tables) return;
    var shopCache = {};
    var pics = {};
    var picsReady = fetch(TM.root + "data/product-images.json").then(function (r) { return r.ok ? r.json() : {}; })
      .then(function (j) { pics = j || {}; }).catch(function () { /* pictures are optional */ });
    Promise.all([fetch(TM.root + "data/prices-summary.json").then(function (r) { if (!r.ok) throw 0; return r.json(); }), picsReady]).then(function (res) {
      var data = res[0];
      $("#pr-updated").textContent = fill(S.updated, { a: fmt(parseDate(data.from)), b: fmt(parseDate(data.to)), n: data.shops.toLocaleString("en-MY") });
      var states = {};
      Object.keys(data.areas).forEach(function (k) {
        var p = k.split("|");
        if (p[0] === "S") states[p[1]] = states[p[1]] || [];
        if (p[0] === "D") (states[p[1]] = states[p[1]] || []).push(p[2]);
      });
      Object.keys(states).forEach(function (s) { states[s].sort(); });
      var cur = { state: "", district: "" };

      function draw(state, district) {
        cur = { state: state, district: district };
        var key = district ? "D|" + state + "|" + district : (state ? "S|" + state : "MY");
        var area = data.areas[key] || {};
        var areaName = district ? district + ", " + state : (state || S.allMy);
        var html = '<p class="pill">' + esc(fill(S.showing, { area: areaName })) + "</p>";
        ["mum", "infant", "followon", "growing", "diaper", "food"].forEach(function (g) {
          var codes = Object.keys(data.items).filter(function (c) { return data.items[c].g === g && area[c]; });
          if (!codes.length) return;
          codes.forEach(function (c) {
            var it = data.items[c], a = area[c];
            it._unit = it.gr ? a[0] / it.gr * 100 : (it.pc ? a[0] / it.pc : 0);
          });
          codes.sort(function (x, y) { return data.items[x]._unit - data.items[y]._unit; });
          html += '<section class="price-group" id="grp-' + g + '" data-g="' + g + '"><h2>' + esc(S.grp[g]) + '</h2><div class="table-wrap"><table><thead><tr><th>' + esc(S.cProduct) +
            '</th><th class="num">' + esc(S.cTypical) + '</th><th class="num hide-sm">' + esc(S.cFrom) + '</th><th class="num">' + esc(S.cUnit) +
            '</th><th class="num hide-sm">' + esc(S.cShops) + "</th></tr></thead><tbody>";
          codes.forEach(function (c) {
            var it = data.items[c], a = area[c];
            var pack = it.pc ? it.u + " · " + (it.t === "pants" ? S.pants : S.tape) : it.u;
            var unit = rm(it._unit) + '<small class="per">' + esc(it.gr ? S.per100 : S.perPiece) + "</small>";
            // Photos only - formula still gets no shop links, ads or commission.
            var pic = pics[c] ?
              '<img class="thumb" src="https://down-my.img.susercontent.com/file/' + encodeURIComponent(pics[c]) + '_tn" alt="" loading="lazy" width="48" height="48">' : "";
            html += '<tr data-code="' + c + '" data-name="' + esc((it.n + " " + S.grp[g]).toLowerCase()) + '"><td class="prod"><div class="prod-row">' + pic + "<div>" + esc(it.n) + "<small>" + esc(pack) +
              (a[2] < 3 ? " · " + esc(S.fewShops) : "") + '</small><button type="button" class="where-btn">' + esc(S.where) +
              '</button></div></div></td><td class="num">' + rm(a[0]) + '</td><td class="num hide-sm">' + rm(a[1]) + '</td><td class="num">' + unit +
              '</td><td class="num hide-sm">' + a[2] + "</td></tr>";
          });
          html += "</tbody></table></div></section>";
        });
        tables.innerHTML = html + '<p class="no-match" id="pr-none" hidden></p>';
        applyFilter();
      }

      // search box + product-type filter (also fed by the "Prices" drop-down: ?q=... and #grp-...)
      var qIn = $("#pr-q"), grpSel = $("#pr-group");
      function applyFilter() {
        var q = (qIn.value || "").toLowerCase().trim(), g = grpSel.value, shown = 0;
        $$(".price-group", tables).forEach(function (sec) {
          var n = 0;
          $$("tr[data-code]", sec).forEach(function (tr) {
            var ok = !q || q.split(/\s+/).every(function (w) { return tr.getAttribute("data-name").indexOf(w) >= 0; });
            tr.hidden = !ok;
            var nx = tr.nextElementSibling;
            if (nx && nx.classList.contains("shops")) nx.hidden = !ok;
            if (ok) n++;
          });
          sec.hidden = !n || (g && sec.getAttribute("data-g") !== g);
          if (!sec.hidden) shown += n;
        });
        var none = $("#pr-none");
        if (none) {
          none.hidden = shown > 0;
          none.innerHTML = esc(fill(S.noMatch, { q: qIn.value })) + ' <button type="button" class="where-btn" id="pr-clear">' + esc(S.clearSearch) + "</button>";
        }
      }
      var params = new URLSearchParams(location.search);
      if (params.get("q")) qIn.value = params.get("q").slice(0, 60);
      var hashG = (location.hash.match(/^#grp-(\w+)$/) || [])[1];
      if (hashG) grpSel.value = hashG;
      qIn.addEventListener("input", applyFilter);
      $("#pr-search").addEventListener("submit", function (e) { e.preventDefault(); applyFilter(); tables.scrollIntoView({ behavior: "smooth", block: "start" }); });
      grpSel.addEventListener("change", applyFilter);
      tables.addEventListener("click", function (e) {
        if (e.target.id === "pr-clear") { qIn.value = ""; grpSel.value = ""; applyFilter(); }
      });
      window.addEventListener("hashchange", function () {
        var h = (location.hash.match(/^#grp-(\w+)$/) || [])[1];
        if (h) { grpSel.value = h; applyFilter(); }
      });

      tables.addEventListener("click", function (e) {
        var btn = e.target.closest(".where-btn"); if (!btn) return;
        var tr = btn.closest("tr"), next = tr.nextElementSibling;
        if (next && next.classList.contains("shops")) { next.remove(); btn.textContent = S.where; return; }
        var row = document.createElement("tr");
        row.className = "shops";
        row.innerHTML = '<td colspan="5"></td>';
        tr.after(row);
        btn.textContent = S.hide;
        var cell = row.firstChild;
        if (!cur.state) { cell.textContent = S.chooseState; return; }
        var code = tr.getAttribute("data-code"), st = cur.state, di = cur.district;
        var p = shopCache[st] || fetch(TM.root + "data/shops/" + slug(st) + ".json").then(function (r) { if (!r.ok) throw 0; return r.json(); });
        shopCache[st] = p;
        p.then(function (sd) {
          var list = [];
          Object.keys(sd.d).forEach(function (d) {
            if (di && d !== di) return;
            (sd.d[d][code] || []).forEach(function (x) { list.push(x); });
          });
          list.sort(function (a, b) { return a[1] - b[1]; });
          list = list.slice(0, 5);
          if (!list.length) { cell.textContent = S.noShops; return; }
          cell.innerHTML = '<ul class="shop-list">' + list.map(function (x) {
            var s = sd.p[x[0]] || ["?", "", ""];
            return "<li><strong>" + rm(x[1]) + "</strong> · " + esc(s[0]) + ' <span class="muted">(' + esc(s[1]) + ")</span>" +
              '<span class="addr">' + esc(s[2]) + " · " + esc(fmt(parseDate(x[2]))) + "</span></li>";
          }).join("") + "</ul>";
        }).catch(function () { delete shopCache[st]; cell.textContent = S.loadFail; });
      });

      areaPicker($("#pr-state"), $("#pr-district"), states, draw);
    }).catch(function () { tables.innerHTML = '<p class="err">' + esc(S.loadFail) + "</p>"; });
  }

  // ---------- taska / tadika finder
  function nursery() {
    var box = $("#nursery-tool"); if (!box) return;
    var links = $("#nu-area-links"), ta = $("#nu-taska"), td = $("#nu-tadika");
    function maps(q) { return "https://www.google.com/maps/search/?api=1&query=" + encodeURIComponent(q); }
    fetch(TM.root + "data/districts.json").then(function (r) { if (!r.ok) throw 0; return r.json(); }).then(function (states) {
      areaPicker($("#nu-state"), $("#nu-district"), states, function (s, d) {
        links.hidden = !s;
        if (!s) return;
        var place = (d ? d + ", " : "") + s;
        ta.href = maps("taska " + place); ta.textContent = fill(S.nuTaska, { area: d || s }) + " ↗";
        td.href = maps("tadika " + place); td.textContent = fill(S.nuTadika, { area: d || s }) + " ↗";
      });
    }).catch(function () { /* near-me buttons still work */ });
  }

  // ---------- keep the current menu tab in view on small screens (phones scroll the menu sideways)
  function navScroll() {
    var nav = $(".nav"), cur = $('.nav [aria-current="page"]');
    if (nav && cur && nav.scrollWidth > nav.clientWidth + 2) nav.scrollLeft = cur.offsetLeft - (nav.clientWidth - cur.offsetWidth) / 2;
    else if (nav) nav.scrollLeft = 0;
  }

  // ---------- "Prices" tab opens its drop-down instead of jumping straight to the page
  function subnav() {
    var tab = $(".tab.has-sub"), panel = $("#subnav-prices");
    if (!tab || !panel) return;
    tab.addEventListener("click", function (e) {
      e.preventDefault();
      var open = panel.hidden;
      panel.hidden = !open;
      tab.setAttribute("aria-expanded", open ? "true" : "false");
      if (open) { var f = $("input", panel); if (f && window.innerWidth >= 700) f.focus(); }
    });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && !panel.hidden) { panel.hidden = true; tab.setAttribute("aria-expanded", "false"); tab.focus(); } });
    // on the prices page the drop-down's group links only change the filter, so close it after a pick
    $$("a", panel).forEach(function (a) { a.addEventListener("click", function () { panel.hidden = true; tab.setAttribute("aria-expanded", "false"); }); });
  }

  // ---------- helper bot: keyword matching over a small list of topics, no AI, nothing leaves the phone
  function bot() {
    var B = S.bot; if (!B) return;
    var page = function (p) { return TM.root + LANG + "/" + p; };
    var fab = document.createElement("button");
    fab.type = "button"; fab.className = "chat-fab"; fab.setAttribute("aria-expanded", "false");
    fab.innerHTML = '<span aria-hidden="true">💬</span> ' + esc(B.open);
    var panel = document.createElement("section");
    panel.className = "chat-panel"; panel.hidden = true; panel.setAttribute("role", "dialog"); panel.setAttribute("aria-label", B.title);
    panel.innerHTML = '<header class="chat-head"><strong>' + esc(B.title) + '</strong><button type="button" class="chat-x" aria-label="' + esc(B.close) + '">✕</button></header>' +
      '<div class="chat-log" aria-live="polite"></div>' +
      '<div class="chat-chips">' + B.chips.map(function (c) { return '<button type="button" data-q="' + esc(c[1]) + '">' + esc(c[0]) + "</button>"; }).join("") + "</div>" +
      '<form class="chat-form"><input type="text" maxlength="200" autocomplete="off" placeholder="' + esc(B.placeholder) + '" aria-label="' + esc(B.placeholder) +
      '"><button type="submit" class="btn small-btn">' + esc(B.send) + "</button></form>" +
      '<p class="chat-note">' + esc(B.note) + "</p>";
    document.body.appendChild(fab); document.body.appendChild(panel);
    var log = $(".chat-log", panel), input = $(".chat-form input", panel), started = false;

    function say(text, who, link) {
      var d = document.createElement("div");
      d.className = "msg " + who;
      d.innerHTML = esc(text) + (link ? '<a class="msg-link" href="' + esc(link[0]) + '">' + esc(link[1]) + " →</a>" : "");
      log.appendChild(d); log.scrollTop = log.scrollHeight;
    }
    function norm(t) { return " " + t.toLowerCase().replace(/[^a-z0-9+]+/g, " ").trim() + " "; }
    function hits(text, kw) {
      if (kw.charAt(0) === "=") return text.indexOf(" " + kw.slice(1) + " ") >= 0;
      return text.indexOf(" " + kw) >= 0;  // start of a word or phrase
    }
    function answer(q) {
      var t = norm(q), byId = {};
      B.intents.forEach(function (it) { byId[it.id] = it; });
      var danger = byId.danger.k.some(function (k) { return hits(t, k); });
      if (danger) return say(byId.danger.a, "bot");
      var m = /(?:week|minggu)\s*(?:ke\s*)?(\d{1,2})\b/.exec(t);
      if (m && +m[1] >= 4 && +m[1] <= 40 && TM.wk) {
        return say(fill(B.weekAns, { w: m[1], size: TM.wk[m[1]] }), "bot", [page("weeks/" + m[1] + ".html"), fill(B.weekLink, { w: m[1] })]);
      }
      var best = null, bestScore = 0;
      B.intents.forEach(function (it) {
        if (it.id === "danger") return;
        var s = 0;
        it.k.forEach(function (k) { if (hits(t, k)) s += k.replace("=", "").length; });
        if (s > bestScore) { best = it; bestScore = s; }
      });
      if (!best) return say(B.fallback, "bot", [page("feedback.html"), B.chips[B.chips.length - 1][0]]);
      if (best.id === "week") {
        var due = parseDate(get("tm_due", ""));
        if (due) {
          var ga = 280 - diffDays(today(), due), w = Math.floor(ga / 7);
          if (ga >= 0 && w <= 44) {
            var pw = Math.min(Math.max(w, 4), 40);
            return say(fill(B.myWeek, { w: w, d: ga % 7 }) + " " + fill(B.weekAns, { w: pw, size: TM.wk[pw] }), "bot",
              [page("weeks/" + pw + ".html"), fill(B.weekLink, { w: pw })]);
          }
        }
      }
      say(best.a, "bot", best.p ? [page(best.p), best.lt] : null);
    }
    function ask(q) { q = q.trim(); if (!q) return; say(q, "me"); answer(q); }
    function open(on) {
      panel.hidden = !on; fab.setAttribute("aria-expanded", on ? "true" : "false");
      if (on && !started) { started = true; say(B.greet, "bot"); }
      if (on) input.focus(); else fab.focus();
    }
    fab.addEventListener("click", function () { open(panel.hidden); });
    $(".chat-x", panel).addEventListener("click", function () { open(false); });
    panel.addEventListener("keydown", function (e) { if (e.key === "Escape") open(false); });
    $(".chat-chips", panel).addEventListener("click", function (e) { var b = e.target.closest("button"); if (b) ask(b.getAttribute("data-q")); });
    $(".chat-form", panel).addEventListener("submit", function (e) { e.preventDefault(); ask(input.value); input.value = ""; });
  }

  dueTool(); weekMarkers(); pantang(); quotes(); bag(); leave(); prices(); nursery(); navScroll(); subnav(); bot();
  window.addEventListener("resize", navScroll);
})();
