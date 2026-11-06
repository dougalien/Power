/* Power — page logic. Plain JavaScript, no build step, works from file:// too. */
(function () {
  "use strict";
  var D = window.POWER_DATA;
  var C = window.POWER_CALC;
  var $ = function (id) { return document.getElementById(id); };

  var state = {
    targetId: "petroleum",
    customQuads: 35.3,
    endUse: 1,
    land: "contiguous",
    log: false,
    densities: {},
    mix: { solar: 50, windSpacing: 50, nuclear: 0, hydro: 0, geothermal: 0, csp: 0 }
  };
  var defaults = {};
  D.SOURCES_LIST.forEach(function (s) { defaults[s.id] = s.density; state.densities[s.id] = s.density; });
  var byId = {};
  D.SOURCES_LIST.forEach(function (s) { byId[s.id] = s; });

  // ---------- formatting ----------
  function sig(n, digits) {
    if (!isFinite(n)) return "∞";
    if (n === 0) return "0";
    var d = digits || 3;
    var p = Math.pow(10, d - 1 - Math.floor(Math.log10(Math.abs(n))));
    return Math.round(n * p) / p;
  }
  function fmt(n, digits) {
    var v = sig(n, digits);
    if (typeof v !== "number") return v;
    return v.toLocaleString("en-US", { maximumSignificantDigits: Math.max(digits || 3, Math.floor(Math.log10(Math.abs(v))) + 1) });
  }
  function fmtPct(p) {
    if (!isFinite(p)) return "∞";
    if (p >= 10) return Math.round(p) + "%";
    if (p >= 1) return p.toFixed(1) + "%";
    if (p >= 0.01) return p.toFixed(2) + "%";
    return "<0.01%";
  }
  function fmtPower(w) {
    if (w >= 1e12) return sig(w / 1e12, 3) + " TW";
    if (w >= 1e9) return sig(w / 1e9, 3) + " GW";
    return sig(w / 1e6, 3) + " MW";
  }
  function el(tag, attrs, text) {
    var e = document.createElement(tag);
    if (attrs) Object.keys(attrs).forEach(function (k) {
      if (k === "style") e.style.cssText = attrs[k]; else e.setAttribute(k, attrs[k]);
    });
    if (text != null) e.textContent = text;
    return e;
  }

  function quads() {
    if (state.targetId === "custom") return Math.max(0, state.customQuads || 0);
    for (var i = 0; i < D.TARGETS.length; i++) if (D.TARGETS[i].id === state.targetId) return D.TARGETS[i].quads;
    return 0;
  }
  function landKm2() { return D.LAND[state.land].km2; }
  function targetLabel() {
    return ({ petroleum: "U.S. petroleum use", fossil: "all U.S. fossil-fuel use", total: "all U.S. energy use", custom: "the custom amount" })[state.targetId];
  }

  // ---------- build controls once ----------
  function buildTarget() {
    var sel = $("target");
    D.TARGETS.forEach(function (t) { sel.appendChild(el("option", { value: t.id }, t.label)); });
    sel.value = state.targetId;
    sel.addEventListener("change", function () {
      state.targetId = sel.value;
      $("custom-wrap").hidden = state.targetId !== "custom";
      render();
    });
    $("custom-quads").addEventListener("input", function (e) { state.customQuads = parseFloat(e.target.value); render(); });
    $("eff").addEventListener("input", function (e) { state.endUse = parseFloat(e.target.value); render(); });
  }

  function buildDensityTable() {
    var body = $("density-body");
    D.SOURCES_LIST.forEach(function (s) {
      var tr = el("tr");
      var tdName = el("td");
      var btn = el("button", { type: "button", "class": "src-name", "aria-expanded": "false" });
      btn.appendChild(el("span", { "class": "swatch", style: "background:" + s.color }));
      btn.appendChild(document.createTextNode(s.name));
      tdName.appendChild(btn);
      var tdVal = el("td", { "class": "num" });
      var input = el("input", { type: "number", min: "0", step: "any", id: "dens-" + s.id, "aria-label": s.name + " power density in watts per square metre" });
      input.value = sig(s.density, 3);
      input.addEventListener("input", function () {
        var v = parseFloat(input.value);
        state.densities[s.id] = v > 0 ? v : 0;
        markChanged();
        render();
      });
      tdVal.appendChild(input);
      tr.appendChild(tdName);
      tr.appendChild(tdVal);
      tr.appendChild(el("td", null, s.basis));
      body.appendChild(tr);

      var noteRow = el("tr", { "class": "note-row", hidden: "" });
      var noteTd = el("td", { colspan: "3" });
      noteTd.textContent = s.note + (s.luie ? " Lovering median: " + s.luie.toLocaleString("en-US") + " ha/TWh/yr." : "");
      noteRow.appendChild(noteTd);
      body.appendChild(noteRow);
      btn.addEventListener("click", function () {
        var open = noteRow.hidden;
        noteRow.hidden = !open;
        btn.setAttribute("aria-expanded", String(open));
      });
    });

    var preset = $("preset");
    Object.keys(D.PRESETS).forEach(function (k) { preset.appendChild(el("option", { value: k }, D.PRESETS[k].label)); });
    preset.addEventListener("change", function () {
      var vals = D.PRESETS[preset.value].values;
      Object.keys(vals).forEach(function (id) { state.densities[id] = vals[id]; });
      syncDensityInputs();
      render();
    });
    $("reset").addEventListener("click", function () {
      Object.keys(defaults).forEach(function (id) { state.densities[id] = defaults[id]; });
      preset.value = "lovering";
      syncDensityInputs();
      render();
    });
  }
  function syncDensityInputs() {
    D.SOURCES_LIST.forEach(function (s) { $("dens-" + s.id).value = sig(state.densities[s.id], 3); });
    markChanged();
  }
  function markChanged() {
    D.SOURCES_LIST.forEach(function (s) {
      var changed = Math.abs(state.densities[s.id] - defaults[s.id]) / defaults[s.id] > 0.005;
      $("dens-" + s.id).classList.toggle("changed", changed);
    });
  }

  function buildMix() {
    var wrap = $("mix-sliders");
    var ids = ["solar", "windSpacing", "nuclear", "hydro", "geothermal", "csp"];
    ids.forEach(function (id) {
      var s = byId[id];
      var row = el("label", { "class": "mix-row" });
      var name = el("span", { "class": "mix-name" });
      name.appendChild(el("span", { "class": "swatch", style: "background:" + s.color }));
      name.appendChild(document.createTextNode(id === "windSpacing" ? "Wind" : s.name));
      var input = el("input", { type: "range", min: "0", max: "100", step: "5", value: String(state.mix[id]) });
      input.style.accentColor = s.color;
      var out = el("output", { id: "mix-out-" + id });
      input.addEventListener("input", function () { state.mix[id] = parseFloat(input.value); render(); });
      row.appendChild(name); row.appendChild(input); row.appendChild(out);
      wrap.appendChild(row);
    });
  }

  function buildDerive() {
    var tgt = $("d-target");
    D.SOURCES_LIST.forEach(function (s) { if (s.clean) tgt.appendChild(el("option", { value: s.id }, s.name)); });
    tgt.value = "windSpacing";
    ["d-mw", "d-area", "d-unit", "d-cf"].forEach(function (id) { $(id).addEventListener("input", renderDerive); });
    $("d-apply").addEventListener("click", function () {
      var v = deriveValue();
      if (v > 0) {
        state.densities[tgt.value] = v;
        syncDensityInputs();
        render();
        $("step-density").scrollIntoView({ behavior: "smooth", block: "start" });
      }
    });
  }
  function deriveValue() {
    var unitToHa = { ha: 1, acre: 0.404686, km2: 100, sqmi: 258.9988 };
    var area = parseFloat($("d-area").value) * unitToHa[$("d-unit").value];
    return C.densityFromPlant(parseFloat($("d-mw").value) || 0, area, (parseFloat($("d-cf").value) || 0) / 100);
  }
  function renderDerive() {
    var v = deriveValue();
    $("d-out").textContent = v > 0 ? "≈ " + fmt(v, 3) + " W/m² of average output" : "Enter a capacity, an area and a capacity factor.";
  }

  function buildSources() {
    var ol = $("source-list");
    Object.keys(D.SOURCES).forEach(function (k) {
      var s = D.SOURCES[k];
      var li = el("li");
      li.appendChild(document.createTextNode(s.text + " "));
      li.appendChild(el("a", { href: s.url, target: "_blank", rel: "noopener" }, s.url.replace(/^https?:\/\//, "")));
      ol.appendChild(li);
    });
  }

  function buildLayton() {
    var wrap = $("layton-bars");
    var rows = D.LAYTON_TABLE1.slice().sort(function (a, b) { return a.jPerM3 - b.jPerM3; });
    var lo = -7, hi = 16; // log10 J/m³ axis
    rows.forEach(function (r) {
      var pos = (Math.log10(r.jPerM3) - lo) / (hi - lo) * 100;
      var row = el("div", { "class": "bar-row", role: "listitem" });
      row.appendChild(el("div", { "class": "bar-label" }, r.name));
      var track = el("div", { "class": "bar-track" });
      track.appendChild(el("div", { "class": "bar-fill", style: "width:" + pos + "%;background:var(--accent)" }));
      var label = el("span", { "class": "bar-value", style: pos > 70 ? "right:" + (100 - pos) + "%;color:var(--accent-ink)" : "left:" + pos + "%" }, r.jPerM3.toExponential(1).replace("e+", " × 10^").replace("e-", " × 10^-") + " J/m³");
      track.appendChild(label);
      row.appendChild(track);
      wrap.appendChild(row);
    });
  }

  // ---------- render ----------
  function results() {
    var q = quads();
    return D.SOURCES_LIST.map(function (s) {
      var a = C.areaKm2(q, state.densities[s.id], s.clean ? state.endUse : 1);
      return { s: s, km2: a, pct: a / landKm2() * 100 };
    });
  }

  function render() {
    var q = quads();
    var w = C.quadsToWatts(q);
    $("eff-out").textContent = state.endUse.toFixed(2);
    $("target-readout").innerHTML = "<strong>" + fmt(q, 3) + " quadrillion Btu per year</strong> is the same as running <strong>" + fmtPower(w) +
      "</strong> of power around the clock, every hour of the year." +
      (state.endUse < 1 ? " With the efficiency credit, the clean sources must supply " + fmtPower(w * state.endUse) + "." : "");

    var res = results();
    var land = D.LAND[state.land];

    // headline
    var clean = res.filter(function (r) { return r.s.clean; });
    var big = clean.reduce(function (a, b) { return b.km2 > a.km2 ? b : a; });
    var small = clean.reduce(function (a, b) { return b.km2 < a.km2 ? b : a; });
    $("results-headline").innerHTML = "To replace " + targetLabel() + ", the land needed ranges from <strong>" + fmtPct(small.pct) +
      "</strong> of the " + land.label.toLowerCase() + " (" + small.s.name.toLowerCase() + ") to <strong>" + fmtPct(big.pct) + "</strong> (" + big.s.name.toLowerCase() + ").";

    renderBars(res);
    renderSquares(res);
    renderTable(res);
    renderMix();
  }

  function renderBars(res) {
    var wrap = $("bars");
    wrap.innerHTML = "";
    var land = landKm2();
    var maxV = Math.max(land, Math.max.apply(null, res.map(function (r) { return isFinite(r.km2) ? r.km2 : 0; })));
    var minV = Math.min.apply(null, res.map(function (r) { return r.km2 > 0 ? r.km2 : Infinity; }));
    var scaleMax = state.log ? maxV * 1.5 : Math.max(land, maxV) * 1.05;
    var logLo = Math.log10(Math.max(minV / 3, 1e-3)), logHi = Math.log10(scaleMax);
    function pos(v) {
      if (!(v > 0)) return 0;
      if (!isFinite(v)) return 100;
      if (state.log) return Math.max(0, (Math.log10(v) - logLo) / (logHi - logLo) * 100);
      return v / scaleMax * 100;
    }
    var limitPos = pos(land);
    res.forEach(function (r) {
      var row = el("div", { "class": "bar-row", role: "listitem" });
      var lab = el("div", { "class": "bar-label" });
      lab.appendChild(el("span", { "class": "swatch", style: "background:" + r.s.color }));
      lab.appendChild(document.createTextNode(r.s.name));
      row.appendChild(lab);
      var track = el("div", { "class": "bar-track" });
      var p = Math.min(100, pos(r.km2));
      track.appendChild(el("div", { "class": "bar-fill" + (r.pct > 100 ? " over" : ""), style: "width:" + p + "%;background:" + r.s.color }));
      track.appendChild(el("div", { "class": "bar-limit", style: "left:" + limitPos + "%", title: "Total land area" }));
      var text = fmtPct(r.pct) + " · " + fmt(r.km2, 3) + " km²";
      var inside = p > 62;
      track.appendChild(el("span", { "class": "bar-value", style: inside ? "right:" + (100 - p) + "%;color:#fff;text-shadow:0 0 3px rgba(0,0,0,.6)" : "left:" + p + "%" }, text));
      row.appendChild(track);
      wrap.appendChild(row);
    });
    var note = el("div", { "class": "limit-label" }, "Red line = all land in the " + D.LAND[state.land].label.toLowerCase());
    wrap.appendChild(note);
  }

  function renderSquares(res) {
    var svg = $("squares");
    var ns = "http://www.w3.org/2000/svg";
    while (svg.firstChild) svg.removeChild(svg.firstChild);
    var land = landKm2();
    var items = res.filter(function (r) { return r.s.id !== "windFootprint" && isFinite(r.km2) && r.km2 > 0; })
      .sort(function (a, b) { return b.km2 - a.km2; });
    var maxArea = Math.max(land, items.length ? items[0].km2 : 0);
    var full = 380, pad = 10;
    function side(a) { return Math.sqrt(a / maxArea) * full; }
    // land outline
    var ls = side(land);
    var rect = document.createElementNS(ns, "rect");
    rect.setAttribute("x", pad); rect.setAttribute("y", pad + full - ls);
    rect.setAttribute("width", ls); rect.setAttribute("height", ls);
    rect.setAttribute("fill", "var(--track)"); rect.setAttribute("stroke", "var(--limit)"); rect.setAttribute("stroke-width", "2");
    svg.appendChild(rect);
    var t = document.createElementNS(ns, "text");
    t.setAttribute("x", pad + 6); t.setAttribute("y", pad + full - ls + 18);
    t.setAttribute("fill", "var(--muted)"); t.setAttribute("font-size", "13");
    t.textContent = D.LAND[state.land].label;
    svg.appendChild(t);
    items.forEach(function (r) {
      var sd = side(r.km2);
      var sq = document.createElementNS(ns, "rect");
      sq.setAttribute("x", pad); sq.setAttribute("y", pad + full - sd);
      sq.setAttribute("width", Math.max(sd, 1.5)); sq.setAttribute("height", Math.max(sd, 1.5));
      sq.setAttribute("fill", r.s.color); sq.setAttribute("fill-opacity", "0.85");
      sq.setAttribute("stroke", "var(--card)"); sq.setAttribute("stroke-width", "1");
      var title = document.createElementNS(ns, "title");
      title.textContent = r.s.name + ": " + fmtPct(r.pct);
      sq.appendChild(title);
      svg.appendChild(sq);
    });
    var leg = $("squares-legend");
    leg.innerHTML = "";
    items.forEach(function (r) {
      var sp = el("span");
      sp.appendChild(el("span", { "class": "swatch", style: "background:" + r.s.color }));
      sp.appendChild(document.createTextNode(r.s.name + " " + fmtPct(r.pct)));
      leg.appendChild(sp);
    });
  }

  function renderTable(res) {
    var body = $("result-body");
    body.innerHTML = "";
    var tx = D.LAND.texas.km2;
    res.forEach(function (r) {
      var tr = el("tr");
      var td = el("td");
      td.appendChild(el("span", { "class": "swatch", style: "background:" + r.s.color }));
      td.appendChild(document.createTextNode(r.s.name));
      tr.appendChild(td);
      tr.appendChild(el("td", { "class": "num" }, fmt(r.km2, 3)));
      tr.appendChild(el("td", { "class": "num" }, fmt(r.km2 / C.KM2_PER_SQMI, 3)));
      tr.appendChild(el("td", { "class": "num" }, fmtPct(r.pct)));
      tr.appendChild(el("td", { "class": "num" }, fmt(r.km2 / tx, 2)));
      body.appendChild(tr);
    });
  }

  function renderMix() {
    var total = 0;
    Object.keys(state.mix).forEach(function (id) { total += state.mix[id]; });
    var shares = {};
    Object.keys(state.mix).forEach(function (id) {
      shares[id] = total > 0 ? state.mix[id] / total : 0;
      $("mix-out-" + id).textContent = Math.round(shares[id] * 100) + "%";
    });
    if (total === 0) { $("mix-readout").textContent = "Move at least one slider."; return; }
    var a = C.mixAreaKm2(quads(), shares, state.densities, state.endUse);
    var pct = a / landKm2() * 100;
    $("mix-readout").innerHTML = "This mix needs <strong>" + fmt(a, 3) + " km²</strong> (" + fmt(a / C.KM2_PER_SQMI, 3) + " sq mi), which is <strong>" +
      fmtPct(pct) + "</strong> of the " + D.LAND[state.land].label.toLowerCase() + ", or " + fmt(a / D.LAND.texas.km2, 2) + " times the size of Texas.";
  }

  // ---------- init ----------
  buildTarget();
  buildDensityTable();
  buildMix();
  buildDerive();
  buildSources();
  buildLayton();
  $("land").addEventListener("change", function (e) { state.land = e.target.value; render(); });
  $("logscale").addEventListener("change", function (e) { state.log = e.target.checked; render(); });
  renderDerive();
  render();
})();
