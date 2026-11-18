# SANDI Energy Manager

Vlastní integrace pro Home Assistant pro řízení nabíjení elektromobilu, bojleru a zásuvek podle naměřeného přebytku z fotovoltaiky a odběru EPS. Integrace používá existující entity Home Assistantu. Měření z měniče pouze čte.

## Instalace

1. V **Nastavení → Marketplace → Vlastní repozitáře** přidej tento repozitář v kategorii Integrace a nainstaluj ho.
2. V **Nastavení → Zařízení a služby → Přidat integraci** zvol **SANDI Energy Manager**. Vyber senzory výkonu, stav baterie, tarif HDO, entity nabíječky a termostat svého systému.
3. Správci Home Assistantu uvidí v postranní nabídce panel **Energie domu**. Panel je součástí integrace a používá entity, které jsi vybral při nastavení. Senzory `sensor.sandi_energy_*` vytváří integrace.
4. V panelu otevři **Solární zásuvky → Přidat zásuvku**. Vyhledej zařízení, nastav prioritu, skutečný příkon a minimální dobu zapnutí a vypnutí. **Upravit** otevře samostatné nastavení zásuvky. **Odebrat z řízení** ji vyřadí ze seznamu regulátoru bez povelu zásuvce.

## Provoz

- Po instalaci integrace nabízí náhled. Přepínání zdroje, změny proudu, řízení bojleru a spínání zásuvek se zapínají samostatně v nastavení. Před aktivací vypni původní automatizace ovládající stejné entity.
- Priorita je posuvník **−5 až +5**. Vyšší číslo má přednost při přidělení výkonu. Záporná priorita dovoluje vypnutí kvůli pořadí. Nula a kladná priorita před takovým vypnutím chrání již běžící zátěž. Ochrana při přetížení EPS a další provozní podmínky platí dál. Skupinový posuvník zásuvek určuje pořadí celé skupiny, ochranu jednotlivé zásuvky určuje její vlastní posuvník. Nabíjení ze sítě v nízkém tarifu běží mimo FV pořadí.
- Panel obsahuje **Nastavení regulátoru** pro limity, priority a aktivaci. Existující priority se při aktualizaci převedou na záporné hodnoty podle původního pořadí. Šestá a další různá priorita sdílí hodnotu −5.
- **Nabíječka** nabízí volbu režimu FVE a NT, ruční start a stop, nastavení proudu a rychlé omezení na 6 A. Ruční start pracuje s potvrzeným nastaveným proudem a aktuálním zdrojem. U FVE vyžaduje čerstvé měření a dostatečnou rezervu. Automatické omezení proudu a proud pro NT jsou v nastavení panelu.
- **Bojler** nabízí zapnutí, vypnutí a podporované presety `activity`, `eco` a `sleep`. Automatika vybírá preset podle denního pásma a ETA baterie a zohledňuje limit EPS. Ruční povely k nabíječce i bojleru jsou dostupné při vypnuté automatice daného zařízení v regulátoru. Původní automatizace v Home Assistantu mohou jejich stavy dál měnit.
- Výběr nejdřív nabízí entity označené jako zásuvky, potom další spínače. Přidávej jen zařízení, která jsou napájená z EPS. Novou zásuvku můžeš nejdřív uložit ručně a do automatického řízení ji zařadit později. Společný přepínač řízení zásuvek je v provozním nastavení integrace.
- Sekce **Základní entity** ukazuje všech 15 vstupů regulátoru včetně aktuální hodnoty a ID zdrojové entity. Přiřazení se mění přes nabídku **Přenastavit** u integrace.
- Pokud používáš přepínání FVE a sítě, ověř význam poloh přepínače a hardwarové blokování obou zdrojů. Automatické přepnutí čeká na ukončení nabíjecí relace, nízký odběr a ustálení nové polohy.
- Skutečné reakce zařízení a mapování entit ověř v náhledu před zapnutím řízení.
