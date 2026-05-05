#!/usr/bin/env python3
"""
Bandi FER Sardegna 2026 — ROI Calculator
========================================

Computes simple payback + ROI 10/25 years for solar PV installation under Bando FER PMI.

Usage:
    python calc_roi.py --consumo-annuo 38000 --tariffa 0.28 --kwp 25 --area NORD-EST --tipo-impresa PMI

License: MIT (see LICENSE)
Source:  https://github.com/gp-impianti/bandi-fer-sardegna-2026-calculator
Author:  GP Impianti — Lodè (NU), Sardegna
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# ─── Producibilità benchmark PVGIS-SARAH3 (kWh/kWp/anno) ──────────────────────
PVGIS_BENCHMARK = {
    "NORD-EST": 1520,    # Olbia, Costa Smeralda, Gallura
    "CENTRALE": 1480,    # Nuoro, Lodè, Baronia interna
    "MERIDIONALE": 1560, # Cagliari, Sulcis, Campidano
}

# ─── Costi tipici kWp installato chiavi-in-mano (€/kWp, IVA esclusa) ──────────
COSTO_KWP_TIER_1 = 1440  # Tier 1 modules + inverter ibrido + accumulo proporzionale

# ─── Contributo Bando FER 2026 ────────────────────────────────────────────────
CONTRIBUTO_PERC = {
    "microimprese": 0.65,
    "PMI": 0.50,
}

# ─── Tariffa SSP GSE 2025 medio (€/kWh) ───────────────────────────────────────
TARIFFA_SSP_DEFAULT = 0.12

# ─── Autoconsumo tipico con accumulo proporzionato (%) ────────────────────────
AUTOCONSUMO_TIPICO = 0.60  # 60% autoconsumato, 40% ceduto SSP


def compute_roi(
    consumo_annuo_kwh: float,
    tariffa_eur_kwh: float,
    kwp_installati: float,
    area: str,
    tipo_impresa: str,
    autoconsumo_perc: float = AUTOCONSUMO_TIPICO,
    costo_kwp: float = COSTO_KWP_TIER_1,
    tariffa_ssp: float = TARIFFA_SSP_DEFAULT,
    degrado_anno: float = 0.005,
) -> dict:
    """
    Compute ROI metrics for solar PV under Bando FER 2026.

    Args:
        consumo_annuo_kwh: yearly electricity consumption (kWh)
        tariffa_eur_kwh: bought electricity tariff (€/kWh, mix F1+F2+F3, IVA esclusa)
        kwp_installati: installed peak power (kWp)
        area: macro-area sarda ("NORD-EST" | "CENTRALE" | "MERIDIONALE")
        tipo_impresa: "microimprese" or "PMI"
        autoconsumo_perc: share of production self-consumed (default 0.60)
        costo_kwp: cost per kWp turnkey (€/kWp, default 1440)
        tariffa_ssp: GSE Scambio sul Posto tariff (€/kWh, default 0.12)
        degrado_anno: yearly linear panel degradation (default 0.005 = 0.5%/yr)

    Returns:
        dict with full ROI breakdown
    """
    if area not in PVGIS_BENCHMARK:
        raise ValueError(f"Area '{area}' not in {list(PVGIS_BENCHMARK.keys())}")
    if tipo_impresa not in CONTRIBUTO_PERC:
        raise ValueError(f"Tipo impresa '{tipo_impresa}' not in {list(CONTRIBUTO_PERC.keys())}")

    producibilità_kwh_kwp = PVGIS_BENCHMARK[area]
    produzione_annua = kwp_installati * producibilità_kwh_kwp

    autoconsumati = produzione_annua * autoconsumo_perc
    ceduti_ssp = produzione_annua * (1 - autoconsumo_perc)

    risparmio_autoconsumo = autoconsumati * tariffa_eur_kwh
    ricavi_ssp = ceduti_ssp * tariffa_ssp
    risparmio_totale_anno = risparmio_autoconsumo + ricavi_ssp

    investimento_lordo = kwp_installati * costo_kwp
    contributo = investimento_lordo * CONTRIBUTO_PERC[tipo_impresa]
    investimento_netto = investimento_lordo - contributo

    payback_anni = investimento_netto / risparmio_totale_anno if risparmio_totale_anno > 0 else float("inf")

    # ROI cumulativo con degrado lineare
    def cumulative_savings(years: int) -> float:
        total = 0.0
        for yr in range(1, years + 1):
            factor = (1 - degrado_anno) ** (yr - 1)
            total += risparmio_totale_anno * factor
        return total

    roi_10_anni_perc = (cumulative_savings(10) - investimento_netto) / investimento_netto * 100
    roi_25_anni_perc = (cumulative_savings(25) - investimento_netto) / investimento_netto * 100

    return {
        "input": {
            "consumo_annuo_kwh": consumo_annuo_kwh,
            "tariffa_eur_kwh": tariffa_eur_kwh,
            "kwp_installati": kwp_installati,
            "area": area,
            "tipo_impresa": tipo_impresa,
        },
        "produzione": {
            "producibilità_kwh_kwp_anno": producibilità_kwh_kwp,
            "produzione_annua_kwh": produzione_annua,
            "autoconsumati_kwh": autoconsumati,
            "ceduti_ssp_kwh": ceduti_ssp,
        },
        "flussi": {
            "risparmio_autoconsumo_eur": risparmio_autoconsumo,
            "ricavi_ssp_eur": ricavi_ssp,
            "risparmio_totale_anno_eur": risparmio_totale_anno,
        },
        "investimento": {
            "investimento_lordo_eur": investimento_lordo,
            "contributo_eur": contributo,
            "investimento_netto_eur": investimento_netto,
        },
        "metriche": {
            "payback_anni": round(payback_anni, 2),
            "roi_10_anni_perc": round(roi_10_anni_perc, 1),
            "roi_25_anni_perc": round(roi_25_anni_perc, 1),
        },
    }


def format_report(result: dict) -> str:
    inp = result["input"]
    prod = result["produzione"]
    fl = result["flussi"]
    inv = result["investimento"]
    m = result["metriche"]

    return f"""=== ROI Bandi FER 2026 — GP Impianti calculator ===

