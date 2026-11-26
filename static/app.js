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
      if (w < 4) { out.innerHTML = '<div class="week-card"><p class="wc-week">' + esc(fill(S.weeksDays, { w: w, d: d })) + "</p><p>" + esc(S.early) + "</p></div>"; return; }
      // Progress card: week, trimester, baby size, a progress bar to the due date, link to that week
      var pw = Math.min(w, 40), info = (TM.weeks || {})[pw] || ["👶", ""];
      var tri = w <= 13 ? 1 : (w <= 27 ? 2 : 3), pct = Math.min(100, Math.round(ga / 280 * 100));
      out.innerHTML = '<div class="week-card">' +
        '<div class="wc-top"><span class="wc-emoji" aria-hidden="true">' + info[0] + "</span><div>" +
        '<p class="wc-week">' + esc(fill(S.wcWeek, { w: w })) + ' <span>' + esc(fill(S.wcDays, { d: d })) + "</span></p>" +
        '<p class="wc-sub">' + esc(fill(S.tri, { t: tri })) + " · " + esc(fill(S.sizeOf, { size: info[1] })) + "</p></div></div>" +
        '<div class="progress" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="' + pct + '"><span style="width:' + pct + '%"></span></div>' +
        '<div class="wc-foot"><span>' + esc(fill(S.daysToGo, { n: left, date: fmt(due) })) + "</span>" +
        '<a class="btn small-btn" href="weeks/' + pw + '.html">' + esc(fill(S.readWeek, { w: pw })) + " →</a></div></div>";
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
    var tri = $('.dtabs[data-group="tri"]');  // weeks index: open the trimester you're in
    if (tri && w >= 4 && w <= 40) tri.setAttribute("data-default", w <= 13 ? "t1" : w <= 27 ? "t2" : "t3");
    var li = $('.week-list li[data-week="' + w + '"]');
    if (li) { li.classList.add("current"); li.querySelector(".wk-n").insertAdjacentHTML("beforeend", ' <span class="pill">' + esc(S.youAreHere) + "</span>"); }
  }

  // ---------- pantang planner: tradition pills, summary tiles, timeline with icons
  function pantang() {
    var box = $("#pantang-tool"); if (!box) return;
    var trad = $("#p-trad"), daysWrap = $("#p-days-wrap"), days = $("#p-days"), date = $("#p-date"), out = $("#p-result");
    var pills = $$(".pill-opt", box);
    var st = get("tm_pantang", {});
    if (st.trad) trad.value = st.trad;
    if (st.days) days.value = st.days;
    if (st.kind) $$('input[name="p-kind"]').forEach(function (r) { r.checked = r.value === st.kind; });
    date.value = st.date || get("tm_due", "") || "";
    function sync() {
      daysWrap.hidden = trad.value !== "custom";
      pills.forEach(function (b) { b.setAttribute("aria-pressed", b.getAttribute("data-v") === trad.value ? "true" : "false"); });
    }
    pills.forEach(function (b) { b.addEventListener("click", function () { trad.value = b.getAttribute("data-v"); sync(); if (date.value) run(); }); });
    trad.addEventListener("change", sync); sync();
    $$('input[name="p-kind"]').forEach(function (r) { r.addEventListener("change", function () { if (date.value) run(); }); });

    function run() {
      var d = parseDate(date.value);
      if (!d) { out.innerHTML = '<p class="err">' + esc(S.pickDate) + "</p>"; return; }
      var kind = ($('input[name="p-kind"]:checked') || {}).value || "due";
      var n = trad.value === "custom" ? Math.max(7, Math.min(120, parseInt(days.value, 10) || 40)) : parseInt(trad.value, 10);
      set("tm_pantang", { trad: trad.value, days: days.value, kind: kind, date: date.value });
      var t = today(), end = addDays(d, n - 1), dayNo = diffDays(d, t) + 1;
      // summary tiles
      var tiles = '<div class="stats p-stats">' +
        '<div class="stat t1"><p class="stat-label">' + esc(S.pEndsLbl) + '</p><p class="stat-big">' + esc(fmt(end)) + '</p><p class="stat-small">' + esc(fill(S.pDaysN, { n: n })) + "</p></div>";
      if (dayNo >= 1 && dayNo <= n) {
        tiles += '<div class="stat t2"><p class="stat-label">' + esc(S.pTodayLbl) + '</p><p class="stat-big">' + esc(fill(S.pDayOf, { d: dayNo, n: n })) + "</p>" +
          '<div class="progress"><span style="width:' + Math.round(dayNo / n * 100) + '%"></span></div></div>';
      } else if (dayNo < 1) {
        tiles += '<div class="stat t2"><p class="stat-label">' + esc(S.pStartsLbl) + '</p><p class="stat-big">' + esc(fill(S.pInDays, { n: 1 - dayNo })) + '</p><p class="stat-small">' + esc(fmt(d)) + "</p></div>";
      }
      tiles += '<div class="stat t3"><p class="stat-label">' + esc(S.pCheckLbl) + '</p><p class="stat-big">' + esc(fmt(addDays(d, 41))) + '</p><p class="stat-small">' + esc(S.pCheckSmall) + "</p></div></div>";
      var before = [[-168, "📋", S.pShortlist], [-140, "💳", S.pBook], [-42, "🛒", S.pBuy], [-28, "👜", S.pBag]];
      var after = [
        [0, "👶", (kind === "birth" ? S.pBirth : S.pDue) + " - " + S.pVacc], [3, "🤱", S.pMilk], [6, "👨", S.pPat],
        [41, "🩺", S.pCheck], [n - 1, "🌿", fill(S.pEnd, { n: n })], [59, "📝", S.pReg], [97, "💼", S.pMat]
      ].sort(function (x, y) { return x[0] - y[0]; });
      var nextMarked = false;
      function list(items, title) {
        var h = "<h3>" + esc(title) + '</h3><ol class="timeline tl2">';
        items.forEach(function (it) {
          var day = addDays(d, it[0]), cls = day < t ? "past" : "";
          if (!cls && !nextMarked) { cls = "next"; nextMarked = true; }
          h += '<li class="' + cls + '"><span class="tl-ico" aria-hidden="true">' + it[1] + '</span><div><span class="when">' + esc(fmt(day)) +
            (iso(day) === iso(t) ? ' <span class="badge">' + esc(S.pToday) + "</span>" : "") +
            (cls === "next" ? ' <span class="badge">' + esc(S.pNext) + "</span>" : "") + "</span>" + esc(it[2]) + "</div></li>";
        });
        return h + "</ol>";
      }
      var html = tiles + (kind === "due" ? list(before, S.pBefore) : "") + list(after, S.pAfter);
      if (kind === "due") html += '<p class="hint">' + esc(S.pNoteDue) + "</p>";
      out.innerHTML = html;
    }
    $("#p-go").addEventListener("click", run);
    if (st.date) run();
  }

  // ---------- confinement quotes: compact cards (pick a centre -> summary line; details folded away)
  function quotes() {
    var box = $("#quote-tool"); if (!box) return;
    var cards = $$(".quote", box), out = $("#q-result"), addBtn = $("#q-add");
    var saved = get("tm_quotes", []), presets = {}, presetsReady = false, pendingAdd = null;
    function val(c, n) { return c.querySelector('[name="' + n + '"]'); }
    // "+ Add to comparison" on a centre card / typical price: fill the next empty quote and open the Compare tab
    document.addEventListener("click", function (e) {
      var b = e.target.closest("[data-compare]"); if (!b) return;
      var id = b.getAttribute("data-compare");
      function go() {
        pendingAdd = null;
        if (!presets[id]) return;
        var c = cards.filter(function (q) { return !q.hidden && !val(q, "price").value && !val(q, "name").value; })[0] ||
                cards.filter(function (q) { return q.hidden; })[0] || cards[cards.length - 1];
        c.hidden = false;
        var sel = val(c, "preset"); sel.value = id; sel.dispatchEvent(new Event("change"));
        b.textContent = S.qAdded;
        var tab = $("#tb-cost-compare"); if (tab) tab.click();
        box.scrollIntoView({ behavior: "smooth", block: "start" });
      }
      if (presetsReady) go(); else pendingAdd = go;
    });
    cards.forEach(function (c, i) {
      var q = saved[i] || {};
      ["name", "price", "days", "ratio"].forEach(function (k) { if (q[k] !== undefined && q[k] !== "") val(c, k).value = q[k]; });
      $$('input[name="inc"]', c).forEach(function (cb) { cb.checked = (q.inc || []).indexOf(cb.value) >= 0; });
      if (q.price || q.name) c.hidden = false;
    });
    function noteFor(p) {
      if (!p) return "";
      if (p.kind === "typical") return esc((LANG === "ms" ? p.note_ms : p.note_en) + " " + S.preTypicalNote);
      var price = rm(p.price_from_rm).replace(".00", "") + (p.price_to_rm ? " - " + rm(p.price_to_rm).replace(".00", "") : "");
      var cav = p["caveat_" + LANG] || p.caveat_en || "";
      var expired = p.valid_until && iso(today()) > p.valid_until ? " " + S.promoEnded : "";
      return esc(fill(p.days_unstated ? S.preCentreNoteNoDays : S.preCentreNote, { d: p.days, price: price, date: fmt(parseDate(p.checked)) })) +
        (cav ? " <strong>" + esc(cav + expired) + "</strong>" : "") +
        ' <a href="' + esc(p.source_url) + '" target="_blank" rel="noopener">' + esc(S.preSource) + " ↗</a>";
    }
    function summary(c) {
      var p = parseFloat(val(c, "price").value), d = parseInt(val(c, "days").value, 10), sum = $(".q-sum", c);
      if (p > 0 && d > 0) {
        sum.innerHTML = "<strong>" + rm(p).replace(".00", "") + "</strong> · " + d + " " + esc(S.qDays) + " · <strong>" + rm(p / d).replace(".00", "") + "</strong>" + esc(S.qPerDay);
        sum.hidden = false;
      } else sum.hidden = true;
    }
    function applyPreset(c, p) {
      val(c, "name").value = p.kind === "typical" ? (LANG === "ms" ? p.ms : p.en) : p.name;
      val(c, "price").value = p.kind === "typical" ? p.price : p.price_from_rm;
      val(c, "days").value = p.days || 28;
      var ratio = p.kind === "typical" ? p.ratio : p.babies_per_nurse;
      val(c, "ratio").value = ratio || "";
      var inc = (p.kind === "typical" ? p.inc : p.includes) || {};
      $$('input[name="inc"]', c).forEach(function (cb) { cb.checked = inc[cb.value] === true; });
    }
    function setTip(c, p) { $(".q-tip", c).innerHTML = p ? makeTip(noteFor(p)) : ""; }
    fetch(TM.root + "data/confinement.json?v=" + TM.ver).then(function (r) { return r.ok ? r.json() : null; }).then(function (d) {
      if (!d) return;
      var html = '<optgroup label="' + esc(S.preTypical) + '">' + d.typical.map(function (t) {
        presets[t.id] = Object.assign({ kind: "typical" }, t);
        return '<option value="' + esc(t.id) + '">' + esc(LANG === "ms" ? t.ms : t.en) + "</option>";
      }).join("") + "</optgroup>";
      var byState = {};
      (d.centres || []).forEach(function (c, i) {
        var id = "c" + i;
        presets[id] = Object.assign({ kind: "centre" }, c);
        (byState[c.state] = byState[c.state] || []).push('<option value="' + id + '">' +
          esc(c.name + " · " + S.qFrom + " " + rm(c.price_from_rm).replace(".00", "")) + "</option>");
      });
      Object.keys(byState).sort().forEach(function (st) {
        html += '<optgroup label="' + esc(fill(S.preCentres, { state: st })) + '">' + byState[st].join("") + "</optgroup>";
      });
      presetsReady = true;
      if (pendingAdd) setTimeout(pendingAdd, 0);
      cards.forEach(function (c, i) {
        var sel = val(c, "preset");
        sel.insertAdjacentHTML("beforeend", html);
        var q = saved[i] || {};
        if (q.preset && presets[q.preset]) { sel.value = q.preset; setTip(c, presets[q.preset]); }
        sel.addEventListener("change", function () {
          var p = presets[sel.value];
          if (p) applyPreset(c, p);
          setTip(c, p);
          render();
        });
      });
    }).catch(function () { /* drop-down is optional */ });
    function read() {
      return cards.map(function (c) {
        return {
          // until the drop-down has loaded its options, keep the saved choice instead of wiping it
          preset: presetsReady ? val(c, "preset").value : ((saved[cards.indexOf(c)] || {}).preset || ""),
          name: val(c, "name").value.trim(), price: val(c, "price").value,
          days: val(c, "days").value, ratio: val(c, "ratio").value,
          inc: $$('input[name="inc"]:checked', c).map(function (cb) { return cb.value; })
        };
      });
    }
    function render() {
      var qs = read();
      set("tm_quotes", qs);
      cards.forEach(summary);
      addBtn.hidden = cards.every(function (c) { return !c.hidden; });
      var rows = [];
      qs.forEach(function (q, i) {
        var p = parseFloat(q.price), d = parseInt(q.days, 10);
        if (p > 0 && d > 0) rows.push({ name: q.name || fill(S.qQuote, { n: i + 1 }), price: p, days: d, per: p / d, ratio: parseInt(q.ratio, 10) });
      });
      if (rows.length < 2) { out.innerHTML = rows.length ? '<p class="hint">' + esc(S.qOneMore) + "</p>" : ""; return; }
      rows.sort(function (a, b) { return a.per - b.per; });
      out.innerHTML = '<ol class="rank">' + rows.map(function (r, k) {
        return '<li class="' + (k === 0 ? "best" : "") + '"><span class="rank-name">' + esc(r.name) +
          (k === 0 ? ' <span class="badge">' + esc(S.qLowest) + "</span>" : "") +
          (r.ratio > 4 ? '<span class="flag">⚠ ' + esc(S.qWarn) + "</span>" : "") +
          '</span><span class="rank-per"><strong>' + rm(r.per).replace(".00", "") + "</strong>" + esc(S.qPerDay) + "</span></li>";
      }).join("") + "</ol>";
    }
    box.addEventListener("input", render);
    box.addEventListener("change", render);
    addBtn.addEventListener("click", function () {
      var next = cards.find(function (c) { return c.hidden; });
      if (next) { next.hidden = false; val(next, "preset").focus(); }
      render();
    });
    $("#q-clear").addEventListener("click", function () {
      cards.forEach(function (c, i) {
        ["name", "price", "ratio"].forEach(function (n) { val(c, n).value = ""; });
        val(c, "days").value = 28; val(c, "preset").value = ""; setTip(c, null);
        $$('input[type="checkbox"]', c).forEach(function (cb) { cb.checked = false; });
        $(".q-edit", c).open = false;
        c.hidden = i > 1;
      });
      render();
    });
    render();
  }

  // ---------- taska / tadika compare: ranked by first-year cost (12 x monthly fee + registration/deposit)
  function nurseryCompare() {
    var box = $("#nu-compare"); if (!box) return;
    var cards = $$(".quote", box), out = $("#nu-result"), addBtn = $("#nu-add"), F = ["preset", "name", "fee", "reg_fee", "open", "close", "ratio"];
    var saved = get("tm_nursery", []), P = {};
    (TM.nu || []).forEach(function (o) { P[o.id] = o; });
    function val(c, n) { return c.querySelector('[name="' + n + '"]'); }
    function applyPreset(c, o) {
      val(c, "name").value = o.name;
      val(c, "fee").value = o.fee === null ? "" : o.fee;
      val(c, "reg_fee").value = o.reg === null ? "" : o.reg;
      $$('input[name="inc"]', c).forEach(function (cb) { cb.checked = !!(o.inc || {})[cb.value]; });
    }
    cards.forEach(function (c) {
      val(c, "preset").addEventListener("change", function () { var o = P[this.value]; if (o) applyPreset(c, o); render(); });
    });
    // "+ Add to comparison" on a government taska/tadika card
    document.addEventListener("click", function (e) {
      var b = e.target.closest("[data-nu-add]"); if (!b) return;
      var o = P[b.getAttribute("data-nu-add")]; if (!o) return;
      var c = cards.filter(function (q) { return !q.hidden && !val(q, "name").value && !val(q, "fee").value; })[0] ||
              cards.filter(function (q) { return q.hidden; })[0] || cards[cards.length - 1];
      c.hidden = false; val(c, "preset").value = o.id; applyPreset(c, o); render();
      b.textContent = S.qAdded;
      box.scrollIntoView({ behavior: "smooth", block: "start" });
    });
    cards.forEach(function (c, i) {
      var q = saved[i] || {};
      F.forEach(function (k) { if (q[k]) val(c, k).value = q[k]; });
      $$('input[name="inc"]', c).forEach(function (cb) { cb.checked = (q.inc || []).indexOf(cb.value) >= 0; });
      if (q.name || q.fee) c.hidden = false;
    });
    function render() {
      var qs = cards.map(function (c) {
        var q = { inc: $$('input[name="inc"]:checked', c).map(function (cb) { return cb.value; }) };
        F.forEach(function (k) { q[k] = val(c, k).value.trim(); });
        return q;
      });
      set("tm_nursery", qs);
      addBtn.hidden = cards.every(function (c) { return !c.hidden; });
      var rows = [];
      qs.forEach(function (q, i) {
        var fee = parseFloat(q.fee) || 0, reg = parseFloat(q.reg_fee) || 0, sum = $(".q-sum", cards[i]);
        var hours = q.open && q.close ? q.open + " - " + q.close : "";
        var hasFee = q.fee !== "" && !isNaN(parseFloat(q.fee));
        if (hasFee && (fee > 0 || q.name)) {
          var year = fee * 12 + reg;
          sum.innerHTML = (year === 0 ? "<strong>" + esc(S.nuFree) + "</strong>" :
            "<strong>" + rm(fee).replace(".00", "") + "</strong>" + esc(S.nuMonth) + " · " + esc(S.nuYear) + " <strong>" + rm(year).replace(".00", "") + "</strong>") +
            (hours ? " · " + esc(hours) : "");
          sum.hidden = false;
          rows.push({ name: q.name || fill(S.nuOption, { n: i + 1 }), year: year, fee: fee, hours: hours, reg: q.inc.indexOf("reg") >= 0, ratio: q.ratio });
        } else sum.hidden = true;
      });
      if (rows.length < 2) { out.innerHTML = rows.length ? '<p class="hint">' + esc(S.nuOneMore) + "</p>" : ""; return; }
      rows.sort(function (a, b) { return a.year - b.year; });
      out.innerHTML = '<ol class="rank">' + rows.map(function (r, k) {
        return '<li class="' + (k === 0 ? "best" : "") + '"><span class="rank-name">' + esc(r.name) +
          (k === 0 ? ' <span class="badge">' + esc(S.nuCheapest) + "</span>" : "") +
          (r.hours ? '<span class="flag muted-flag">' + esc(r.hours) + "</span>" : "") +
          (!r.reg ? '<span class="flag">⚠ ' + esc(S.nuNotReg) + "</span>" : "") +
          '</span><span class="rank-per"><strong>' + (r.year === 0 ? esc(S.nuFree) : rm(r.year).replace(".00", "")) + "</strong> " + (r.year === 0 ? "" : esc(S.nuYear)) + "</span></li>";
      }).join("") + "</ol>";
    }
    box.addEventListener("input", render);
    box.addEventListener("change", render);
    addBtn.addEventListener("click", function () {
      var next = cards.find(function (c) { return c.hidden; });
      if (next) { next.hidden = false; val(next, "name").focus(); }
      render();
    });
    $("#nu-clear").addEventListener("click", function () {
      cards.forEach(function (c, i) {
        F.forEach(function (k) { val(c, k).value = ""; });
        $$('input[type="checkbox"]', c).forEach(function (cb) { cb.checked = false; });
        c.hidden = i > 1;
      });
      render();
    });
    render();
  }


  // ---------- home: stage tabs (pregnant / new mum / mum & kids); picks a sensible tab from the saved due date
  function homeTabs() {
    var tabs = $$(".stage-tab"); if (!tabs.length) return;
    var due = parseDate(get("tm_due", "")), stage = get("tm_stage", "");
    if (!stage) stage = due ? (diffDays(today(), due) < 0 ? "new" : "preg") : (get("tm_fert", {}).lmp ? "before" : "preg");
    function show(sv) {
      tabs.forEach(function (t) { t.setAttribute("aria-selected", t.getAttribute("data-stage") === sv ? "true" : "false"); });
      $$(".stage-panel").forEach(function (p) { p.hidden = p.getAttribute("data-stage") !== sv; });
    }
    tabs.forEach(function (t) { t.addEventListener("click", function () { var v = t.getAttribute("data-stage"); set("tm_stage", v); show(v); }); });
    show(stage);
  }

  // ---------- vaccination dates from the baby's birth date (ticks saved on this phone)
  function vaccines() {
    var box = $("#vax-tool"); if (!box) return;
    var input = $("#vax-birth"), out = $("#vax-result"), st = get("tm_vax", { birth: "", done: {} });
    input.value = st.birth || "";
    function addMonths(d, m) { var x = new Date(d.getTime()); x.setUTCMonth(x.getUTCMonth() + m); return x; }
    function render() {
      var b = parseDate(input.value);
      if (!b) { out.innerHTML = ""; return; }
      st.birth = input.value; set("tm_vax", st);
      var t = today(), nextDone = false, html = '<ol class="vax-list">';
      (TM.vax || []).forEach(function (v, i) {
        var due = addMonths(b, v[0]), done = !!st.done[i], cls = done ? "done" : (due < t ? "late" : "");
        if (!done && !nextDone && due >= addDays(t, -60)) { cls += " next"; nextDone = true; }
        html += '<li class="' + cls + '"><label class="vax-check"><input type="checkbox" data-i="' + i + '"' + (done ? " checked" : "") + "></label>" +
          '<div class="vax-main"><span class="vax-age">' + esc(v[0] === 0 ? S.vaxBirth : fill(S.vaxMonths, { m: v[0] })) + "</span>" +
          "<strong>" + esc(v[1]) + "</strong>" + (v[2] ? '<span class="muted small"> · ' + esc(v[2]) + "</span>" : "") + "</div>" +
          '<span class="vax-date">' + esc(fmt(due)) + "</span></li>";
      });
      out.innerHTML = html + "</ol>";
    }
    input.addEventListener("change", render);
    out.addEventListener("change", function (e) {
      var cb = e.target.closest("input[data-i]"); if (!cb) return;
      st.done[cb.getAttribute("data-i")] = cb.checked; set("tm_vax", st); render();
    });
    render();
  }

  // ---------- after-birth documents: JPN deadline (60 days Peninsular, 14 Sabah/Sarawak), MyKad at 12, EPF from 14
  function afterBirth() {
    var box = $("#docs-tool"); if (!box) return;
    var input = $("#docs-birth"), out = $("#docs-result"), pills = $$(".pill-opt[data-r]", box);
    var st = get("tm_docs_info", null);
    if (!st) {  // first visit: reuse a birth date the mum already typed on the vaccine or pantang page
      var vx = get("tm_vax", {}), pt = get("tm_pantang", {});
      st = { birth: vx.birth || (pt.kind === "birth" ? pt.date : "") || "", region: "pen" };
    }
    input.value = st.birth || "";
    function addYears(d, y) { var x = new Date(d.getTime()); x.setUTCFullYear(x.getUTCFullYear() + y); return x; }
    function setRegion(r) {
      st.region = r;
      pills.forEach(function (p) { p.setAttribute("aria-pressed", p.getAttribute("data-r") === r ? "true" : "false"); });
    }
    function render() {
      var b = parseDate(input.value), epfLine = $("#sv-epf-date");
      if (!b) { out.innerHTML = ""; if (epfLine) epfLine.hidden = true; return; }
      st.birth = input.value; set("tm_docs_info", st);
      var limit = st.region === "pen" ? 60 : 14, last = addDays(b, limit - 1), left = diffDays(today(), last);
      var regSmall = left > 0 ? fill(S.dLeft, { n: left }) : left === 0 ? S.dLastDay : (st.region === "pen" ? S.dLatePen : S.dLateSS);
      var epf = addYears(b, 14);
      out.innerHTML = '<div class="stats">' +
        '<div class="stat t1' + (left < 0 ? " late" : "") + '"><p class="stat-label">' + esc(S.dRegBy) + '</p><p class="stat-big">' + esc(fmt(last)) + '</p><p class="stat-small">' + esc(regSmall) + "</p></div>" +
        '<div class="stat t2"><p class="stat-label">' + esc(S.dMyKad) + '</p><p class="stat-big">' + esc(fmt(addYears(b, 12))) + '</p><p class="stat-small">' + esc(S.dMyKadSmall) + "</p></div>" +
        '<div class="stat"><p class="stat-label">' + esc(S.dEpf) + '</p><p class="stat-big">' + esc(fmt(epf)) + '</p><p class="stat-small">' + esc(S.dEpfSmall) + "</p></div></div>";
      if (epfLine) { epfLine.textContent = fill(S.dEpfFrom, { d: fmt(epf) }); epfLine.hidden = false; }
    }
    pills.forEach(function (p) { p.addEventListener("click", function () { setRegion(p.getAttribute("data-r")); set("tm_docs_info", st); render(); }); });
    input.addEventListener("change", render);
    setRegion(st.region || "pen");
    render();
  }

  // ---------- delivery cost: government hospital bill from MOH rates (TM.gov) + private hospital state filter
  function deliveryCost() {
    var box = $("#gov-tool");
    if (box && TM.gov) {
      var G = TM.gov, st = get("tm_gov", { cls: "c3", type: "normal", days: 2, ac: true }), days = $("#gv-days"), ac = $("#gv-ac"), out = $("#gv-result");
      var defDays = { normal: 2, assisted: 2, twins: 3, csec: 3 };
      function press(g, v) { $$('.pill-opt[data-g="' + g + '"]', box).forEach(function (b) { b.setAttribute("aria-pressed", b.getAttribute("data-v") === v ? "true" : "false"); }); }
      function render() {
        var n = Math.max(1, Math.min(14, parseInt(days.value, 10) || 1)), base = st.cls.slice(0, 2);
        st.days = n; st.ac = ac.checked; set("tm_gov", st);
        var fee = G.d[st.type][base], ward = G.w[st.cls][ac.checked ? 1 : 0] * n, care = G.t[base] * n, room = base === "c1" ? G.room : 0;
        var total = fee + ward + care + room;
        var rows = [[S.gvFee, fee], [fill(S.gvWard, { n: n }), ward], [fill(S.gvCare, { n: n }), care]];
        if (room) rows.push([st.type === "csec" ? S.gvTheatre : S.gvRoom, room]);
        out.innerHTML = '<div class="gv-total"><p class="stat-label">' + esc(S.gvEstimate) + '</p><p class="stat-big">' + esc(rm(total).replace(".00", "")) + "</p></div>" +
          '<ul class="gv-break">' + rows.map(function (r) { return "<li><span>" + esc(r[0]) + "</span><strong>" + esc(r[1] ? rm(r[1]).replace(".00", "") : S.gvFree) + "</strong></li>"; }).join("") + "</ul>";
      }
      $$(".pill-opt[data-g]", box).forEach(function (b) {
        b.addEventListener("click", function () {
          var g = b.getAttribute("data-g"), v = b.getAttribute("data-v");
          st[g] = v; press(g, v);
          if (g === "type") days.value = defDays[v];
          render();
        });
      });
      days.addEventListener("input", render); ac.addEventListener("change", render);
      days.value = st.days || 2; ac.checked = st.ac !== false; press("cls", st.cls); press("type", st.type); render();
    }
  }

  // ---------- state chips: filter the cards (data-state) inside the list named by data-for
  function stateChips() {
    $$(".state-chips[data-for]").forEach(function (bar) {
      var list = document.getElementById(bar.getAttribute("data-for")), chips = $$(".chip-btn", bar);
      var askBox = bar.getAttribute("data-ask") ? document.getElementById(bar.getAttribute("data-ask")) : null;
      if (!list) return;
      chips.forEach(function (c) {
        c.addEventListener("click", function () {
          var s = c.getAttribute("data-state");
          chips.forEach(function (o) { o.setAttribute("aria-pressed", o === c ? "true" : "false"); });
          $$("[data-state]", list).forEach(function (h) { h.hidden = !!s && h.getAttribute("data-state") !== s; });
          if (askBox) {
            var any = false;
            $$("li", askBox).forEach(function (li) { li.hidden = !!s && li.getAttribute("data-state") !== s; if (!li.hidden) any = true; });
            askBox.hidden = !any;
          }
        });
      });
    });
  }

  // ---------- "Sort by" drop-downs for card lists (confinement centres, taska/tadika): reorder by data-s-<key>
  function cardSort() {
    $$("select[data-sort-for]").forEach(function (sel) {
      var list = document.getElementById(sel.getAttribute("data-sort-for")); if (!list) return;
      var key = "tm_sort_" + list.id;
      function apply() {
        var v = sel.value.split(":"), k = "data-s-" + v[0], dir = v[1] === "desc" ? -1 : 1;
        var cards = $$(":scope > [" + k + "]", list);
        cards.sort(function (a, b) {
          var x = a.getAttribute(k), y = b.getAttribute(k), nx = parseFloat(x), ny = parseFloat(y);
          var c = !isNaN(nx) && !isNaN(ny) ? nx - ny : x.localeCompare(y);
          return c * dir || a.getAttribute("data-s-name").localeCompare(b.getAttribute("data-s-name"));
        });
        cards.forEach(function (c) { list.appendChild(c); });
      }
      var saved = get(key, "");
      if (saved && $('option[value="' + saved + '"]', sel)) sel.value = saved;
      sel.addEventListener("change", function () { set(key, sel.value); apply(); });
      apply();
    });
  }

  // ---------- big tabs on many pages: only the chosen panel shows, so there's little to scroll.
  // Remembers the choice per group; data-hash groups also read/write #key; data-count tabs show ticked/total.
  function tabGroups() {
    $$(".dtabs[data-group]").forEach(function (bar) {
      var g = bar.getAttribute("data-group"), btns = $$(".dtab", bar), panels = $$('.dpanel[data-group="' + g + '"]');
      var keys = btns.map(function (b) { return b.getAttribute("data-tab"); });
      function panel(k) { return panels.filter(function (p) { return p.getAttribute("data-tab") === k; })[0]; }
      function show(k, save) {
        btns.forEach(function (b) { var on = b.getAttribute("data-tab") === k; b.setAttribute("aria-selected", on ? "true" : "false"); b.tabIndex = on ? 0 : -1; });
        panels.forEach(function (p) { p.hidden = p.getAttribute("data-tab") !== k; });
        if (save) set("tm_tab_" + g, k);
      }
      function counts() {
        btns.forEach(function (b) {
          if (!b.hasAttribute("data-count")) return;
          var p = panel(b.getAttribute("data-tab")); if (!p) return;
          var cbs = $$('input[type="checkbox"][data-key]', p), n = cbs.filter(function (c) { return c.checked; }).length;
          var big = $(".dt-big", b); if (big) big.textContent = n + " / " + cbs.length;
          b.classList.toggle("all-done", cbs.length > 0 && n === cbs.length);
        });
      }
      btns.forEach(function (b, i) {
        b.addEventListener("click", function () {
          var k = b.getAttribute("data-tab"); show(k, true);
          if (bar.hasAttribute("data-hash")) { try { history.replaceState(null, "", "#" + k); } catch (e) { /* file:// */ } }
        });
        b.addEventListener("keydown", function (e) {
          var d = e.key === "ArrowRight" ? 1 : e.key === "ArrowLeft" ? -1 : 0; if (!d) return;
          var n = btns[(i + d + btns.length) % btns.length]; n.focus(); n.click(); e.preventDefault();
        });
      });
      document.addEventListener("change", counts);
      document.addEventListener("click", function (e) { if (e.target.closest("#bag-reset")) setTimeout(counts, 0); });
      counts();
      var h = location.hash.replace("#", ""), saved = get("tm_tab_" + g, ""), def = bar.getAttribute("data-default");
      show(bar.hasAttribute("data-hash") && keys.indexOf(h) >= 0 ? h : keys.indexOf(saved) >= 0 ? saved : keys.indexOf(def) >= 0 ? def : keys[0], false);
    });
  }

  // ---------- light / dark switch (saved on this phone; the <head> script applies it before the page paints)
  function themeSwitch() {
    var btn = $("#theme-btn"); if (!btn) return;
    var root = document.documentElement, mq = window.matchMedia ? window.matchMedia("(prefers-color-scheme: dark)") : null;
    function current() { return root.getAttribute("data-theme") || (mq && mq.matches ? "dark" : "light"); }
    function label() {
      var dark = current() === "dark";
      btn.setAttribute("aria-label", dark ? S.toLight : S.toDark); btn.title = dark ? S.toLight : S.toDark;
      btn.setAttribute("data-mode", dark ? "dark" : "light");
    }
    btn.addEventListener("click", function () {
      var next = current() === "dark" ? "light" : "dark";
      root.setAttribute("data-theme", next); set("tm_theme", next); label();
    });
    label();
  }

  // ---------- breast milk: "use by" from when it was expressed and where it is stored (KKM times)
  function milk() {
    var box = $("#milk-tool"); if (!box) return;
    var when = $("#milk-when"), where = $("#milk-where"), out = $("#milk-result");
    var n = new Date(); n.setMinutes(n.getMinutes() - n.getTimezoneOffset());
    when.value = n.toISOString().slice(0, 16);
    function render() {
      var t = when.value ? new Date(when.value) : null, opt = where.options[where.selectedIndex];
      if (!t || isNaN(t)) { out.innerHTML = ""; return; }
      var hrs = parseFloat(opt.getAttribute("data-h")), use = new Date(t.getTime() + hrs * 3600 * 1000);
      var txt = use.toLocaleString(LOCALE, { weekday: "short", day: "numeric", month: "short", hour: "numeric", minute: "2-digit" });
      out.innerHTML = '<div class="stat t1"><p class="stat-label">' + esc(S.milkUseBy) + '</p><p class="stat-big">' + esc(txt) + "</p>" +
        '<p class="stat-small">' + esc(fill(S.milkLabel, { a: t.toLocaleString(LOCALE, { day: "numeric", month: "short", hour: "numeric", minute: "2-digit" }) })) + "</p></div>";
    }
    when.addEventListener("input", render); where.addEventListener("change", render); render();
  }

  // ---------- baby names: search, filter by boy/girl, favourites saved on this phone
  function names() {
    var box = $("#names-tool"); if (!box) return;
    var q = $("#nm-q"), list = $("#nm-list"), fav = get("tm_names_fav", {}), filter = "all", origin = "all";
    var oBtns = $$(".nm-origin .chip-btn", box);
    oBtns.forEach(function (b) { b.addEventListener("click", function () {
      origin = b.getAttribute("data-o"); oBtns.forEach(function (o) { o.setAttribute("aria-pressed", o === b ? "true" : "false"); }); render(); }); });
    var segs = $$(".nm-seg button", box), letter = "all", azBtns = $$("#nm-az button", box), count = $("#nm-count");
    azBtns.forEach(function (b) { b.addEventListener("click", function () {
      letter = b.getAttribute("data-l"); azBtns.forEach(function (o) { o.setAttribute("aria-pressed", o === b ? "true" : "false"); }); render(); }); });
    function render() {
      var qq = (q.value || "").toLowerCase().trim(), rows = (TM.names || []).filter(function (n) {
        if (filter === "fav" && !fav[n[0]]) return false;
        if (origin !== "all" && n[3] !== origin) return false;
        if (filter === "m" || filter === "f") { if (n[1] !== filter) return false; }
        if (letter !== "all" && n[0].charAt(0).toUpperCase() !== letter) return false;
        return !qq || (n[0] + " " + n[2]).toLowerCase().indexOf(qq) >= 0;
      }).sort(function (a, b) { return a[0].localeCompare(b[0]); });
      count.textContent = fill(S.nmCount, { n: rows.length });
      var lastL = "";
      list.innerHTML = rows.length ? rows.map(function (n) {
        var L = n[0].charAt(0).toUpperCase(), head = "";
        if (letter === "all" && L !== lastL) { head = '<li class="nm-letter" aria-hidden="true">' + esc(L) + "</li>"; lastL = L; }
        return head + '<li class="nm-' + n[1] + '"><div><strong>' + esc(n[0]) + '</strong><span class="muted">' + esc(n[2]) + "</span></div>" +
          '<button type="button" class="nm-fav" data-n="' + esc(n[0]) + '" aria-pressed="' + (fav[n[0]] ? "true" : "false") + '" aria-label="' + esc(S.nmFav) + '">' + (fav[n[0]] ? "♥" : "♡") + "</button></li>";
      }).join("") : '<li class="muted">' + esc(S.nmNone) + "</li>";
    }
    segs.forEach(function (b) { b.addEventListener("click", function () {
      filter = b.getAttribute("data-f"); segs.forEach(function (o) { o.setAttribute("aria-pressed", o === b ? "true" : "false"); }); render(); }); });
    q.addEventListener("input", render);
    list.addEventListener("click", function (e) {
      var b = e.target.closest(".nm-fav"); if (!b) return;
      var k = b.getAttribute("data-n"); if (fav[k]) delete fav[k]; else fav[k] = 1; set("tm_names_fav", fav); render();
    });
    render();
  }

  // ---------- fertile days: ovulation about 14 days before the next period
  function fertility() {
    var box = $("#fert-tool"); if (!box) return;
    var lmp = $("#fert-lmp"), cyc = $("#fert-cycle"), out = $("#fert-result"), st = get("tm_fert", {});
    if (st.lmp) lmp.value = st.lmp; if (st.cycle) cyc.value = st.cycle;
    function render() {
      var d = parseDate(lmp.value), c = Math.max(21, Math.min(40, parseInt(cyc.value, 10) || 28));
      if (!d) { out.innerHTML = ""; return; }
      set("tm_fert", { lmp: lmp.value, cycle: c });
      var ov = addDays(d, c - 14), from = addDays(ov, -5), to = addDays(ov, 1), next = addDays(d, c), due = addDays(d, 280);
      out.innerHTML = '<div class="stats">' +
        '<div class="stat t1"><p class="stat-label">' + esc(S.fWindow) + '</p><p class="stat-big">' + esc(fmt(from).replace(/ \d{4}$/, "")) + " – " + esc(fmt(to)) + '</p><p class="stat-small">' + esc(S.fWindowSmall) + "</p></div>" +
        '<div class="stat t2"><p class="stat-label">' + esc(S.fOv) + '</p><p class="stat-big">' + esc(fmt(ov)) + "</p></div>" +
        '<div class="stat t3"><p class="stat-label">' + esc(S.fNext) + '</p><p class="stat-big">' + esc(fmt(next)) + '</p><p class="stat-small">' + esc(fill(S.fDue, { d: fmt(due) })) + "</p></div></div>";
    }
    lmp.addEventListener("change", render); cyc.addEventListener("input", render); render();
  }

  // ---------- kick counter + contraction timer (kept on this phone)
  function labour() {
    var k = $("#kick-tool");
    if (k) {
      var kc = $("#kick-count"), kt = $("#kick-time"), kst = get("tm_kicks", { start: 0, n: 0 }), timer;
      function kr() {
        kc.textContent = kst.n;
        if (!kst.start) { kt.textContent = S.kickIdle; return; }
        var mins = Math.floor((Date.now() - kst.start) / 60000);
        kt.textContent = kst.n >= 10 ? fill(S.kickDone, { m: mins }) : fill(S.kickRunning, { m: mins });
      }
      $("#kick-btn").addEventListener("click", function () { if (!kst.start) kst.start = Date.now(); kst.n += 1; set("tm_kicks", kst); kr(); });
      $("#kick-reset").addEventListener("click", function () { kst = { start: 0, n: 0 }; set("tm_kicks", kst); kr(); });
      timer = setInterval(kr, 30000); kr();
    }
    var c = $("#con-tool");
    if (c) {
      var btn = $("#con-btn"), log = $("#con-log"), sum = $("#con-sum"), cst = get("tm_con", []), cur = null, tick;
      function mmss(ms) { var s2 = Math.round(ms / 1000); return Math.floor(s2 / 60) + ":" + ("0" + (s2 % 60)).slice(-2); }
      function cr() {
        btn.textContent = cur ? S.conStop : S.conStart;
        btn.classList.toggle("running", !!cur);
        var rows = cst.slice(-8).reverse();
        log.innerHTML = rows.map(function (r, i) {
          var prev = cst[cst.length - 1 - i - 1];
          return "<li><span>" + new Date(r.s).toLocaleTimeString(LOCALE, { hour: "numeric", minute: "2-digit" }) + "</span><span>" + esc(S.conLasts) + " <strong>" + mmss(r.e - r.s) +
            "</strong></span><span>" + (prev ? esc(S.conApart) + " <strong>" + mmss(r.s - prev.s) + "</strong>" : "") + "</span></li>";
        }).join("");
        var last = cst.slice(-4);
        if (last.length >= 3) {
          var gaps = [], lens = [];
          for (var i = 1; i < last.length; i++) gaps.push(last[i].s - last[i - 1].s);
          last.forEach(function (r) { lens.push(r.e - r.s); });
          var avg = function (a) { return a.reduce(function (x, y) { return x + y; }, 0) / a.length; };
          sum.textContent = fill(S.conAvg, { gap: mmss(avg(gaps)), len: mmss(avg(lens)) });
        } else sum.textContent = S.conHint;
      }
      btn.addEventListener("click", function () {
        if (!cur) { cur = { s: Date.now() }; tick = setInterval(function () { btn.textContent = S.conStop + " · " + mmss(Date.now() - cur.s); }, 1000); }
        else { clearInterval(tick); cur.e = Date.now(); cst.push(cur); cur = null; set("tm_con", cst.slice(-50)); }
        cr();
      });
      $("#con-reset").addEventListener("click", function () { cst = []; set("tm_con", cst); cr(); });
      cr();
    }
  }

  // ---------- hospital bag
  function bag() {
    var boxes = $$("input[data-key]"); if (!boxes.length) return;
    var storeEl = document.querySelector("[data-store]");
    var storeKey = storeEl ? storeEl.getAttribute("data-store") : "tm_bag";
    var txtProg = (storeEl && storeEl.getAttribute("data-progress")) || S.bagProgress;
    var txtDone = (storeEl && storeEl.getAttribute("data-done")) || S.bagDone;
    var st = get(storeKey, {}), prog = $("#bag-progress");
    function upd() {
      var n = boxes.filter(function (b) { return b.checked; }).length;
      prog.textContent = n === boxes.length ? txtDone : fill(txtProg, { n: n, t: boxes.length });
      var bar = $("#bag-bar"); if (bar) bar.style.width = Math.round(n / boxes.length * 100) + "%";
    }
    boxes.forEach(function (b) {
      b.checked = !!st[b.getAttribute("data-key")];
      b.addEventListener("change", function () { st[b.getAttribute("data-key")] = b.checked; set(storeKey, st); upd(); });
    });
    $("#bag-reset").addEventListener("click", function () { st = {}; set(storeKey, st); boxes.forEach(function (b) { b.checked = false; }); upd(); });
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
      // three stat tiles: mum's leave, back to work, dad's leave
      function tile(label, big, small, cls) {
        return '<div class="stat ' + (cls || "") + '"><p class="stat-label">' + esc(label) + '</p><p class="stat-big">' + esc(big) + "</p>" +
          (small ? '<p class="stat-small">' + esc(small) + "</p>" : "") + "</div>";
      }
      var h = '<div class="stats">' +
        tile(S.lvMatEnds, fmt(addDays(m, 97)), fill(S.lvStarts, { a: fmt(m), n: 98 }), "t1") +
        tile(S.lvBackLbl, fmt(addDays(m, 98)), S.lvBackNote, "t2") +
        tile(S.lvPatEnds, fmt(addDays(p, 6)), fill(S.lvStarts, { a: fmt(p), n: 7 }), "t3") + "</div>";
      if (diffDays(m, b) > 30) h += '<p class="err">' + esc(S.lvEarly) + "</p>";
      out.innerHTML = h;
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
    var picsReady = fetch(TM.root + "data/product-images.json?v=" + TM.ver).then(function (r) { return r.ok ? r.json() : {}; })
      .then(function (j) { pics = j || {}; }).catch(function () { /* pictures are optional */ });
    Promise.all([fetch(TM.root + "data/prices-summary.json?v=" + TM.ver).then(function (r) { if (!r.ok) throw 0; return r.json(); }), picsReady]).then(function (res) {
      var data = res[0];
      var sortSel = $("#pr-sort");
      function nameOf(it) { return LANG === "ms" && it.nm ? it.nm : it.n; }
      if (sortSel) {
        sortSel.value = get("tm_pr_sort", "unit");
        sortSel.addEventListener("change", function () { set("tm_pr_sort", sortSel.value); draw(cur.state, cur.district); });
      }
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
        var html = "";  // the area is already visible in the drop-downs
        var sortBy = sortSel ? sortSel.value : "unit";
        (TM.grpOrder || ["mum", "infant", "followon", "growing", "diaper", "food"]).forEach(function (g) {
          var codes = Object.keys(data.items).filter(function (c) { return data.items[c].g === g && area[c]; });
          if (!codes.length) return;
          codes.forEach(function (c) {
            var it = data.items[c], a = area[c];
            it._unit = it.gr ? a[0] / it.gr * 100 : (it.pc ? a[0] / it.pc : 0);
          });
          codes.sort(function (x, y) {
            var X = data.items[x], Y = data.items[y], ax = area[x], ay = area[y];
            if (sortBy === "az") return nameOf(X).localeCompare(nameOf(Y));
            if (sortBy === "shops") return ay[2] - ax[2];
            if (sortBy === "from") return ax[1] - ay[1];
            if (sortBy === "typical" || !X._unit || !Y._unit) return ax[0] - ay[0];
            return X._unit - Y._unit;
          });
          html += '<section class="price-group" id="grp-' + g + '" data-g="' + g + '"><h2>' + esc(S.grp[g]) +
            ((g === "infant" || g === "followon") ? " " + makeTip(esc(S.bfNote)) : "") + '</h2><div class="table-wrap"><table><thead><tr><th>' + esc(S.cProduct) +
            '</th><th class="num">' + esc(S.cTypical) + '</th><th class="num hide-sm">' + esc(S.cFrom) + '</th><th class="num">' + esc(S.cUnit) +
            '</th><th class="num hide-sm">' + esc(S.cShops) + "</th></tr></thead><tbody>";
          codes.forEach(function (c) {
            var it = data.items[c], a = area[c];
            var pack = it.pc ? it.u + " · " + (it.t === "pants" ? S.pants : S.tape) : it.u;
            var unit = it._unit ? rm(it._unit) + '<small class="per">' + esc(it.gr ? S.per100 : S.perPiece) + "</small>" : '<span class="muted">–</span>';
            // Photos only - formula still gets no shop links, ads or commission.
            var pic = pics[c] ?
              '<img class="thumb" src="https://down-my.img.susercontent.com/file/' + encodeURIComponent(pics[c]) + '_tn" alt="" loading="lazy" width="48" height="48">' : "";
            html += '<tr data-code="' + c + '" data-name="' + esc((it.n + " " + (it.nm || "") + " " + S.grp[g]).toLowerCase()) + '"><td class="prod"><div class="prod-row">' + pic + "<div>" + esc(nameOf(it)) + "<small>" + esc(pack) +
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
        var code = tr.getAttribute("data-code"), st = cur.state, di = cur.district;
        var it0 = data.items[code];
        // Online prices (Shopee, Lazada, pharmacies) are often cheaper than shop shelves - Google Shopping lists them.
        var online = '<a class="online" href="https://www.google.com/search?tbm=shop&amp;q=' + encodeURIComponent(nameOf(it0) + " " + it0.u) +
          '" target="_blank" rel="noopener">' + esc(S.online) + " ↗</a>";
        if (!cur.state) { cell.innerHTML = esc(S.chooseState) + "<br>" + online; return; }
        var p = shopCache[st] || fetch(TM.root + "data/shops/" + slug(st) + ".json?v=" + TM.ver).then(function (r) { if (!r.ok) throw 0; return r.json(); });
        shopCache[st] = p;
        p.then(function (sd) {
          var list = [];
          Object.keys(sd.d).forEach(function (d) {
            if (di && d !== di) return;
            (sd.d[d][code] || []).forEach(function (x) { list.push(x); });
          });
          list.sort(function (a, b) { return a[1] - b[1]; });
          list = list.slice(0, 5);
          if (!list.length) { cell.innerHTML = esc(S.noShops) + "<br>" + online; return; }
          cell.innerHTML = '<ul class="shop-list">' + list.map(function (x) {
            var s = sd.p[x[0]] || ["?", "", ""];
            return "<li><strong>" + rm(x[1]) + "</strong> · " + esc(s[0]) + ' <span class="muted">(' + esc(s[1]) + ")</span>" +
              '<span class="addr">' + esc(s[2]) + " · " + esc(fmt(parseDate(x[2]))) + "</span></li>";
          }).join("") + "</ul>" + online;
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
    fetch(TM.root + "data/districts.json?v=" + TM.ver).then(function (r) { if (!r.ok) throw 0; return r.json(); }).then(function (states) {
      areaPicker($("#nu-state"), $("#nu-district"), states, function (s, d) {
        links.hidden = !s;
        if (!s) return;
        var place = (d ? d + ", " : "") + s;
        ta.href = maps("taska " + place); ta.textContent = fill(S.nuTaska, { area: d || s }) + " ↗";
        td.href = maps("tadika " + place); td.textContent = fill(S.nuTadika, { area: d || s }) + " ↗";
      });
    }).catch(function () { /* near-me buttons still work */ });
  }

  // ---------- freshness: GitHub Pages lets browsers keep pages ~10 min; if this page is an old saved copy, reload once
  // An old saved copy of a page (browser cache, or "back") gets swapped for the new one.
  // Checked on every page and every time a page is shown again; at most one reload per page per new version.
  function freshness() {
    if (!TM.ver || !window.fetch) return;
    try {  // tidy the address bar after a refresh (drop the ?v= we added)
      var u0 = new URL(location.href);
      if (u0.searchParams.has("v")) { u0.searchParams.delete("v"); history.replaceState(null, "", u0.pathname + u0.search + u0.hash); }
    } catch (e) { /* old browser */ }
    function check() {
      fetch(TM.root + "version.json?t=" + Date.now(), { cache: "no-store" }).then(function (r) { return r.ok ? r.json() : null; }).then(function (j) {
        if (!j || !j.v || j.v === TM.ver) return;
        var key = "tm_reloaded_" + j.v + "_" + location.pathname;
        try { if (sessionStorage.getItem(key)) return; sessionStorage.setItem(key, "1"); } catch (e) { return; }
        try {  // a new address makes the browser fetch the page again instead of reusing its saved copy
          var u = new URL(location.href); u.searchParams.set("v", j.v); location.replace(u.toString());
        } catch (e) { location.reload(); }
      }).catch(function () { /* offline: keep the saved copy */ });
    }
    check();
    window.addEventListener("pageshow", function (e) { if (e.persisted) check(); });
  }

  // ---------- menu (a <details> drop-down on the left): close on outside click, Escape or after picking
  // On laptops (>= 1100px wide) the menu is pinned open as a sidebar on the left; on phones it's the ☰ drop-down.
  function menu() {
    var m = $("details.menu"); if (!m) return;
    var wide = window.matchMedia("(min-width: 1100px)");
    function pin() {
      document.documentElement.classList.toggle("pinned", wide.matches);
      if (wide.matches) m.open = true; else m.open = false;
    }
    pin();
    if (wide.addEventListener) wide.addEventListener("change", pin); else wide.addListener(pin);
    m.addEventListener("toggle", function () { if (wide.matches && !m.open) m.open = true; });
    document.addEventListener("click", function (e) { if (!wide.matches && m.open && !m.contains(e.target)) m.open = false; });
    document.addEventListener("keydown", function (e) { if (!wide.matches && e.key === "Escape" && m.open) { m.open = false; $("summary", m).focus(); } });
    $$(".menu-panel a", m).forEach(function (a) { a.addEventListener("click", function () { if (!wide.matches) m.open = false; }); });
    // one section open at a time (older browsers ignore <details name>)
    var grps = $$(".menu-grp", m);
    grps.forEach(function (d) { d.addEventListener("toggle", function () { if (d.open) grps.forEach(function (o) { if (o !== d) o.open = false; }); }); });
  }

  // ---------- ⓘ tips: hover on computers, tap on phones; one open at a time, kept on screen
  function makeTip(htmlText) {
    return '<span class="tip"><button type="button" class="tip-btn" aria-label="' + esc(S.moreInfo) + '" aria-expanded="false">i</button>' +
      '<span class="tip-bubble" role="tooltip">' + htmlText + "</span></span>";
  }
  function place(t) {
    var b = $(".tip-bubble", t); b.style.marginLeft = "0px";
    var r = b.getBoundingClientRect(), vw = document.documentElement.clientWidth;
    if (r.right > vw - 8) b.style.marginLeft = -(r.right - vw + 8) + "px";
    else if (r.left < 8) b.style.marginLeft = (8 - r.left) + "px";
  }
  function tips() {
    document.addEventListener("click", function (e) {
      var btn = e.target.closest(".tip-btn");
      $$(".tip.open").forEach(function (t) { if (!btn || !t.contains(btn)) { t.classList.remove("open"); $(".tip-btn", t).setAttribute("aria-expanded", "false"); } });
      if (btn) {
        e.preventDefault(); e.stopPropagation();
        var t = btn.parentNode, on = !t.classList.contains("open");
        t.classList.toggle("open", on); btn.setAttribute("aria-expanded", on ? "true" : "false");
        if (on) place(t);
      }
    });
    document.addEventListener("mouseover", function (e) { var t = e.target.closest(".tip"); if (t) place(t); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") $$(".tip.open").forEach(function (t) { t.classList.remove("open"); }); });
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

  // ---------- shared: baby's birth date typed on any page (vaccines, documents, aqiqah, growth, solids)
  function babyBirth() {
    var b = get("tm_baby_birth", "");
    if (b) return b;
    var vx = get("tm_vax", {}), dc = get("tm_docs_info", {}), pt = get("tm_pantang", {});
    return vx.birth || dc.birth || (pt.kind === "birth" ? pt.date : "") || "";
  }
  function addMonthsU(d, m) { var x = new Date(d.getTime()); x.setUTCMonth(x.getUTCMonth() + m); return x; }

  // ---------- antenatal check-ups: dated list from the due date (LMP = due - 280 days), ticks saved
  function antenatal() {
    var box = $("#ante-tool"); if (!box) return;
    var input = $("#ante-due"), out = $("#ante-result"), st = get("tm_ante", { due: "", done: {} });
    input.value = st.due || get("tm_due", "") || "";
    function render() {
      var due = parseDate(input.value);
      if (!due) { out.innerHTML = ""; return; }
      var lmp = addDays(due, -280), t = today(), ga = diffDays(lmp, t);
      if (ga < -30 || ga > 50 * 7) { out.innerHTML = '<p class="err">' + esc(S.badDate) + "</p>"; return; }
      st.due = input.value; set("tm_ante", st); set("tm_due", input.value);
      var html = ga >= 0 && ga <= 42 * 7 ? '<p class="ante-now">' + esc(fill(S.weeksDays, { w: Math.floor(ga / 7), d: ga % 7 })) + "</p>" : "";
      var nextDone = false;
      html += '<ol class="vax-list ante-list">';
      (TM.ante || []).forEach(function (it) {
        var k = it[0], a = it[1], b = it[2], start = addDays(lmp, a * 7), end = addDays(lmp, b * 7 + (b > a ? -1 : 0));
        var done = !!st.done[k], when, cls = done ? "done" : "";
        if (k === "booking") when = fill(S.anteBefore, { d: fmt(addDays(lmp, 12 * 7)) });
        else if (a === b) when = fmt(start);
        else when = fmt(start) + " – " + fmt(end);
        var label = k === "post" ? S.antePost : a === 0 ? fill(S.anteBeforeWk, { b: b }) : a === b ? fill(S.anteWeek, { a: a }) : fill(S.anteWeeks, { a: a, b: b });
        if (!done) {
          if (t >= start && t <= end && k !== "kicks") cls = "now";
          else if (t > end) cls = "late";
          if (!nextDone && t <= end && k !== "kicks") { cls += " next"; nextDone = true; }
        }
        html += '<li class="' + cls + '"><label class="vax-check"><input type="checkbox" data-k="' + esc(k) + '"' + (done ? " checked" : "") + ' aria-label="' + esc(it[4]) + '"></label>' +
          '<div class="vax-main"><span class="vax-age">' + esc(label) + "</span><strong>" + esc(it[3] + " " + it[4]) + "</strong>" +
          (it[5] ? '<span class="ante-tip">' + esc(it[5]) + "</span>" : "") +
          (it[6] ? ' <a class="ante-link" href="' + esc(it[6]) + '">' + esc(S.anteOpen) + " →</a>" : "") +
          (cls.indexOf("late") >= 0 && k !== "post" && k !== "due" ? '<span class="ante-miss">' + esc(S.anteMissed) + "</span>" : "") +
          '</div><span class="vax-date">' + esc(when) + "</span></li>";
      });
      out.innerHTML = html + "</ol>";
    }
    input.addEventListener("change", render);
    out.addEventListener("change", function (e) {
      var cb = e.target.closest("input[data-k]"); if (!cb) return;
      st.done[cb.getAttribute("data-k")] = cb.checked; set("tm_ante", st); render();
    });
    render();
  }

  // ---------- first-year budget: all numbers editable, saved as typed
  function rm0(n) { return "RM" + Math.round(n).toLocaleString("en-MY"); }
  function budget() {
    var box = $("#bud-tool"); if (!box) return;
    var out = $("#bud-result"), st = get("tm_budget", {});
    var fields = $$("select[name], input[name]", box);
    fields.forEach(function (f) { if (st[f.name] !== undefined && st[f.name] !== null) f.value = st[f.name]; });
    function num(name) { var f = $('[name="' + name + '"]', box), v = parseFloat(f && f.value); return isFinite(v) && v > 0 ? v : 0; }
    function pick(name) {
      var sel = $('select[name="' + name + '"]', box), custom = sel.value === "custom";
      $('.bud-custom[data-for="' + name + '"]', box).hidden = !custom;
      return custom ? num(name + "_rm") : parseFloat(sel.value) || 0;
    }
    function render() {
      var rows = [
        [S.budDeliv, pick("deliv")],
        [S.budConf, pick("conf")],
        [fill(S.budDiaper, { n: num("dpd") }), num("dpd") * num("dprice") * 365],
        [S.budMilk, num("milk") * 12],
        [S.budItems, num("items")],
        [fill(S.budCare, { m: Math.min(12, num("care_m")) }), num("care") * Math.min(12, num("care_m"))]
      ];
      var total = rows.reduce(function (s, r) { return s + r[1]; }, 0);
      var html = '<ul class="bud-lines">' + rows.map(function (r) {
        return "<li><span>" + esc(r[0]) + "</span><strong>" + esc(rm0(r[1])) + "</strong></li>";
      }).join("") + "<li><span>" + esc(S.budVax) + "</span><strong>" + esc(S.budFree) + "</strong></li></ul>" +
        '<div class="bud-total"><span>' + esc(S.budTotal) + '</span><strong>' + esc(rm0(total)) + "</strong>" +
        '<small>' + esc(fill(S.budMonth, { rm: rm0(total / 12) })) + "</small></div>";
      out.innerHTML = html;
      fields.forEach(function (f) { st[f.name] = f.value; });
      set("tm_budget", st);
    }
    box.addEventListener("input", render);
    box.addEventListener("change", render);
    render();
  }

  // ---------- EPDS: scored on this page only, nothing saved
  function epds() {
    var form = $("#epds"); if (!form) return;
    var out = $("#epds-result");
    function render() {
      var n = 0, score = 0, q10 = 0;
      for (var i = 1; i <= 10; i++) {
        var c = $('input[name="q' + i + '"]:checked', form);
        if (c) { n++; score += +c.value; if (i === 10) q10 = +c.value; }
      }
      var html = "";
      if (q10 > 0) html += '<div class="box danger epds-urgent"><p><strong>' + esc(S.epdsUrgent) + "</strong></p></div>";
      if (n < 10) { out.innerHTML = html + '<p class="hint">' + esc(fill(S.epdsDone, { n: n })) + "</p>"; return; }
      var high = score >= 12;
      html += '<div class="result epds-res ' + (high ? "high" : "low") + '"><p class="epds-score">' + esc(fill(S.epdsScore, { s: score })) + "</p>" +
        "<p>" + esc(high ? S.epdsHigh : S.epdsLow) + '</p><p class="small muted">' + esc(S.epdsPrivate) + "</p></div>";
      out.innerHTML = html;
    }
    form.addEventListener("change", render);
    render();
  }

  // ---------- aqiqah: 7th / 14th / 21st day (birth day = day 1)
  function aqiqah() {
    var box = $("#aq-tool"); if (!box) return;
    var input = $("#aq-birth"), out = $("#aq-result");
    input.value = babyBirth();
    function render() {
      var b = parseDate(input.value);
      if (!b) { out.innerHTML = ""; return; }
      set("tm_baby_birth", input.value);
      var t = today(), html = '<div class="stats">';
      [[7, S.aq7], [14, S.aq14], [21, S.aq21]].forEach(function (d, i) {
        var day = addDays(b, d[0] - 1), left = diffDays(t, day);
        var small = left > 0 ? fill(S.aqLeft, { n: left }) : left === 0 ? S.aqToday : S.aqPassed;
        html += '<div class="stat' + (i < 2 ? " t" + (i + 1) : "") + (left < 0 ? " past" : "") + '"><p class="stat-label">' + esc(d[1]) + '</p><p class="stat-big">' +
          esc(fmt(day)) + '</p><p class="stat-small">' + esc(small) + "</p></div>";
      });
      out.innerHTML = html + "</div>";
    }
    input.addEventListener("change", render);
    render();
  }

  // ---------- first foods: 6-month and 1-year dates
  function solids() {
    var box = $("#sol-tool"); if (!box) return;
    var input = $("#sol-birth"), out = $("#sol-result");
    input.value = babyBirth();
    function render() {
      var b = parseDate(input.value);
      if (!b) { out.innerHTML = ""; return; }
      set("tm_baby_birth", input.value);
      var t = today(), six = addMonthsU(b, 6), one = addMonthsU(b, 12), l6 = diffDays(t, six), l12 = diffDays(t, one);
      out.innerHTML = '<div class="stats"><div class="stat t1' + (l6 < 0 ? " past" : "") + '"><p class="stat-label">' + esc(S.solSix) + '</p><p class="stat-big">' + esc(fmt(six)) +
        '</p><p class="stat-small">' + esc(l6 > 0 ? fill(S.aqLeft, { n: l6 }) : S.solStarted) + '</p></div><div class="stat t2' + (l12 < 0 ? " past" : "") + '"><p class="stat-label">' + esc(S.solOne) +
        '</p><p class="stat-big">' + esc(fmt(one)) + '</p><p class="stat-small">' + esc(S.solOneSmall) + "</p></div></div>";
    }
    input.addEventListener("change", render);
    render();
  }

  // ---------- baby growth: WHO LMS z-score -> "heavier than about N in 100 babies"
  function growth() {
    var box = $("#gr-tool"); if (!box || !TM.who) return;
    var st = get("tm_growth", { sex: "b", birth: "", list: [] });
    if (!st.birth) st.birth = babyBirth();
    var birth = $("#gr-birth"), date = $("#gr-date"), w = $("#gr-w"), l = $("#gr-l"), out = $("#gr-result");
    var sexBtns = $$(".pill-opt[data-sex]", box);
    birth.value = st.birth || ""; date.value = iso(today());
    function setSex(s) { st.sex = s; sexBtns.forEach(function (b) { b.setAttribute("aria-pressed", b.getAttribute("data-sex") === s ? "true" : "false"); }); }
    function lms(tab, months) {
      var i = Math.max(0, Math.min(23, Math.floor(months))), f = Math.max(0, Math.min(1, months - i)), a = tab[i], b = tab[i + 1];
      return [a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f, a[2] + (b[2] - a[2]) * f];
    }
    function zOf(v, p) { return Math.abs(p[0]) < 1e-9 ? Math.log(v / p[1]) / p[2] : (Math.pow(v / p[1], p[0]) - 1) / (p[0] * p[2]); }
    function cdf(z) {  // normal CDF (Abramowitz-Stegun 7.1.26)
      var t = 1 / (1 + 0.3275911 * Math.abs(z) / Math.SQRT2), y = 1 - (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t - 0.284496736) * t + 0.254829592) * t * Math.exp(-z * z / 2);
      return z >= 0 ? (1 + y) / 2 : (1 - y) / 2;
    }
    function judge(v, kind, months, sex) {
      if (!v) return null;
      var p = lms(TM.who[kind][sex], months), z = zOf(v, p), pc = Math.round(cdf(z) * 100);
      pc = Math.max(1, Math.min(99, pc));
      var verdict = z < -2 ? S.grLow : z > 2 ? S.grHigh : S.grOk;
      return { z: z, pc: pc, cls: z < -2 || z > 2 ? "out" : "ok", txt: fill(kind === "w" ? S.grPctW : S.grPctL, { p: pc }), verdict: verdict, med: p[1] };
    }
    function ageOf(b, d) { return diffDays(b, d) / 30.4375; }
    function line(r) { return r ? '<p class="gr-line ' + r.cls + '">' + esc(r.txt) + " <strong>" + esc(r.verdict) + "</strong></p>" : ""; }
    function history() {
      var b = parseDate(st.birth); if (!b || !st.list.length) return "";
      var rows = st.list.slice().sort(function (a, c) { return a.d < c.d ? 1 : -1; }).map(function (m) {
        var d = parseDate(m.d), mo = ageOf(b, d); if (mo < 0 || mo > 24) return "";
        var rw = judge(m.w, "w", mo, st.sex), rl = judge(m.l, "l", mo, st.sex);
        return "<tr><td>" + esc(fmt(d)) + "<br><small>" + esc(fill(S.grAge, { m: Math.floor(mo) })) + "</small></td><td>" + (m.w ? esc(m.w + " kg") + (rw ? '<br><small class="' + rw.cls + '">' + rw.pc + "/100</small>" : "") : "–") +
          "</td><td>" + (m.l ? esc(m.l + " cm") + (rl ? '<br><small class="' + rl.cls + '">' + rl.pc + "/100</small>" : "") : "–") +
          '</td><td><button type="button" class="link-btn muted" data-del="' + esc(m.d) + '" aria-label="' + esc(S.grDel) + '">✕</button></td></tr>';
      }).join("");
      return '<h3 class="gr-h">' + esc(S.grHist) + '</h3><div class="table-wrap"><table class="gr-table"><thead><tr><th>' + esc(S.grWhen) + "</th><th>" + esc(S.grW) + "</th><th>" + esc(S.grL) +
        "</th><th></th></tr></thead><tbody>" + rows + "</tbody></table></div>";
    }
    function show(msg) {
      var b = parseDate(birth.value), d = parseDate(date.value), html = "";
      if (msg) html += '<p class="err">' + esc(msg) + "</p>";
      var last = st.list.filter(function (m) { return m.d === date.value; })[0];
      if (b && d && last) {
        var mo = ageOf(b, d);
        if (mo >= 0 && mo <= 24) {
          var rw = judge(last.w, "w", mo, st.sex), rl = judge(last.l, "l", mo, st.sex), p = lms(TM.who.w[st.sex], mo), q = lms(TM.who.l[st.sex], mo);
          html += '<div class="result gr-res"><p class="gr-age">' + esc(fill(S.grAge, { m: Math.floor(mo) })) + " · " + esc(fmt(d)) + "</p>" + line(rw) + line(rl) +
            '<p class="small muted">' + esc(fill(S.grMed, { w: p[1].toFixed(1), l: q[1].toFixed(1) })) + "</p></div>";
        }
      }
      out.innerHTML = html + history();
    }
    sexBtns.forEach(function (b) { b.addEventListener("click", function () { setSex(b.getAttribute("data-sex")); set("tm_growth", st); show(); }); });
    birth.addEventListener("change", function () { st.birth = birth.value; set("tm_growth", st); if (birth.value) set("tm_baby_birth", birth.value); show(); });
    $("#gr-add").addEventListener("click", function () {
      var b = parseDate(birth.value), d = parseDate(date.value), wv = parseFloat(w.value), lv = parseFloat(l.value);
      if (!b || !d || (!(wv > 0) && !(lv > 0))) return show(S.grNeed);
      if (d < b || d > today()) return show(S.badDate);
      if (ageOf(b, d) > 24) return show(S.grOld);
      if ((wv > 0 && (wv < 1 || wv > 25)) || (lv > 0 && (lv < 40 || lv > 100))) return show(S.badDate);
      st.birth = birth.value; set("tm_baby_birth", birth.value);
      st.list = st.list.filter(function (m) { return m.d !== date.value; });
      st.list.push({ d: date.value, w: wv > 0 ? wv : null, l: lv > 0 ? lv : null });
      set("tm_growth", st); w.value = ""; l.value = ""; show();
    });
    out.addEventListener("click", function (e) {
      var del = e.target.closest("[data-del]"); if (!del) return;
      st.list = st.list.filter(function (m) { return m.d !== del.getAttribute("data-del"); }); set("tm_growth", st); show();
    });
    setSex(st.sex || "b");
    show();
  }

  freshness(); tips(); menu(); dueTool(); homeTabs(); weekMarkers(); pantang(); quotes(); nurseryCompare(); bag(); leave(); prices(); nursery();
  themeSwitch(); vaccines(); afterBirth(); deliveryCost(); stateChips(); cardSort(); tabGroups(); milk(); names(); fertility(); labour(); bot();
  antenatal(); budget(); epds(); aqiqah(); solids(); growth();
})();
