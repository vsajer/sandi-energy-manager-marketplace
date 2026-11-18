const numberFormat = new Intl.NumberFormat("cs-CZ", { maximumFractionDigits: 1 });

const layout = `
  <style>
    :host {
      display: block;
      min-height: 100%;
      color: var(--primary-text-color, #142820);
      background: var(--primary-background-color, #eef4f0);
      font-family: var(--paper-font-body1_-_font-family, system-ui, sans-serif);
      --energy-accent: var(--primary-color, #23866a);
      --energy-surface: var(--card-background-color, white);
      --energy-line: var(--divider-color, #d7e3db);
    }
    header {
      position: sticky;
      top: 0;
      z-index: 1;
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 14px;
      min-height: 56px;
      padding: 0 max(16px, env(safe-area-inset-right)) 0 max(12px, env(safe-area-inset-left));
      background: var(--app-header-background-color, var(--energy-surface));
      color: var(--app-header-text-color, inherit);
      box-shadow: 0 1px 0 var(--energy-line);
    }
    .heading, .panel-heading { display: flex; align-items: center; gap: 10px; }
    h1 { margin: 0; font-size: 20px; font-weight: 600; }
    h2 { margin: 0; font-size: 18px; font-weight: 650; }
    ha-icon { --mdc-icon-size: 21px; }
    .panel-heading ha-icon, .tile ha-icon { color: var(--energy-accent); }
    button, a { color: inherit; font: inherit; }
    button { cursor: pointer; }
    .menu { display: none; background: none; border: 0; border-radius: 50%; padding: 8px; }
    :host([narrow]) .menu { display: inline-flex; }
    .settings { text-decoration: none; border: 1px solid currentColor; padding: 7px 12px; border-radius: 10px; white-space: nowrap; }
    .settings:focus-visible, .menu:focus-visible { outline: 2px solid currentColor; outline-offset: 3px; }
    main { max-width: 1180px; margin: auto; padding: 20px 18px 34px; }
    .overview { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 12px; }
    .mode { font-size: 13px; font-weight: 600; padding: 5px 10px; border-radius: 20px;
      border: 1px solid var(--energy-line); background: var(--energy-surface); white-space: nowrap; }
    .metrics, .detail { display: grid; gap: 12px; }
    .metrics { grid-template-columns: repeat(4, minmax(0, 1fr)); margin-bottom: 12px; }
    .detail { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .card, .tile { min-width: 0; background: var(--energy-surface); border: 1px solid var(--energy-line); border-radius: 15px; }
    .tile { padding: 13px; display: grid; gap: 7px; align-content: start; }
    .card { padding: 16px; }
    .tile span, dt, th, .hint { color: var(--secondary-text-color, #516259); font-size: 13px; }
    .tile strong { font-size: clamp(19px, 3vw, 27px); font-weight: 620; overflow-wrap: anywhere; }
    .card.full { grid-column: 1 / -1; }
    progress { width: 100%; height: 6px; accent-color: var(--energy-accent); }
    dl { margin: 10px 0 0; }
    dl div { display: flex; align-items: baseline; justify-content: space-between; gap: 12px;
      padding: 9px 0; border-bottom: 1px solid var(--energy-line); }
    dd { margin: 0; font-size: 14px; text-align: right; overflow-wrap: anywhere; }
    p { margin: 12px 0 0; font-size: 14px; }
    .error { color: var(--error-color, #b62222); overflow-wrap: anywhere; }
    .table-wrap { overflow-x: auto; margin-top: 8px; }
    table { width: 100%; border-collapse: collapse; text-align: left; }
    th, td { padding: 8px 9px 8px 0; border-bottom: 1px solid var(--energy-line); }
    td { font-size: 14px; }
    th:first-child { min-width: 115px; }
    @media (max-width: 720px) {
      .metrics { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .detail { grid-template-columns: minmax(0, 1fr); }
      main { padding: 14px 10px 24px; }
    }
  </style>
  <header>
    <div class="heading">
      <button type="button" class="menu" aria-label="Otevřít postranní nabídku"><ha-icon icon="mdi:menu"></ha-icon></button>
      <h1>Energie domu</h1>
    </div>
    <a class="settings" href="/config/integrations/integration/sandi_energy">Nastavení</a>
  </header>
  <main>
    <div class="overview"><h2>Přehled výkonu</h2><span class="mode" data-field="control"></span></div>
    <section class="metrics" aria-label="Přehled výkonu">
      <div class="tile"><ha-icon icon="mdi:solar-power"></ha-icon><span>Výroba FVE</span><strong data-field="pv"></strong></div>
      <div class="tile"><ha-icon icon="mdi:transmission-tower"></ha-icon><span>Odběr EPS</span><strong data-field="eps"></strong><progress hidden aria-label="Využití limitu EPS"></progress><span data-field="eps_limit"></span></div>
      <div class="tile"><ha-icon icon="mdi:battery-medium"></ha-icon><span>Domácí baterie</span><strong data-field="soc"></strong></div>
      <div class="tile"><ha-icon icon="mdi:clock-outline"></ha-icon><span>Odhad do nabití</span><strong data-field="eta"></strong></div>
    </section>
    <div class="detail">
      <section class="card">
        <div class="panel-heading"><ha-icon icon="mdi:ev-station"></ha-icon><h2>Nabíjení auta</h2></div>
        <dl>
          <div><dt>Režim</dt><dd data-field="ev_mode"></dd></div>
          <div><dt>Zdroj</dt><dd data-field="actual_source"></dd></div>
          <div><dt>Nízký tarif HDO</dt><dd data-field="tariff"></dd></div>
          <div><dt>Příkon nabíječky</dt><dd data-field="ev_power"></dd></div>
          <div><dt>Nastavený / cílový proud</dt><dd data-field="amps"></dd></div>
          <div><dt>Priorita na FVE</dt><dd data-field="ev_priority"></dd></div>
        </dl>
        <p class="hint" data-field="ev_reason"></p><p class="error" data-field="ev_error" hidden></p>
      </section>
      <section class="card">
        <div class="panel-heading"><ha-icon icon="mdi:water-boiler"></ha-icon><h2>Bojler</h2></div>
        <dl>
          <div><dt>Stav termostatu</dt><dd data-field="boiler_mode"></dd></div>
          <div><dt>Teplota vody</dt><dd data-field="temperature"></dd></div>
          <div><dt>Cílový preset regulátoru</dt><dd data-field="target_preset"></dd></div>
          <div><dt>Priorita</dt><dd data-field="boiler_priority"></dd></div>
        </dl>
        <p class="hint" data-field="boiler_reason"></p><p class="error" data-field="boiler_error" hidden></p>
      </section>
      <section class="card full">
        <div class="panel-heading"><ha-icon icon="mdi:power-socket-eu"></ha-icon><h2>Solární zásuvky</h2></div>
        <dl><div><dt>Priorita skupiny</dt><dd data-field="outlet_priority"></dd></div></dl>
        <p class="hint" data-field="outlet_reason"></p>
        <div class="table-wrap" hidden>
          <table><thead><tr><th>Zásuvka</th><th>Priorita</th><th>Příkon</th><th>Stav</th><th>Cíl</th></tr></thead><tbody></tbody></table>
        </div>
      </section>
    </div>
  </main>`;

