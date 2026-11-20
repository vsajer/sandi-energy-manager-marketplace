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
    .page-nav { display: flex; align-items: center; gap: 5px; }
    .settings { text-decoration: none; padding: 7px 10px; border-radius: 8px; white-space: nowrap; }
    .settings[aria-current="page"] { background: var(--energy-surface); box-shadow: inset 0 -2px var(--energy-accent); }
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
    .outlet-heading { display: flex; justify-content: space-between; align-items: center; gap: 10px; flex-wrap: wrap; }
    .action { padding: 8px 12px; border-radius: 9px; background: transparent; border: 1px solid var(--energy-line); }
    .action.primary { background: var(--energy-accent); color: var(--text-primary-color, white); border-color: transparent; }
    .action.remove { color: var(--error-color, #b62222); }
    .action:focus-visible, input:focus-visible, select:focus-visible { outline: 2px solid var(--energy-accent); outline-offset: 2px; }
    .action:disabled { opacity: .6; cursor: wait; }
    .outlet-form, .entity-form { margin-top: 16px; border-top: 1px solid var(--energy-line); padding-top: 14px; }
    .form-grid { display: grid; grid-template-columns: repeat(4, minmax(90px, 1fr)); gap: 10px; margin-top: 12px; }
    .picker { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 2fr); gap: 10px; margin-top: 12px; }
    label { display: grid; gap: 5px; min-width: 0; font-size: 13px; }
    input, select { box-sizing: border-box; width: 100%; color: inherit; font: inherit;
      padding: 8px; border: 1px solid var(--energy-line); border-radius: 7px; background: var(--energy-surface); }
    .enabled { display: flex; align-items: center; gap: 8px; margin-top: 12px; }
    .enabled input { width: auto; }
    .form-footer { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 14px; }
    .form-footer .remove { margin-inline-start: auto; }
    .message { color: var(--secondary-text-color); }
    .message:empty { display: none; }
    .message[data-error] { color: var(--error-color, #b62222); }
    .entity-id { display: block; color: var(--secondary-text-color, #516259); font-size: 12px; overflow-wrap: anywhere; }
    .log-details { overflow-wrap: anywhere; }
    .log-time { white-space: nowrap; }
    .device-controls { border-top: 1px solid var(--energy-line); margin-top: 14px; padding-top: 12px; }
    .device-controls h3, .tuning h3 { margin: 0 0 8px; font-size: 15px; }
    .buttons { display: flex; flex-wrap: wrap; gap: 8px; align-items: end; margin-top: 8px; }
    .buttons label { max-width: 180px; }
    .action[aria-pressed="true"] { border-color: var(--energy-accent); color: var(--energy-accent); font-weight: 650; }
    .tuning { scroll-margin-top: 72px; }
    .settings-page .tuning { grid-row: 1; }
    .meter-picker { margin-top: 12px; }
    .settings-group { margin-top: 15px; }
    .settings-group .form-grid { margin-top: 0; }
    .range-label { display: flex; justify-content: space-between; align-items: baseline; gap: 8px; }
    .range-label output { font-weight: 700; font-size: 15px; white-space: nowrap; }
    input[type="range"] { padding-inline: 0; accent-color: var(--energy-accent); border: 0; }
    [hidden] { display: none !important; }
    @media (max-width: 720px) {
      .metrics { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .detail { grid-template-columns: minmax(0, 1fr); }
      .form-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .picker { grid-template-columns: minmax(0, 1fr); }
      main { padding: 14px 10px 24px; }
    }
  </style>
  <header>
    <div class="heading">
      <button type="button" class="menu" aria-label="Otevřít postranní nabídku"><ha-icon icon="mdi:menu"></ha-icon></button>
      <h1>Energie domu</h1>
    </div>
    <nav class="page-nav" aria-label="Energie domu">
      <a class="settings overview-link" href="/sandi-energy" aria-current="page">Přehled</a>
      <a class="settings settings-link" href="/sandi-energy/nastaveni">Nastavení</a>
      <a class="settings log-link" href="/sandi-energy/protokol">Protokol</a>
    </nav>
  </header>
  <main class="overview-page">
    <div class="overview"><h2>Přehled výkonu</h2><span class="mode" data-field="control"></span></div>
    <section class="metrics" aria-label="Přehled výkonu">
      <div class="tile"><ha-icon icon="mdi:solar-power"></ha-icon><span>Výroba FVE</span><strong data-field="pv"></strong></div>
      <div class="tile"><ha-icon icon="mdi:transmission-tower"></ha-icon><span>Odběr EPS</span><strong data-field="eps"></strong><progress hidden aria-label="Využití limitu EPS"></progress><span data-field="eps_limit"></span></div>
      <div class="tile"><ha-icon icon="mdi:battery-medium"></ha-icon><span>Domácí baterie</span><strong data-field="soc"></strong></div>
      <div class="tile"><ha-icon icon="mdi:clock-outline"></ha-icon><span>Odhad do nabití</span><strong data-field="eta"></strong></div>
    </section>
    <div class="detail">
      <section class="card">
        <div class="panel-heading"><ha-icon icon="mdi:ev-station"></ha-icon><h2>Nabíječka EV</h2></div>
        <dl>
          <div><dt>Režim</dt><dd data-field="ev_mode"></dd></div>
          <div><dt>Zdroj</dt><dd data-field="actual_source"></dd></div>
          <div><dt>ATS přepínač</dt><dd data-field="ats_state"></dd></div>
          <div><dt>Nízký tarif HDO</dt><dd data-field="tariff"></dd></div>
          <div><dt>Příkon nabíječky</dt><dd data-field="ev_power"></dd></div>
          <div><dt>Nastavený / cílový proud</dt><dd data-field="amps"></dd></div>
          <div><dt>Priorita na FVE</dt><dd data-field="ev_priority"></dd></div>
        </dl>
        <p class="hint" data-field="ev_reason"></p><p class="error" data-field="ev_error" hidden></p>
        <div class="device-controls">
          <h3>Ovládání nabíječky</h3>
          <div class="buttons">
            <button type="button" class="action" data-command="solar_mode">Režim FVE</button>
            <button type="button" class="action" data-command="night_mode">Režim nízkého tarifu</button>
          </div>
          <div class="buttons">
            <label>Ruční proud (A) <input class="charge-amps" type="number" step="1" min="6" required></label>
            <button type="button" class="action" data-command="ev_current">Nastavit proud</button>
            <button type="button" class="action" data-command="ev_limit">Omezit na 6 A</button>
          </div>
          <div class="buttons">
            <button type="button" class="action primary" data-command="ev_start">Spustit nabíjení</button>
            <button type="button" class="action" data-command="ev_stop">Zastavit nabíjení</button>
          </div>
          <p class="hint" data-field="ev_manual"></p>
          <p class="message ev-message" role="status"></p>
        </div>
      </section>
      <section class="card">
        <div class="panel-heading"><ha-icon icon="mdi:water-boiler"></ha-icon><h2>Bojler</h2></div>
        <dl>
          <div><dt>Stav termostatu</dt><dd data-field="boiler_mode"></dd></div>
          <div><dt>Teplota vody</dt><dd data-field="temperature"></dd></div>
          <div><dt>Preset termostatu</dt><dd data-field="boiler_preset"></dd></div>
          <div><dt>Cílový preset regulátoru</dt><dd data-field="target_preset"></dd></div>
          <div><dt>Priorita</dt><dd data-field="boiler_priority"></dd></div>
        </dl>
        <p class="hint" data-field="boiler_reason"></p><p class="error" data-field="boiler_error" hidden></p>
        <div class="device-controls">
          <h3>Ovládání bojleru</h3>
          <div class="buttons">
            <label>Preset bojleru <select class="boiler-choice" required></select></label>
            <button type="button" class="action" data-command="boiler_preset">Nastavit preset</button>
          </div>
          <div class="buttons">
            <button type="button" class="action primary" data-command="boiler_on">Zapnout bojler</button>
            <button type="button" class="action" data-command="boiler_off">Vypnout bojler</button>
          </div>
          <p class="hint" data-field="boiler_manual"></p>
          <p class="message boiler-message" role="status"></p>
        </div>
      </section>
      <section class="card full">
        <div class="panel-heading"><ha-icon icon="mdi:power-socket-eu"></ha-icon><h2>Solární spotřebiče</h2></div>
        <p class="hint" data-field="outlet_reason"></p>
        <div class="table-wrap overview-outlets" hidden>
          <table><thead><tr><th>Spotřebič</th><th>Priorita</th><th>Orientační příkon</th><th>Aktuální příkon</th><th>Stav</th><th>Cíl</th></tr></thead><tbody></tbody></table>
        </div>
      </section>
    </div>
  </main>
  <main class="settings-page" hidden>
    <div class="detail">
      <section class="card full">
        <div class="outlet-heading">
          <div class="panel-heading"><ha-icon icon="mdi:power-socket-eu"></ha-icon><h2>Solární zásuvky</h2></div>
          <button type="button" class="action primary add-outlet">Přidat zásuvku</button>
        </div>
        <p class="hint">Každý spotřebič má vlastní prioritu v pořadí s nabíječkou EV a bojlerem.</p>
        <div class="table-wrap settings-outlets" hidden>
          <table><thead><tr><th>Spotřebič</th><th>Priorita</th><th>Orientační příkon</th><th>Aktuální příkon</th><th>Stav</th><th>Cíl</th><th>Úpravy</th></tr></thead><tbody></tbody></table>
        </div>
        <form class="outlet-form" hidden>
          <h3 class="form-title"></h3>
          <div class="picker">
            <label>Vyhledat zařízení <input type="search" name="search" placeholder="Název nebo ID entity"></label>
            <label>Zásuvka nebo spínač <select name="entity" required></select></label>
          </div>
          <div class="form-grid">
            <label><span class="range-label">Priorita <output class="outlet-priority"></output></span>
              <input type="range" name="priority" min="-5" max="5" step="1"></label>
            <label>Orientační příkon (W) <input type="number" name="watts" min="1" max="20000" required></label>
            <label>Min. zapnutí (s) <input type="number" name="min_on_s" min="0" max="86400" required></label>
            <label>Min. vypnutí (s) <input type="number" name="min_off_s" min="0" max="86400" required></label>
          </div>
          <div class="picker meter-picker">
            <label>Vyhledat senzor příkonu <input type="search" name="meter_search" placeholder="Název nebo ID senzoru"></label>
            <label>Senzor aktuálního příkonu (volitelný) <select name="power_sensor"></select></label>
          </div>
          <p class="hint">Orientační příkon slouží pro start a zastoupí chybějící měření. Čerstvá hodnota ze senzoru se používá pro zapnutý spotřebič.</p>
          <label class="enabled"><input type="checkbox" name="enabled"> Zařadit do automatického řízení FVE</label>
          <div class="form-footer">
            <button type="submit" class="action primary">Uložit zásuvku</button>
            <button type="button" class="action cancel-outlet">Zrušit</button>
            <button type="button" class="action remove remove-outlet" hidden>Odebrat z řízení</button>
          </div>
        </form>
        <p class="message outlet-message" role="status"></p>
      </section>
      <section class="card full tuning">
        <h2>Limity, priority a aktivace</h2>
        <p class="hint">Zápornou prioritu smí regulátor při nedostatku výkonu odstavit. Nula a kladná priorita chrání běžící zátěž před vypnutím kvůli pořadí. Ochrany a konec nízkého tarifu fungují dál.</p>
        <form class="tuning-form" hidden>
          <div class="tuning-fields"></div>
          <p class="hint">Původní automatizace mohou ovládat stejné entity. Ruční povely jsou dostupné při vypnutém automatickém řízení daného zařízení v tomto regulátoru.</p>
          <p class="hint">Automatické přepínání přes IN Grid relé povol po ověření polohy ATS a hardwarového blokování zdrojů.</p>
          <div class="form-footer"><button class="action primary" type="submit">Uložit nastavení</button></div>
        </form>
        <p class="message tuning-message" role="status"></p>
      </section>
      <section class="card full">
        <div class="panel-heading"><ha-icon icon="mdi:lan-connect"></ha-icon><h2>Základní entity</h2></div>
        <div class="table-wrap">
          <table><thead><tr><th>Role v regulátoru</th><th>Entita Home Assistantu</th><th>Aktuální stav</th><th>Úpravy</th></tr></thead><tbody class="entity-rows"></tbody></table>
        </div>
        <div class="outlet-heading form-footer">
          <h3>Sledované entity</h3>
          <button type="button" class="action primary add-entity" disabled>Přidat sledovanou entitu</button>
        </div>
        <p class="hint">Hodnoty těchto entit slouží jen ke sledování.</p>
        <div class="table-wrap watched-table" hidden>
          <table><thead><tr><th>Entita Home Assistantu</th><th>Aktuální stav</th><th>Úpravy</th></tr></thead><tbody class="watched-rows"></tbody></table>
        </div>
        <form class="entity-form" hidden>
          <h3 class="entity-form-title"></h3>
          <div class="picker">
            <label>Vyhledat entitu <input type="search" name="search" placeholder="Název nebo ID entity"></label>
            <label>Entita Home Assistantu <select name="entity" required></select></label>
          </div>
          <div class="form-footer">
            <button class="action primary" type="submit">Uložit entitu</button>
            <button class="action cancel-entity" type="button">Zrušit</button>
            <button class="action remove remove-entity" type="button" hidden>Odebrat ze sledování</button>
          </div>
        </form>
        <p class="message entity-message" role="status"></p>
      </section>
    </div>
  </main>
  <main class="log-page" hidden>
    <section class="card">
      <div class="panel-heading"><ha-icon icon="mdi:clipboard-text-clock-outline"></ha-icon><h2>Protokol činnosti</h2></div>
      <p class="hint">Posledních 300 záznamů od aktualizace. U povelů je uveden výsledek volání služby Home Assistantu.</p>
      <p class="message log-message" role="status"></p>
      <div class="table-wrap log-table" hidden>
        <table><thead><tr><th>Čas</th><th>Zdroj</th><th>Akce</th><th>Entita</th><th>Výsledek a údaje</th></tr></thead><tbody class="log-rows"></tbody></table>
      </div>
    </section>
  </main>`;

const evModes = { manual: "Ruční", waiting: "Čeká", solar: "FVE", night: "Nízký tarif" };
const boilerModes = { off: "Vypnutý", heat: "Topení", auto: "Automaticky" };
const presets = { activity: "Aktivní", eco: "Úsporný", sleep: "Útlum" };
const unavailable = ["unknown", "unavailable"];
const outletNumbers = ["priority", "watts", "min_on_s", "min_off_s"];
const settingGroups = [
  ["Automatické řízení", {
    control_ev: "Řídit nabíjecí relaci a proud",
    control_source: "IN Grid relé",
    sonoff_on_is_solar: "ATS přepínač zapnutý = FVE",
    control_boiler: "Řídit bojler",
    control_outlets: "Řídit solární zásuvky",
  }],
  ["Priority", {
    ev_priority: "Nabíječka EV",
    boiler_priority: "Bojler",
  }],
  ["Příkony a limity", {
    phases: "Počet fází nabíječky",
    solar_max_a: "Maximální proud z FVE (A)",
    night_a: "Proud v nízkém tarifu (A)",
    pv_reserve_w: "Rezerva výkonu FVE (W)",
    inverter_limit_w: "Limit EPS (W)",
    boiler_w: "Příkon bojleru (W)",
    power_max_age_s: "Maximální stáří měření (s)",
  }],
];
const inputRoles = {
  pv: "Výroba FVE",
  eps: "Odběr EPS",
  overload: "Činný výkon EPS",
  soc: "Nabití domácí baterie",
  eta: "Odhad do nabití",
  ev_power: "Příkon nabíječky",
  ev_status: "Stav nabíječky",
  connected: "Auto připojeno",
  tariff: "Nízký tarif HDO",
  solar_enabled: "Nabíjení z FVE",
  night_enabled: "Nabíjení v nízkém tarifu",
  source: "ATS přepínač",
  session: "Spínač nabíjecí relace",
  current: "Nastavený proud nabíječky",
  boiler: "Termostat bojleru",
};
const auditActions = {
  turn_on: "Zapnout", turn_off: "Vypnout", set_value: "Nastavit hodnotu",
  set_hvac_mode: "Nastavit režim termostatu", set_preset_mode: "Nastavit preset bojleru",
  entity_assign: "Změna základní entity", watch_add: "Přidání sledované entity",
  watch_change: "Změna sledované entity", watch_remove: "Odebrání sledované entity",
  controls_save: "Změna nastavení regulátoru", outlet_add: "Přidání zásuvky",
  outlet_edit: "Úprava zásuvky", outlet_remove: "Odebrání zásuvky",
};
const auditOrigins = { automatic: "Automatika", manual: "Ruční povel", settings: "Nastavení" };
const auditKeys = {
  ...Object.assign({}, ...settingGroups.map(([, fields]) => fields)),
  previous: "Původní entita", role: "Role", value: "Hodnota", preset_mode: "Preset",
  hvac_mode: "Režim", enabled: "Automatické řízení", priority: "Priorita",
  watts: "Orientační příkon (W)", min_on_s: "Min. zapnutí (s)", min_off_s: "Min. vypnutí (s)",
  power_sensor: "Senzor příkonu",
};
const dateFormat = new Intl.DateTimeFormat("cs-CZ", { dateStyle: "short", timeStyle: "medium" });

function entityMatches(id, name, query) {
  const normalize = (value) => value.toLocaleLowerCase("cs").normalize("NFD").replace(/\p{M}/gu, "");
  const searchable = normalize(id + " " + name);
  const prefixes = [normalize(id), normalize(name), ...searchable.split(/[\s._-]+/)];
  return normalize(query.trim()).split(/\s+/).every((part) => prefixes.some((prefix) => prefix.startsWith(part)));
}

function entityOption(id, name) {
  const option = document.createElement("option");
  option.value = id;
  option.textContent = id && id !== name ? name + " · " + id : name;
  return option;
}

function quantity(value, unit) {
  if (value == null || value === "" || !Number.isFinite(Number(value))) return "—";
  return numberFormat.format(Number(value)) + (unit ? " " + unit : "");
}

function stateLabel(state, labels) {
  if (!state || unavailable.includes(state)) return "—";
  return labels[state] ?? state;
}

function priorityLabel(value) {
  if (value == null || value === "") return "—";
  return value > 0 ? "+" + value : value < 0 ? "−" + Math.abs(value) : "0";
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
    this.outletTables = [root.querySelector(".overview-outlets"), root.querySelector(".settings-outlets")];
    this.pages = [root.querySelector(".overview-page"), root.querySelector(".settings-page"), root.querySelector(".log-page")];
    this.pageLinks = [...root.querySelectorAll(".page-nav a")];
    this.entityRows = root.querySelector(".entity-rows");
    this.watchedRows = root.querySelector(".watched-rows");
    this.watchedTable = root.querySelector(".watched-table");
    this.entityForm = root.querySelector(".entity-form");
    this.entityMessage = root.querySelector(".entity-message");
    this.addEntity = root.querySelector(".add-entity");
    this.removeEntity = root.querySelector(".remove-entity");
    this.logRows = root.querySelector(".log-rows");
    this.logTable = root.querySelector(".log-table");
    this.logMessage = root.querySelector(".log-message");
    this.addEntity.addEventListener("click", () => this.openEntity(null, null));
    this.entityForm.elements.search.addEventListener("input", () => this.fillEntityPicker());
    this.entityForm.addEventListener("submit", (event) => {
      event.preventDefault();
      this.saveEntity(false);
    });
    this.removeEntity.addEventListener("click", () => this.saveEntity(true));
    root.querySelector(".cancel-entity").addEventListener("click", () => this.closeEntityForm());
    this.form = root.querySelector(".outlet-form");
    this.formTitle = root.querySelector(".form-title");
    this.addOutlet = root.querySelector(".add-outlet");
    this.removeOutlet = root.querySelector(".remove-outlet");
    this.message = root.querySelector(".outlet-message");
    this.picker = this.form.querySelector(".picker");
    this.controls = this.form.elements;
    this.outletPriority = root.querySelector(".outlet-priority");
    this.tuningForm = root.querySelector(".tuning-form");
    this.tuningFields = root.querySelector(".tuning-fields");
    this.tuningMessage = root.querySelector(".tuning-message");
    this.evMessage = root.querySelector(".ev-message");
    this.boilerMessage = root.querySelector(".boiler-message");
    this.ampInput = root.querySelector(".charge-amps");
    this.boilerChoice = root.querySelector(".boiler-choice");
    this.deviceButtons = [...root.querySelectorAll("[data-command]")];
    this.deviceButtons.forEach((button) => {
      button.addEventListener("click", () => this.sendDeviceCommand(button.dataset.command));
    });
    this.tuningForm.addEventListener("submit", (event) => {
      event.preventDefault();
      this.saveControls();
    });
    this.controls.priority.addEventListener("input", () => {
      this.outletPriority.value = priorityLabel(this.controls.priority.valueAsNumber);
    });
    this.addOutlet.addEventListener("click", () => this.openOutlet());
    this.controls.search.addEventListener("input", () => this.fillPicker());
    this.controls.meter_search.addEventListener("input", () => this.fillMeterPicker(this.controls.power_sensor.value));
    this.form.addEventListener("submit", (event) => {
      event.preventDefault();
      this.saveOutlet(false);
    });
    this.removeOutlet.addEventListener("click", () => this.saveOutlet(true));
    root.querySelector(".cancel-outlet").addEventListener("click", () => {
      this.form.hidden = true;
      this.setMessage("");
      this.addOutlet.focus();
    });
    root.querySelector(".menu").addEventListener("click", () => {
      this.dispatchEvent(new CustomEvent("hass-toggle-menu", { bubbles: true, composed: true }));
    });
  }

  connectedCallback() {
    this.showPage();
    this.queueUpdate();
  }

  disconnectedCallback() {
    this.unsubscribe("entity");
    this.unsubscribe("audit");
  }

  set narrow(value) {
    this.toggleAttribute("narrow", Boolean(value));
  }

  set hass(value) {
    const first = !this.currentHass;
    this.currentHass = value;
    if (first) this.showPage();
    this.queueUpdate();
  }

  set panel(value) {
    this.panelConfig = value?.config;
    this.showPage();
    this.queueUpdate();
  }

  set route(value) {
    this.currentRoute = value;
    this.showPage();
  }

  showPage() {
    const path = this.currentRoute?.path || window.location.pathname.slice("/sandi-energy".length);
    const page = { nastaveni: 1, protokol: 2 }[path.split("/").filter(Boolean)[0]] ?? 0;
    this.pages.forEach((element, index) => { element.hidden = page !== index; });
    this.pageLinks.forEach((element, index) => {
      if (page === index) element.setAttribute("aria-current", "page");
      else element.removeAttribute("aria-current");
    });
    if (page === 1 && this.currentHass && this.panelConfig && !this.controlSnapshot && !this.loadingControls) {
      this.loadControls();
    }
    if (!this.isConnected || !this.currentHass || !this.panelConfig) return;
    this.subscribe("entity", "entities", (settings) => {
      this.entitySettings = settings;
      this.addEntity.disabled = false;
      this.queueUpdate();
    });
    if (page === 2) {
      this.subscribe("audit", "audit", (payload) => this.updateAudit(payload));
    } else {
      this.unsubscribe("audit");
    }
  }

  get entities() {
    return this.entitySettings?.mapping ?? this.panelConfig?.entities ?? {};
  }

  subscribe(key, command, receive) {
    const property = key + "Subscription";
    if (this[property]) return;
    const subscription = this.currentHass.connection.subscribeMessage(
      (payload) => { if (this[property] === subscription) receive(payload); },
      { type: "sandi_energy/" + command + "/subscribe", entry_id: this.panelConfig.entry_id },
    );
    this[property] = subscription;
    subscription.catch((err) => {
      if (this[property] !== subscription) return;
      this[property] = null;
      this.report(key === "audit" ? this.logMessage : this.entityMessage,
        err.message || "Data se nepodařilo načíst.", true);
    });
  }

  unsubscribe(key) {
    const property = key + "Subscription";
    this[property]?.then((release) => release()).catch(() => {});
    this[property] = null;
  }

  setMessage(text, error = false) {
    this.report(this.message, text, error);
  }

  report(element, text, error = false) {
    element.textContent = text;
    element.toggleAttribute("data-error", error);
  }

  callSettings(type, changes = {}) {
    return this.currentHass.callWS({ type, entry_id: this.panelConfig.entry_id, ...changes });
  }

  async openOutlet(entity) {
    if (this.settingsBusy) return;
    this.settingsBusy = true;
    this.addOutlet.disabled = true;
    this.setMessage("Načítám nastavení zásuvek…");
    try {
      this.settings = await this.callSettings("sandi_energy/outlets");
      this.selectedOutlet = this.settings.outlets.find((item) => item.entity === entity) ?? null;
      if (entity && !this.selectedOutlet) throw new Error("Zásuvka už není v seznamu.");
      const fields = this.selectedOutlet ?? this.settings.defaults;
      this.controls.meter_search.value = "";
      this.fillMeterPicker(fields.power_sensor);
      for (const key of outletNumbers) this.controls[key].value = fields[key];
      this.outletPriority.value = priorityLabel(fields.priority);
      this.controls.enabled.checked = fields.enabled;
      this.controls.search.value = "";
      this.controls.entity.replaceChildren();
      this.controls.entity.disabled = Boolean(this.selectedOutlet);
      this.picker.hidden = Boolean(this.selectedOutlet);
      this.removeOutlet.hidden = !this.selectedOutlet;
      this.formTitle.textContent = this.selectedOutlet ? this.outletLabel(entity) : "Přidat zásuvku";
      if (!this.selectedOutlet) this.fillPicker();
      this.form.hidden = false;
      this.setMessage("");
      (this.selectedOutlet ? this.controls.priority : this.controls.search).focus();
    } catch (err) {
      this.setMessage(err.message || "Nastavení se nepodařilo načíst.", true);
    } finally {
      this.settingsBusy = false;
      this.addOutlet.disabled = false;
    }
  }

  async loadControls() {
    this.loadingControls = true;
    this.report(this.tuningMessage, "Načítám nastavení…");
    try {
      const settings = await this.callSettings("sandi_energy/controls");
      this.drawControls(settings);
      this.report(this.tuningMessage, "");
    } catch (err) {
      this.report(this.tuningMessage, err.message || "Nastavení se nepodařilo načíst.", true);
    } finally {
      this.loadingControls = false;
    }
  }

  drawControls({ values, ranges }) {
    this.controlSnapshot = values;
    this.tuningFields.replaceChildren(...settingGroups.map(([title, entries]) => {
      const group = document.createElement("div");
      group.className = "settings-group";
      const heading = document.createElement("h3");
      heading.textContent = title;
      const fields = document.createElement("div");
      fields.className = "form-grid";
      for (const [key, labelText] of Object.entries(entries)) {
        const label = document.createElement("label");
        const input = document.createElement(key === "phases" ? "select" : "input");
        input.name = key;
        if (key === "phases") {
          for (const count of [1, 3]) {
            const option = document.createElement("option");
            option.value = count;
            option.textContent = String(count);
            input.append(option);
          }
        } else if (typeof values[key] === "boolean") {
          input.type = "checkbox";
          input.checked = values[key];
          label.className = "enabled";
        } else {
          input.type = key.endsWith("_priority") ? "range" : "number";
          [input.min, input.max] = ranges[key];
          input.step = "1";
          input.required = true;
        }
        input.value = values[key];
        const caption = document.createElement("span");
        caption.textContent = labelText;
        if (input.type === "range") {
          const output = document.createElement("output");
          output.value = priorityLabel(values[key]);
          caption.className = "range-label";
          caption.append(output);
          input.addEventListener("input", () => { output.value = priorityLabel(input.valueAsNumber); });
        }
        if (input.type === "checkbox") label.append(input, caption);
        else label.append(caption, input);
        fields.append(label);
      }
      group.append(heading, fields);
      return group;
    }));
    this.tuningForm.hidden = false;
  }

  async saveControls() {
    if (this.savingControls) return;
    const elements = this.tuningForm.elements;
    const settings = Object.fromEntries(Object.entries(this.controlSnapshot).map(([key, value]) => [
      key, typeof value === "boolean" ? elements[key].checked : Number(elements[key].value),
    ]));
    this.savingControls = true;
    const button = this.tuningForm.querySelector("button[type=submit]");
    button.disabled = true;
    try {
      this.drawControls(await this.callSettings("sandi_energy/controls/save", {
        expected: this.controlSnapshot, settings,
      }));
      this.report(this.tuningMessage, "Nastavení regulátoru bylo uloženo.");
    } catch (err) {
      this.report(this.tuningMessage, err.message || "Nastavení se nepodařilo uložit.", true);
      if (err.code === "conflict") this.controlSnapshot = null;
    } finally {
      this.savingControls = false;
      button.disabled = false;
    }
  }

  async sendDeviceCommand(command) {
    if (this.commandPending) return;
    const message = command.startsWith("boiler_") ? this.boilerMessage : this.evMessage;
    const entities = this.entities;
    const states = this.currentHass.states;
    let value;
    if (command === "ev_current") {
      if (!this.ampInput.reportValidity()) return;
      value = this.ampInput.valueAsNumber;
    } else if (command === "ev_limit") {
      command = "ev_current";
      value = 6;
    } else if (command === "boiler_preset") {
      if (!this.boilerChoice.reportValidity()) return;
      value = this.boilerChoice.value;
    } else if (command === "solar_mode" || command === "night_mode") {
      const id = command === "solar_mode" ? entities.solar_enabled : entities.night_enabled;
      value = states[id]?.state === "off";
    }
    this.commandPending = true;
    this.queueUpdate();
    this.report(message, "Odesílám povel…");
    try {
      const data = value === undefined ? { command, mapping: entities } : { command, value, mapping: entities };
      await this.callSettings("sandi_energy/device/command", data);
      this.report(message, "Povel byl odeslán.");
    } catch (err) {
      this.report(message, err.message || "Povel se nepodařilo odeslat.", true);
    } finally {
      this.commandPending = false;
      this.queueUpdate();
    }
  }

  updateDeviceControls(states, entities, ev, boiler) {
    const charger = states[entities.current];
    const thermostat = states[entities.boiler];
    if (charger?.attributes) {
      const { min, max, step } = charger.attributes;
      this.ampInput.min = Math.max(6, min ?? 6);
      this.ampInput.max = max ?? "";
      this.ampInput.step = step ?? 1;
      if (this.shadowRoot.activeElement !== this.ampInput && this.ampInput.dataset.observed !== charger.state) {
        this.ampInput.dataset.observed = charger.state;
        this.ampInput.value = unavailable.includes(charger.state) ? "" : charger.state;
      }
    }
    const choices = (thermostat?.attributes.preset_modes ?? []).filter((value) => Object.hasOwn(presets, value));
    const signature = choices.join(",");
    if (this.presetSignature !== signature) {
      this.presetSignature = signature;
      this.boilerChoice.replaceChildren(...choices.map((choice) => {
        const option = document.createElement("option");
        option.value = choice;
        option.textContent = presets[choice];
        return option;
      }));
      if (choices.includes(thermostat?.attributes.preset_mode)) {
        this.boilerChoice.value = thermostat.attributes.preset_mode;
      }
    }
    const solar = states[entities.solar_enabled]?.state;
    const night = states[entities.night_enabled]?.state;
    for (const button of this.deviceButtons) {
      const command = button.dataset.command;
      const helper = command === "solar_mode" ? solar : command === "night_mode" ? night : null;
      if (command.endsWith("_mode")) {
        button.setAttribute("aria-pressed", String(helper === "on"));
        button.disabled = this.commandPending || (helper !== "on" && helper !== "off");
      } else if (command.startsWith("ev_")) {
        button.disabled = this.commandPending || ev.control_enabled === true;
      } else {
        button.disabled = this.commandPending || boiler.control_enabled === true
          || (command === "boiler_preset" && !choices.length);
      }
    }
    this.ampInput.disabled = ev.control_enabled === true;
    this.boilerChoice.disabled = boiler.control_enabled === true || !choices.length;
  }

  outletLabel(entity) {
    return this.currentHass?.states[entity]?.attributes.friendly_name || entity;
  }

  fillMeterPicker(previous) {
    const select = this.controls.power_sensor;
    const entities = this.entities;
    const excluded = new Set([entities.pv, entities.eps, entities.overload, entities.ev_power,
      ...this.settings.outlets.filter((item) => item.entity !== this.selectedOutlet?.entity).map((item) => item.power_sensor)]);
    const search = this.controls.meter_search.value;
    const list = Object.entries(this.currentHass.states)
      .filter(([id, state]) => id.startsWith("sensor.") && !excluded.has(id)
        && ["W", "kW"].includes(state.attributes.unit_of_measurement)
        && entityMatches(id, this.outletLabel(id), search))
      .map(([id]) => [id, this.outletLabel(id)])
      .sort((left, right) => left[1].localeCompare(right[1], "cs") || left[0].localeCompare(right[0]));
    if (previous && !list.some(([id]) => id === previous)) list.unshift([previous, this.outletLabel(previous)]);
    select.replaceChildren(...[["", "Pouze orientační příkon"], ...list].map(([id, name]) => entityOption(id, name)));
    select.value = previous ?? "";
  }

  fillPicker() {
    const select = this.controls.entity;
    const previous = select.value;
    const search = this.controls.search.value;
    const excluded = new Set([...this.settings.excluded, ...this.settings.outlets.map((item) => item.entity)]);
    const candidates = Object.entries(this.currentHass?.states ?? {})
      .filter(([id]) => id.startsWith("switch.") && !excluded.has(id))
      .map(([id, state]) => ({
        id,
        label: this.outletLabel(id),
        outlet: state.attributes.device_class === "outlet",
      }))
      .filter(({ id, label }) => entityMatches(id, label, search))
      .sort((left, right) => left.label.localeCompare(right.label, "cs") || left.id.localeCompare(right.id));

    const prompt = document.createElement("option");
    prompt.value = "";
    prompt.textContent = candidates.length ? "Vyber zásuvku nebo spínač" : "Žádná odpovídající zařízení";
    select.replaceChildren(prompt);
    for (const [isOutlet, label] of [[true, "Chytré zásuvky"], [false, "Další spínače"]]) {
      const group = document.createElement("optgroup");
      group.label = label;
      for (const item of candidates.filter((candidate) => candidate.outlet === isOutlet)) {
        group.append(entityOption(item.id, item.label));
      }
      if (group.childElementCount) select.append(group);
    }
    if (candidates.some((item) => item.id === previous)) select.value = previous;
  }

  async saveOutlet(remove) {
    if (this.settingsBusy) return;
    const entity = this.selectedOutlet?.entity ?? this.controls.entity.value;
    if (!entity || (remove && !this.selectedOutlet)) return;
    const settings = remove ? null : {
      ...Object.fromEntries(outletNumbers.map((key) => [key, this.controls[key].valueAsNumber])),
      enabled: this.controls.enabled.checked,
    };
    if (settings && this.controls.power_sensor.value) settings.power_sensor = this.controls.power_sensor.value;
    this.settingsBusy = true;
    this.addOutlet.disabled = true;
    this.setMessage(remove ? "Odebírám zásuvku…" : "Ukládám nastavení…");
    try {
      this.settings = await this.callSettings("sandi_energy/outlets/save", {
        entity,
        expected: this.selectedOutlet,
        settings,
      });
      this.form.hidden = true;
      this.setMessage(remove ? "Zásuvka byla odebrána z regulátoru." : "Nastavení zásuvky bylo uloženo.");
    } catch (err) {
      this.setMessage(err.message || "Změnu se nepodařilo uložit.", true);
    } finally {
      this.settingsBusy = false;
      this.addOutlet.disabled = false;
      if (this.form.hidden) this.addOutlet.focus();
    }
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
    const entities = this.entities;
    const diagnostics = this.panelConfig?.diagnostics ?? {};
    const boilerEntity = states[entities.boiler];
    const tariff = states[entities.tariff]?.state;
    const ev = states[diagnostics.ev]?.attributes ?? {};
    const boiler = states[diagnostics.boiler]?.attributes ?? {};
    const outlets = states[diagnostics.outlets]?.attributes ?? {};
    const active = [ev, boiler, outlets].some((item) => item.control_enabled === true);
    const currentAndTarget = [ev.current_setpoint_a, ev.target_current_a].map((value) => quantity(value));
    const powerLimit = ev.eps_limit_w ?? this.panelConfig?.eps_limit_w;
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
      ats_state: stateLabel(states[entities.source]?.state, { on: "Zapnutý", off: "Vypnutý" }),
      tariff: stateLabel(tariff, { on: "Aktivní", off: "Vypnutý" }),
      ev_power: quantity(ev.ev_w, "W"),
      amps: currentAndTarget.join(" / ") + (currentAndTarget.every((item) => item === "—") ? "" : " A"),
      ev_priority: priorityLabel(outlets.ev_priority),
      ev_reason: ev.reason ?? "",
      ev_error: ev.last_error ?? "",
      ev_manual: ev.control_enabled ? "Nabíječku řídí automatika." : "Ruční start používá aktuální zdroj a nastavený proud bez ohledu na časový plán.",
      boiler_mode: stateLabel(boilerEntity?.state, boilerModes),
      temperature: quantity(boilerEntity?.attributes.current_temperature, "°C"),
      boiler_preset: stateLabel(boilerEntity?.attributes.preset_mode, presets),
      target_preset: stateLabel(boiler.target_preset, presets),
      boiler_priority: priorityLabel(outlets.boiler_priority),
      boiler_reason: boiler.reason ?? "",
      boiler_error: boiler.last_error ?? "",
      boiler_manual: boiler.control_enabled ? "Bojler řídí automatika podle ETA baterie a EPS." : "",
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
    this.updateInputs(entities, states);
    this.updateDeviceControls(states, entities, ev, boiler);
  }

  updateInputs(entities, states) {
    const watched = this.entitySettings?.watched ?? [];
    const describe = (id) => {
      const state = states[id];
      const value = state?.state;
      const unit = state?.attributes.unit_of_measurement;
      return [state?.attributes.friendly_name, unit && Number.isFinite(Number(value))
        ? quantity(value, unit)
        : stateLabel(value, { ...boilerModes, on: "Zapnuto", off: "Vypnuto" })];
    };
    const values = Object.keys(inputRoles).map((key) => [key, entities[key] ?? null, ...describe(entities[key])]);
    const additional = watched.map((id) => [null, id, ...describe(id)]);
    const signature = JSON.stringify([Boolean(this.entitySettings), values, additional]);
    if (signature === this.inputSignature) return;
    this.inputSignature = signature;
    const focused = this.shadowRoot.activeElement?.dataset.entityEdit;
    const render = ([role, id, name, value]) => {
      const row = document.createElement("tr");
      if (role) row.insertCell().textContent = inputRoles[role];
      const entity = row.insertCell();
      entity.textContent = name || id || "Nepřiřazena";
      if (name && id) {
        const label = document.createElement("span");
        label.className = "entity-id";
        label.textContent = id;
        entity.append(label);
      }
      row.insertCell().textContent = value;
      const button = document.createElement("button");
      button.type = "button";
      button.className = "action";
      button.textContent = id ? "Upravit" : "Přiřadit";
      button.dataset.entityEdit = role ?? id;
      button.setAttribute("aria-label", button.textContent + " · " + (inputRoles[role] ?? name ?? id));
      button.disabled = !this.entitySettings;
      button.addEventListener("click", () => this.openEntity(role, id));
      row.insertCell().append(button);
      return row;
    };
    this.entityRows.replaceChildren(...values.map(render));
    this.watchedRows.replaceChildren(...additional.map(render));
    this.watchedTable.hidden = !additional.length;
    if (focused) this.shadowRoot.querySelector(`[data-entity-edit="${CSS.escape(focused)}"]`)?.focus({ preventScroll: true });
  }

  openEntity(role, id) {
    if (!this.entitySettings || this.entityBusy) return;
    this.entityEdit = { role, expected: id };
    const fields = this.entityForm.elements;
    fields.search.value = "";
    this.entityForm.querySelector(".entity-form-title").textContent = role ? inputRoles[role]
      : id ? "Upravit sledovanou entitu" : "Přidat sledovanou entitu";
    this.removeEntity.hidden = Boolean(role) || !id;
    this.fillEntityPicker(id);
    this.report(this.entityMessage, "");
    this.entityForm.hidden = false;
    fields.search.focus();
  }

  fillEntityPicker(previous = this.entityForm.elements.entity.value) {
    const { role, expected } = this.entityEdit;
    const fields = this.entityForm.elements;
    const domain = this.entitySettings.domains[role];
    const excluded = new Set(role ? [] : this.entitySettings.watched.filter((id) => id !== expected));
    const candidates = Object.keys(this.currentHass.states)
      .filter((id) => (!domain || id.startsWith(domain + ".")) && !excluded.has(id)
        && entityMatches(id, this.outletLabel(id), fields.search.value))
      .sort((a, b) => this.outletLabel(a).localeCompare(this.outletLabel(b), "cs") || a.localeCompare(b));
    if (previous && !candidates.includes(previous)) candidates.unshift(previous);
    fields.entity.replaceChildren(entityOption("", candidates.length ? "Vyber entitu" : "Žádné odpovídající entity"),
      ...candidates.map((id) => entityOption(id, this.outletLabel(id))));
    fields.entity.value = previous ?? "";
  }

  closeEntityForm() {
    if (this.entityBusy) return;
    this.entityForm.hidden = true;
    const key = this.entityEdit?.role ?? this.entityEdit?.expected;
    const button = key && this.shadowRoot.querySelector(`[data-entity-edit="${CSS.escape(key)}"]`);
    (button || this.addEntity).focus();
    this.entityEdit = null;
  }

  async saveEntity(remove) {
    if (this.entityBusy || !this.entityEdit) return;
    const entity = remove ? null : this.entityForm.elements.entity.value;
    this.entityBusy = true;
    const buttons = this.entityForm.querySelectorAll("button");
    buttons.forEach((button) => { button.disabled = true; });
    let saved = false;
    try {
      await this.callSettings("sandi_energy/entities/save", { ...this.entityEdit, entity });
      saved = true;
      this.report(this.entityMessage, remove ? "Entita byla odebrána ze sledování." : "Entita byla uložena.");
    } catch (err) {
      this.report(this.entityMessage, err.message || "Entitu se nepodařilo uložit.", true);
    } finally {
      this.entityBusy = false;
      buttons.forEach((button) => { button.disabled = false; });
      if (saved) this.closeEntityForm();
    }
  }

  updateAudit({ history, record }) {
    if (history) this.auditHistory = history;
    if (record) this.auditHistory = [record, ...(this.auditHistory ?? [])].slice(0, 300);
    const rows = this.auditHistory ?? [];
    this.logTable.hidden = !rows.length;
    this.report(this.logMessage, rows.length ? "" : "Zatím žádné záznamy.");
    this.logRows.replaceChildren(...rows.map((item) => {
      const row = document.createElement("tr");
      row.insertCell().textContent = dateFormat.format(new Date(item.time));
      row.cells[0].className = "log-time";
      row.insertCell().textContent = auditOrigins[item.origin] ?? item.origin;
      row.insertCell().textContent = auditActions[item.action] ?? item.action;
      const entity = row.insertCell();
      entity.textContent = item.entity ? (this.outletLabel(item.entity) || item.entity) : "—";
      if (item.entity && entity.textContent !== item.entity) {
        const id = document.createElement("span");
        id.className = "entity-id";
        id.textContent = item.entity;
        entity.append(id);
      }
      const details = Object.entries(item.details ?? {}).filter(([, value]) => value != null).map(([key, value]) =>
        (auditKeys[key] ?? key) + " – " + (key === "role" ? (inputRoles[value] ?? value)
          : typeof value === "boolean" ? (value ? "Ano" : "Ne") : value));
      const outcome = item.error ? "Chyba · " + item.error : item.origin === "settings" ? "Uloženo" : "Povel přijat";
      const cell = row.insertCell();
      cell.className = item.error ? "log-details error" : "log-details";
      cell.textContent = [outcome, ...details].join(" · ");
      return row;
    }));
  }

  updateOutlets(outlets, states) {
    const ordered = [...outlets].sort((a, b) => b.priority - a.priority
      || this.outletLabel(a.entity).localeCompare(this.outletLabel(b.entity), "cs")
      || a.entity.localeCompare(b.entity));
    const labels = ordered.map((outlet) => [
      outlet.entity,
      states[outlet.entity]?.attributes.friendly_name ?? outlet.entity,
      priorityLabel(outlet.priority),
      quantity(outlet.watts, "W"),
      outlet.measured_w != null ? quantity(outlet.measured_w, "W") : outlet.power_sensor ? "Nedostupný" : "—",
      outlet.on == null ? "Nedostupná" : outlet.on ? "Zapnutá" : "Vypnutá",
      outlet.error || (!outlet.enabled ? "Ručně" : outlet.target_on ? "Zapnout" : "Vypnout"),
    ]);
    const signature = JSON.stringify(labels);
    if (signature === this.outletSignature) return;
    this.outletSignature = signature;
    this.outletTables.forEach((table, page) => {
      table.hidden = !labels.length;
      table.querySelector("tbody").replaceChildren(...labels.map(([id, ...row]) => {
        const element = document.createElement("tr");
        for (const value of row) element.insertCell().textContent = String(value);
        if (page === 1) {
          const edit = document.createElement("button");
          edit.type = "button";
          edit.className = "action";
          edit.textContent = "Upravit";
          edit.setAttribute("aria-label", "Upravit " + row[0]);
          edit.addEventListener("click", () => this.openOutlet(id));
          element.insertCell().append(edit);
        }
        return element;
      }));
    });
  }
}

if (!customElements.get("sandi-energy-panel")) {
  customElements.define("sandi-energy-panel", SandiEnergyPanel);
}