Input:
  Consumo annuo:           {inp['consumo_annuo_kwh']:,.0f} kWh
  Tariffa media:           {inp['tariffa_eur_kwh']:.3f} €/kWh
  Impianto installato:     {inp['kwp_installati']:.1f} kWp
  Area:                    {inp['area']}
  Tipo impresa:            {inp['tipo_impresa']}

Produzione (PVGIS-SARAH3 {prod['producibilità_kwh_kwp_anno']} kWh/kWp):
  Produzione annua:        {prod['produzione_annua_kwh']:,.0f} kWh
  Autoconsumati (60%):     {prod['autoconsumati_kwh']:,.0f} kWh
  Ceduti SSP (40%):        {prod['ceduti_ssp_kwh']:,.0f} kWh

Flussi annui:
  Risparmio autoconsumo:   {fl['risparmio_autoconsumo_eur']:,.0f} €/anno
  Ricavi SSP (0,12 €/kWh): {fl['ricavi_ssp_eur']:,.0f} €/anno
  Risparmio totale:        {fl['risparmio_totale_anno_eur']:,.0f} €/anno

Investimento:
  Lordo:                   {inv['investimento_lordo_eur']:,.0f} €
  Contributo Bando FER:    {inv['contributo_eur']:,.0f} €
  Netto cliente:           {inv['investimento_netto_eur']:,.0f} €

Metriche:
  Payback semplice:        {m['payback_anni']} anni
  ROI 10 anni:             {m['roi_10_anni_perc']:+.1f}%
  ROI 25 anni (deg 0,5%):  {m['roi_25_anni_perc']:+.1f}%
"""


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Bandi FER Sardegna 2026 — ROI Calculator")
    p.add_argument("--consumo-annuo", type=float, required=True, help="kWh/anno consumati")
    p.add_argument("--tariffa", type=float, required=True, help="€/kWh tariffa elettrica media (mix F1+F2+F3)")
    p.add_argument("--kwp", type=float, required=True, help="kWp installati")
    p.add_argument("--area", choices=["NORD-EST", "CENTRALE", "MERIDIONALE"], default="NORD-EST")
    p.add_argument("--tipo-impresa", choices=["microimprese", "PMI"], default="PMI")
    p.add_argument("--autoconsumo", type=float, default=AUTOCONSUMO_TIPICO, help="autoconsumo % (default 0.60)")
    p.add_argument("--json", action="store_true", help="output JSON instead of text")
    args = p.parse_args(argv)

    result = compute_roi(
        consumo_annuo_kwh=args.consumo_annuo,
        tariffa_eur_kwh=args.tariffa,
        kwp_installati=args.kwp,
        area=args.area,
        tipo_impresa=args.tipo_impresa,
        autoconsumo_perc=args.autoconsumo,
    )

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(format_report(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