const evModes = { manual: "Ruční", waiting: "Čeká", solar: "FVE", night: "Nízký tarif" };
const boilerModes = { off: "Vypnutý", heat: "Topení", auto: "Automaticky" };
const presets = { activity: "Aktivní", eco: "Úsporný", sleep: "Útlum" };
const unavailable = ["unknown", "unavailable"];

function quantity(value, unit) {
  if (value == null || value === "" || !Number.isFinite(Number(value))) return "—";
  return numberFormat.format(Number(value)) + (unit ? " " + unit : "");
}

function stateLabel(state, labels) {
  if (!state || unavailable.includes(state)) return "—";
  return labels[state] ?? state;
}

class SandiEnergyPanel extends HTMLElement {
  constructor() {
    super();
    const root = this.attachShadow({ mode: "open" });
    root.innerHTML = layout;
    this.fields = Object.fromEntries(
      Array.from(root.querySelectorAll("[data-field]"), (el) => [el.dataset.field, el])
    );
    this.meter = root.querySelector("progress");
    this.table = root.querySelector(".table-wrap");
    this.rows = root.querySelector("tbody");
    root.querySelector(".menu").addEventListener("click", () => {
      this.dispatchEvent(new CustomEvent("hass-toggle-menu", { bubbles: true, composed: true }));
    });
  }

