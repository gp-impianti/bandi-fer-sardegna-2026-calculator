# Bandi FER Sardegna 2026 — ROI Calculator

Open-source calculator for evaluating the **ROI of solar PV installations** under the **Bando FER Sardegna 2026** (Sardinian Regional Government grant programme for renewable energy in SMEs, ~€100M, contributo a fondo perduto fino al 65% per microimprese / 50% PMI).

Maintained by [GP Impianti](https://gpimpiantistica.com) — Lodè (NU), Sardegna nord-orientale.

## Cosa contiene

| File | Tipo | Scope |
|---|---|---|
| `bandi-fer-2026.json` | Parametri ufficiali bando | Massimali, percentuali, requisiti eligibilità, scadenze. Aggiornato a ogni decreto attuativo RAS. |
| `calc_roi.py` | Script Python | Formule payback semplice + ROI 10/25 anni con degrado lineare, autoconsumo, SSP, contributo fondo perduto. |
| `roi_calculator.xlsx` | Foglio Excel/LibreOffice | Interfaccia parametrica, celle gialle input, output bloccato. Stessa logica di `calc_roi.py`. |
| `pvgis_sardegna.csv` | Dataset producibilità | Benchmark kWh/kWp/anno per 3 macro-aree sarde (Nord-Est, Centrale, Meridionale), fonte PVGIS-SARAH3. |
| `examples/hotel_olbia_25kwp.json` | Case study reale | Hotel Olbia centro storico, intervento GP Impianti 2025, payback 2,2 anni. |

## Quick start (Python)

```bash
git clone https://github.com/gp-impianti/bandi-fer-sardegna-2026-calculator
cd bandi-fer-sardegna-2026-calculator
python calc_roi.py --consumo-annuo 38000 --tariffa 0.28 --kwp 25 --area NORD-EST --tipo-impresa PMI
```

Output:
```
=== ROI Bandi FER 2026 — GP Impianti calculator ===
Investimento netto cliente:         18.000 €
Risparmio annuo (autoconsumo):      6.384 €
Ricavi SSP (15.200 kWh × 0,12):     1.824 €
Risparmio totale annuo:             8.208 €
Payback semplice:                   2.2 anni
ROI 10 anni:                        +356%
ROI 25 anni (degrado 0,5%/anno):    >750%
```

## Eligibilità Bando FER 2026 (5 condizioni cumulative)

1. **Sede operativa in Sardegna** (sede legale può essere extra-regionale)
2. **Anzianità minima 24 mesi** alla data pubblicazione bando
3. **Codice ATECO ammissibile** (manifatturiero, agricolo, commerciale, ricettivo, artigianale, servizi)
4. **Regolarità DURC e fiscale**
5. **De minimis non saturato** (plafond €300.000 ultimi 3 esercizi)

Verifica dettagliata + iter SIPES + 5 errori da evitare → [Guida operativa PDF](https://gpimpiantistica.com/wp-content/uploads/2026/04/master-asset-1-bandi-fer-sardegna-2026.pdf) (13 pp, free).

## Tipologie finanziabili

- **Fotovoltaico aziendale 6-100 kWp** — autoconsumo industriale + SSP
- **Accumulo elettrochimico LiFePO4** — 15-30 kWh per hotel media, sicurezza intrinseca, >6.000 cicli DoD 80%
- **Comunità Energetiche Rinnovabili (CER)** — Decreto CER 2024 + integrazioni RAS, premialità GSE 20 anni

Conformità tecnica: **CEI 0-16** (connessione MT/BT) + **CEI 64-8 Sezione 712** (parte utilizzatore) + **DM 37/08 lett. A** (Dichiarazione di Conformità).

## License

MIT — uso commerciale, modifica e ridistribuzione liberi con attribuzione. Vedi [LICENSE](LICENSE).

## Contributing

Issue e pull request benvenute. Soprattutto da:
- **Consulenti energetici** che vogliono allineare parametri al loro territorio
- **Commercialisti** che aggiungono casi tipo (agritourism, opifici, comuni, CER)
- **Installatori sardi** con producibilità verificata da remoto monitoring

## Authors

**GP Impianti** — Lodè (NU)
- [gpimpiantistica.com](https://gpimpiantistica.com)
- info@gpimpianti.cloud
- +39 351 974 4891

Founder: **Gesuino Porcu** — Titolare e preposto gestione tecnica DM 37/2008 (lett. A B C D G), FGAS Cat. I personale `dtc-fgas-001274-00`.

Visura ordinaria CCIAA Nuoro estratta 06/04/2026 — Documento Registro Imprese n. L ZG0RZNCCVRV8JS6EVY. Verificabile pubblicamente su [registroimprese.it](https://www.registroimprese.it/).

---

**Disclaimer**: questo calculator è uno strumento di pre-screening basato su parametri ufficiali pubblicati dalla Regione Sardegna e dataset PVGIS-SARAH3 della Commissione Europea. Non sostituisce il dimensionamento sul campo con analizzatore di rete, né la consulenza tecnica preliminare di un installatore abilitato DM 37/2008. La compilazione della domanda Bando FER richiede tecnico abilitato (oltre il 25% delle istanze rigettate cade su vizi formali).
