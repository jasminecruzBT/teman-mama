  // ---------- "Tanya ibu-ibu" forum (Supabase REST; all writes go through checked database functions)
  function forum() {
    var box = $("#forum"); if (!box) return;
    var F = TM.forum || {};
    if (!F.url || !F.key) { $("#fm-soon").hidden = false; return; }
    box.hidden = false;
    var API = F.url.replace(/\/$/, "") + "/rest/v1/", H = { apikey: F.key, Authorization: "Bearer " + F.key };
    var dev = get("tm_dev", ""); if (!dev) { dev = Array.prototype.map.call(crypto.getRandomValues(new Uint8Array(12)), function (b) { return ("0" + b.toString(16)).slice(-2); }).join(""); set("tm_dev", dev); }
    var myVotes = get("tm_forum_votes", {}), nick = $("#fm-nick"), list = $("#fm-list"), detail = $("#fm-detail"), listWrap = $("#fm-listwrap");
    nick.value = get("tm_forum_nick", "");
    var topic = "", sortBy = "new", q = "";
    var TOPICS = S.fmTopics || {};
    function api(path, opt) {
      opt = opt || {};
      return fetch(API + path, { method: opt.method || "GET", headers: Object.assign({ "Content-Type": "application/json" }, H, opt.headers || {}), body: opt.body ? JSON.stringify(opt.body) : undefined })
        .then(function (r) { return r.text().then(function (t) { var j = t ? JSON.parse(t) : null; if (!r.ok) throw new Error((j && j.message) || "error"); return j; }); });
    }
    function errText(e) { var m = String(e && e.message || ""); return S["fmErr_" + m] || S.fmErr; }
    function ago(iso) {
      var s = (Date.now() - new Date(iso).getTime()) / 1000, rtf = window.Intl && Intl.RelativeTimeFormat ? new Intl.RelativeTimeFormat(LOCALE, { numeric: "auto" }) : null;
      var u = s < 3600 ? ["minute", -Math.max(1, Math.round(s / 60))] : s < 86400 ? ["hour", -Math.round(s / 3600)] : ["day", -Math.round(s / 86400)];
      return rtf ? rtf.format(u[1], u[0]) : fmt(new Date(iso));
    }
    function votesHtml(kind, p) {
      var mv = myVotes[kind + p.id] || 0;
      return '<div class="fm-votes" data-kind="' + kind + '" data-id="' + p.id + '">' +
        '<button type="button" class="fm-up" aria-pressed="' + (mv === 1) + '" aria-label="' + esc(S.fmUp) + '">👍 <span>' + p.up + "</span></button>" +
        '<button type="button" class="fm-down" aria-pressed="' + (mv === -1) + '" aria-label="' + esc(S.fmDown) + '">👎 <span>' + p.down + "</span></button>" +
        '<button type="button" class="fm-report link-btn muted">' + esc(S.fmReport) + "</button></div>";
    }
    function loadList() {
      var path = "questions?select=id,created_at,topic,title,nickname,up,down,score,answers&limit=40" +
        (topic ? "&topic=eq." + topic : "") + (sortBy === "open" ? "&answers=eq.0" : "") +
        (q ? "&title=ilike." + encodeURIComponent("*" + q.replace(/[*,()]/g, " ") + "*") : "") +
        (sortBy === "top" ? "&order=score.desc,created_at.desc" : "&order=created_at.desc");
      list.innerHTML = '<li class="muted">' + esc(S.fmLoading) + "</li>";
      api(path).then(function (rows) {
        list.innerHTML = rows.length ? rows.map(function (r) {
          return '<li><a class="fm-item" href="#q-' + r.id + '"><span class="fm-topic">' + esc(TOPICS[r.topic] || r.topic) + '</span><strong>' + esc(r.title) + "</strong>" +
            '<span class="fm-meta">' + esc(r.nickname) + " · " + esc(ago(r.created_at)) + " · 💬 " + r.answers + " · 👍 " + r.up + "</span></a></li>";
        }).join("") : '<li class="muted">' + esc(S.fmNone) + "</li>";
      }).catch(function () { list.innerHTML = '<li class="err">' + esc(S.fmLoadFail) + "</li>"; });
    }
    function loadDetail(id) {
      listWrap.hidden = true; detail.hidden = false;
      detail.innerHTML = '<p class="muted">' + esc(S.fmLoading) + "</p>";
      Promise.all([api("questions?id=eq." + id + "&select=id,created_at,topic,title,body,nickname,up,down,answers"),
                   api("answers?question_id=eq." + id + "&select=id,created_at,body,nickname,up,down,score&order=score.desc,created_at.asc")]).then(function (res) {
        var qq = res[0][0], ans = res[1];
        if (!qq) { detail.innerHTML = '<p class="err">' + esc(S.fmGone) + '</p><a class="btn ghost" href="#">← ' + esc(S.fmBack) + "</a>"; return; }
        detail.innerHTML = '<a class="link-btn" href="#">← ' + esc(S.fmBack) + "</a>" +
          '<article class="card fm-q"><span class="fm-topic">' + esc(TOPICS[qq.topic] || qq.topic) + "</span><h2>" + esc(qq.title) + "</h2>" +
          (qq.body ? "<p>" + esc(qq.body) + "</p>" : "") + '<p class="fm-meta">' + esc(qq.nickname) + " · " + esc(ago(qq.created_at)) + "</p>" + votesHtml("q", qq) + "</article>" +
          "<h3>" + esc(fill(S.fmAnswers, { n: ans.length })) + "</h3>" +
          (ans.length ? '<ul class="fm-answers">' + ans.map(function (a) {
            return '<li class="card"><p>' + esc(a.body) + '</p><p class="fm-meta">' + esc(a.nickname) + " · " + esc(ago(a.created_at)) + "</p>" + votesHtml("a", a) + "</li>";
          }).join("") + "</ul>" : '<p class="muted">' + esc(S.fmNoAnswers) + "</p>") +
          '<form class="card fm-form" id="fm-answer"><label class="field">' + esc(S.fmYourAnswer) + '<textarea name="body" rows="4" maxlength="2000" required></textarea></label>' +
          '<p class="hint">' + esc(S.fmRulesShort) + '</p><button type="submit" class="btn">' + esc(S.fmPostAnswer) + '</button><p class="fm-msg" aria-live="polite"></p></form>';
        detail.dataset.id = id;
      }).catch(function () { detail.innerHTML = '<p class="err">' + esc(S.fmLoadFail) + "</p>"; });
    }
    function route() {
      var m = location.hash.match(/^#q-(\d+)$/);
      if (m) loadDetail(m[1]); else { detail.hidden = true; listWrap.hidden = false; loadList(); }
    }
    // voting + reporting (both views)
    box.addEventListener("click", function (e) {
      var v = e.target.closest(".fm-votes"); if (!v) return;
      var kind = v.getAttribute("data-kind"), id = +v.getAttribute("data-id"), key = kind + id;
      if (e.target.closest(".fm-report")) {
        if (!window.confirm(S.fmReportAsk)) return;
        api("rpc/report_post", { method: "POST", body: { p_kind: kind, p_id: id, p_device: dev } }).then(function () { e.target.closest(".fm-report").textContent = S.fmReported; })
          .catch(function (er) { alert(errText(er)); });
        return;
      }
      var want = e.target.closest(".fm-up") ? 1 : e.target.closest(".fm-down") ? -1 : 0; if (!want) return;
      var now = myVotes[key] || 0, val = now === want ? 0 : want;
      api("rpc/cast_vote", { method: "POST", body: { p_kind: kind, p_id: id, p_device: dev, p_value: val } }).then(function () {
        var up = v.querySelector(".fm-up span"), dn = v.querySelector(".fm-down span");
        if (now === 1) up.textContent = +up.textContent - 1; if (now === -1) dn.textContent = +dn.textContent - 1;
        if (val === 1) up.textContent = +up.textContent + 1; if (val === -1) dn.textContent = +dn.textContent + 1;
        if (val) myVotes[key] = val; else delete myVotes[key];
        set("tm_forum_votes", myVotes);
        v.querySelector(".fm-up").setAttribute("aria-pressed", val === 1); v.querySelector(".fm-down").setAttribute("aria-pressed", val === -1);
      }).catch(function (er) { alert(errText(er)); });
    });
    // post an answer
    box.addEventListener("submit", function (e) {
      if (e.target.id !== "fm-answer") return;
      e.preventDefault();
      var f = e.target, msg = f.querySelector(".fm-msg"), btn = f.querySelector("button");
      set("tm_forum_nick", nick.value);
      btn.disabled = true; msg.textContent = "";
      api("rpc/post_answer", { method: "POST", body: { p_question: +detail.dataset.id, p_body: f.body.value, p_nickname: nick.value || S.fmAnon, p_device: dev } })
        .then(function () { loadDetail(detail.dataset.id); })
        .catch(function (er) { msg.textContent = errText(er); msg.className = "fm-msg err"; btn.disabled = false; });
    });
    // ask a question
    var askForm = $("#fm-ask");
    $("#fm-ask-open").addEventListener("click", function () { askForm.hidden = !askForm.hidden; if (!askForm.hidden) askForm.querySelector("[name=title]").focus(); });
    askForm.addEventListener("submit", function (e) {
      e.preventDefault();
      var msg = $("#fm-ask-msg"), btn = askForm.querySelector("button[type=submit]");
      set("tm_forum_nick", nick.value);
      btn.disabled = true; msg.textContent = "";
      api("rpc/ask_question", { method: "POST", body: { p_topic: askForm.topic.value, p_title: askForm.title.value, p_body: askForm.body.value,
        p_nickname: nick.value || S.fmAnon, p_lang: LANG, p_device: dev } })
        .then(function (id) { askForm.reset(); askForm.hidden = true; btn.disabled = false; location.hash = "#q-" + id; })
        .catch(function (er) { msg.textContent = errText(er); msg.className = "err"; btn.disabled = false; });
    });
    $$(".fm-chips .chip-btn", box).forEach(function (c) {
      c.addEventListener("click", function () { topic = c.getAttribute("data-topic"); $$(".fm-chips .chip-btn", box).forEach(function (o) { o.setAttribute("aria-pressed", o === c ? "true" : "false"); }); loadList(); });
    });
    $("#fm-sort").addEventListener("change", function () { sortBy = this.value; loadList(); });
    var qt; $("#fm-q").addEventListener("input", function () { var v = this.value; clearTimeout(qt); qt = setTimeout(function () { q = v.trim(); loadList(); }, 350); });
    window.addEventListener("hashchange", route);
    route();
  }