  connectedCallback() {
    this.queueUpdate();
  }

  set narrow(value) {
    this.toggleAttribute("narrow", Boolean(value));
  }

  set hass(value) {
    this.currentHass = value;
    this.queueUpdate();
  }

  set panel(value) {
    this.panelConfig = value?.config;
    this.queueUpdate();
  }

  queueUpdate() {
    if (!this.isConnected || this.renderQueued) return;
    this.renderQueued = true;
    requestAnimationFrame(() => {
      this.renderQueued = false;
      if (this.isConnected) this.update();
    });
  }

  update() {
    const states = this.currentHass?.states ?? {};
    const entities = this.panelConfig?.entities ?? {};
    const diagnostics = this.panelConfig?.diagnostics ?? {};
    const boilerEntity = states[entities.boiler];
    const tariff = states[entities.tariff]?.state;
    const ev = states[diagnostics.ev]?.attributes ?? {};
    const boiler = states[diagnostics.boiler]?.attributes ?? {};
    const outlets = states[diagnostics.outlets]?.attributes ?? {};
    const active = [ev, boiler, outlets].some((item) => item.control_enabled === true);
    const currentAndTarget = [ev.current_setpoint_a, ev.target_current_a].map((value) => quantity(value));
    const powerLimit = this.panelConfig?.eps_limit_w;
    const eps = ev.eps_w ?? boiler.eps_active_w;

    const values = {
      control: active ? "Řízení aktivní" : "Náhled",
      pv: quantity(ev.pv_w, "W"),
      eps: quantity(eps, "W"),
      eps_limit: powerLimit ? "Limit " + quantity(powerLimit, "W") : "",
      soc: quantity(ev.battery_soc, "%"),
      eta: quantity(states[entities.eta]?.state, "min"),
      ev_mode: stateLabel(states[diagnostics.ev]?.state, evModes),
      actual_source: ev.actual_source ?? "—",
      tariff: stateLabel(tariff, { on: "Aktivní", off: "Vypnutý" }),
      ev_power: quantity(ev.ev_w, "W"),
      amps: currentAndTarget.join(" / ") + (currentAndTarget.every((item) => item === "—") ? "" : " A"),
      ev_priority: outlets.ev_priority ?? "—",
      ev_reason: ev.reason ?? "",
      ev_error: ev.last_error ?? "",
      boiler_mode: stateLabel(boilerEntity?.state, boilerModes),
      temperature: quantity(boilerEntity?.attributes.current_temperature, "°C"),
      target_preset: stateLabel(boiler.target_preset, presets),
      boiler_priority: outlets.boiler_priority ?? "—",
      boiler_reason: boiler.reason ?? "",
      boiler_error: boiler.last_error ?? "",
      outlet_priority: outlets.priority ?? "—",
      outlet_reason: outlets.reason ?? "",
    };
    for (const [key, value] of Object.entries(values)) {
      const target = this.fields[key];
      const label = String(value);
      if (target.textContent !== label) target.textContent = label;
      if (target.classList.contains("error")) target.hidden = !value;
    }
    this.meter.hidden = !powerLimit || eps == null;
    if (!this.meter.hidden) {
      this.meter.max = powerLimit;
      this.meter.value = Math.min(powerLimit, eps);
    }
    this.updateOutlets(outlets.outlets ?? [], states);
  }

  updateOutlets(outlets, states) {
    const labels = outlets.map((outlet) => [
      states[outlet.entity]?.attributes.friendly_name ?? outlet.entity,
      outlet.priority,
      quantity(outlet.watts, "W"),
      outlet.on == null ? "Nedostupná" : outlet.on ? "Zapnutá" : "Vypnutá",
      outlet.error || (!outlet.enabled ? "Ručně" : outlet.target_on ? "Zapnout" : "Vypnout"),
    ]);
    const signature = JSON.stringify(labels);
    if (signature === this.outletSignature) return;
    this.outletSignature = signature;
    this.table.hidden = !labels.length;
    this.rows.replaceChildren(...labels.map((row) => {
      const element = document.createElement("tr");
      for (const value of row) {
        const cell = element.insertCell();
        cell.textContent = String(value);
      }
      return element;
    }));
  }
}

if (!customElements.get("sandi-energy-panel")) {
  customElements.define("sandi-energy-panel", SandiEnergyPanel);
}
