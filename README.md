# SANDI Energy Manager

Vlastní integrace pro Home Assistant pro řízení nabíjení elektromobilu, bojleru a zásuvek podle naměřeného přebytku z fotovoltaiky a odběru EPS. Integrace používá existující entity Home Assistantu. Měření z měniče pouze čte.

## Instalace

1. V **Nastavení → Marketplace → Vlastní repozitáře** přidej tento repozitář v kategorii Integrace a nainstaluj ho.
2. V **Nastavení → Zařízení a služby → Přidat integraci** zvol **SANDI Energy Manager**. Vyber senzory výkonu, stav baterie, tarif HDO, entity nabíječky a termostat svého systému.
3. Správci Home Assistantu uvidí v postranní nabídce panel **Energie domu**. Panel je součástí integrace a používá entity, které jsi vybral při nastavení. Senzory `sensor.sandi_energy_*` vytváří integrace.
4. **Přehled** ukazuje hodnoty a ovládání. Na stránce **Nastavení** otevři **Solární zásuvky → Přidat zásuvku**. Vyber zařízení, zadej orientační příkon a případně přiřaď samostatný senzor ve W nebo kW. Regulátor používá orientační příkon při startu a při výpadku měření. U běžícího spotřebiče použije čerstvou hodnotu ze senzoru, pokud je k dispozici.

## Provoz

- Po instalaci integrace nabízí náhled. Přepínání zdroje, změny proudu, řízení bojleru a spínání zásuvek se zapínají samostatně v nastavení. Před aktivací vypni původní automatizace ovládající stejné entity.
- Priorita je posuvník **−5 až +5**. Nabíječka EV, bojler a každý spotřebič se řadí podle svého čísla. Vyšší číslo má přednost při přidělení výkonu. Záporná priorita dovoluje vypnutí kvůli pořadí. Nula a kladná priorita před takovým vypnutím chrání již běžící zátěž. Ochrana při přetížení EPS a další provozní podmínky platí dál. Nabíjení ze sítě v nízkém tarifu běží mimo FV pořadí.
- Stránka **Nastavení** obsahuje limity, priority a aktivaci. Při přechodu z verze 0.5 se hodnoty jednotlivých spotřebičů zachovají. Z dřívější verze se priority převádějí na záporné hodnoty podle původního pořadí. Šestá a další různá priorita sdílí hodnotu −5.
- **Nabíječka** nabízí volbu režimu FVE a NT, ruční start a stop, nastavení proudu a rychlé omezení na 6 A. Ruční start pracuje s potvrzeným nastaveným proudem a aktuálním zdrojem. U FVE vyžaduje čerstvé měření a dostatečnou rezervu. Automatické omezení proudu a proud pro NT jsou v nastavení panelu.
- **Bojler** nabízí zapnutí, vypnutí a podporované presety `activity`, `eco` a `sleep`. Automatika vybírá preset podle denního pásma a ETA baterie a zohledňuje limit EPS. Ruční povely k nabíječce i bojleru jsou dostupné při vypnuté automatice daného zařízení v regulátoru. Původní automatizace v Home Assistantu mohou jejich stavy dál měnit.
- Výběr nejdřív nabízí entity označené jako zásuvky, potom další spínače. Přidávej jen zařízení, která jsou napájená z EPS. Novou zásuvku můžeš nejdřív uložit ručně a do automatického řízení ji zařadit později. Společný přepínač řízení zásuvek je v provozním nastavení integrace.
- V **Nastavení → Základní entity** můžeš upravit přiřazení všech 15 vstupů a přidávat, měnit či odebírat entity určené jen ke sledování. Ve výběrech entit funguje vyhledávání podle začátku názvu, jednotlivých slov nebo ID bez ohledu na diakritiku. Zásuvky se zobrazují od nejvyšší priority a při shodě abecedně podle názvu.
- **Protokol** v panelu zobrazuje automatické a ruční povely odeslané integrací, výsledek volání služby Home Assistantu a změny nastavení uložené z panelu. Posledních 300 záznamů se uchovává místně v Home Assistantu.
- Pokud používáš přepínání FVE a sítě, ověř význam poloh přepínače a hardwarové blokování obou zdrojů. Automatické přepnutí čeká na ukončení nabíjecí relace, nízký odběr a ustálení nové polohy.
- Skutečné reakce zařízení a mapování entit ověř v náhledu před zapnutím řízení.
