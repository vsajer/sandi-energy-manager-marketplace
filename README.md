# SANDI Energy Manager

Vlastní integrace pro Home Assistant pro řízení nabíjení elektromobilu, bojleru a zásuvek podle naměřeného přebytku z fotovoltaiky a odběru EPS. Integrace používá existující entity Home Assistantu. Měření z měniče pouze čte.

## Instalace

1. V **Nastavení → Marketplace → Vlastní repozitáře** přidej tento repozitář v kategorii Integrace a nainstaluj ho.
2. V **Nastavení → Zařízení a služby → Přidat integraci** zvol **SANDI Energy Manager**. Vyber senzory výkonu, stav baterie, tarif HDO, entity nabíječky a termostat svého systému.
3. Přidávej zásuvky v nastavení integrace. Menší číslo priority má přednost. Zadej skutečný příkon spotřebičů a ověř zvolený limit EPS podle vlastní instalace.
4. Správci Home Assistantu uvidí v postranní nabídce panel **Energie domu**. Panel je součástí integrace a používá entity, které jsi vybral při nastavení. Senzory `sensor.sandi_energy_*` vytváří integrace.

## Provoz

- Po instalaci integrace nabízí náhled. Přepínání zdroje, změny proudu, řízení bojleru a spínání zásuvek se zapínají samostatně v nastavení. Před aktivací vypni původní automatizace ovládající stejné entity.
- Prioritu lze nastavit pro solární nabíjení, bojler i skupinu zásuvek. Každá zásuvka má vlastní pořadí a minimální dobu zapnutí a vypnutí. Nabíjení ze sítě v nízkém tarifu běží mimo FV pořadí.
- Pokud používáš přepínání FVE a sítě, ověř význam poloh přepínače a hardwarové blokování obou zdrojů. Automatické přepnutí čeká na ukončení nabíjecí relace, nízký odběr a ustálení nové polohy.
- Skutečné reakce zařízení a mapování entit ověř v náhledu před zapnutím řízení.
