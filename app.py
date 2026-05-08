"""
Bourse360 — single-file Streamlit app
Run with:  streamlit run bourse360.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import requests
import os
from datetime import datetime, timezone
from functools import lru_cache

# ═══════════════════════════════════════════════════════════════════════════════
# DATA LAYER
# ═══════════════════════════════════════════════════════════════════════════════


# ══════════════════════════════════════════════════════════════════════════════
# BOURSE360 BRAND ASSETS — Inline SVG logos (no external files needed)
# ══════════════════════════════════════════════════════════════════════════════

_B360_LOGO_FULL = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 90" role="img">
<title>Bourse360 — Ghana Markets Terminal</title>
<defs>
  <linearGradient id="lg1" x1="0%" y1="0%" x2="100%" y2="100%">
    <stop offset="0%" stop-color="#0ea5e9"/>
    <stop offset="100%" stop-color="#6366f1"/>
  </linearGradient>
  <linearGradient id="lg2" x1="0%" y1="0%" x2="0%" y2="100%">
    <stop offset="0%" stop-color="#38bdf8"/>
    <stop offset="100%" stop-color="#6366f1" stop-opacity="0.5"/>
  </linearGradient>
</defs>
<circle cx="44" cy="45" r="35" fill="none" stroke="url(#lg1)" stroke-width="2"/>
<circle cx="44" cy="45" r="27" fill="#0d1117"/>
<path d="M 24 30 A 24 24 0 0 1 64 30" fill="none" stroke="#38bdf8" stroke-width="2.5" stroke-linecap="round"/>
<circle cx="64" cy="30" r="4" fill="#38bdf8"/>
<circle cx="24" cy="30" r="3" fill="#6366f1"/>
<rect x="32" y="53" width="5" height="12" rx="1" fill="url(#lg2)" opacity="0.55"/>
<rect x="40" y="47" width="5" height="18" rx="1" fill="url(#lg2)" opacity="0.75"/>
<rect x="48" y="41" width="5" height="24" rx="1" fill="url(#lg2)"/>
<polyline points="34,53 42,44 50,38 58,32" fill="none" stroke="#38bdf8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
<circle cx="58" cy="32" r="3" fill="#38bdf8"/>
<text x="88" y="52" font-family="Arial Black,sans-serif" font-weight="900" font-size="34" fill="#f1f5f9" letter-spacing="-1">Bourse<tspan fill="#38bdf8">360</tspan></text>
<text x="89" y="68" font-family="Arial,sans-serif" font-size="10" fill="#475569" letter-spacing="3">GHANA MARKETS TERMINAL</text>
</svg>"""

_B360_LOGO_SMALL = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 185 52" role="img">
<title>Bourse360</title>
<defs>
  <linearGradient id="slg1" x1="0%" y1="0%" x2="100%" y2="100%">
    <stop offset="0%" stop-color="#0ea5e9"/>
    <stop offset="100%" stop-color="#6366f1"/>
  </linearGradient>
  <linearGradient id="slg2" x1="0%" y1="0%" x2="0%" y2="100%">
    <stop offset="0%" stop-color="#38bdf8"/>
    <stop offset="100%" stop-color="#6366f1" stop-opacity="0.5"/>
  </linearGradient>
</defs>
<circle cx="25" cy="26" r="20" fill="none" stroke="url(#slg1)" stroke-width="1.5"/>
<circle cx="25" cy="26" r="15" fill="#0d1117"/>
<path d="M 12 17 A 14 14 0 0 1 38 17" fill="none" stroke="#38bdf8" stroke-width="2" stroke-linecap="round"/>
<circle cx="38" cy="17" r="3" fill="#38bdf8"/>
<rect x="18" y="31" width="3" height="8" rx="1" fill="url(#slg2)" opacity="0.55"/>
<rect x="23" y="27" width="3" height="12" rx="1" fill="url(#slg2)" opacity="0.75"/>
<rect x="28" y="22" width="3" height="17" rx="1" fill="url(#slg2)"/>
<polyline points="19,31 24,25 29,19 36,14" fill="none" stroke="#38bdf8" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
<circle cx="36" cy="14" r="2.5" fill="#38bdf8"/>
<text x="52" y="30" font-family="Arial Black,sans-serif" font-weight="900" font-size="19" fill="#f1f5f9" letter-spacing="-0.5">Bourse<tspan fill="#38bdf8">360</tspan></text>
<text x="53" y="43" font-family="Arial,sans-serif" font-size="8" fill="#475569" letter-spacing="2.5">GHANA MARKETS</text>
</svg>"""

_B360_MARK_ONLY = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 50 50" role="img">
<title>Bourse360 mark</title>
<defs>
  <linearGradient id="mlg1" x1="0%" y1="0%" x2="100%" y2="100%">
    <stop offset="0%" stop-color="#0ea5e9"/>
    <stop offset="100%" stop-color="#6366f1"/>
  </linearGradient>
  <linearGradient id="mlg2" x1="0%" y1="0%" x2="0%" y2="100%">
    <stop offset="0%" stop-color="#38bdf8"/>
    <stop offset="100%" stop-color="#6366f1" stop-opacity="0.5"/>
  </linearGradient>
</defs>
<circle cx="25" cy="25" r="23" fill="none" stroke="url(#mlg1)" stroke-width="2"/>
<circle cx="25" cy="25" r="17" fill="#0d1117"/>
<path d="M 8 16 A 18 18 0 0 1 42 16" fill="none" stroke="#38bdf8" stroke-width="2.5" stroke-linecap="round"/>
<circle cx="42" cy="16" r="3.5" fill="#38bdf8"/>
<rect x="16" y="32" width="4" height="9" rx="1" fill="url(#mlg2)" opacity="0.55"/>
<rect x="22" y="27" width="4" height="14" rx="1" fill="url(#mlg2)" opacity="0.8"/>
<rect x="28" y="22" width="4" height="19" rx="1" fill="url(#mlg2)"/>
<polyline points="18,32 24,25 30,19 38,12" fill="none" stroke="#38bdf8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
<circle cx="38" cy="12" r="3" fill="#38bdf8"/>
</svg>"""

GSE_API     = "https://dev.kwayisi.org/apis/gse"
FALLBACK_URL = "https://african-markets.com/en/stock-markets/gse/listed-companies"
HEADERS     = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/html, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "no-cache",
}

def _safe_get(url: str, timeout: int = 20, retries: int = 3) -> requests.Response | None:
    """Robust HTTP GET with retries — handles cloud network latency."""
    import time
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=timeout)
            resp.raise_for_status()
            return resp
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)  # exponential backoff: 1s, 2s, 4s
            continue
    return None

# SECTOR_MAP defined below after _GSE_COMPANIES

CHART_COLORS = ["#378ADD", "#1D9E75", "#EF9F27", "#E24B4A", "#7F77DD", "#D85A30"]
PERIOD_DAYS  = {"1M": 30, "3M": 90, "6M": 180, "1Y": 365, "All": 99999}


# ── Market hours ──────────────────────────────────────────────────────────────

def market_is_open() -> bool:
    now = datetime.now(timezone.utc)
    if now.weekday() >= 5:
        return False
    opens  = now.replace(hour=10, minute=0, second=0, microsecond=0)
    closes = now.replace(hour=15, minute=0, second=0, microsecond=0)
    return opens <= now <= closes


# ── Column name aliases (covers all known GSE API variants) ─────────────────

# Maps every known raw column name → our standard name
# ── Column normalisation ─────────────────────────────────────────────────────
# The GSE API /live endpoint returns:
#   "name"   = ticker symbol (e.g. "GCB", "MTNGH")  ← NOT the company name
#   "price"  = current price
#   "change" = price change % (0 for unchanged stocks)
#   "volume" = shares traded
# Company full names come from /equities/<symbol> profile endpoint.

_COL_ALIASES = {
    # ticker / symbol
    "ticker": "symbol", "code": "symbol", "equity": "symbol",
    # company full name (scraper sources)
    "company": "name", "stock": "name", "description": "name",
    # price
    "closeprice": "price", "close": "price", "last price": "price",
    "lastprice": "price", "last": "price", "currentprice": "price",
    # change %
    "pricechg": "change", "chg%": "change", "change%": "change",
    "changepct": "change", "percentchange": "change", "pct_change": "change",
    "pricechange": "change", "chgpct": "change",
    # volume
    "vol": "volume", "tradedvolume": "volume", "shares": "volume",
}

# Cache of symbol -> full company name fetched from /equities/<symbol>
_COMPANY_NAMES: dict = {}


# ── Full GSE listed company database ─────────────────────────────────────────
_GSE_COMPANIES = {
    "ACCESS": {
        "name":        "Access Bank Ghana Plc",
        "listed":      "21st December, 2016",
        "capital":     "GHS 400,000,000",
        "issued":      "118,093,134",
        "authorised":  "173,947,596 ordinary shares",
        "sector":      "Financials",
        "office":      "Starlets '91 Road Opposite Accra Sports Stadium, Osu Accra",
        "nature":      "Public limited liability company licensed to carry out universal banking.",
        "directors":   "Ama Sarpong Bawuah (Chairperson), Pearl Nkrumah (Managing Director), David Dodoo-Arhin, Bayuo Warisa, Hadiza Ambursa, Yvette Adounvo Atekpe, Jacob Kwame Kholi, Elikem Nutifafa Kuenyehia",
    },
    "ADB": {
        "name":        "Agricultural Development Bank",
        "listed":      "December 12, 2016",
        "capital":     "GHC 698,700,000",
        "issued":      "346,952,253",
        "authorised":  "—",
        "sector":      "Financials",
        "nature":      "A development bank with a mandate to provide banking and credit services to support agricultural development in Ghana.",
    },
    "AGA": {
        "name":        "AngloGold Ashanti Plc",
        "listed":      "27/04/2004",
        "capital":     "ZAR 4,899,021,716.98",
        "issued":      "417,339,100 ordinary shares",
        "authorised":  "600,000,000",
        "sector":      "Mining",
    },
    "ALW": {
        "name":        "Aluworks Ltd",
        "listed":      "29/11/1996",
        "capital":     "GHS —",
        "issued":      "236,685,180 ordinary shares",
        "authorised":  "1,000,000,000 ordinary shares",
        "sector":      "Manufacturing",
    },
    "ALLGH": {
        "name":        "Atlantic Lithium Limited",
        "listed":      "13/05/2024",
        "capital":     "AUD$ 129,873,021",
        "issued":      "649,669,053",
        "authorised":  "—",
        "sector":      "Mining",
    },
    "ASG": {
        "name":        "Asante Gold Corporation",
        "listed":      "29/06/2022",
        "capital":     "C$ 20,366,275",
        "issued":      "315,010,000",
        "authorised":  "—",
        "sector":      "Mining",
    },
    "BOPP": {
        "name":        "Benso Oil Palm Plantation Ltd",
        "listed":      "16/04/2004",
        "capital":     "GHS —",
        "issued":      "34,800,000",
        "authorised":  "50,000,000 shares of no par value",
        "sector":      "Agribusiness",
    },
    "CAL": {
        "name":        "CalBank PLC",
        "listed":      "05/11/2004",
        "capital":     "GHS —",
        "issued":      "548,260,000",
        "authorised":  "1,000,000,000",
        "sector":      "Financials",
    },
    "CLYD": {
        "name":        "Clydestone (Ghana) Limited",
        "listed":      "19/05/2004",
        "capital":     "GHS —",
        "issued":      "34,000,000",
        "authorised":  "100,000,000",
        "sector":      "Real Estate",
    },
    "CMLT": {
        "name":        "Camelot Ghana Ltd",
        "listed":      "17/09/1999",
        "capital":     "GHS 217,467",
        "issued":      "6,830,000",
        "authorised":  "20,000,000",
        "sector":      "Manufacturing",
    },
    "CPC": {
        "name":        "Cocoa Processing Company",
        "listed":      "14/02/2003",
        "capital":     "GHS —",
        "issued":      "2,038,070,000",
        "authorised":  "20,000,000,000",
        "sector":      "Consumer Goods",
    },
    "DASPHARMA": {
        "name":        "Dannex Ayrton Starwin Plc",
        "listed":      "—",
        "capital":     "—",
        "issued":      "—",
        "authorised":  "—",
        "sector":      "Healthcare",
    },
    "EGH": {
        "name":        "Ecobank Ghana PLC",
        "listed":      "13/07/2022",
        "capital":     "GHS 226.64 million",
        "issued":      "293,230,000",
        "authorised":  "500,000,000",
        "sector":      "Financials",
    },
    "EGL": {
        "name":        "Enterprise Group PLC",
        "listed":      "—",
        "capital":     "GHS 258,886,100",
        "issued":      "170,892,825",
        "authorised":  "200,000,000",
        "sector":      "Insurance",
    },
    "ETI": {
        "name":        "Ecobank Transnational Inc",
        "listed":      "11/09/2006",
        "capital":     "US$ 867,714,000",
        "issued":      "24,067,750,000",
        "authorised":  "800,000,000",
        "sector":      "Financials",
    },
    "FML": {
        "name":        "Fan Milk Limited",
        "listed":      "18/10/1991",
        "capital":     "GHS —",
        "issued":      "116,210,000",
        "authorised":  "200,000,000",
        "sector":      "Consumer Goods",
    },
    "GCB": {
        "name":        "Ghana Commercial Bank Limited",
        "listed":      "17/05/1996",
        "capital":     "GHC 72,000,000",
        "issued":      "265,000,000",
        "authorised":  "1,500,000,000",
        "sector":      "Financials",
    },
    "GGBL": {
        "name":        "Guinness Ghana Breweries Plc",
        "listed":      "23/08/1991",
        "capital":     "GHS 272,879,113.44",
        "issued":      "100,000,000",
        "authorised":  "—",
        "sector":      "Consumer Goods",
    },
    "GOIL": {
        "name":        "GOIL PLC",
        "listed":      "16/11/2007",
        "capital":     "GHS —",
        "issued":      "391,860,000",
        "authorised":  "1,000,000,000",
        "sector":      "Oil & Gas",
    },
    "MAC": {
        "name":        "Mega African Capital Limited",
        "listed":      "23/04/2014",
        "capital":     "GHS —",
        "issued":      "9,950,000",
        "authorised":  "—",
        "sector":      "Financials",
    },
    "MTNGH": {
        "name":        "MTN Ghana",
        "listed":      "05/09/2018",
        "capital":     "GHS 1,363,000,000",
        "issued":      "—",
        "authorised":  "100,000,000,000",
        "sector":      "Telecoms",
    },
    "PBC": {
        "name":        "Produce Buying Company Ltd",
        "listed":      "17/05/2000",
        "capital":     "GHC 4,914,377",
        "issued":      "480,000,000",
        "authorised":  "20,000,000,000",
        "sector":      "Agribusiness",
    },
    "RBGH": {
        "name":        "Republic Bank (Ghana) PLC",
        "listed":      "05/10/1994",
        "capital":     "GHC 401,190,624",
        "issued":      "851,966,373",
        "authorised":  "1,000,000,000",
        "sector":      "Financials",
    },
    "SCB": {
        "name":        "Standard Chartered Bank Ghana Ltd",
        "listed":      "—",
        "capital":     "GHS —",
        "issued":      "115,510,000 ordinary + 17,480,000 pref",
        "authorised":  "250,000,000 ordinary",
        "sector":      "Financials",
    },
    "SIC": {
        "name":        "SIC Insurance Company Limited",
        "listed":      "25/01/2008",
        "capital":     "GHC 2,500,000",
        "issued":      "195,650,000",
        "authorised":  "500,000,000",
        "sector":      "Insurance",
    },
    "SOGEGH": {
        "name":        "Societe Generale Ghana Limited",
        "listed":      "13/10/1995",
        "capital":     "GHC 62,393,557.80",
        "issued":      "429,060,000",
        "authorised":  "500,000,000",
        "sector":      "Financials",
    },
    "SWL": {
        "name":        "Sam Wood Ltd",
        "listed":      "24/04/2002",
        "capital":     "GHC 220,990",
        "issued":      "21,830,000",
        "authorised":  "100,000,000",
        "sector":      "Manufacturing",
    },
    "TBL": {
        "name":        "Trust Bank Limited (The Gambia)",
        "listed":      "15/11/2002",
        "capital":     "Dalasis 200,000,000",
        "issued":      "22,750,000",
        "authorised":  "200,000,000",
        "sector":      "Financials",
    },
    "TLW": {
        "name":        "Tullow Oil Plc",
        "listed":      "27/07/2011",
        "capital":     "GBP 144,728,808.80",
        "issued":      "906,960,000",
        "authorised":  "—",
        "sector":      "Oil & Gas",
    },
    "TOTAL": {
        "name":        "TotalEnergies Ghana PLC",
        "listed":      "—",
        "capital":     "GHS 51,222,715.01",
        "issued":      "111,874,072",
        "authorised":  "111,874,072",
        "sector":      "Oil & Gas",
    },
    "UNIL": {
        "name":        "Unilever Ghana PLC",
        "listed":      "—",
        "capital":     "GHS —",
        "issued":      "62,500,000",
        "authorised":  "100,000,000",
        "sector":      "Consumer Goods",
    },
    "ZEN": {
        "name":        "Zen Petroleum Limited",
        "listed":      "—",
        "capital":     "GHS —",
        "issued":      "—",
        "authorised":  "—",
        "sector":      "Oil & Gas",
        "nature":      "Independent downstream petroleum marketing company operating fuel service stations and providing bulk fuel supply across Ghana.",
    },
    "SAMBA": {
        "name":        "Kasapreko Company Limited",
        "listed":      "—",
        "capital":     "GHS —",
        "issued":      "—",
        "authorised":  "—",
        "sector":      "Consumer Goods",
        "nature":      "One of Ghana's largest beverage manufacturers, producing alcoholic and non-alcoholic drinks including Alomo Bitters, Kasapreko Schnapps, and a wide range of water and juice products.",
    },
}

# Quick name lookup (backward compat with existing code)
_GSE_NAMES = {k: v["name"] for k, v in _GSE_COMPANIES.items()}
# Extra tickers from live feed not in company database
_GSE_NAMES.update({
    "ZEN":     "Zen Petroleum Limited",
    "SAMBA":   "Kasapreko Company Limited",
    "DIGICUT": "Digicut Ghana Limited",
    "HORDS":   "Hords Limited",
    "MMH":     "Meridian-Marshalls Holdings",
    "IIL":     "Industrial Insurance Limited",
    "GLD":     "Gold Fields Limited",
    "AADS":    "Dannex Ayrton Starwin Plc",
})


# ── Company descriptions (for Stock Detail "About" section) ─────────────────
_GSE_ABOUT = {
    "GCB":    "GCB Bank Limited is the largest indigenous Ghanaian bank by total assets. Established in 1953, it operates a nationwide network of branches and provides retail, commercial, and corporate banking services across Ghana.",
    "MTNGH":  "MTN Ghana (Scancom PLC) is the largest telecommunications company in Ghana, providing mobile voice, data, and financial services (MoMo) to millions of subscribers. Listed on the GSE in 2018.",
    "GOIL":   "GOIL PLC (Ghana Oil Company) is Ghana's leading petroleum marketing company, operating over 200 service stations and providing bulk fuel, lubricants, and aviation fueling services nationwide.",
    "EGH":    "Ecobank Ghana PLC is part of the pan-African Ecobank Group, providing banking services across retail, corporate, and investment banking segments. One of the largest banks by branch network in Ghana.",
    "ETI":    "Ecobank Transnational Incorporated (ETI) is the parent company of the Ecobank Group, one of Africa's largest banking groups with presence in 35 African countries.",
    "GGBL":   "Guinness Ghana Breweries PLC manufactures and markets premium beers and malt beverages in Ghana. Products include Guinness, Star Beer, Orijin, and Malta Guinness.",
    "TOTAL":  "TotalEnergies Ghana PLC is the leading oil marketing company in Ghana, operating a network of service stations and providing lubricants, bitumen, and industrial fuel products.",
    "SCB":    "Standard Chartered Bank Ghana Ltd is one of the oldest and most prestigious banks in Ghana, providing a full range of financial services to individuals, SMEs, and corporate clients.",
    "CAL":    "CalBank PLC is a leading commercial bank in Ghana focused on retail, SME, and corporate banking. Known for its innovative digital banking products and growing branch network.",
    "SOGEGH": "Societe Generale Ghana Limited is part of the global Societe Generale Group, offering retail, corporate, and investment banking services to individuals and businesses in Ghana.",
    "ACCESS": "Access Bank Ghana PLC is a subsidiary of Access Bank Group, one of Africa's largest banks. Provides retail, business, and corporate banking services across Ghana.",
    "FML":    "Fan Milk Limited is a leading manufacturer and marketer of frozen dairy and juice products in Ghana under the Fan brand. A household name with products sold through over 15,000 pushcarts.",
    "ALLGH":  "Atlantic Lithium Limited is developing the Ewoyaa Lithium Project in Ghana's Central Region — set to become Ghana's first lithium mine. The company collaborates with Piedmont Lithium and benefits from strong government support.",
    "SIC":    "SIC Insurance Company Limited is one of Ghana's oldest and largest insurance companies, offering life, non-life, and reinsurance products to individuals and corporate clients.",
    "BOPP":   "Benso Oil Palm Plantation Ltd operates one of the largest oil palm plantations in Ghana. Products include crude palm oil and palm kernel oil supplied to local and international markets.",
    "AGA":    "AngloGold Ashanti Plc is one of the world's largest gold mining companies. Operations in Ghana include the Obuasi and Iduapriem mines, which are among Africa's most productive gold mines.",
    "ASG":    "Asante Gold Corporation is a gold exploration and development company focused on projects in Ghana, including the Kubi Gold Project and Fahiakoba deposit in the Ashanti Gold Belt.",
    "EGL":    "Enterprise Group PLC is one of Ghana's leading financial services holding companies, with subsidiaries spanning life insurance (Enterprise Life), general insurance, properties, and trustees.",
    "RBGH":   "Republic Bank (Ghana) PLC, formerly HFC Bank, is a full-service commercial bank providing mortgage finance, retail banking, and corporate banking services across Ghana.",
    "UNIL":   "Unilever Ghana PLC manufactures and distributes a wide range of consumer goods including personal care products (Vaseline, Lux), home care (OMO, Sunlight), and food products (Lipton, Royco).",
    "TLW":    "Tullow Oil Plc is one of Africa's leading independent oil companies, operating the Jubilee and TEN oil fields offshore Ghana, which together produce hundreds of thousands of barrels per day.",
    "ADB":    "Agricultural Development Bank (ADB) is a state-owned development financial institution supporting Ghana's agricultural sector with affordable credit, savings, and financial services.",
    "PBC":    "Produce Buying Company Ltd is a major cocoa purchasing company in Ghana, licensed by COCOBOD to purchase and export cocoa beans from farmers across the country.",
    "CPC":    "Cocoa Processing Company (CPC) processes raw cocoa beans into semi-finished products including cocoa liquor, cocoa butter, and cocoa powder for export and domestic use.",
    "CLYD":   "Clydestone (Ghana) Limited provides information technology solutions and services to businesses and institutions in Ghana, including software development, systems integration, and ICT consulting.",
    "CMLT":   "Camelot Ghana Ltd is a printing and publishing company providing commercial printing, security printing, and office supplies to businesses and government institutions in Ghana.",
    "ZEN":    "Zen Petroleum Limited is an independent downstream petroleum marketing company operating a growing network of fuel service stations across Ghana. The company provides bulk fuel supply, lubricants, and related petroleum products to industrial and retail customers.",
    "SAMBA":  "Kasapreko Company Limited is one of Ghana's largest and most recognised beverage manufacturers. The company produces a wide portfolio of alcoholic and non-alcoholic beverages including the iconic Alomo Bitters, Kasapreko Schnapps, Kasapreko Water, and various juice products. With a strong distribution network across Ghana and export presence in West Africa, Kasapreko is a household brand in the FMCG space.",
}
# Auto-build sector map now that _GSE_COMPANIES is defined
SECTOR_MAP = {k: v["sector"] for k, v in _GSE_COMPANIES.items()}
SECTOR_MAP.update({
    "AIRTELGH": "Telecoms",    "TOR":   "Oil & Gas",
    "HFC":      "Financials",  "GSR":   "Mining",
    "MOGL":     "Mining",      "AYRTN": "Healthcare",
    "ZEN":      "Oil & Gas",   "SAMBA": "Consumer Goods",
    "DIGICUT":  "Technology",  "HORDS": "Healthcare",
    "MMH":      "Financials",  "IIL":   "Insurance",
})

# ── Logo & avatar helpers (module-level so all pages can use them) ──────────
import base64 as _b64_mod, pathlib as _path_mod

# Sector-based badge colours (consistent across all cards and table)
_SC_COLORS = {
    "GCB":"#0a1f3d,#60a5fa","EGH":"#0a1f3d,#60a5fa","SCB":"#0a1f3d,#60a5fa",
    "CAL":"#0a1f3d,#60a5fa","ETI":"#0a1f3d,#60a5fa","ACCESS":"#0a1f3d,#60a5fa",
    "SOGEGH":"#0a1f3d,#60a5fa","RBGH":"#0a1f3d,#60a5fa","ADB":"#0a1f3d,#60a5fa",
    "MTNGH":"#2d1d00,#fbbf24",
    "GOIL":"#001a0d,#34d399","TOR":"#001a0d,#34d399","TOTAL":"#001a0d,#34d399",
    "GGBL":"#2d0808,#f87171","FML":"#2d0808,#f87171","UNIL":"#2d0808,#f87171",
    "BOPP":"#0d1f00,#86efac","PBC":"#0d1f00,#86efac",
    "MOGL":"#1f1000,#fb923c","GSR":"#1f1000,#fb923c","AGA":"#1f1000,#fb923c",
    "ALLGH":"#130a24,#c084fc","AYRTN":"#130a24,#c084fc","CPC":"#130a24,#c084fc",
    "SIC":"#001020,#38bdf8","ENTERPRISE":"#001020,#38bdf8",
    "CLYD":"#200010,#f472b6","HFC":"#200010,#f472b6",
    "CMLT":"#1a1000,#fb923c","ASG":"#1f1000,#fbbf24","AADS":"#0d1f00,#86efac",
    "BOPP":"#0d1f00,#86efac","CLYD":"#200010,#f472b6",
}
_AV_FALLBACK = [
    ("#0c2a4a","#38bdf8"), ("#0d2b1a","#4ade80"), ("#2a1a0c","#fb923c"),
    ("#1a0c2a","#a78bfa"), ("#2a0c1a","#f472b6"), ("#0c2a22","#34d399"),
]

# ── Logo loader ──────────────────────────────────────────────────────────
# Maps GSE ticker symbols to your actual logo filenames in the logos/ folder.
# Add more entries here as you collect more logos.
import base64, pathlib

_LOGO_FILES = {
    # ── Exact filenames from logos/ folder (updated May 2026) ────────────────
    "ACCESS":      "accessbankghana_logo",
    "ADB":         "ADB images",
    "ALW":         "ALUWORKS",          # Aluworks Ltd
    "ALLGH":       "atlantic_lithium_limited_logo",
    "AGA":         "AngloGold",         # AngloGold Ashanti
    "CAL":         "CALbank PLC",
    "CMLT":        "Camelot",
    "CLYD":        "Ckydestone",        # note: Clydestone logo filename
    "CPC":         "cocoa-processing-company",
    "DASPHARMA":   "Dannex images",
    "EGH":         "Ecobank_Logo.svg",
    "ETI":         "ETI",               # Ecobank Transnational
    "FML":         "Fan milk-logo",
    "FAB":         "first atlantic",    # First Atlantic Bank
    "GCB":         "GCB",
    "AGA_2":       "gh-aad-logo",       # alternate AngloGold
    "BOPP":        "gh-bopp-logo",
    "EGL":         "gh-egl-logo",
    "ENTERPRISE":  "gh-egl-logo",
    "PBC":         "gh-pbc-logo",
    "SIC":         "gh-sic-logo",
    "SOGEGH":      "gh-sogegh-logo",
    "TLW":         "gh-tlw-logo",
    "TOTAL":       "gh-total-logo",
    "GOIL":        "GOIL",
    "GGBL":        "Guiness",           # Guinness Ghana (note spelling in folder)
    "MAC":         "mega",              # Mega African Capital
    "MTNGH":       "MTNGH",
    "GGBL_ALT":    "New_Guinness_Ghana_Logo",
    "RBGH":        "RBGH images",
    "SWL":         "sam wood",
    "SCB":         "Standard Chartered", # Standard Chartered new filename
    "UNIL":        "Unilever.svg",
    # ZEN logo seen — add when ticker confirmed
}

# Alias map for duplicate/alternate filenames
_LOGO_ALIASES = {
    "GGBL": ["Guiness", "New_Guinness_Ghana_Logo"],
    "AGA":  ["AngloGold", "gh-aad-logo"],
    "SCB":  ["Standard Chartered", "Standard_Chartered-Logo.wine"],
    "FML":  ["Fan milk-logo", "fanmilk"],
    "ETI":  ["ETI", "Ecobank_Logo"],
}

def _load_logo_b64(sym: str) -> str | None:
    """
    Returns base64 data URI for logo.
    Searches in 'logo/' and 'logos/' folders.
    Tries: exact map → alias map → symbol name → fuzzy scan.
    """
    import base64, pathlib as _pl

    # Build all candidate base filenames
    candidates = []
    if sym in _LOGO_FILES:
        candidates.append(_LOGO_FILES[sym])
    if sym in _LOGO_ALIASES:
        candidates.extend(_LOGO_ALIASES[sym])
    candidates += [sym.upper(), sym.lower(), sym,
                   sym.replace("GH",""), sym + "GH"]

    for folder_name in ["logo", "logos"]:
        logos_dir = _pl.Path(folder_name)
        if not logos_dir.exists():
            continue

        # Strategy 1: exact filename from map
        candidates = []
        if sym in _LOGO_FILES:
            candidates.append(_LOGO_FILES[sym])
        # Strategy 2: ticker name variants
        candidates += [sym.upper(), sym.lower(), sym]

        for base_name in candidates:
            for ext in ["png", "jpg", "jpeg", "svg", "webp", "PNG", "JPG", "SVG"]:
                path = logos_dir / f"{base_name}.{ext}"
                if path.exists():
                    mime = "image/svg+xml" if ext.lower() == "svg" else f"image/{ext.lower()}"
                    data = base64.b64encode(path.read_bytes()).decode()
                    return f"data:{mime};base64,{data}"

        # Strategy 3: fuzzy scan — strip spaces/dashes/underscores and compare
        try:
            def _normalise(s):
                return s.lower().replace("-","").replace("_","").replace(" ","").replace(".","")

            ticker_norm = _normalise(sym)
            all_files   = list(logos_dir.iterdir())

            # Exact normalised match first
            for f in all_files:
                if _normalise(f.stem) == ticker_norm:
                    ext  = f.suffix[1:].lower()
                    mime = "image/svg+xml" if ext == "svg" else f"image/{ext}"
                    return f"data:{mime};base64,{base64.b64encode(f.read_bytes()).decode()}"

            # Prefix match (e.g. "accessbankghana_logo" starts with "access")
            for f in all_files:
                if _normalise(f.stem).startswith(ticker_norm) and len(ticker_norm) >= 3:
                    ext  = f.suffix[1:].lower()
                    mime = "image/svg+xml" if ext == "svg" else f"image/{ext}"
                    return f"data:{mime};base64,{base64.b64encode(f.read_bytes()).decode()}"

            # Contains match (e.g. "MTN" inside "MTN Ghana Logo")
            for f in all_files:
                if ticker_norm in _normalise(f.stem) and len(ticker_norm) >= 3:
                    ext  = f.suffix[1:].lower()
                    mime = "image/svg+xml" if ext == "svg" else f"image/{ext}"
                    return f"data:{mime};base64,{base64.b64encode(f.read_bytes()).decode()}"
        except Exception:
            pass

    return None

def _av(sym):
    logo_uri = _load_logo_b64(sym)
    if logo_uri:
        # Real logo image found in logos/ folder
        return f'''<div class="sc-avatar" style="background:#0d1117;border:1px solid #1e2d3d;padding:4px">
          <img src="{logo_uri}" style="width:100%;height:100%;object-fit:contain;border-radius:6px" alt="{sym}"/>
        </div>'''
    # Fallback: sector-coloured wordmark badge
    if sym in _SC_COLORS:
        bg, fg = _SC_COLORS[sym].split(",")
    else:
        i = sum(ord(c) for c in sym) % len(_AV_FALLBACK)
        bg, fg = _AV_FALLBACK[i]
    wm_big  = sym[0]
    wm_rest = sym[1:3] if len(sym) > 1 else ""
    return f"""<div class="sc-avatar" style="background:{bg};border:1px solid {fg}22;flex-direction:column;line-height:1">
      <div style="font-size:14px;font-weight:900;color:{fg};letter-spacing:-1px;font-family:Arial Black,sans-serif">{wm_big}</div>
      <div style="font-size:7px;font-weight:700;color:{fg}99;letter-spacing:1px;margin-top:-2px">{wm_rest}</div>
    </div>"""

def _company(sym, name):
    return _GSE_NAMES.get(sym, name) if name == sym else name



def _fetch_all_company_names(symbols: list) -> dict:
    """Start with hardcoded map, then enrich from API /equities endpoint."""
    names = dict(_GSE_NAMES)  # start with known names
    try:
        resp = _safe_get(f"{GSE_API}/equities", timeout=20)
        if resp is None:
            return names
        for item in resp.json():
            raw = {k.lower(): v for k, v in item.items()}
            # API returns ticker in "name" field
            sym = str(raw.get("name", raw.get("ticker", raw.get("symbol", "")))).upper().strip()
            # Try multiple possible company name fields
            company = (
                raw.get("company") or raw.get("equity") or
                raw.get("description") or raw.get("fullname") or
                raw.get("longname") or names.get(sym, sym)
            )
            if sym and company:
                names[sym] = str(company).strip()
    except Exception:
        pass
    return names


def _normalise_columns(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [c.lower().strip() for c in df.columns]
    return df.rename(columns=_COL_ALIASES)


def _coerce_numeric(df: pd.DataFrame) -> pd.DataFrame:
    for col in ["price", "change", "volume"]:
        if col in df.columns:
            df[col] = (
                df[col].astype(str)
                       .str.replace("%", "", regex=False)
                       .str.replace(",", "", regex=False)
                       .str.strip()
            )
            df[col] = pd.to_numeric(df[col], errors="coerce")
    if "volume" in df.columns:
        df["volume"] = df["volume"].fillna(0).astype(int)
    if "change" in df.columns:
        df["change"] = df["change"].fillna(0)
    return df


def _finalise(df: pd.DataFrame, company_names: dict = None) -> pd.DataFrame:
    """Ensure all required columns exist with correct values."""
    required = ["symbol", "name", "price", "change", "volume"]

    # API sends ticker in "name" col — detect and fix:
    # If there is no "symbol" col but there IS a "name" col with short uppercase values,
    # those are tickers, not company names.
    if "symbol" not in df.columns or df["symbol"].astype(str).str.strip().eq("").all():
        if "name" in df.columns:
            df["symbol"] = df["name"]

    df["symbol"] = df["symbol"].astype(str).str.upper().str.strip()

    # Attach full company names if available
    if company_names:
        df["name"] = df["symbol"].map(company_names).fillna(df["symbol"])
    elif "name" not in df.columns or df["name"].astype(str).str.strip().eq(df["symbol"]).all():
        # No company names yet — use symbol as placeholder
        df["name"] = df["symbol"]

    for col in ["price", "change", "volume"]:
        if col not in df.columns:
            df[col] = 0

    return df[required].dropna(subset=["price"]).reset_index(drop=True)


def _build_df(raw: pd.DataFrame, company_names: dict = None) -> pd.DataFrame:
    return _finalise(_coerce_numeric(_normalise_columns(raw.copy())), company_names)


# ── Live prices ───────────────────────────────────────────────────────────────

_LAST_RAW_COLS: list  = []
_LAST_RAW_SAMPLE: list = []
_DATA_SOURCE: str     = "none"


@st.cache_data(ttl=900, show_spinner="Loading live market data…")
def get_live_prices() -> pd.DataFrame:
    """
    Source priority:
      1. GSE API /live  (tickers in "name" col, company names from /equities)
      2. african-markets.com scrape
      3. gse_history.csv / gse_history.xlsx (most recent date as fallback)
    """
    global _LAST_RAW_COLS, _LAST_RAW_SAMPLE, _DATA_SOURCE

    # Fetch company name lookup from /equities (best-effort, silent fail)
    company_names = _fetch_all_company_names([])

    # ── 1. GSE API ────────────────────────────────────────────────────────────
    try:
        resp = _safe_get(f"{GSE_API}/live", timeout=20)
        if resp is not None:
            raw = pd.DataFrame(resp.json())
            _LAST_RAW_COLS   = raw.columns.tolist()
            _LAST_RAW_SAMPLE = raw.head(3).to_dict("records")
            _DATA_SOURCE     = "GSE API"
            result = _build_df(raw, company_names)
            if not result.empty:
                return result
        else:
            _DATA_SOURCE = "GSE API unreachable"
    except Exception as e:
        _DATA_SOURCE = f"GSE API failed: {e}"

    # ── 2. African-markets scrape ─────────────────────────────────────────────
    try:
        tables = pd.read_html(FALLBACK_URL)
        for tbl in tables:
            _LAST_RAW_COLS   = tbl.columns.tolist()
            _LAST_RAW_SAMPLE = tbl.head(3).to_dict("records")
            result = _build_df(tbl, company_names)
            if not result.empty and "price" in result.columns:
                _DATA_SOURCE = "african-markets.com"
                return result
    except Exception as e:
        _DATA_SOURCE = f"Scrape failed: {e}"

    # ── 3. Local CSV ──────────────────────────────────────────────────────────
    try:
        df = pd.read_csv("gse_history.csv")
        _LAST_RAW_COLS   = df.columns.tolist()
        _LAST_RAW_SAMPLE = df.head(3).to_dict("records")
        df = _normalise_columns(df)
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
            df = df[df["date"] == df["date"].max()]
        if "change" not in df.columns:
            df["change"] = 0.0
        result = _build_df(df, company_names)
        if not result.empty:
            _DATA_SOURCE = "gse_history.csv"
            return result
    except Exception as e:
        _DATA_SOURCE = f"CSV failed: {e}"

    # ── Cloud fallback: load from gse_history CSV/Excel ─────────────────────
    # Your CSV structure (confirmed):
    #   date, ticker, last_price, percent_change, symbol, price, change, volume
    #   Dates mixed format: "27/03/2026" and "2026-03-31"
    #   Real price data is in "price" column with "symbol" column populated
    for _p in ["gse_history.csv", "gse_history.xlsx"]:
        try:
            _h = pd.read_excel(_p, engine="openpyxl") if _p.endswith(".xlsx") else pd.read_csv(_p)
            _h.columns = [c.lower().strip() for c in _h.columns]

            # ── Must have symbol and price ────────────────────────────────────
            if "symbol" not in _h.columns or "price" not in _h.columns:
                continue

            # ── Coerce price first ────────────────────────────────────────────
            _h["price"] = pd.to_numeric(_h["price"], errors="coerce").fillna(0)

            # ── Drop rows with no symbol or no price ─────────────────────────
            _h = _h.dropna(subset=["symbol"])
            _h = _h[_h["symbol"].astype(str).str.strip() != ""]
            _h = _h[_h["symbol"].astype(str).str.strip() != "nan"]

            # ── Parse dates — handle BOTH formats ────────────────────────────
            if "date" in _h.columns:
                _h["date"] = pd.to_datetime(_h["date"], dayfirst=True,
                                            errors="coerce")
                _h = _h.dropna(subset=["date"])
                # Get most recent date that has real price data
                _h_with_price = _h[_h["price"] > 0]
                if _h_with_price.empty:
                    continue
                _latest = _h_with_price["date"].max()
                _h = _h_with_price[_h_with_price["date"] == _latest].copy()


            # ── Change — calculate % from absolute price change ───────────────
            _abs_chg = pd.to_numeric(
                _h.get("change", pd.Series([0]*len(_h))), errors="coerce"
            ).fillna(0)
            _pct_chg = pd.to_numeric(
                _h.get("percent_change", pd.Series([float("nan")]*len(_h))),
                errors="coerce"
            )
            if _pct_chg.notna().sum() > 0:
                _h["change"] = _pct_chg.fillna(0)
            else:
                # percent_change all NaN — derive from absolute change
                _prev_close = (_h["price"] - _abs_chg).replace(0, float("nan"))
                _h["change"] = (_abs_chg / _prev_close * 100).fillna(0).round(2)

            # ── Volume ────────────────────────────────────────────────────────
            if "volume" not in _h.columns:
                _h["volume"] = 0
            _h["volume"] = pd.to_numeric(_h["volume"],
                                          errors="coerce").fillna(0).astype(int)

            # ── Enrich name ───────────────────────────────────────────────────
            _h["symbol"] = _h["symbol"].astype(str).str.strip().str.upper()
            _h["name"]   = _h["symbol"].map(
                lambda s: _GSE_NAMES.get(s, s)
            )

            # ── Return if valid ───────────────────────────────────────────────
            if not _h.empty and _h["price"].sum() > 0:
                return _h[["symbol","name","price","change","volume"]].reset_index(drop=True)

        except Exception:
            continue

    # ── Final stub: company list with zero prices ─────────────────────────────
    return pd.DataFrame([
        {"symbol": s, "name": i.get("name", s),
         "price": 0.0, "change": 0.0, "volume": 0}
        for s, i in _GSE_COMPANIES.items()
    ])


# ── Daily CSV snapshot ───────────────────────────────────────────────────────

def save_daily_snapshot(df: pd.DataFrame, filepath: str = "gse_history.csv") -> bool:
    """
    Appends today's live prices to gse_history.csv.
    Deduplicates by date+symbol so re-runs don't create duplicate rows.
    Also reads existing gse_history.xlsx if CSV doesn't exist yet.
    Returns True if new rows were saved.
    """
    if df.empty:
        return False
    try:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        snap  = df.copy()
        snap["date"]      = today
        snap["timestamp"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        if os.path.exists(filepath):
            existing = pd.read_csv(filepath)
            # Drop today's rows for this symbol set (so we overwrite with latest)
            if "date" in existing.columns and "symbol" in existing.columns:
                existing = existing[existing["date"] != today]
            combined = pd.concat([existing, snap], ignore_index=True)
        else:
            combined = snap

        combined.to_csv(filepath, index=False)
        return True
    except Exception as e:
        return False


def load_historical_comparison(symbol: str, filepath: str = "gse_history.csv") -> pd.DataFrame:
    """
    Loads all historical daily closes for a symbol from the CSV.
    Returns DataFrame with columns: date, price, change, volume
    """
    try:
        df = pd.read_csv(filepath)
        df.columns = [c.lower().strip() for c in df.columns]
        if "symbol" not in df.columns and "name" in df.columns:
            df = df.rename(columns={"name": "symbol"})
        df = df[df["symbol"].astype(str).str.upper() == symbol.upper()].copy()
        df["date"]  = pd.to_datetime(df["date"], errors="coerce")
        df["price"] = pd.to_numeric(df["price"], errors="coerce")
        return df.dropna(subset=["date","price"]).sort_values("date").reset_index(drop=True)
    except Exception:
        return pd.DataFrame(columns=["date","price","change","volume"])


# ── Historical EOD ────────────────────────────────────────────────────────────

@st.cache_data(ttl=3600, show_spinner="Loading history…")
def get_history(symbol: str) -> pd.DataFrame:
    """
    Source priority:
      1. gse_history.csv (local — built daily by save_daily_snapshot)
      2. GSE API /equities/<symbol>/eod (online fallback)
    Returns DataFrame with columns: date, price, change, volume
    """
    frames = []

    # ── 1. Local CSV/Excel (primary — always has data if app has run before) ─
    for csv_path in ["gse_history.csv", "gse_history.xlsx", "data/gse_history.csv", "data/gse_history.xlsx"]:
        try:
            if csv_path.endswith(".xlsx") or csv_path.endswith(".xls"):
                df = pd.read_excel(csv_path, engine="openpyxl")
            else:
                df = pd.read_csv(csv_path)
            df = _normalise_columns(df)
            # Detect symbol column
            sym_col = next((c for c in ["symbol","name"] if c in df.columns), df.columns[0])
            mask = df[sym_col].astype(str).str.upper().str.strip() == symbol.upper().strip()
            if mask.any():
                df = df[mask].copy()
                if "date" in df.columns:
                    df["date"] = pd.to_datetime(df["date"], errors="coerce")
                df = _coerce_numeric(df)
                if "volume" not in df.columns:
                    df["volume"] = 0
                if "change" not in df.columns:
                    df["change"] = df["price"].pct_change() * 100
                df = df.dropna(subset=["price","date"]).sort_values("date").reset_index(drop=True)
                if not df.empty:
                    frames.append(df)
                    break
        except Exception:
            pass

    # ── 2. GSE API EOD (online supplement) ────────────────────────────────────
    try:
        resp = _safe_get(f"{GSE_API}/equities/{symbol.lower()}/eod", timeout=20)
        if resp is None:
            raise Exception("API unreachable")
        df = _normalise_columns(pd.DataFrame(resp.json()))
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
        elif "name" in df.columns:
            df = df.rename(columns={"name": "date"})
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = _coerce_numeric(df)
        if "volume" not in df.columns:
            df["volume"] = 0
        if "change" not in df.columns:
            df["change"] = df["price"].pct_change() * 100
        df = df.dropna(subset=["price","date"]).sort_values("date").reset_index(drop=True)
        if not df.empty:
            frames.append(df)
    except Exception:
        pass

    if not frames:
        return pd.DataFrame(columns=["date","price","change","volume"])

    # Merge CSV + API data, deduplicate by date, keep latest value per date
    combined = pd.concat(frames, ignore_index=True)
    combined = combined.sort_values("date").drop_duplicates(subset=["date"], keep="last")
    return combined.reset_index(drop=True)


# ── Company profile ───────────────────────────────────────────────────────────

@st.cache_data(ttl=86400, show_spinner=False)
def get_profile(symbol: str) -> dict:
    try:
        resp = requests.get(
            f"{GSE_API}/equities/{symbol.lower()}",
            headers=HEADERS, timeout=10,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return {}


# ── Technical indicators ──────────────────────────────────────────────────────

def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    close = df["price"]

    # RSI (14)
    delta = close.diff()
    gain  = delta.clip(lower=0).rolling(14).mean()
    loss  = (-delta.clip(upper=0)).rolling(14).mean()
    df["RSI"] = (100 - 100 / (1 + gain / loss.replace(0, float("nan")))).round(2)

    # MACD (12, 26, 9)
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    df["MACD"]      = (ema12 - ema26).round(4)
    df["Signal"]    = df["MACD"].ewm(span=9, adjust=False).mean().round(4)
    df["MACD_Hist"] = (df["MACD"] - df["Signal"]).round(4)

    # Bollinger Bands (20, 2σ)
    sma20 = close.rolling(20).mean()
    std20 = close.rolling(20).std()
    df["BB_Upper"] = (sma20 + 2 * std20).round(4)
    df["BB_Lower"] = (sma20 - 2 * std20).round(4)
    df["BB_Mid"]   = sma20.round(4)

    # SMA 50
    df["SMA50"] = close.rolling(50).mean().round(4)

    return df


# ── Alerts ────────────────────────────────────────────────────────────────────

def _normalise_change(df: pd.DataFrame) -> pd.DataFrame:
    """
    GSE API sometimes returns change as a decimal fraction (0.033 = 3.3%).
    Detect and convert: if all abs values < 1 and not all zero, multiply by 100.
    """
    df = df.copy()
    chg = df["change"].dropna()
    nonzero = chg[chg != 0]
    if len(nonzero) > 0 and (nonzero.abs() < 1).all():
        df["change"] = (df["change"] * 100).round(2)
    return df


def generate_alerts(df: pd.DataFrame, thresholds: dict) -> list[dict]:
    df = _normalise_change(df)
    alerts = []
    for _, row in df.iterrows():
        chg = float(row.get("change", 0) or 0)
        sym = str(row.get("symbol", "") or row.get("name", ""))
        if chg <= thresholds["drop"]:
            alerts.append({"type": "danger",  "symbol": sym,
                "msg": f"{sym} fell {chg:.2f}% — below {thresholds['drop']}% threshold",
                "change": chg})
        elif chg >= thresholds["rise"]:
            alerts.append({"type": "success", "symbol": sym,
                "msg": f"{sym} rose {chg:.2f}% — above +{thresholds['rise']}% threshold",
                "change": chg})
    return sorted(alerts, key=lambda x: abs(x["change"]), reverse=True)


# ── Analytics engine — returns, volatility, risk metrics, signals ────────────

def compute_stock_analytics(symbol: str) -> dict:
    """
    Returns a full analytics dict for a stock:
      ytd_return, volatility, sharpe, rsi_signal, macd_signal,
      support, resistance, avg_volume, price_vs_sma20, momentum_5d
    """
    hist = get_history(symbol)
    result = {
        "ytd_return": None, "volatility": None, "sharpe": None,
        "signal": "HOLD", "signal_score": 0,
        "rsi_signal": "—", "macd_signal": "—",
        "support": None, "resistance": None,
        "momentum_5d": None, "price_vs_sma20": None,
    }
    if hist.empty or len(hist) < 5:
        return result

    hist = add_indicators(hist)
    prices = hist["price"]

    # YTD return (from first price in history)
    if len(prices) >= 2 and prices.iloc[0] > 0:
        result["ytd_return"] = round((prices.iloc[-1] - prices.iloc[0]) / prices.iloc[0] * 100, 2)

    # Annualised volatility (std of daily returns × √252)
    daily_returns = prices.pct_change().dropna()
    if len(daily_returns) >= 5:
        result["volatility"] = round(daily_returns.std() * (252 ** 0.5) * 100, 2)

        # Sharpe ratio (assume 0% risk-free for GHS)
        mean_ret = daily_returns.mean() * 252
        std_ret  = daily_returns.std() * (252 ** 0.5)
        result["sharpe"] = round(mean_ret / std_ret, 2) if std_ret > 0 else None

    # Support & resistance (rolling 20-day min/max)
    if len(prices) >= 20:
        result["support"]    = round(float(prices.tail(20).min()), 2)
        result["resistance"] = round(float(prices.tail(20).max()), 2)

    # 5-day momentum
    if len(prices) >= 6:
        result["momentum_5d"] = round(
            (prices.iloc[-1] - prices.iloc[-6]) / prices.iloc[-6] * 100, 2
        )

    # Price vs SMA20
    if "BB_Mid" in hist.columns and not hist["BB_Mid"].dropna().empty:
        sma20 = float(hist["BB_Mid"].dropna().iloc[-1])
        curr  = float(prices.iloc[-1])
        result["price_vs_sma20"] = round((curr - sma20) / sma20 * 100, 2) if sma20 > 0 else None

    # Signal engine — composite buy/hold/sell score
    score = 0
    signals = []

    # RSI signal
    rsi_vals = hist["RSI"].dropna()
    if not rsi_vals.empty:
        rsi = float(rsi_vals.iloc[-1])
        if rsi < 35:
            score += 2; signals.append("RSI oversold")
            result["rsi_signal"] = f"BUY ({rsi:.0f})"
        elif rsi > 65:
            score -= 2; signals.append("RSI overbought")
            result["rsi_signal"] = f"SELL ({rsi:.0f})"
        else:
            result["rsi_signal"] = f"NEUTRAL ({rsi:.0f})"

    # MACD signal
    if not hist["MACD"].dropna().empty and not hist["Signal"].dropna().empty:
        macd   = float(hist["MACD"].dropna().iloc[-1])
        signal = float(hist["Signal"].dropna().iloc[-1])
        if macd > signal:
            score += 1; result["macd_signal"] = "BUY (crossover)"
        else:
            score -= 1; result["macd_signal"] = "SELL (crossunder)"

    # Momentum signal
    if result["momentum_5d"] is not None:
        if result["momentum_5d"] > 3:   score += 1
        elif result["momentum_5d"] < -3: score -= 1

    # Price vs SMA
    if result["price_vs_sma20"] is not None:
        if result["price_vs_sma20"] > 2:    score += 1
        elif result["price_vs_sma20"] < -2:  score -= 1

    result["signal_score"] = score
    if   score >= 3:  result["signal"] = "STRONG BUY"
    elif score >= 1:  result["signal"] = "BUY"
    elif score <= -3: result["signal"] = "STRONG SELL"
    elif score <= -1: result["signal"] = "SELL"
    else:             result["signal"] = "HOLD"

    return result


def market_analytics_summary(df: pd.DataFrame) -> dict:
    """Compute market-wide analytics from live prices."""
    if df.empty:
        return {}
    total_vol = int(df["volume"].sum())
    active    = df[df["volume"] > 0]
    breadth   = round(len(df[df["change"] > 0]) / max(len(df), 1) * 100, 1)
    return {
        "breadth_pct": breadth,       # % of stocks advancing
        "avg_change":  round(float(df["change"].mean()), 2),
        "top_mover":   df.loc[df["change"].abs().idxmax(), "symbol"] if not df.empty else "—",
        "active_stocks": len(active),
    }


# ── Market summary ────────────────────────────────────────────────────────────

def market_summary(df: pd.DataFrame) -> dict:
    if df.empty:
        return {}
    vol = int(df["volume"].sum())
    return {
        "gainers":      int((df["change"] > 0).sum()),
        "losers":       int((df["change"] < 0).sum()),
        "unchanged":    int((df["change"] == 0).sum()),
        "total_volume": vol,
        "vol_label":    f"{vol/1_000_000:.2f}M" if vol >= 1_000_000 else f"{vol:,}",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# APP CONFIG & SESSION STATE
# ═══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Bourse360 — Ghana Markets",
    page_icon="🔵",
    layout="wide",
    initial_sidebar_state="expanded",
)
# Inject dark background before any component renders
st.markdown("""
<style>
html, body, [data-testid="stApp"] { background-color:#07091a !important; }
[data-testid="stHeader"]  {
    background:#07091a !important;
    border-bottom:1px solid #141d2e !important;
}
[data-testid="stToolbar"] { background:#07091a !important; }
/* Bourse360 brand gradient overlay */
[data-testid="stApp"]::before {
    content:""; position:fixed; inset:0; pointer-events:none;
    background:radial-gradient(ellipse at 15% 0%,rgba(14,165,233,0.04) 0%,transparent 55%),
               radial-gradient(ellipse at 85% 100%,rgba(99,102,241,0.04) 0%,transparent 55%),
               radial-gradient(ellipse at 50% 50%,rgba(56,189,248,0.01) 0%,transparent 70%);
    z-index:0;
}

/* ── Hide "nav" / "Navigation" radio label ── */
[data-testid="stRadio"] > label { display:none !important; }
[data-testid="stRadio"] > div   { gap:2px !important; }

/* ── Radio nav pill styling ── */
[data-testid="stRadio"] label {
    background:transparent !important;
    border-radius:8px !important;
    padding:9px 14px !important;
    margin:1px 0 !important;
    display:flex !important;
    align-items:center !important;
    cursor:pointer !important;
    font-size:13px !important;
    font-weight:500 !important;
    color:#64748b !important;
    transition:all .15s !important;
    border:1px solid transparent !important;
}
[data-testid="stRadio"] label:hover {
    background:#111827 !important;
    color:#94a3b8 !important;
}
[data-testid="stRadio"] label:has(input:checked) {
    background:#0f2744 !important;
    color:#38bdf8 !important;
    border-color:#1e3a5f !important;
}
/* Hide the radio circle dot */
[data-testid="stRadio"] label > div:first-child { display:none !important; }

/* ── Dataframe dark theme ── */
[data-testid="stDataFrame"] > div { border-radius:12px !important; overflow:hidden !important; }
.stDataFrame iframe { border-radius:12px !important; }
[data-testid="stDataFrame"] { background:#0d1117 !important; }

/* ── Sidebar refinements ── */
[data-testid="stSidebar"] { background:#0b0f1a !important; }
[data-testid="stSidebarContent"] { padding:0 12px !important; }

/* ── Main content bg ── */
.main .block-container { background:#0a0e1a !important; max-width:1400px !important; }

/* ── Hide Streamlit branding ── */
#MainMenu, footer, header { visibility:hidden !important; }
[data-testid="stDecoration"] { display:none !important; }
</style>""", unsafe_allow_html=True)

if "watchlist" not in st.session_state:
    st.session_state.watchlist = ["GCB", "MTNGH"]
if "alert_thresholds" not in st.session_state:
    st.session_state.alert_thresholds = {"drop": -5.0, "rise": 2.0}
if "page" not in st.session_state:
    st.session_state.page = "Overview"
if "sim_result" not in st.session_state:
    st.session_state.sim_result = None
if "portfolio" not in st.session_state:
    st.session_state.portfolio = []  # list of {symbol, shares, buy_price, date}
if "selected_symbol" not in st.session_state:
    st.session_state.selected_symbol = None



# ═══════════════════════════════════════════════════════════════════════════════
# SHARED DATA LOAD
# ═══════════════════════════════════════════════════════════════════════════════

df_live = get_live_prices()
# Normalise change column (handles decimal fraction vs % format)
if not df_live.empty:
    df_live = _normalise_change(df_live)
    # Auto-save today's snapshot to CSV for historical comparison
    save_daily_snapshot(df_live)
else:
    # ── Hard fallback: build stub df from company database ─────────────────
    # This ensures the app ALWAYS renders even when all APIs are unreachable
    # Prices default to 0 — user sees company list but no live data
    _stub = []
    for _sym, _info in _GSE_COMPANIES.items():
        _stub.append({
            "symbol": _sym,
            "name":   _info.get("name", _sym),
            "price":  0.0,
            "change": 0.0,
            "volume": 0,
        })
    if _stub:
        df_live = pd.DataFrame(_stub)

symbols = sorted(df_live["symbol"].dropna().tolist()) if not df_live.empty else []

# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("""
    <style>
    /* ── Global dark theme ── */
    html, body, [data-testid="stApp"] {
        background-color: #0a0e1a !important;
        color: #e2e8f0 !important;
    }
    [data-testid="stSidebar"] {
        background: #0d1117 !important;
        border-right: 1px solid #1e2d3d !important;
    }
    [data-testid="stSidebar"] * { color: #cbd5e1 !important; }
    .main .block-container {
        background: #0a0e1a !important;
        padding-top: 1.5rem !important;
        max-width: 1400px !important;
    }
    /* Force ALL iframes (dataframe) to dark */
    iframe { background: #0d1117 !important; }
    /* stDataFrame wrapper */
    [data-testid="stDataFrame"] > div > div { background: #0d1117 !important; border-radius:12px !important; }
    /* Inputs */
    [data-testid="stTextInput"] input,
    [data-testid="stSelectbox"] div,
    [data-testid="stMultiSelect"] div {
        background: #161b27 !important;
        border-color: #1e2d3d !important;
        color: #e2e8f0 !important;
    }
    /* Radio nav pills */
    [data-testid="stRadio"] label {
        background: transparent !important;
        border-radius: 8px !important;
        padding: 8px 12px !important;
        margin: 2px 0 !important;
        display: block !important;
        cursor: pointer !important;
        transition: background .15s !important;
        font-size: 13px !important;
    }
    [data-testid="stRadio"] label:hover { background: #1a2332 !important; }
    [data-testid="stRadio"] [aria-checked="true"] + div label,
    [data-testid="stRadio"] label:has(input:checked) {
        background: #1a2d4a !important;
        color: #38bdf8 !important;
    }
    /* Buttons */
    [data-testid="stButton"] button {
        background: #161b27 !important;
        border: 1px solid #1e2d3d !important;
        color: #94a3b8 !important;
        border-radius: 8px !important;
        font-size: 12px !important;
    }
    [data-testid="stButton"] button:hover {
        background: #1a2332 !important;
        border-color: #38bdf8 !important;
        color: #38bdf8 !important;
    }
    /* Sliders */
    [data-testid="stSlider"] [role="slider"] { background: #38bdf8 !important; }
    /* Divider */
    hr { border-color: #1e2d3d !important; }
    /* Scrollbar */
    ::-webkit-scrollbar { width: 4px; height: 4px; }
    ::-webkit-scrollbar-track { background: #0d1117; }
    ::-webkit-scrollbar-thumb { background: #1e2d3d; border-radius: 2px; }
    /* Dataframe */
    [data-testid="stDataFrame"] {
        border: 1px solid #1e2d3d !important;
        border-radius: 12px !important;
        overflow: hidden !important;
        background: #0d1117 !important;
    }
    [data-testid="stDataFrame"] iframe { background: #0d1117 !important; }
    [data-testid="stDataFrame"] > div  { background: #0d1117 !important; }
    /* Expander */
    [data-testid="stExpander"] {
        background: #0d1117 !important;
        border: 1px solid #1e2d3d !important;
        border-radius: 10px !important;
    }
    /* Metric */
    [data-testid="stMetric"] { background: #0d1117 !important; }
    /* Plotly charts transparent bg */
    .js-plotly-plot .plotly { background: transparent !important; }
    /* Hide radio wrapper label ("nav" text) */
    div[data-testid="stRadio"] > label { display:none !important; }
    div[data-testid="stRadio"] > div[role="radiogroup"] { gap:2px !important; }
    div[data-testid="stRadio"] label {
        padding: 9px 12px !important; border-radius:8px !important;
        font-size:13px !important; font-weight:500 !important;
        color:#64748b !important; border:1px solid transparent !important;
        display:flex !important; align-items:center !important;
        transition:all .15s !important; margin:1px 0 !important;
    }
    div[data-testid="stRadio"] label:hover {
        background:#111827 !important; color:#94a3b8 !important;
    }
    div[data-testid="stRadio"] label:has(input:checked) {
        background:#0f2744 !important; color:#38bdf8 !important;
        border-color:#1e3a5f !important;
    }
    /* Hide radio dot/circle */
    div[data-testid="stRadio"] label > div:first-child { display:none !important; }
    /* Hide "nav" label text specifically */
    div[data-testid="stRadio"] > label[data-testid="stWidgetLabel"] { display:none !important; }
    </style>
    """, unsafe_allow_html=True)

    # Sidebar header
    st.markdown(f"""
    <div style="padding:4px 2px 16px">
      <div style="width:100%">{_B360_LOGO_SMALL}</div>
      <div style="height:1px;background:linear-gradient(90deg,#6366f122,#38bdf833,transparent);
           margin:10px 0 0"></div>
    </div>
    """, unsafe_allow_html=True)

    if market_is_open():
        st.markdown('<div style="background:#052e16;border:1px solid #166534;border-radius:8px;padding:8px 12px;font-size:12px;color:#4ade80;margin-bottom:8px">● MARKET OPEN · 10:00–15:00 GMT</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="background:#1c1917;border:1px solid #292524;border-radius:8px;padding:8px 12px;font-size:12px;color:#78716c;margin-bottom:8px">○ MARKET CLOSED</div>', unsafe_allow_html=True)

    st.markdown(f'<div style="font-size:10px;color:#475569;margin-bottom:12px;padding-left:2px">Last refreshed: {datetime.now(timezone.utc).strftime("%H:%M:%S GMT")}</div>', unsafe_allow_html=True)

    if st.button("↺  Refresh data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.divider()

    # ── Grouped navigation CSS ───────────────────────────────────────────────
    st.markdown("""
    <style>
    .nav-group-label {
        font-size:9px; font-weight:800; color:#334155;
        text-transform:uppercase; letter-spacing:.14em;
        padding:14px 0 6px 4px; display:block;
        border-top:1px solid #1e2d3d; margin-top:4px;
    }
    .nav-group-label:first-child { border-top:none; padding-top:4px; }
    /* Hide default radio label */
    [data-testid="stRadio"] > label { display:none !important; }
    </style>""", unsafe_allow_html=True)

    # All pages in order — groups defined by labels injected between them
    _all_pages = [
        "Overview", "Stock Detail", "Sector Analysis",
        "Market Review", "Heatmap",
        "Compare Stocks", "Advanced Charts", "AI Signals",
        "Portfolio", "Portfolio Simulator",
    ]

    # Group label injected before these pages
    _group_labels = {
        "Overview":        "Markets",
        "Compare Stocks":  "Analytics",
        "Portfolio":       "Portfolio",
    }

    # Render group labels + radio
    for _pg in _all_pages:
        if _pg in _group_labels:
            st.markdown(
                f'<span class="nav-group-label">{_group_labels[_pg]}</span>',
                unsafe_allow_html=True
            )

    page = st.radio(
        "Navigation",
        _all_pages,
        index=_all_pages.index(st.session_state.page)
              if st.session_state.page in _all_pages else 0,
        label_visibility="hidden",
        format_func=lambda x: {
            "Overview":            "🏠  Market overview",
            "Stock Detail":        "📈  Stock detail",
            "Sector Analysis":     "🏭  Sector analysis",
            "Market Review":       "📰  Daily market review",
            "Heatmap":             "🟩  Market heatmap",
            "Compare Stocks":      "⚖️  Compare stocks",
            "Advanced Charts":     "📊  Advanced charts",
            "AI Signals":          "🤖  AI signal panel",
            "Portfolio":           "💼  Portfolio tracker",
            "Portfolio Simulator": "💰  Portfolio simulator",
        }.get(x, x),
    )
    st.session_state.page = page

    # ── Render group section headers above radio ──────────────────────────────
    # Streamlit radio doesn't support native section headers so we use
    # CSS nth-child to inject visual separators between groups
    st.markdown("""
    <style>
    /* Radio option list items */
    [data-testid="stRadio"] > div > div { gap:0 !important; }

    /* Group dividers — before Compare Stocks (6th item) and Portfolio (9th) */
    [data-testid="stRadio"] > div > div > label:nth-child(6)::before {
        content:"ANALYTICS";
        display:block; font-size:9px; font-weight:800; color:#334155;
        text-transform:uppercase; letter-spacing:.14em;
        padding:12px 0 6px 14px;
        border-top:1px solid #1e2d3d; margin-bottom:0;
    }
    [data-testid="stRadio"] > div > div > label:nth-child(9)::before {
        content:"PORTFOLIO";
        display:block; font-size:9px; font-weight:800; color:#334155;
        text-transform:uppercase; letter-spacing:.14em;
        padding:12px 0 6px 14px;
        border-top:1px solid #1e2d3d; margin-bottom:0;
    }
    /* MARKETS label at very top */
    [data-testid="stRadio"] > div > div > label:nth-child(1)::before {
        content:"MARKETS";
        display:block; font-size:9px; font-weight:800; color:#334155;
        text-transform:uppercase; letter-spacing:.14em;
        padding:4px 0 6px 14px; margin-bottom:0;
    }
    </style>""", unsafe_allow_html=True)

    st.divider()

    st.markdown('<div style="font-size:10px;font-weight:600;color:#475569;letter-spacing:.08em;text-transform:uppercase;margin-bottom:8px">Alert thresholds</div>', unsafe_allow_html=True)
    st.session_state.alert_thresholds["drop"] = st.slider(
        "Drop alert (%)", -20.0, -1.0,
        value=st.session_state.alert_thresholds["drop"], step=0.5,
    )
    st.session_state.alert_thresholds["rise"] = st.slider(
        "Rise alert (%)", 1.0, 20.0,
        value=st.session_state.alert_thresholds["rise"], step=0.5,
    )

    st.divider()

    st.markdown('<div style="font-size:10px;font-weight:600;color:#475569;letter-spacing:.08em;text-transform:uppercase;margin-bottom:8px">Watchlist</div>', unsafe_allow_html=True)
    wl_input = st.text_input("Add symbol", placeholder="e.g. GCB").upper().strip()
    if st.button("+ Add to watchlist", use_container_width=True) and wl_input:
        if wl_input not in st.session_state.watchlist:
            st.session_state.watchlist.append(wl_input)
            st.rerun()
    for sym in list(st.session_state.watchlist):
        c1, c2 = st.columns([4, 1])
        row_live = df_live[df_live["symbol"] == sym] if not df_live.empty else pd.DataFrame()
        chg = f"{row_live['change'].values[0]:+.2f}%" if not row_live.empty else ""
        color = "#4ade80" if (not row_live.empty and row_live['change'].values[0] >= 0) else "#f87171"
        c1.markdown(f'<div style="font-size:12px;color:#e2e8f0">{sym} <span style="color:{color};font-size:11px">{chg}</span></div>', unsafe_allow_html=True)
        if c2.button("✕", key=f"rm_{sym}"):
            st.session_state.watchlist.remove(sym)
            st.rerun()
# ═══════════════════════════════════════════════════════════════════════════════
# SHARED DATA LOAD
# ═══════════════════════════════════════════════════════════════════════════════

df_live = get_live_prices()
# Normalise change column (handles decimal fraction vs % format)
if not df_live.empty:
    df_live = _normalise_change(df_live)
symbols = sorted(df_live["symbol"].dropna().tolist()) if not df_live.empty else []


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════════

if page == "Overview":

    st.markdown("""
    <style>
    /* ── Pro dark card system ── */
    .pro-header {
        display:flex; align-items:center; justify-content:space-between;
        margin-bottom:1.5rem; padding-bottom:1rem;
        border-bottom:1px solid #1e2d3d;
    }
    .pro-header-title { font-size:26px; font-weight:800; color:#f1f5f9; letter-spacing:-.3px; }
    .pro-header-sub   { font-size:13px; color:#475569; margin-top:2px; }
    .pro-header-time  { font-size:12px; color:#334155; font-family:monospace; }

    .kpi-grid { display:grid; grid-template-columns:repeat(5,1fr); gap:10px; margin-bottom:1.5rem; }
    .kpi-card {
        background:#0d1117; border:1px solid #1e2d3d; border-radius:14px;
        padding:18px 22px; position:relative; overflow:hidden;
        transition:border-color .2s, transform .2s;
    }
    .kpi-card:hover { border-color:#334155; transform:translateY(-2px); }
    .kpi-card::before {
        content:""; position:absolute; top:0; left:0; right:0; height:2px;
    }
    .kpi-green::before  { background:linear-gradient(90deg,#22c55e,#16a34a); }
    .kpi-red::before    { background:linear-gradient(90deg,#ef4444,#dc2626); }
    .kpi-blue::before   { background:linear-gradient(90deg,#38bdf8,#0ea5e9); }
    .kpi-purple::before { background:linear-gradient(90deg,#a78bfa,#7c3aed); }
    .kpi-lbl { font-size:10px; font-weight:600; color:#475569; text-transform:uppercase;
               letter-spacing:.08em; margin-bottom:8px; }
    .kpi-val { font-size:30px; font-weight:800; color:#f1f5f9; line-height:1; }
    .kpi-sub { font-size:11px; color:#334155; margin-top:6px; }

    /* ── Invisible overlay button covers entire stock card ── */
    .stock-card + div [data-testid="stButton"] button {
        position:absolute !important;
        top:-88px !important; left:0 !important;
        width:100% !important; height:88px !important;
        background:transparent !important;
        border:none !important; opacity:0 !important;
        cursor:pointer !important; z-index:10 !important;
    }
    .stock-card + div { position:relative !important; margin-top:-4px !important; }

    /* ── Grid card buttons — styled as clean "View" link ── */
    [data-testid="stButton"] button[kind="secondary"] {
        background:#111827 !important; border:1px solid #1e2d3d !important;
        color:#334155 !important; font-size:10px !important;
        padding:3px 0 !important; border-radius:0 0 14px 14px !important;
        margin-top:-14px !important; width:100% !important;
        letter-spacing:.06em !important; text-transform:uppercase !important;
        transition:all .15s !important;
    }
    [data-testid="stButton"] button[kind="secondary"]:hover {
        background:#1a2d4a !important; color:#38bdf8 !important;
        border-color:#38bdf8 !important;
    }

    /* ── Card hover glow effect ── */
    .stock-card:hover {
        border-color:#38bdf8 !important;
        box-shadow:0 0 0 1px #38bdf822 !important;
        transform:translateY(-1px) !important;
        transition:all .18s ease !important;
    }
    .stock-card { transition:all .18s ease !important; }
    .section-label {
        font-size:10px; font-weight:800; color:#38bdf8; text-transform:uppercase;
        letter-spacing:.14em; margin:1.75rem 0 .85rem;
        display:flex; align-items:center; gap:10px;
    }
    .section-label::before {
        content:""; width:3px; height:14px; background:#38bdf8;
        border-radius:2px; display:inline-block;
    }
    .section-label::after {
        content:""; flex:1; height:1px;
        background:linear-gradient(90deg,#1e2d3d,transparent);
    }

    .stock-card {
        background:#0d1117; border:1px solid #1e2d3d; border-radius:14px;
        padding:16px 18px; margin-bottom:6px;
        display:flex; align-items:center; justify-content:space-between;
        transition:all .18s ease; cursor:pointer;
    }
    .stock-card:hover {
        border-color:#38bdf8; background:#060d18;
        box-shadow:0 4px 20px rgba(56,189,248,0.06);
        transform:translateY(-1px);
    }
    .sc-left  { display:flex; align-items:center; gap:14px; }
    .sc-avatar {
        width:42px; height:42px; border-radius:10px;
        display:flex; align-items:center; justify-content:center;
        font-size:13px; font-weight:800; flex-shrink:0; letter-spacing:.5px;
        flex-direction:column; line-height:1;
    }
    .sc-sym  { font-size:15px; font-weight:700; color:#f1f5f9; }
    .sc-name { font-size:11px; color:#475569; margin-top:2px; }
    .sc-right { text-align:right; }
    .sc-price { font-size:15px; font-weight:600; color:#cbd5e1; font-family:monospace; }
    .sc-badge {
        display:inline-block; font-size:11px; font-weight:700;
        padding:3px 10px; border-radius:20px; margin-top:4px;
        font-family: monospace; letter-spacing:.3px;
    }
    .badge-up { background:#052e16; color:#4ade80; border:1px solid #166534; }
    .badge-dn { background:#1c0a0a; color:#f87171; border:1px solid #7f1d1d; }
    .badge-nt { background:#0f172a; color:#64748b; border:1px solid #1e2d3d; }

    .alert-card {
        border-radius:14px; padding:14px 18px; margin-bottom:8px;
        display:flex; align-items:flex-start; gap:14px;
        transition:transform .15s ease;
    }
    .alert-card:hover { transform:translateX(3px); }
    .alert-danger  { background:rgba(28,10,10,0.9); border:1px solid #7f1d1d;
        box-shadow:0 0 20px rgba(239,68,68,0.04); }
    .alert-success { background:rgba(2,28,14,0.9); border:1px solid #14532d;
        box-shadow:0 0 20px rgba(34,197,94,0.04); }
    .alert-dot { width:8px; height:8px; border-radius:50%; margin-top:5px; flex-shrink:0; }
    .dot-danger  { background:#ef4444; box-shadow:0 0 8px #ef4444; animation:pulse 2s infinite; }
    .dot-success { background:#22c55e; box-shadow:0 0 8px #22c55e; animation:pulse 2s infinite; }
    @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.5} }
    .alert-sym  { font-size:13px; font-weight:700; color:#f1f5f9; }
    .alert-msg  { font-size:12px; color:#94a3b8; margin-top:2px; }
    .alert-time { font-size:10px; color:#334155; margin-top:4px; font-family:monospace; }

    .wl-card {
        background:#0d1117; border:1px solid #1e2d3d; border-radius:12px;
        padding:14px 18px; margin-bottom:8px;
        display:flex; align-items:center; justify-content:space-between;
    }
    .wl-bar-bg   { height:3px; background:#1e2d3d; border-radius:2px; width:80px; margin-top:6px; }
    .wl-bar-fill { height:3px; border-radius:2px; }

    .eq-table-wrap { background:#0d1117; border:1px solid #1e2d3d;
        border-radius:12px; overflow:hidden; margin-top:.5rem; }
    [data-testid="stDataFrame"] table { background:#0d1117 !important; }
    [data-testid="stDataFrame"] th {
        background:#111827 !important; color:#475569 !important;
        font-size:11px !important; text-transform:uppercase !important;
        letter-spacing:.06em !important; border-bottom:1px solid #1e2d3d !important;
    }
    [data-testid="stDataFrame"] td { color:#cbd5e1 !important; font-size:13px !important; }
    [data-testid="stTextInput"] input {
        background:#0d1117 !important; border:1px solid #1e2d3d !important;
        color:#e2e8f0 !important; border-radius:8px !important;
    }

    /* ── Force dataframe dark ── */
    [data-testid="stDataFrame"] iframe,
    [data-testid="stDataFrame"] > div,
    [data-testid="stDataFrame"] table,
    .stDataFrame { background:#0d1117 !important; }

    /* glowing row hover */
    [data-testid="stDataFrame"] tr:hover td {
        background:#111827 !important;
    }

    /* ── Hide label above hidden radio ── */
    [data-testid="stRadio"] > label { display:none !important; }

    /* ── Plotly chart bg ── */
    .js-plotly-plot, .plot-container, .svg-container {
        background:transparent !important;
    }

    /* ── Info / warning banners ── */
    [data-testid="stAlert"] {
        background:#0d1117 !important;
        border:1px solid #1e2d3d !important;
        border-radius:10px !important;
        color:#64748b !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Show data status banner only when prices are zero
    _all_zero = (df_live["price"].sum() == 0) if not df_live.empty else True
    if _all_zero and df_live.empty:
        st.markdown("""
        <div style="background:#1c1400;border:1px solid #92400e;border-radius:10px;
             padding:12px 18px;margin-bottom:1rem;display:flex;align-items:center;gap:12px">
          <span style="font-size:18px">📡</span>
          <div>
            <div style="font-size:13px;font-weight:600;color:#fbbf24">
              Live data temporarily unavailable</div>
            <div style="font-size:11px;color:#92400e;margin-top:2px">
              The GSE API is unreachable from the cloud server right now.
              Company list is shown from the database. Prices will load when the API recovers.
              Click <b>Refresh data</b> to retry.</div>
          </div>
        </div>""", unsafe_allow_html=True)

    # ── ALL computation before render ────────────────────────────────────────────
    # Market summary (needed for sentiment)
    _ov_sum      = market_summary(df_live)
    _ov_gainers  = _ov_sum.get("gainers",   0)
    _ov_losers   = _ov_sum.get("losers",    0)
    _ov_unchanged= _ov_sum.get("unchanged", 0)
    _ov_mkt      = market_analytics_summary(df_live)
    _ov_breadth  = _ov_mkt.get("breadth_pct", 0)
    _ov_avg_chg  = _ov_mkt.get("avg_change",  0)

    # Index computation — use only stocks with actual price movement
    _fin_syms    = [s for s in df_live["symbol"] if SECTOR_MAP.get(s) == "Financials"]
    _fin_df      = df_live[df_live["symbol"].isin(_fin_syms)]
    _active      = df_live[df_live["change"] != 0]
    _fin_active  = _fin_df[_fin_df["change"] != 0]
    _gse_ci_chg  = float(_active["change"].mean())     if not _active.empty     else 0
    _gse_fsi_chg = float(_fin_active["change"].mean()) if not _fin_active.empty else 0
    _ci_col  = "#4ade80" if _gse_ci_chg  >= 0 else "#f87171"
    _fsi_col = "#4ade80" if _gse_fsi_chg >= 0 else "#f87171"
    _ci_arr  = "▲" if _gse_ci_chg  >= 0 else "▼"
    _fsi_arr = "▲" if _gse_fsi_chg >= 0 else "▼"

    # Sector bars
    _df_sec = df_live.copy()
    _df_sec["sector"] = _df_sec["symbol"].map(SECTOR_MAP).fillna("Other")
    _sector_perf = (
        _df_sec.groupby("sector")["change"]
        .mean().reset_index()
        .rename(columns={"change":"avg_chg"})
        .sort_values("avg_chg", ascending=False)
    )

    # Sentiment engine — must be before render
    _sent_label, _sent_conf, _sent_score, _sent_col = _compute_sentiment(
        df_live, _ov_gainers, _ov_losers, _ov_unchanged, _ov_avg_chg, _ov_breadth
    )

    # ── Market Indices + Sentiment (very top of page) ───────────────────────────
    # ── Render the index + sentiment + sector bars ────────────────────────────
    ix_col, sent_col, sec_col = st.columns([2, 1.2, 2])

    with ix_col:
        st.markdown(f"""
        <div style="background:#0d1117;border:1px solid #1e2d3d;border-radius:12px;
             padding:14px 18px;height:100%">
          <div style="font-size:9px;font-weight:800;color:#334155;text-transform:uppercase;
               letter-spacing:.12em;margin-bottom:10px">Market indices</div>
          <div style="display:flex;justify-content:space-between;align-items:center;
               margin-bottom:8px;padding-bottom:8px;border-bottom:1px solid #1e2d3d">
            <div>
              <div style="font-size:11px;font-weight:700;color:#94a3b8">GSE Composite Index</div>
              <div style="font-size:9px;color:#334155">GSE-CI · All equities</div>
            </div>
            <div style="text-align:right">
              <div style="font-size:15px;font-weight:800;color:{_ci_col};font-family:monospace">
                {_ci_arr} {"+" if _gse_ci_chg>=0 else ""}{_gse_ci_chg:.2f}%</div>
              <div style="font-size:9px;color:#334155">avg daily return</div>
            </div>
          </div>
          <div style="display:flex;justify-content:space-between;align-items:center">
            <div>
              <div style="font-size:11px;font-weight:700;color:#94a3b8">GSE Financial Index</div>
              <div style="font-size:9px;color:#334155">GSE-FSI · Financials</div>
            </div>
            <div style="text-align:right">
              <div style="font-size:15px;font-weight:800;color:{_fsi_col};font-family:monospace">
                {_fsi_arr} {"+" if _gse_fsi_chg>=0 else ""}{_gse_fsi_chg:.2f}%</div>
              <div style="font-size:9px;color:#334155">avg daily return</div>
            </div>
          </div>
        </div>""", unsafe_allow_html=True)

    with sent_col:
        st.markdown(f"""
        <div style="background:#0d1117;border:1px solid #1e2d3d;border-radius:12px;
             padding:14px 18px;height:100%;text-align:center">
          <div style="font-size:9px;font-weight:800;color:#334155;text-transform:uppercase;
               letter-spacing:.12em;margin-bottom:8px">Market sentiment</div>
          <div style="font-size:18px;font-weight:900;color:{_sent_col};line-height:1;
               margin-bottom:6px">{_sent_label}</div>
          <div style="font-size:11px;color:#475569;margin-bottom:8px">
            Confidence: <b style="color:{_sent_col}">{_sent_conf}%</b></div>
          <div style="background:#1e2d3d;border-radius:99px;height:6px;overflow:hidden">
            <div style="width:{_sent_conf}%;height:6px;background:{_sent_col};
                 border-radius:99px;transition:width .5s"></div>
          </div>
          <div style="font-size:9px;color:#334155;margin-top:8px;line-height:1.4">
            Based on breadth · movers · avg move · volume bias</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom:.5rem'></div>", unsafe_allow_html=True)

    # ── Live ticker tape ───────────────────────────────────────────────────────
    ticker_items = []
    for _, r in df_live.iterrows():
        sym = str(r["symbol"])
        chg = float(r["change"])
        prc = float(r["price"])
        clr = "#4ade80" if chg > 0 else "#f87171" if chg < 0 else "#64748b"
        arrow = "▲" if chg > 0 else "▼" if chg < 0 else "●"
        ticker_items.append(
            f'<span style="margin:0 24px;white-space:nowrap">'
            f'<span style="color:#94a3b8;font-weight:700">{sym}</span> '
            f'<span style="color:#e2e8f0;font-family:monospace">GH₵ {prc:.2f}</span> '
            f'<span style="color:{clr};font-size:11px">{arrow} {chg:+.2f}%</span></span>'
        )
    ticker_html = "".join(ticker_items * 3)  # 3 copies for seamless CSS loop

    # Build tape HTML using string concat — avoids f-string re-evaluation of {}
    _tape_html = (
        "<style>@keyframes tickerscroll{"
        "0%{transform:translateX(0)}"
        "100%{transform:translateX(-33.33%)}}"
        ".ticker-inner{display:inline-flex;animation:tickerscroll 55s linear infinite;"
        "white-space:nowrap}</style>"
        "<div style='background:#0b0f1c;border-top:1px solid #1e2d3d;"
        "border-bottom:1px solid #1e2d3d;padding:0;margin-bottom:1.25rem;"
        "overflow:hidden;position:relative'>"
        "<div style='display:flex;align-items:center'>"
        "<div style='background:linear-gradient(135deg,#0ea5e9,#6366f1);"
        "padding:6px 14px;font-size:10px;font-weight:900;color:#fff;"
        "letter-spacing:.1em;white-space:nowrap;flex-shrink:0'>LIVE</div>"
        "<div style='flex:1;overflow:hidden;padding:7px 0'>"
        "<div class='ticker-inner'>" + ticker_html + "</div>"
        "</div></div></div>"
    )
    st.markdown(_tape_html, unsafe_allow_html=True)

    summary         = market_summary(df_live)
    gainers_count   = summary.get("gainers",   0)
    losers_count    = summary.get("losers",    0)
    unchanged_count = summary.get("unchanged", 0)
    vol_label       = summary.get("vol_label", "—")
    now_str         = datetime.now(timezone.utc).strftime("%d %b %Y · %H:%M GMT")
    mkt_analytics   = market_analytics_summary(df_live)
    breadth_pct     = mkt_analytics.get("breadth_pct", 0)
    avg_chg         = mkt_analytics.get("avg_change", 0)

    # ── Market Sentiment Engine ───────────────────────────────────────────────
    def _compute_sentiment(df, gainers, losers, unchanged, avg_change, breadth):
        """
        Proprietary sentiment score based on:
        breadth (40%) + avg_move (30%) + volume_bias (20%) + mover_ratio (10%)
        Returns: (label, confidence, score, color)
        """
        score = 0.0
        # Breadth (% advancing)
        score += (breadth - 50) * 0.8          # +/-40 pts max
        # Average market move
        score += avg_change * 6                 # +/-30 pts at ±5%
        # Mover ratio
        total_movers = gainers + losers
        if total_movers > 0:
            ratio = (gainers - losers) / total_movers
            score += ratio * 10                 # +/-10 pts
        # Volume-weighted bias
        try:
            vol_up   = df[df["change"] > 0]["volume"].sum()
            vol_down = df[df["change"] < 0]["volume"].sum()
            vol_tot  = vol_up + vol_down
            if vol_tot > 0:
                score += ((vol_up - vol_down) / vol_tot) * 20  # +/-20 pts
        except Exception:
            pass

        # Map score to label + confidence
        if   score >= 25:  label, col = "Strongly Bullish", "#4ade80"
        elif score >= 10:  label, col = "Bullish",          "#86efac"
        elif score >= -10: label, col = "Neutral",          "#94a3b8"
        elif score >= -25: label, col = "Bearish",          "#fca5a5"
        else:              label, col = "Strongly Bearish", "#f87171"

        confidence = min(int(abs(score) / 50 * 100 + 45), 95)
        return label, confidence, score, col

    # (all computation done above render block — _sent_label, _ci_col etc. already set)


    # ── Header ─────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="pro-header" style="align-items:center">
      <div style="width:320px;max-width:55%">{_B360_LOGO_FULL}</div>
      <div style="text-align:right">
        <div class="pro-header-time">{now_str}</div>
        <div style="font-size:11px;color:#334155;margin-top:4px">
          {"<span style='color:#22c55e;font-weight:700'>● MARKET OPEN</span>" if market_is_open() else "<span style='color:#475569'>○ Market closed</span>"}
          &nbsp;·&nbsp; BismarkDataLab Inc</div>
      </div>
    </div>""", unsafe_allow_html=True)

    # ── Global search bar (ISEDAN-style) ──────────────────────────────────────
    search_query = st.text_input("",
        placeholder="🔍  Search symbol or company name…",
        label_visibility="collapsed", key="global_search_top")
    search_query = search_query or st.session_state.get("global_search_top","")
    if search_query and len(search_query) >= 2:
        q = search_query.upper()
        results = df_live[
            df_live["symbol"].str.upper().str.contains(q, na=False) |
            df_live["name"].str.upper().str.contains(q, na=False)
        ].head(8)
        if not results.empty:
            st.markdown('<div style="background:#0d1117;border:1px solid #1e2d3d;border-radius:12px;overflow:hidden;margin-bottom:12px">', unsafe_allow_html=True)
            for _, r in results.iterrows():
                sym   = str(r["symbol"])
                cname = _GSE_NAMES.get(sym, str(r["name"]))
                chg   = float(r["change"])
                chg_c = "#4ade80" if chg > 0 else "#f87171" if chg < 0 else "#475569"
                logo  = _load_logo_b64(sym)
                av    = f'<img src="{logo}" style="width:32px;height:32px;object-fit:contain;border-radius:8px;background:#111827;padding:2px">' if logo else f'<div style="width:32px;height:32px;border-radius:8px;background:#0c2a4a;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:900;color:#38bdf8">{sym[:2]}</div>'
                st.markdown(f'''<div style="display:flex;align-items:center;gap:12px;padding:10px 16px;
                    border-bottom:1px solid #111827;cursor:pointer">
                    {av}
                    <div style="flex:1"><div style="font-size:13px;font-weight:700;color:#f1f5f9">{sym}</div>
                    <div style="font-size:11px;color:#475569">{cname}</div></div>
                    <div style="text-align:right"><div style="font-size:13px;font-weight:600;color:#e2e8f0;font-family:monospace">GH₵ {r["price"]:.2f}</div>
                    <div style="font-size:11px;color:{chg_c}">{"+" if chg>=0 else ""}{chg:.2f}%</div></div>
                </div>''', unsafe_allow_html=True)
                if st.button(f"Open {sym}", key=f"srch_{sym}", use_container_width=True):
                    st.session_state["selected_symbol"] = sym
                    st.session_state.page = "Stock Detail"
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    # ── KPI cards (with market analytics) ────────────────────────────────────
    mkt_analytics = market_analytics_summary(df_live)
    breadth_pct   = mkt_analytics.get("breadth_pct", 0)
    avg_chg       = mkt_analytics.get("avg_change", 0)
    top_mover     = mkt_analytics.get("top_mover", "—")
    avg_col       = "#4ade80" if avg_chg >= 0 else "#f87171"
    breadth_col   = "#4ade80" if breadth_pct >= 50 else "#f87171"
    breadth_lbl   = "Bullish" if breadth_pct >= 60 else "Bearish" if breadth_pct <= 40 else "Neutral"

    st.markdown(f"""
    <div class="kpi-grid">
      <div class="kpi-card kpi-green">
        <div class="kpi-lbl">Gainers</div>
        <div class="kpi-val" style="color:#4ade80">{gainers_count}</div>
        <div class="kpi-sub">stocks advancing</div>
      </div>
      <div class="kpi-card kpi-red">
        <div class="kpi-lbl">Losers</div>
        <div class="kpi-val" style="color:#f87171">{losers_count}</div>
        <div class="kpi-sub">stocks declining</div>
      </div>
      <div class="kpi-card kpi-blue">
        <div class="kpi-lbl">Unchanged</div>
        <div class="kpi-val" style="color:#38bdf8">{unchanged_count}</div>
        <div class="kpi-sub">no movement today</div>
      </div>
      <div class="kpi-card kpi-purple">
        <div class="kpi-lbl">Total volume</div>
        <div class="kpi-val" style="color:#a78bfa">{vol_label}</div>
        <div class="kpi-sub">shares traded today</div>
      </div>
      <div class="kpi-card" style="border-top-color:#fbbf24 !important">
        <div class="kpi-lbl" style="color:#92400e">Avg move</div>
        <div class="kpi-val" style="color:{avg_col};font-size:22px">{"+" if avg_chg>=0 else ""}{avg_chg:.2f}%</div>
        <div class="kpi-sub">avg across all equities</div>
      </div>
    </div>""", unsafe_allow_html=True)

    # ── Avatar colour helper ───────────────────────────────────────────────────
    # (avatar/logo helpers moved to module level above)


    def _sparkline(sym: str, width=100, height=36) -> str:
        """Generate a clean SVG sparkline with area fill — used in stock cards."""
        try:
            hist = load_historical_comparison(sym)
            if len(hist) < 2:
                return ""
            prices = hist["price"].tail(20).tolist()
            if len(prices) < 2:
                return ""
            mn, mx = min(prices), max(prices)
            rng = mx - mn
            if rng == 0:
                # Flat line
                mid_y = height / 2
                return (f'<svg width="{width}" height="{height}" style="display:block;overflow:visible">' +
                        f'<line x1="0" y1="{mid_y}" x2="{width}" y2="{mid_y}" ' +
                        f'stroke="#475569" stroke-width="1.5" stroke-dasharray="4,3"/></svg>')
            pad = 2
            xs = [pad + i * ((width - 2*pad) / (len(prices)-1)) for i in range(len(prices))]
            ys = [pad + (height - 2*pad) - ((p - mn) / rng) * (height - 2*pad) for p in prices]
            pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in zip(xs, ys))
            color = "#4ade80" if prices[-1] >= prices[0] else "#f87171"
            fill_col = "rgba(34,197,94,0.12)" if color == "#4ade80" else "rgba(239,68,68,0.12)"
            fill_pts = (f"{xs[0]:.1f},{height} " + pts +
                        f" {xs[-1]:.1f},{height}")
            # Endpoint dot
            ex, ey = xs[-1], ys[-1]
            return (f'<svg width="{width}" height="{height}" style="display:block;overflow:visible">' +
                    f'<polygon points="{fill_pts}" fill="{fill_col}"/>' +
                    f'<polyline points="{pts}" fill="none" stroke="{color}" ' +
                    f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>' +
                    f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="3" fill="{color}"/>' +
                    f'</svg>')
        except Exception:
            return ""

    def _sparkline_dummy(sym: str, width=100, height=36) -> str:
        """Placeholder sparkline using today's change direction."""
        try:
            row = df_live[df_live["symbol"] == sym]
            if row.empty: return ""
            chg = float(row["change"].values[0])
            color = "#4ade80" if chg >= 0 else "#f87171"
            fill  = "rgba(34,197,94,0.1)" if chg >= 0 else "rgba(239,68,68,0.1)"
            # Draw a simple directional line
            if chg >= 0:
                pts = f"0,{height-4} 20,{height*0.7:.0f} 50,{height*0.5:.0f} 80,{height*0.3:.0f} {width},{height*0.15:.0f}"
            else:
                pts = f"0,{height*0.15:.0f} 20,{height*0.3:.0f} 50,{height*0.5:.0f} 80,{height*0.7:.0f} {width},{height-4}"
            fill_pts = f"0,{height} " + pts + f" {width},{height}"
            return (f'<svg width="{width}" height="{height}" style="display:block;overflow:visible">' +
                    f'<polygon points="{fill_pts}" fill="{fill}"/>' +
                    f'<polyline points="{pts}" fill="none" stroke="{color}" ' +
                    f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>' +
                    f'</svg>')
        except Exception:
            return ""

    def _get_sparkline(sym):
        """Use CSV history if available, else directional dummy."""
        sp = _sparkline(sym)
        return sp if sp else _sparkline_dummy(sym)

    def _LEGACY_sparkline(sym: str, width=80, height=28) -> str:
        """[kept for compat] Generate a tiny inline SVG sparkline from CSV history."""
        try:
            hist = load_historical_comparison(sym)
            if len(hist) < 2:
                return ""
            prices = hist["price"].tail(14).tolist()
            mn, mx = min(prices), max(prices)
            if mx == mn:
                return ""
            xs = [i * (width / (len(prices)-1)) for i in range(len(prices))]
            ys = [height - ((p - mn) / (mx - mn)) * height for p in prices]
            pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in zip(xs, ys))
            color = "#4ade80" if prices[-1] >= prices[0] else "#f87171"
            # Fill area under line
            fill_pts = f"0,{height} " + pts + f" {width},{height}"
            return f'''<svg width="{width}" height="{height}" style="display:block">
              <defs>
                <linearGradient id="sg_{sym}" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stop-color="{color}" stop-opacity="0.3"/>
                  <stop offset="100%" stop-color="{color}" stop-opacity="0"/>
                </linearGradient>
              </defs>
              <polygon points="{fill_pts}" fill="url(#sg_{sym})"/>
              <polyline points="{pts}" fill="none" stroke="{color}" stroke-width="1.5"
                stroke-linecap="round" stroke-linejoin="round"/>
            </svg>'''
        except Exception:
            return ""

    # ── Gainers & Losers ───────────────────────────────────────────────────────
    gainers_df = df_live[df_live["change"] > 0].nlargest(5, "change")
    losers_df  = df_live[df_live["change"] < 0].nsmallest(5, "change")

    # ── Watchlist horizontal scroll strip (like ISEDAN) ─────────────────────
    if st.session_state.watchlist:
        wl_chips = ""
        for wsym in st.session_state.watchlist:
            wr = df_live[df_live["symbol"]==wsym]
            wchg = float(wr["change"].values[0]) if not wr.empty else 0
            wpr  = float(wr["price"].values[0])  if not wr.empty else 0
            wlog = _load_logo_b64(wsym)
            wbg  = "rgba(34,197,94,0.1)"  if wchg>0 else "rgba(239,68,68,0.1)"  if wchg<0 else "rgba(30,45,61,0.5)"
            wbdr = "#4ade8033" if wchg>0 else "#f8717133" if wchg<0 else "#1e2d3d"
            wimghtml = f'<img src="{wlog}" style="width:32px;height:32px;object-fit:contain;border-radius:8px;background:#0d1117;padding:2px">' if wlog else f'<div style="width:32px;height:32px;border-radius:8px;background:#0c2a4a;display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:900;color:#38bdf8">{wsym[:2]}</div>'
            wc = "#4ade80" if wchg>0 else "#f87171" if wchg<0 else "#475569"
            _wname = _GSE_NAMES.get(wsym, wsym)
            _wname_short = (_wname[:16] + "…") if len(_wname) > 16 else _wname
            wl_chips += f'''<div style="flex-shrink:0;background:{wbg};border:1px solid {wbdr};
            border-radius:14px;padding:10px 14px;min-width:120px;cursor:pointer"
            onclick="">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:5px">{wimghtml}
            <div><div style="font-size:12px;font-weight:700;color:#f1f5f9">{wsym}</div>
            <div style="font-size:9px;color:#475569;margin-top:1px">{_wname_short}</div></div></div>
            <div style="font-size:13px;font-weight:700;color:{wc}">{"+" if wchg>=0 else ""}{wchg:.2f}%</div>
            <div style="font-size:10px;color:#475569;margin-top:1px">GH₵ {wpr:.2f}</div>
            </div>'''
        st.markdown(
            "<div style='display:flex;gap:10px;overflow-x:auto;padding:4px 0 12px;"
            "scrollbar-width:none;-ms-overflow-style:none'>" + wl_chips + "</div>",
            unsafe_allow_html=True)

    # ── TOP GAINERS grid (3-col like ISEDAN image 5) ───────────────────────────
    # ── Market breadth visual anchor ─────────────────────────────────────────
    _total = gainers_count + losers_count + unchanged_count
    if _total > 0:
        _g_pct = gainers_count / _total * 100
        _l_pct = losers_count  / _total * 100
        _u_pct = unchanged_count / _total * 100
        st.markdown(f"""
        <div style="background:#0d1117;border:1px solid #1e2d3d;border-radius:12px;
             padding:14px 18px;margin-bottom:1rem">
          <div style="display:flex;align-items:center;justify-content:space-between;
               margin-bottom:10px">
            <div style="font-size:10px;font-weight:800;color:#475569;text-transform:uppercase;
                 letter-spacing:.1em">Market breadth</div>
            <div style="font-size:11px;color:#475569">
              <span style="color:#4ade80;font-weight:700">{gainers_count} advancing</span>
              &nbsp;·&nbsp;
              <span style="color:#f87171;font-weight:700">{losers_count} declining</span>
              &nbsp;·&nbsp;
              <span style="color:#475569">{unchanged_count} flat</span>
            </div>
          </div>
          <div style="display:flex;border-radius:99px;overflow:hidden;height:10px;gap:2px">
            <div style="width:{_g_pct:.1f}%;background:#22c55e;border-radius:99px 0 0 99px;
                 transition:width .5s"></div>
            <div style="width:{_u_pct:.1f}%;background:#1e2d3d"></div>
            <div style="width:{_l_pct:.1f}%;background:#ef4444;border-radius:0 99px 99px 0;
                 transition:width .5s"></div>
          </div>
          <div style="display:flex;justify-content:space-between;margin-top:6px">
            <div style="font-size:10px;color:#4ade80">{_g_pct:.0f}% advancing</div>
            <div style="font-size:10px;color:#475569">{_u_pct:.0f}% flat</div>
            <div style="font-size:10px;color:#f87171">{_l_pct:.0f}% declining</div>
          </div>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-label">Top gainers (1D)</div>', unsafe_allow_html=True)

    if gainers_df.empty:
        st.markdown('<div style="color:#334155;font-size:13px;padding:12px">No gainers today</div>', unsafe_allow_html=True)
    else:
        gcols = st.columns(3)
        for gi, (_, row) in enumerate(gainers_df.head(9).iterrows()):
            sym   = str(row["symbol"])
            _rn  = str(row.get("name",""))
            name = _GSE_NAMES.get(sym) or (_rn if _rn not in ["nan","",sym] else sym)
            price = float(row["price"])
            chg   = float(row["change"])
            prev  = price / (1 + chg/100) if chg != -100 else price
            abs_chg = price - prev
            logo  = _load_logo_b64(sym)
            av_html = f'<img src="{logo}" style="width:44px;height:44px;object-fit:contain;border-radius:50%;background:#111827;padding:3px;border:2px solid #1e2d3d">' if logo else f'<div style="width:44px;height:44px;border-radius:50%;background:#0c2a4a;display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:900;color:#38bdf8;border:2px solid #1e3a5f">{sym[:2]}</div>'
            # Get analytics for this stock
            _a = compute_stock_analytics(sym)
            _ytd_str  = f"+{_a['ytd_return']:.1f}%" if _a['ytd_return'] and _a['ytd_return']>=0 else (f"{_a['ytd_return']:.1f}%" if _a['ytd_return'] else "—")
            _vol_str  = f"{_a['volatility']:.1f}%"   if _a['volatility'] else "—"
            _sig      = _a["signal"]
            _sig_col  = {"STRONG BUY":"#4ade80","BUY":"#86efac","HOLD":"#94a3b8",
                         "SELL":"#fca5a5","STRONG SELL":"#f87171"}.get(_sig, "#94a3b8")
            _sig_bg   = {"STRONG BUY":"rgba(34,197,94,0.15)","BUY":"rgba(34,197,94,0.1)",
                         "HOLD":"rgba(71,85,105,0.15)","SELL":"rgba(239,68,68,0.1)",
                         "STRONG SELL":"rgba(239,68,68,0.15)"}.get(_sig, "rgba(71,85,105,0.1)")

            with gcols[gi % 3]:
                st.markdown(f"""
                <div style="background:#0d1117;border:1px solid #1e2d3d;border-radius:16px;
                     padding:16px;margin-bottom:10px;position:relative;overflow:hidden;
                     transition:all .2s;cursor:pointer">
                  <div style="position:absolute;top:10px;right:10px">
                    <span style="background:rgba(34,197,94,0.15);color:#4ade80;font-size:11px;
                      font-weight:800;padding:4px 9px;border-radius:99px">▲ +{chg:.2f}%</span>
                  </div>
                  <div style="margin-bottom:10px">{av_html}</div>
                  <div style="font-size:15px;font-weight:800;color:#f1f5f9">{sym}</div>
                  <div style="font-size:11px;color:#475569;margin-bottom:8px;
                       white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{name[:22]}</div>
                  <div style="font-size:18px;font-weight:800;color:#e2e8f0;font-family:monospace">
                    GH₵ {price:.2f}</div>
                  <div style="font-size:12px;color:#4ade80;margin-top:2px;font-family:monospace">
                    +{abs_chg:.2f}</div>
                  <div style="display:flex;gap:6px;margin-top:8px;flex-wrap:wrap">
                    <span style="background:{_sig_bg};color:{_sig_col};font-size:10px;
                        font-weight:800;padding:2px 8px;border-radius:99px">{_sig}</span>
                    {"<span style='background:rgba(71,85,105,0.2);color:#64748b;font-size:10px;padding:2px 8px;border-radius:99px'>YTD " + _ytd_str + "</span>" if _ytd_str != "—" else ""}
                    {"<span style='background:rgba(71,85,105,0.2);color:#64748b;font-size:10px;padding:2px 8px;border-radius:99px'>Vol " + _vol_str + "</span>" if _vol_str != "—" else ""}
                  </div>
                </div>""", unsafe_allow_html=True)
                if st.button(f"View {sym} →", key=f"btn_g_{sym}",
                             use_container_width=True, help=f"Open {name}"):
                    st.session_state["selected_symbol"] = sym
                    st.session_state.page = "Stock Detail"
                    st.rerun()

    # ── TOP LOSERS grid ────────────────────────────────────────────────────────
    st.markdown('<div class="section-label">Top losers (1D)</div>', unsafe_allow_html=True)

    if losers_df.empty:
        st.markdown('<div style="color:#334155;font-size:13px;padding:12px">No losers today</div>', unsafe_allow_html=True)
    else:
        lcols = st.columns(3)
        for li, (_, row) in enumerate(losers_df.head(9).iterrows()):
            sym   = str(row["symbol"])
            _rn  = str(row.get("name",""))
            name = _GSE_NAMES.get(sym) or (_rn if _rn not in ["nan","",sym] else sym)
            price = float(row["price"])
            chg   = float(row["change"])
            prev  = price / (1 + chg/100) if chg != -100 else price
            abs_chg = price - prev
            logo  = _load_logo_b64(sym)
            av_html = f'<img src="{logo}" style="width:44px;height:44px;object-fit:contain;border-radius:50%;background:#111827;padding:3px;border:2px solid #1e2d3d">' if logo else f'<div style="width:44px;height:44px;border-radius:50%;background:#1c0a0a;display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:900;color:#f87171;border:2px solid #7f1d1d">{sym[:2]}</div>'
            with lcols[li % 3]:
                st.markdown(f"""
                <div style="background:#0d1117;border:1px solid #1e2d3d;border-radius:16px;
                     padding:16px;margin-bottom:10px;position:relative;overflow:hidden;cursor:pointer">
                  <div style="position:absolute;top:10px;right:10px">
                    <span style="background:rgba(239,68,68,0.15);color:#f87171;font-size:11px;
                      font-weight:800;padding:4px 9px;border-radius:99px">▼ {chg:.2f}%</span>
                  </div>
                  <div style="margin-bottom:10px">{av_html}</div>
                  <div style="font-size:15px;font-weight:800;color:#f1f5f9">{sym}</div>
                  <div style="font-size:11px;color:#475569;margin-bottom:8px;
                       white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{name[:22]}</div>
                  <div style="font-size:18px;font-weight:800;color:#e2e8f0;font-family:monospace">
                    GH₵ {price:.2f}</div>
                  <div style="font-size:12px;color:#f87171;margin-top:2px;font-family:monospace">
                    {abs_chg:.2f}</div>
                </div>""", unsafe_allow_html=True)
                if st.button(f"View {sym} →", key=f"btn_l_{sym}",
                             use_container_width=True, help=f"Open {name}"):
                    st.session_state["selected_symbol"] = sym
                    st.session_state.page = "Stock Detail"
                    st.rerun()

    # ── Alerts ─────────────────────────────────────────────────────────────────
    st.markdown('<div class="section-label">Critical alerts</div>', unsafe_allow_html=True)
    alerts = generate_alerts(df_live, st.session_state.alert_thresholds)
    if alerts:
        for a in alerts:
            cls  = "alert-danger"  if a["type"] == "danger"  else "alert-success"
            dcls = "dot-danger"    if a["type"] == "danger"  else "dot-success"
            sym  = str(a["symbol"])
            name = _GSE_NAMES.get(sym, sym)
            detail = a["msg"].split("—",1)[-1].strip()
            thresh = st.session_state.alert_thresholds
            st.markdown(f"""
            <div class="alert-card {cls}">
              <div class="alert-dot {dcls}"></div>
              <div>
                <div class="alert-sym">{sym} <span style="font-weight:400;color:#64748b">· {name}</span></div>
                <div class="alert-msg">{detail}</div>
                <div class="alert-time">THRESHOLD · DROP {thresh["drop"]}% / RISE +{thresh["rise"]}%</div>
              </div>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown('<div style="color:#334155;font-size:13px;padding:12px 0">No alerts triggered based on current thresholds.</div>', unsafe_allow_html=True)

    # ── Watchlist ──────────────────────────────────────────────────────────────
    st.markdown('<div class="section-label">Watchlist audit</div>', unsafe_allow_html=True)
    wl_set = set(s.upper().strip() for s in st.session_state.watchlist)
    wl_df  = df_live[
        df_live["symbol"].str.upper().str.strip().isin(wl_set) |
        df_live["name"].str.upper().str.strip().isin(wl_set)
    ]
    if not wl_df.empty:
        for _, row in wl_df.iterrows():
            sym   = str(row["symbol"])
            _rn  = str(row.get("name",""))
            name = _GSE_NAMES.get(sym) or (_rn if _rn not in ["nan","",sym] else sym)
            chg   = float(row["change"])
            pct   = min(max((chg + 10) / 20, 0), 1)
            bar_c = "#22c55e" if chg >= 0 else "#ef4444"
            bcls  = "badge-up" if chg >= 0 else "badge-dn"
            sign  = "▲ +" if chg >= 0 else "▼ "
            st.markdown(f"""
            <div class="wl-card">
              <div class="sc-left">{_av(sym)}
                <div>
                  <div class="sc-sym">{sym}</div>
                  <div class="sc-name">{name}</div>
                  <div class="wl-bar-bg">
                    <div class="wl-bar-fill" style="width:{int(pct*100)}%;background:{bar_c}"></div>
                  </div>
                </div>
              </div>
              <div class="sc-right">
                <div class="sc-price">GH₵ {row['price']:.2f}</div>
                <span class="sc-badge {bcls}">{sign}{abs(chg):.2f}%</span>
              </div>
            </div>""", unsafe_allow_html=True)
            if st.button("", key=f"btn_wl_{sym}", help=f"View {name} detail"):
                st.session_state["selected_symbol"] = sym
                st.session_state.page = "Stock Detail"
                st.rerun()
    else:
        st.markdown('<div style="color:#334155;font-size:13px;padding:12px 0">No watchlist symbols in today&#39;s data. Add via the sidebar.</div>', unsafe_allow_html=True)

    # ── Sector performance bars (after watchlist) ────────────────────────────
    with sec_col:
        _bars_html = ""
        _sector_sorted = _sector_perf.sort_values("avg_chg", ascending=True)
        _max_abs = max(_sector_sorted["avg_chg"].abs().max(), 0.01)
        for _, _sr in _sector_sorted.iterrows():
            _sv   = float(_sr["avg_chg"])
            # Skip truly zero sectors — show grey flat line instead
            if abs(_sv) < 0.001:
                _sc   = "#475569"
                _sbg  = "rgba(71,85,105,0.1)"
                _sw   = 2  # thin grey stub
                _sarr = "●"
                _val_str = "  0.00%"
            elif _sv > 0:
                _sc   = "#4ade80"
                _sbg  = "rgba(34,197,94,0.12)"
                _sw   = max(int(abs(_sv) / _max_abs * 100), 4)
                _sarr = "▲"
                _val_str = f"+{_sv:.2f}%"
            else:
                _sc   = "#f87171"
                _sbg  = "rgba(239,68,68,0.12)"
                _sw   = max(int(abs(_sv) / _max_abs * 100), 4)
                _sarr = "▼"
                _val_str = f"{_sv:.2f}%"

            # Full sector name — abbreviate only if > 14 chars
            _sname = _sr["sector"]
            _sname_display = _sname if len(_sname) <= 14 else _sname[:12] + "…"

            _bars_html += (
                f"<div style='display:flex;align-items:center;gap:8px;margin-bottom:6px'>"
                f"<div style='font-size:10px;font-weight:600;color:#64748b;width:90px;"
                f"text-align:right;flex-shrink:0;white-space:nowrap'>{_sname_display}</div>"
                f"<div style='flex:1;background:#1e2d3d;border-radius:3px;height:5px;overflow:hidden'>"
                f"<div style='width:{_sw}%;height:5px;background:{_sc};"
                f"border-radius:3px'></div></div>"
                f"<div style='font-size:11px;font-weight:700;color:{_sc};"
                f"font-family:monospace;width:58px;flex-shrink:0;text-align:right'>"
                f"{_sarr} {_val_str}</div></div>"
            )
        _sec_container = (
            "<div style='background:#0d1117;border:1px solid #1e2d3d;border-radius:12px;"
            "padding:14px 18px;height:100%'>"
            "<div style='font-size:9px;font-weight:800;color:#334155;text-transform:uppercase;"
            "letter-spacing:.12em;margin-bottom:10px'>Sector performance</div>"
            + _bars_html +
            "</div>"
        )
        st.markdown(_sec_container, unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom:.75rem'></div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom:.5rem'></div>", unsafe_allow_html=True)

    # ── All equities ───────────────────────────────────────────────────────────
    st.markdown('<div class="section-label">All equities</div>', unsafe_allow_html=True)
    search = st.text_input("", placeholder="🔍  Search symbol or company name…", label_visibility="collapsed")
    disp = df_live.copy()
    disp["name"] = disp.apply(
        lambda r: _GSE_NAMES.get(str(r["symbol"]), str(r["name"])) if str(r["name"]) == str(r["symbol"]) else str(r["name"]), axis=1
    )
    if search:
        q = search.upper()
        disp = disp[disp["symbol"].str.upper().str.contains(q, na=False) | disp["name"].str.upper().str.contains(q, na=False)]
    disp["Price (GH₵)"] = disp["price"].map("{:.2f}".format)
    disp["Change (%)"]  = disp["change"].map("{:+.2f}%".format)
    disp["Volume"]      = disp["volume"].map("{:,}".format)
    # Build fully custom dark HTML table with click buttons
    rows_html = ""
    eq_syms_order = []  # track order for buttons
    for _, r in disp.iterrows():
        eq_syms_order.append(str(r["symbol"]))
        chg_val = float(r["change"])
        if chg_val > 0:
            chg_color = "#4ade80"
            chg_bg    = "rgba(34,197,94,0.08)"
            chg_str   = f"+{chg_val:.2f}%"
        elif chg_val < 0:
            chg_color = "#f87171"
            chg_bg    = "rgba(239,68,68,0.08)"
            chg_str   = f"{chg_val:.2f}%"
        else:
            chg_color = "#475569"
            chg_bg    = "transparent"
            chg_str   = "+0.00%"

        sym      = str(r["symbol"])
        _rname = str(r.get("name",""))
        cname  = _GSE_NAMES.get(sym) or (_rname if _rname not in ["nan","",sym] else sym) if str(r["name"]) == sym else str(r["name"])
        price    = f"GH₵ {float(r['price']):.2f}"
        vol      = f"{int(r['volume']):,}"

        # Avatar colours
        _AV2 = [
            ("#0c2a4a","#38bdf8"), ("#0d2b1a","#4ade80"), ("#2a1a0c","#fb923c"),
            ("#1a0c2a","#a78bfa"), ("#2a0c1a","#f472b6"), ("#0c2a22","#34d399"),
        ]
        ai = sum(ord(c) for c in sym) % len(_AV2)
        av_bg, av_fg = _AV2[ai]

        # Sector-based logo colours for a richer badge feel
        _SECTOR_COLORS = {
            "GCB":"#1a3a6b,#60a5fa","EGH":"#1a3a6b,#60a5fa","SCB":"#1a3a6b,#60a5fa",
            "CAL":"#1a3a6b,#60a5fa","ETI":"#1a3a6b,#60a5fa","ACCESS":"#1a3a6b,#60a5fa",
            "SOGEGH":"#1a3a6b,#60a5fa","RBGH":"#1a3a6b,#60a5fa","ADB":"#1a3a6b,#60a5fa",
            "MTNGH":"#3d2800,#fbbf24","GOIL":"#002a14,#34d399","TOR":"#002a14,#34d399",
            "TOTAL":"#002a14,#34d399","GCB":"#1a3a6b,#60a5fa",
            "GGBL":"#3d0a0a,#f87171","FML":"#3d0a0a,#f87171","UNIL":"#3d0a0a,#f87171",
            "BOPP":"#1a2800,#86efac","PBC":"#1a2800,#86efac",
            "MOGL":"#2a1a00,#fb923c","GSR":"#2a1a00,#fb923c","AGA":"#2a1a00,#fb923c",
            "ALLGH":"#1a0d2e,#c084fc","AYRTN":"#1a0d2e,#c084fc","CPC":"#1a0d2e,#c084fc",
            "SIC":"#001a2e,#38bdf8","ENTERPRISE":"#001a2e,#38bdf8",
            "CLYD":"#2e001a,#f472b6","HFC":"#2e001a,#f472b6",
        }
        sc = _SECTOR_COLORS.get(sym, f"{av_bg},{av_fg}")
        sc_bg, sc_fg = sc.split(",")

        # Word mark: first letter big, rest small
        wm_big  = sym[0]
        wm_rest = sym[1:3] if len(sym) > 1 else ""

        logo_uri_tbl = _load_logo_b64(sym)
        if logo_uri_tbl:
            badge_html = f'''<div style="width:38px;height:38px;border-radius:9px;
                background:#0d1117;border:1px solid #1e2d3d;flex-shrink:0;
                display:flex;align-items:center;justify-content:center;padding:3px;overflow:hidden">
                <img src="{logo_uri_tbl}" style="width:100%;height:100%;object-fit:contain;border-radius:6px" alt="{sym}"/>
              </div>'''
        else:
            badge_html = f'''<div style="width:38px;height:38px;border-radius:9px;background:{sc_bg};
                border:1px solid {sc_fg}22;flex-shrink:0;display:flex;align-items:center;
                justify-content:center;flex-direction:column;line-height:1">
                <div style="font-size:15px;font-weight:900;color:{sc_fg};letter-spacing:-1px;
                     font-family:Arial Black,sans-serif">{wm_big}</div>
                <div style="font-size:8px;font-weight:700;color:{sc_fg}99;letter-spacing:1px;
                     margin-top:-1px">{wm_rest}</div>
              </div>'''

        rows_html += f"""
        <tr class="eq-row">
          <td style="width:160px">
            <div style="display:flex;align-items:center;gap:12px">
              {badge_html}
              <span style="font-weight:700;color:#f1f5f9;font-size:13px">{sym}</span>
            </div>
          </td>
          <td style="color:#94a3b8;font-size:13px">{cname}</td>
          <td style="color:#e2e8f0;font-family:'Courier New',monospace;font-size:13px;font-weight:600">GH₵ {float(r["price"]):.2f}</td>
          <td>
            <span style="background:{chg_bg};color:{chg_color};font-size:12px;font-weight:700;
                 font-family:monospace;padding:3px 12px;border-radius:20px;
                 border:1px solid {chg_color}33">{chg_str}</span>
          </td>
          <td style="color:#475569;font-size:12px;font-family:monospace">{vol}</td>
        </tr>"""

    st.markdown('<div style="font-size:11px;color:#334155;margin-bottom:6px">Click a symbol button below to open full detail</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div style="border:1px solid #1e2d3d;border-radius:14px;overflow:hidden;margin-top:8px;
                max-height:520px;overflow-y:auto">
      <table style="width:100%;border-collapse:collapse;background:#0d1117">
        <thead>
          <tr style="background:#111827;border-bottom:1px solid #1e2d3d;position:sticky;top:0">
            <th style="padding:12px 16px;text-align:left;font-size:10px;font-weight:700;
                color:#475569;text-transform:uppercase;letter-spacing:.08em;width:140px">Symbol</th>
            <th style="padding:12px 16px;text-align:left;font-size:10px;font-weight:700;
                color:#475569;text-transform:uppercase;letter-spacing:.08em">Company</th>
            <th style="padding:12px 16px;text-align:left;font-size:10px;font-weight:700;
                color:#475569;text-transform:uppercase;letter-spacing:.08em">Price</th>
            <th style="padding:12px 16px;text-align:left;font-size:10px;font-weight:700;
                color:#475569;text-transform:uppercase;letter-spacing:.08em">Change</th>
            <th style="padding:12px 16px;text-align:left;font-size:10px;font-weight:700;
                color:#475569;text-transform:uppercase;letter-spacing:.08em">Volume</th>
          </tr>
        </thead>
        <tbody>{rows_html}</tbody>
      </table>
    </div>
    <style>
    .eq-row {{ border-bottom:1px solid #111827; transition:background .15s; }}
    .eq-row:hover {{ background:#111827 !important; }}
    .eq-row:last-child {{ border-bottom:none; }}
    .eq-row td {{ padding:11px 16px; vertical-align:middle; }}
    </style>
    """, unsafe_allow_html=True)

    # Compact symbol chip grid — cleaner than full buttons
    st.markdown('<div class="section-label" style="margin-top:1rem">Quick navigate</div>', unsafe_allow_html=True)
    chips_html = '<div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:1rem">'
    for sym in eq_syms_order[:min(len(eq_syms_order), 40)]:
        chg_row = df_live[df_live["symbol"] == sym]
        chg_val = float(chg_row["change"].values[0]) if not chg_row.empty else 0.0
        chip_c  = "#4ade80" if chg_val > 0 else "#f87171" if chg_val < 0 else "#475569"
        chip_bg = "rgba(34,197,94,0.08)" if chg_val > 0 else "rgba(239,68,68,0.08)" if chg_val < 0 else "rgba(71,85,105,0.08)"
        chips_html += f'<span style="background:{chip_bg};color:{chip_c};border:1px solid {chip_c}33;font-size:11px;font-weight:700;padding:4px 10px;border-radius:20px;font-family:monospace;letter-spacing:.5px">{sym}</span>'
    chips_html += '</div>'
    st.markdown(chips_html, unsafe_allow_html=True)

    # Search and click via selectbox for navigation
    nav_sym = st.selectbox("Open stock detail for:", [""] + eq_syms_order,
        format_func=lambda s: f"{s}  —  {_GSE_NAMES.get(s, s)}" if s else "Select a symbol…",
        label_visibility="collapsed", key="eq_nav_select")
    if nav_sym:
        st.session_state["selected_symbol"] = nav_sym
        st.session_state.page = "Stock Detail"
        st.rerun()
    # ── Finance news ────────────────────────────────────────────────────────────
    st.markdown('<div class="section-label">Finance news</div>', unsafe_allow_html=True)

    @st.cache_data(ttl=1800, show_spinner=False)
    def fetch_news() -> list[dict]:
        """Fetch finance news from RSS feeds — GhanaWeb, Reuters, BBC Business."""
        import xml.etree.ElementTree as ET
        feeds = [
            ("Ghana Business", "https://www.ghanaweb.com/GhanaHomePage/rss/business.xml"),
            ("Reuters Markets", "https://feeds.reuters.com/reuters/businessNews"),
            ("BBC Business",    "https://feeds.bbci.co.uk/news/business/rss.xml"),
        ]
        articles = []
        for source, url in feeds:
            try:
                r = requests.get(url, headers=HEADERS, timeout=8)
                root = ET.fromstring(r.content)
                for item in root.iter("item"):
                    title = item.findtext("title", "").strip()
                    link  = item.findtext("link",  "").strip()
                    pub   = item.findtext("pubDate", "").strip()
                    desc  = item.findtext("description", "").strip()
                    # Strip HTML tags from description
                    import re
                    desc = re.sub(r'<[^>]+>', '', desc)[:160]
                    if title:
                        articles.append({
                            "source": source, "title": title,
                            "link": link, "date": pub[:16], "desc": desc,
                        })
                    if len([a for a in articles if a["source"] == source]) >= 4:
                        break
            except Exception:
                pass
        return articles[:12]

    news_items = fetch_news()

    if news_items:
        # Group by source
        sources = {}
        for item in news_items:
            sources.setdefault(item["source"], []).append(item)

        src_cols = st.columns(len(sources))
        src_color = {"Ghana Business": "#fbbf24", "Reuters Markets": "#f87171", "BBC Business": "#60a5fa"}

        for col, (src, items) in zip(src_cols, sources.items()):
            color = src_color.get(src, "#94a3b8")
            with col:
                st.markdown(f'''<div style="font-size:10px;font-weight:700;color:{color};
                    text-transform:uppercase;letter-spacing:.1em;margin-bottom:10px;
                    padding-bottom:6px;border-bottom:1px solid #1e2d3d">{src}</div>''',
                    unsafe_allow_html=True)
                for art in items:
                    st.markdown(f'''
                    <a href="{art["link"]}" target="_blank" style="text-decoration:none">
                      <div style="background:#0d1117;border:1px solid #1e2d3d;border-radius:10px;
                           padding:12px 14px;margin-bottom:8px;transition:border-color .2s;
                           cursor:pointer">
                        <div style="font-size:12px;font-weight:600;color:#e2e8f0;
                             line-height:1.4;margin-bottom:6px">{art["title"][:90]}{"…" if len(art["title"])>90 else ""}</div>
                        <div style="font-size:11px;color:#475569;line-height:1.3">{art["desc"][:100]}{"…" if len(art["desc"])>100 else ""}</div>
                        <div style="font-size:10px;color:#334155;margin-top:6px;font-family:monospace">{art["date"]}</div>
                      </div>
                    </a>''', unsafe_allow_html=True)
    else:
        st.markdown('<div style="color:#334155;font-size:13px;padding:8px 0">News unavailable — check your connection.</div>', unsafe_allow_html=True)

    # ── Developer footer ─────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="margin-top:3rem;padding:24px 0 8px;border-top:1px solid #1e2d3d">
      <div style="display:flex;align-items:center;justify-content:space-between;
           flex-wrap:wrap;gap:16px;margin-bottom:16px">
        <div style="width:220px">{_B360_LOGO_SMALL}</div>
        <div style="text-align:right">
          <div style="font-size:11px;color:#334155">
            © 2026 Bourse360 · BismarkDataLab Inc. All rights reserved.</div>
          <div style="font-size:10px;color:#1e2d3d;margin-top:3px">
            Data: Ghana Stock Exchange · dev.kwayisi.org · Built with Streamlit &amp; Python</div>
        </div>
      </div>
    <!-- bottom divider -->
    <div style="margin-top:3rem;padding:20px 0;border-top:1px solid #141d2e;
         display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px">
      <div style="display:flex;align-items:center;gap:16px">
        <div style="width:44px;height:44px;flex-shrink:0;
             background:linear-gradient(135deg,#0ea5e9,#6366f1);
             border-radius:12px;display:flex;align-items:center;justify-content:center;
             box-shadow:0 0 14px rgba(99,102,241,0.3)">
          <span style="font-size:20px;font-weight:900;color:#fff;
               font-family:Arial Black,sans-serif">B</span>
        </div>
        <div>
          <div style="font-size:18px;font-weight:900;color:#f1f5f9;
               font-family:Arial Black,sans-serif;letter-spacing:-.3px">
            Bourse<span style="color:#38bdf8">360</span>
          </div>
          <div style="font-size:11px;color:#334155;margin-top:3px">
            Developed by <span style="color:#38bdf8;font-weight:600">Bismark N. G. Ababio</span>
            &nbsp;·&nbsp; <span style="color:#475569">BismarkDataLab Inc</span>
          </div>
          <div style="font-size:10px;color:#1e2d3d;margin-top:2px">
            Ghana Stock Exchange · Data: dev.kwayisi.org · Built with Streamlit &amp; Python
          </div>
        </div>
      </div>
      <div style="text-align:right">
        <div style="font-size:11px;color:#1e2d3d;font-family:monospace">Built with Streamlit &amp; Python</div>
        <div style="font-size:10px;color:#1a2535;margin-top:2px">© 2026 Bourse360 · BismarkDataLab Inc. All rights reserved.</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: STOCK DETAIL
# ═══════════════════════════════════════════════════════════════════════════════

elif page == "Stock Detail":
    if not symbols:
        st.markdown("""
    <div style="background:#0c1a0c;border:1px solid #166534;border-radius:10px;
         padding:12px 18px;margin-bottom:1rem;display:flex;align-items:center;gap:12px">
      <span style="font-size:20px">📡</span>
      <div>
        <div style="font-size:13px;font-weight:700;color:#4ade80">Connecting to GSE API…</div>
        <div style="font-size:11px;color:#334155;margin-top:3px">
          Run the app locally once during GSE market hours (10:00–15:00 GMT),
          then push <code>gse_history.csv</code> to GitHub — cloud app loads from that file.
          <b>Click Refresh data to retry.</b></div>
      </div>
    </div>""", unsafe_allow_html=True)

    st.markdown("""
    <style>
    .sd-topbar{display:flex;align-items:center;gap:16px;margin-bottom:1.25rem;
        padding:16px 20px;background:#0d1117;border:1px solid #1e2d3d;border-radius:14px;
        flex-wrap:wrap}
    .sd-controls{display:flex;align-items:center;gap:12px;flex-wrap:wrap;flex:1}
    </style>""", unsafe_allow_html=True)

    # ── Top selector bar (prominent, on-page) ─────────────────────────────────
    st.markdown("### Stock detail")
    sel_c1, sel_c2, sel_c3, sel_c4 = st.columns([3, 1.5, 1, 1])

    # Pre-select from session state (set when clicking a card on Overview)
    default_sym = st.session_state.get("selected_symbol", symbols[0] if symbols else "GCB")
    default_idx = symbols.index(default_sym) if default_sym in symbols else 0

    symbol   = sel_c1.selectbox("Select equity", symbols, index=default_idx,
                  format_func=lambda s: f"{s}  —  {_GSE_NAMES.get(s, s)}")
    period   = sel_c2.selectbox("Period", ["1M","3M","6M","1Y","All"], index=2)
    show_bb  = sel_c3.checkbox("Bollinger Bands", value=True)
    show_sma = sel_c4.checkbox("SMA 50", value=False)

    st.session_state["selected_symbol"] = symbol

    # Also keep sidebar controls (secondary)
    with st.sidebar:
        st.divider()
        st.markdown('<div style="font-size:10px;font-weight:600;color:#475569;text-transform:uppercase;letter-spacing:.08em;margin-bottom:6px">Quick select</div>', unsafe_allow_html=True)
        sb_sym = st.selectbox("Symbol", symbols,
            index=symbols.index(symbol) if symbol in symbols else 0,
            key="sb_sym_detail",
            format_func=lambda s: f"{s} · {_GSE_NAMES.get(s,s)[:20]}")
        if sb_sym != symbol:
            st.session_state["selected_symbol"] = sb_sym
            st.rerun()

    hist = get_history(symbol)
    if not hist.empty:
        hist = add_indicators(hist)
        days = PERIOD_DAYS.get(period, 180)
        hist = hist.tail(days).reset_index(drop=True)

    profile = get_profile(symbol)
    row_live = df_live[df_live["symbol"] == symbol]
    name     = row_live["name"].values[0]   if not row_live.empty else symbol
    price    = row_live["price"].values[0]  if not row_live.empty else None
    change   = row_live["change"].values[0] if not row_live.empty else None

    # Resolve full company name — prefer database, then API, then symbol
    _db_name = _GSE_COMPANIES.get(symbol, {}).get("name", "")
    full_name = _db_name if _db_name and _db_name != symbol else (
        _GSE_NAMES.get(symbol) or (name if name != symbol else symbol)
    )
    # Use real logo if available, else sector badge
    _logo_uri_detail = _load_logo_b64(symbol)
    if _logo_uri_detail:
        _badge_detail = f'''<div style="width:56px;height:56px;border-radius:12px;
            background:#0d1117;border:1px solid #1e2d3d;padding:5px;flex-shrink:0;
            display:flex;align-items:center;justify-content:center">
            <img src="{_logo_uri_detail}" style="width:100%;height:100%;object-fit:contain;border-radius:8px"/>
        </div>'''
    else:
        _sc = _SC_COLORS.get(symbol, "#0c2a4a,#38bdf8")
        _bg, _fg = _sc.split(",")
        _badge_detail = f'''<div style="width:56px;height:56px;border-radius:12px;
            background:{_bg};border:1px solid {_fg}33;flex-shrink:0;
            display:flex;align-items:center;justify-content:center;
            flex-direction:column;line-height:1">
            <div style="font-size:20px;font-weight:900;color:{_fg};letter-spacing:-1px;
                 font-family:Arial Black,sans-serif">{symbol[0]}</div>
            <div style="font-size:9px;font-weight:700;color:{_fg}99;letter-spacing:1px">{symbol[1:3]}</div>
        </div>'''
    db_sector = _GSE_COMPANIES.get(symbol, {}).get("sector", "Equity")
    db_listed = _GSE_COMPANIES.get(symbol, {}).get("listed", "")
    listed_str = f"Listed {db_listed}" if db_listed and db_listed not in ["—",""] else ""

    _listed_span = ("<span style='font-size:11px;color:#334155'>· " + listed_str + "</span>") if listed_str else ""
    _sector_span = "<span style='background:#1e2d3d;color:#64748b;font-size:11px;font-weight:600;padding:3px 10px;border-radius:99px'>" + db_sector + "</span>"
    _eq_span     = "<span style='background:rgba(56,189,248,0.1);color:#38bdf8;font-size:11px;font-weight:600;padding:3px 10px;border-radius:99px'>Equity</span>"
    _sym_div     = "<div style='font-size:24px;font-weight:800;color:#f1f5f9;letter-spacing:-.3px'>" + symbol + "</div>"
    _name_div    = "<div style='font-size:13px;color:#475569;margin-top:2px'>" + full_name + "</div>"
    _header_html = (
        "<div style='display:flex;align-items:center;gap:16px;margin-bottom:1.5rem;"
        "padding:20px;background:#0d1117;border:1px solid #1e2d3d;border-radius:14px'>"
        + _badge_detail
        + "<div style='flex:1'>"
        + "<div style='display:flex;align-items:center;gap:8px;margin-bottom:6px;flex-wrap:wrap'>"
        + _sector_span + _eq_span + _listed_span
        + "</div>"
        + _sym_div + _name_div
        + "</div></div>"
    )
    st.markdown(_header_html, unsafe_allow_html=True)

    if price is not None:
        chg_col2 = "#4ade80" if (change or 0)>=0 else "#f87171"
        chg_bg2  = "rgba(34,197,94,0.12)" if (change or 0)>=0 else "rgba(239,68,68,0.12)"
        arrow2   = "▲" if (change or 0)>=0 else "▼"
        prev_p   = price/(1+(change or 0)/100) if (change or 0) != -100 else price
        abs_chg2 = price - prev_p
        st.markdown(f"""
        <div style="margin-bottom:1rem">
          <div style="font-size:38px;font-weight:900;color:#f1f5f9;font-family:monospace;
               letter-spacing:-1px;line-height:1">GH₵ {price:.2f}</div>
          <div style="display:flex;align-items:center;gap:10px;margin-top:8px;flex-wrap:wrap">
            <span style="background:{chg_bg2};color:{chg_col2};font-size:14px;font-weight:700;
                padding:5px 14px;border-radius:99px">{arrow2} {"+" if (change or 0)>=0 else ""}{change:.2f}% today</span>
            <span style="color:{chg_col2};font-size:14px;font-family:monospace">
              {"+" if abs_chg2>=0 else ""}GH₵ {abs_chg2:.2f}</span>
            <span style="color:#334155;font-size:12px">
              {"● MARKET OPEN" if market_is_open() else "● Closed"}</span>
          </div>
        </div>""", unsafe_allow_html=True)
        if not hist.empty:
            sm1, sm2, sm3, sm4 = st.columns(4)
            sm1.metric("Period High", f"GH₵ {hist['price'].max():.2f}")
            sm2.metric("Period Low",  f"GH₵ {hist['price'].min():.2f}")
            sm3.metric("Avg Volume",  f"{int(hist['volume'].mean()):,}")
            sm4.metric("Days tracked", len(hist))

    # ── Company info card (database + API) ─────────────────────────────────
    db_info  = _GSE_COMPANIES.get(symbol, {})
    api_info = profile or {}
    co_sector  = db_info.get("sector",     api_info.get("sector",    "—"))
    co_listed  = db_info.get("listed",     "—")
    co_capital = db_info.get("capital",    "—")
    co_issued  = db_info.get("issued",     "—")
    co_auth    = db_info.get("authorised", "—")
    co_eps     = str(api_info.get("eps",   "—"))
    co_dps     = str(api_info.get("dps",   "—"))
    co_mktcap  = str(api_info.get("marketcap", "—"))

    with st.expander("Company profile", expanded=True):
        st.markdown(f"""
        <style>
        .co-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:.5rem}}
        .co-card{{background:#0d1117;border:1px solid #1e2d3d;border-radius:10px;padding:12px 16px}}
        .co-lbl {{font-size:10px;font-weight:700;color:#475569;text-transform:uppercase;
                  letter-spacing:.08em;margin-bottom:4px}}
        .co-val {{font-size:13px;font-weight:600;color:#e2e8f0}}
        </style>
        <div class="co-grid">
          <div class="co-card"><div class="co-lbl">Sector</div>
            <div class="co-val" style="color:#38bdf8">{co_sector}</div></div>
          <div class="co-card"><div class="co-lbl">Date listed</div>
            <div class="co-val">{co_listed}</div></div>
          <div class="co-card"><div class="co-lbl">Stated capital</div>
            <div class="co-val">{co_capital}</div></div>
          <div class="co-card"><div class="co-lbl">Issued shares</div>
            <div class="co-val">{co_issued}</div></div>
          <div class="co-card"><div class="co-lbl">Authorised shares</div>
            <div class="co-val">{co_auth}</div></div>
          <div class="co-card"><div class="co-lbl">Market cap (API)</div>
            <div class="co-val">{co_mktcap}</div></div>
          <div class="co-card"><div class="co-lbl">EPS</div>
            <div class="co-val">{co_eps}</div></div>
          <div class="co-card"><div class="co-lbl">DPS</div>
            <div class="co-val">{co_dps}</div></div>
        </div>
        """, unsafe_allow_html=True)

    # ── About the company (like ISEDAN image 4) ────────────────────────────
    about_text = _GSE_ABOUT.get(symbol, "")
    _co_data    = _GSE_COMPANIES.get(symbol, {})
    with st.expander(f"About {full_name}", expanded=False):
        # Main description
        if about_text:
            st.markdown(f"""
            <div style="font-size:14px;color:#94a3b8;line-height:1.8;padding:4px 0 12px;
                 text-align:justify">{about_text}</div>""", unsafe_allow_html=True)

        # Company profile grid (always show if data exists)
        if _co_data:
            _office    = _co_data.get("office", "")
            _nature    = _co_data.get("nature", "")
            _directors = _co_data.get("directors", "")

            profile_rows = [
                ("Sector",          _co_data.get("sector","—")),
                ("Date listed",     _co_data.get("listed","—")),
                ("Stated capital",  _co_data.get("capital","—")),
                ("Shares issued",   _co_data.get("issued","—")),
                ("Authorised shares", _co_data.get("authorised","—")),
            ]
            rows_html = "".join(f"""
            <tr>
              <td style="padding:8px 12px;font-size:11px;font-weight:700;color:#475569;
                   text-transform:uppercase;letter-spacing:.06em;white-space:nowrap;
                   border-bottom:1px solid #1e2d3d;width:160px">{lbl}</td>
              <td style="padding:8px 12px;font-size:13px;color:#e2e8f0;
                   border-bottom:1px solid #1e2d3d">{val}</td>
            </tr>""" for lbl, val in profile_rows if val and val != "—")

            if _office:
                rows_html += f"""<tr>
                  <td style="padding:8px 12px;font-size:11px;font-weight:700;color:#475569;
                       text-transform:uppercase;letter-spacing:.06em;border-bottom:1px solid #1e2d3d">Office</td>
                  <td style="padding:8px 12px;font-size:13px;color:#94a3b8;
                       border-bottom:1px solid #1e2d3d">{_office}</td>
                </tr>"""
            if _nature:
                rows_html += f"""<tr>
                  <td style="padding:8px 12px;font-size:11px;font-weight:700;color:#475569;
                       text-transform:uppercase;letter-spacing:.06em;border-bottom:1px solid #1e2d3d">Nature</td>
                  <td style="padding:8px 12px;font-size:13px;color:#94a3b8;
                       border-bottom:1px solid #1e2d3d">{_nature}</td>
                </tr>"""
            if _directors:
                rows_html += f"""<tr>
                  <td style="padding:8px 12px;font-size:11px;font-weight:700;color:#475569;
                       text-transform:uppercase;letter-spacing:.06em">Directors</td>
                  <td style="padding:8px 12px;font-size:12px;color:#64748b;font-style:italic">{_directors}</td>
                </tr>"""

            if rows_html:
                st.markdown(f"""
                <table style="width:100%;border-collapse:collapse;background:#0d1117;
                    border:1px solid #1e2d3d;border-radius:10px;overflow:hidden;margin-top:4px">
                  <tbody>{rows_html}</tbody>
                </table>""", unsafe_allow_html=True)
        else:
            st.caption("No company profile data available yet.")

    if hist.empty:
        st.info("No historical data for this symbol yet — data builds daily when the app runs during market hours.")

    # ── Analytics + previous day comparison ──────────────────────────────────
    analytics = compute_stock_analytics(symbol)
    csv_hist  = load_historical_comparison(symbol)

    if len(csv_hist) >= 2:
        prev_row  = csv_hist.iloc[-2]
        curr_p    = float(row_live["price"].values[0]) if not row_live.empty else None
        prev_p    = float(prev_row["price"])
        if curr_p:
            day_chg     = curr_p - prev_p
            day_chg_pct = (day_chg / prev_p * 100) if prev_p else 0
            pc1, pc2, pc3 = st.columns(3)
            pc1.metric("Yesterday close", f"GH₵ {prev_p:.2f}")
            pc2.metric("Day change", f"GH₵ {abs(day_chg):.2f}", f"{day_chg_pct:+.2f}%")
            pc3.metric("Days tracked", len(csv_hist))

    # Analytics signal + risk card
    sig = analytics["signal"]
    sig_colors = {
        "STRONG BUY":  ("#052e16","#4ade80","#166534"),
        "BUY":         ("#0a1f0a","#86efac","#14532d"),
        "HOLD":        ("#0f172a","#94a3b8","#1e2d3d"),
        "SELL":        ("#1c0a0a","#fca5a5","#7f1d1d"),
        "STRONG SELL": ("#1a0000","#f87171","#991b1b"),
    }
    sbg, sfg, sbdr = sig_colors.get(sig, sig_colors["HOLD"])

    ytd_r  = analytics.get("ytd_return")
    vol_r  = analytics.get("volatility")
    sharpe = analytics.get("sharpe")
    mom5   = analytics.get("momentum_5d")
    pvsma  = analytics.get("price_vs_sma20")
    sup    = analytics.get("support")
    res    = analytics.get("resistance")

    ytd_col = "#4ade80" if (ytd_r and ytd_r >= 0) else "#f87171"
    mom_col = "#4ade80" if (mom5 and mom5 >= 0)   else "#f87171"
    sma_col = "#4ade80" if (pvsma and pvsma >= 0)  else "#f87171"
    sharpe_col = "#4ade80" if (sharpe and sharpe > 1) else "#f87171" if (sharpe and sharpe < 0) else "#94a3b8"
    vol_risk = "Low" if (vol_r and vol_r < 15) else "Medium" if (vol_r and vol_r < 30) else "High" if vol_r else "—"
    ytd_str = ("+" if ytd_r >= 0 else "") + f"{ytd_r:.2f}%" if ytd_r is not None else "—"
    mom_str = ("+" if mom5 >= 0 else "") + f"{mom5:.2f}%" if mom5 is not None else "—"
    sma_str = ("+" if pvsma >= 0 else "") + f"{pvsma:.2f}%" if pvsma is not None else "—"

    st.markdown(f"""
    <style>.acard{{background:rgba(0,0,0,0.3);border-radius:10px;padding:10px 12px}}
    .albl{{font-size:9px;color:#475569;text-transform:uppercase;letter-spacing:.08em;margin-bottom:4px}}
    .aval{{font-size:13px;font-weight:700;color:#e2e8f0}}
    .bigcard{{background:#0d1117;border:1px solid #1e2d3d;border-radius:12px;padding:14px 16px}}
    .biglbl{{font-size:9px;color:#475569;text-transform:uppercase;letter-spacing:.08em;margin-bottom:6px}}
    .bigval{{font-size:20px;font-weight:800;font-family:monospace}}
    .bigsub{{font-size:10px;color:#334155;margin-top:3px}}</style>

    <div style="background:{sbg};border:1px solid {sbdr};border-radius:14px;
         padding:16px 20px;margin:1rem 0">
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px">
        <div style="font-size:11px;font-weight:800;color:{sfg};text-transform:uppercase;letter-spacing:.1em">
          Signal engine</div>
        <div style="background:{sbdr};color:{sfg};font-size:13px;font-weight:900;
             padding:6px 18px;border-radius:99px;letter-spacing:.5px">{sig}</div>
      </div>
      <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px">
        <div class="acard"><div class="albl">RSI Signal</div>
          <div class="aval">{analytics.get("rsi_signal","—")}</div></div>
        <div class="acard"><div class="albl">MACD Signal</div>
          <div class="aval">{analytics.get("macd_signal","—")}</div></div>
        <div class="acard"><div class="albl">5-Day Momentum</div>
          <div class="aval" style="color:{mom_col}">{mom_str}</div></div>
        <div class="acard"><div class="albl">vs SMA 20</div>
          <div class="aval" style="color:{sma_col}">{sma_str}</div></div>
      </div>
    </div>

    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:1rem">
      <div class="bigcard"><div class="biglbl">YTD Return</div>
        <div class="bigval" style="color:{ytd_col}">{ytd_str}</div>
        <div class="bigsub">Year-to-date performance</div></div>
      <div class="bigcard"><div class="biglbl">Volatility (Ann.)</div>
        <div class="bigval" style="color:#fbbf24">{f"{vol_r:.1f}%" if vol_r is not None else "—"}</div>
        <div class="bigsub">{vol_risk} risk</div></div>
      <div class="bigcard"><div class="biglbl">Sharpe Ratio</div>
        <div class="bigval" style="color:{sharpe_col}">{f"{sharpe:.2f}" if sharpe is not None else "—"}</div>
        <div class="bigsub">Risk-adjusted return</div></div>
    </div></div>
    """, unsafe_allow_html=True)

    if sup and res:
        st.markdown(f"""
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:1rem">
          <div class="bigcard" style="border-color:#166534">
            <div class="biglbl">Support (20D)</div>
            <div class="bigval" style="color:#4ade80">GH&#x20B5; {sup:.2f}</div>
          </div>
          <div class="bigcard" style="border-color:#7f1d1d">
            <div class="biglbl">Resistance (20D)</div>
            <div class="bigval" style="color:#f87171">GH&#x20B5; {res:.2f}</div>
          </div>
        </div>""", unsafe_allow_html=True)

    # Main chart — price / volume / RSI / MACD
    fig = make_subplots(
        rows=3, cols=1, shared_xaxes=True,
        row_heights=[0.55, 0.20, 0.25],
        vertical_spacing=0.04,
        subplot_titles=("Price & Volume", "RSI (14)", "MACD (12/26/9)"),
    )

    fig.add_trace(go.Scatter(x=hist["date"], y=hist["price"],
        name="Price", line=dict(color="#378ADD", width=2)), row=1, col=1)

    if show_bb and "BB_Upper" in hist.columns:
        fig.add_trace(go.Scatter(x=hist["date"], y=hist["BB_Upper"],
            line=dict(color="#888780", width=1, dash="dot"), showlegend=False), row=1, col=1)
        fig.add_trace(go.Scatter(x=hist["date"], y=hist["BB_Lower"],
            line=dict(color="#888780", width=1, dash="dot"),
            fill="tonexty", fillcolor="rgba(136,135,128,0.08)", showlegend=False), row=1, col=1)

    if show_sma and "SMA50" in hist.columns:
        fig.add_trace(go.Scatter(x=hist["date"], y=hist["SMA50"],
            name="SMA 50", line=dict(color="#EF9F27", width=1.5)), row=1, col=1)

    vol_colors = ["#1D9E75" if c >= 0 else "#E24B4A" for c in hist["change"].fillna(0)]
    fig.add_trace(go.Bar(x=hist["date"], y=hist["volume"],
        name="Volume", marker_color=vol_colors, opacity=0.5), row=1, col=1)

    fig.add_trace(go.Scatter(x=hist["date"], y=hist["RSI"],
        name="RSI", line=dict(color="#7F77DD", width=1.5)), row=2, col=1)
    fig.add_hline(y=70, line_dash="dot", line_color="#E24B4A", opacity=0.5, row=2, col=1)
    fig.add_hline(y=30, line_dash="dot", line_color="#1D9E75", opacity=0.5, row=2, col=1)

    fig.add_trace(go.Scatter(x=hist["date"], y=hist["MACD"],
        name="MACD", line=dict(color="#378ADD", width=1.5)), row=3, col=1)
    fig.add_trace(go.Scatter(x=hist["date"], y=hist["Signal"],
        name="Signal", line=dict(color="#EF9F27", width=1.5)), row=3, col=1)

    hist_colors = ["#1D9E75" if v >= 0 else "#E24B4A" for v in hist["MACD_Hist"].fillna(0)]
    fig.add_trace(go.Bar(x=hist["date"], y=hist["MACD_Hist"],
        name="Histogram", marker_color=hist_colors, opacity=0.6), row=3, col=1)

    fig.update_layout(
        height=620, margin=dict(l=0, r=0, t=40, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.01),
        hovermode="x unified", xaxis_rangeslider_visible=False,
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_yaxes(showgrid=True, gridcolor="rgba(128,128,128,0.1)")
    fig.update_xaxes(showgrid=False)
    st.plotly_chart(fig, use_container_width=True)

    # RSI signal banner
    rsi_vals = hist["RSI"].dropna()
    if not rsi_vals.empty:
        rsi = rsi_vals.iloc[-1]
        if rsi > 70:
            st.warning(f"RSI {rsi:.1f} — overbought (>70). Consider taking profits.")
        elif rsi < 30:
            st.info(f"RSI {rsi:.1f} — oversold (<30). Potential buying opportunity.")
        else:
            st.success(f"RSI {rsi:.1f} — neutral zone.")

    # Raw data expander
    with st.expander("View raw data"):
        raw = hist[["date", "price", "volume", "RSI", "MACD", "Signal"]].copy()
        raw["date"]   = raw["date"].dt.strftime("%Y-%m-%d")
        raw["price"]  = raw["price"].map("{:.2f}".format)
        raw["RSI"]    = raw["RSI"].map(lambda x: f"{x:.1f}"  if pd.notna(x) else "—")
        raw["MACD"]   = raw["MACD"].map(lambda x: f"{x:.4f}" if pd.notna(x) else "—")
        raw["Signal"] = raw["Signal"].map(lambda x: f"{x:.4f}" if pd.notna(x) else "—")
        st.dataframe(raw.iloc[::-1], use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: SECTOR ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════

elif page == "Sector Analysis":

    st.markdown("""
    <style>
    .sector-hdr{font-size:10px;font-weight:800;color:#475569;text-transform:uppercase;
        letter-spacing:.12em;margin:1.5rem 0 .6rem;padding-left:4px}
    .bubble-wrap{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:.5rem}
    .stock-bubble{padding:8px 16px;border-radius:99px;font-size:13px;font-weight:700;
        cursor:pointer;border:1px solid;transition:all .15s;white-space:nowrap}
    .bubble-up  {background:rgba(34,197,94,0.12);border-color:rgba(34,197,94,0.35);color:#4ade80}
    .bubble-dn  {background:rgba(239,68,68,0.12);border-color:rgba(239,68,68,0.35);color:#f87171}
    .bubble-nt  {background:rgba(30,45,61,0.5);border-color:#1e2d3d;color:#64748b}
    .bubble-up:hover{background:rgba(34,197,94,0.2);transform:scale(1.05)}
    .bubble-dn:hover{background:rgba(239,68,68,0.2);transform:scale(1.05)}
    .bubble-nt:hover{background:#111827;color:#94a3b8;transform:scale(1.05)}
    </style>""", unsafe_allow_html=True)

    st.markdown("### Sector map")
    st.caption("Click any bubble to open full stock detail")

    if df_live.empty:
        st.markdown("""
    <div style="background:#0c1a0c;border:1px solid #166534;border-radius:10px;
         padding:12px 18px;margin-bottom:1rem;display:flex;align-items:center;gap:12px">
      <span style="font-size:20px">📡</span>
      <div>
        <div style="font-size:13px;font-weight:700;color:#4ade80">Connecting to GSE API…</div>
        <div style="font-size:11px;color:#334155;margin-top:3px">
          Run the app locally once during GSE market hours (10:00–15:00 GMT),
          then push <code>gse_history.csv</code> to GitHub — cloud app loads from that file.
          <b>Click Refresh data to retry.</b></div>
      </div>
    </div>""", unsafe_allow_html=True)

    # Build sector groups
    df_s = df_live.copy()
    df_s["sector"] = df_s["symbol"].map(SECTOR_MAP).fillna("Other")
    df_s["name"]   = df_s.apply(lambda r: _GSE_NAMES.get(str(r["symbol"]), str(r["name"])) if str(r["name"])==str(r["symbol"]) else str(r["name"]), axis=1)

    # Summary metric cards
    sector_df = df_s.groupby("sector").agg(
        avg_change=("change","mean"), total_volume=("volume","sum"), count=("symbol","count")
    ).reset_index().sort_values("avg_change", ascending=False)

    best  = sector_df.iloc[0]
    worst = sector_df.iloc[-1]
    c1,c2,c3 = st.columns(3)
    c1.metric("Best sector",     best["sector"],  f"{best['avg_change']:+.2f}%")
    c2.metric("Worst sector",    worst["sector"], f"{worst['avg_change']:+.2f}%")
    c3.metric("Sectors tracked", len(sector_df))

    st.divider()

    # ── Sector bubble map ────────────────────────────────────────────────────
    sector_order = ["Financials","Telecoms","Oil & Gas","Mining","Consumer Goods",
                    "Agribusiness","Manufacturing","Healthcare","Insurance","Real Estate","Other"]

    for sector in sector_order:
        stocks = df_s[df_s["sector"]==sector]
        if stocks.empty:
            continue
        st.markdown(f'<div class="sector-hdr">{sector}</div>', unsafe_allow_html=True)
        bubbles_html = '<div class="bubble-wrap">'
        for _, row in stocks.sort_values("change", ascending=False).iterrows():
            sym = str(row["symbol"])
            chg = float(row["change"])
            if chg > 0:
                cls = "bubble-up"; tag = f"+{chg:.1f}%"
            elif chg < 0:
                cls = "bubble-dn"; tag = f"{chg:.1f}%"
            else:
                cls = "bubble-nt"; tag = ""
            label = f"{sym} <span style='font-size:11px'>{tag}</span>" if tag else sym
            bubbles_html += f'<span class="stock-bubble {cls}">{label}</span>'
        bubbles_html += '</div>'
        st.markdown(bubbles_html, unsafe_allow_html=True)

        # Navigation handled by a single compact selectbox below the map
        pass

    st.divider()

    # ── Sector performance heatmap ───────────────────────────────────────────
    st.markdown('<div class="mr-section" style="margin-top:0">Sector heatmap — avg daily return</div>', unsafe_allow_html=True)
    sector_heat = df_s.groupby("sector").agg(
        avg_chg=("change","mean"), count=("symbol","count")
    ).reset_index()

    heat_html = '<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-bottom:1rem">'
    for _, sr in sector_heat.sort_values("avg_chg", ascending=False).iterrows():
        av = float(sr["avg_chg"])
        intensity = min(abs(av) / 5, 1.0)
        if av > 0:
            bg   = f"rgba(34,197,94,{0.08 + intensity*0.25})"
            border = f"rgba(34,197,94,{0.2 + intensity*0.4})"
            col  = "#4ade80"
            sign = "+"
        elif av < 0:
            bg   = f"rgba(239,68,68,{0.08 + intensity*0.25})"
            border = f"rgba(239,68,68,{0.2 + intensity*0.4})"
            col  = "#f87171"
            sign = ""
        else:
            bg = "rgba(30,45,61,0.5)"; border = "#1e2d3d"; col = "#475569"; sign = ""
        heat_html += f'''<div style="background:{bg};border:1px solid {border};
            border-radius:12px;padding:14px;text-align:center">
          <div style="font-size:10px;font-weight:700;color:#94a3b8;text-transform:uppercase;
               letter-spacing:.06em;margin-bottom:6px">{sr["sector"]}</div>
          <div style="font-size:20px;font-weight:900;color:{col};font-family:monospace">
            {sign}{av:.2f}%</div>
          <div style="font-size:10px;color:#334155;margin-top:4px">{int(sr["count"])} stocks</div>
        </div>'''
    heat_html += '</div>'
    st.markdown(heat_html, unsafe_allow_html=True)

    # ── Stock navigator ──────────────────────────────────────────────────────
    all_sec_syms = df_s["symbol"].tolist()
    nav_pick = st.selectbox(
        "Open stock detail:",
        [""] + all_sec_syms,
        format_func=lambda s: f"{s}  —  {_GSE_NAMES.get(s, s)}" if s else "Select a stock to open detail…",
        label_visibility="collapsed",
        key="sec_nav_pick",
    )
    if nav_pick:
        st.session_state["selected_symbol"] = nav_pick
        st.session_state.page = "Stock Detail"
        st.rerun()

    st.divider()

    # ── Sector performance bar chart ────────────────────────────────────────
    st.markdown('<div class="section-label" style="margin-top:0">Sector performance</div>', unsafe_allow_html=True)
    col_a, col_b = st.columns(2)

    with col_a:
        colors = ["#4ade80" if v>=0 else "#f87171" for v in sector_df["avg_change"]]
        fig_bar = go.Figure(go.Bar(
            x=sector_df["avg_change"].round(2), y=sector_df["sector"],
            orientation="h", marker_color=colors,
            text=sector_df["avg_change"].map("{:+.2f}%".format),
            textposition="outside", textfont=dict(color="#94a3b8", size=11),
        ))
        fig_bar.update_layout(
            height=340, margin=dict(l=0,r=50,t=10,b=0),
            plot_bgcolor="#080c16", paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=True, gridcolor="#1e2d3d", tickfont=dict(color="#334155")),
            yaxis=dict(showgrid=False, tickfont=dict(color="#94a3b8")),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_b:
        fig_pie = px.pie(sector_df[sector_df["total_volume"]>0],
            values="total_volume", names="sector", hole=0.5,
            color_discrete_sequence=["#38bdf8","#4ade80","#fb923c","#a78bfa",
                "#f472b6","#34d399","#fbbf24","#f87171","#60a5fa","#86efac"])
        fig_pie.update_layout(
            height=340, margin=dict(l=0,r=0,t=10,b=0),
            plot_bgcolor="#080c16", paper_bgcolor="rgba(0,0,0,0)",
            legend=dict(font=dict(color="#475569",size=10),bgcolor="rgba(0,0,0,0)"),
        )
        fig_pie.update_traces(textposition="inside", textinfo="percent+label",
            textfont=dict(size=10))
        st.plotly_chart(fig_pie, use_container_width=True)


elif page == "Compare Stocks":
    st.title("Compare stocks")
    st.caption("Side-by-side normalised price performance")

    if not symbols:
        st.markdown("""
    <div style="background:#0c1a0c;border:1px solid #166534;border-radius:10px;
         padding:12px 18px;margin-bottom:1rem;display:flex;align-items:center;gap:12px">
      <span style="font-size:20px">📡</span>
      <div>
        <div style="font-size:13px;font-weight:700;color:#4ade80">Connecting to GSE API…</div>
        <div style="font-size:11px;color:#334155;margin-top:3px">
          Run the app locally once during GSE market hours (10:00–15:00 GMT),
          then push <code>gse_history.csv</code> to GitHub — cloud app loads from that file.
          <b>Click Refresh data to retry.</b></div>
      </div>
    </div>""", unsafe_allow_html=True)

    with st.sidebar:
        st.divider()
        st.markdown("**Comparison controls**")
        selected  = st.multiselect("Select 2–5 equities", symbols,
                                   default=symbols[:2], max_selections=5)
        period    = st.selectbox("Period", ["1M", "3M", "6M", "1Y", "All"], index=2)
        normalise = st.checkbox("Normalise to 100 (indexed)", value=True)

    if len(selected) < 2:
        st.info("Select at least 2 equities from the sidebar to compare.")
        st.stop()

    # Check if any history exists at all
    _has_any_history = any(not get_history(s).empty for s in selected)
    if not _has_any_history:
        st.markdown("""
        <div style="background:#0d1117;border:1px solid #1e2d3d;border-radius:14px;
             padding:28px;text-align:center;margin:2rem 0">
          <div style="font-size:20px;color:#38bdf8;margin-bottom:10px">📈</div>
          <div style="font-size:15px;font-weight:700;color:#e2e8f0;margin-bottom:8px">
            No historical data yet</div>
          <div style="font-size:13px;color:#475569;max-width:420px;margin:0 auto;line-height:1.6">
            Historical price data builds automatically each day the app runs during
            GSE market hours (10:00–15:00 GMT). Run the app daily and charts will
            appear here within a few days.</div>
        </div>""", unsafe_allow_html=True)
        st.stop()

    days = PERIOD_DAYS.get(period, 180)
    fig  = go.Figure()
    stats_rows = []

    for i, sym in enumerate(selected):
        hist = get_history(sym)
        if hist.empty:
            continue  # silently skip — no history yet
        hist = hist.tail(days).reset_index(drop=True)
        name_row = df_live[df_live["symbol"] == sym]
        name = name_row["name"].values[0] if not name_row.empty else sym

        y = hist["price"]
        if normalise and len(y) > 0 and y.iloc[0] != 0:
            y = (y / y.iloc[0]) * 100

        fig.add_trace(go.Scatter(
            x=hist["date"], y=y.round(2),
            name=f"{sym} — {name}",
            line=dict(color=CHART_COLORS[i % len(CHART_COLORS)], width=2),
            hovertemplate="%{y:.2f}<extra>" + sym + "</extra>",
        ))

        raw    = hist["price"]
        pct_chg = ((raw.iloc[-1] - raw.iloc[0]) / raw.iloc[0] * 100) if len(raw) > 1 else 0
        stats_rows.append({
            "Symbol": sym, "Company": name,
            f"Return ({period})": f"{pct_chg:+.2f}%",
            "High": f"GH₵ {raw.max():.2f}",
            "Low":  f"GH₵ {raw.min():.2f}",
            "Volatility": f"{raw.std():.2f}",
        })

    if normalise:
        fig.add_hline(y=100, line_dash="dot", line_color="gray", opacity=0.4)

    fig.update_layout(
        height=450, margin=dict(l=0, r=0, t=10, b=0),
        yaxis_title="Indexed (base=100)" if normalise else "Price (GH₵)",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.01),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_yaxes(showgrid=True, gridcolor="rgba(128,128,128,0.1)")
    fig.update_xaxes(showgrid=False)
    st.plotly_chart(fig, use_container_width=True)

    if stats_rows:
        st.subheader(f"Performance summary · {period}")
        st.dataframe(pd.DataFrame(stats_rows), use_container_width=True, hide_index=True)

    # Correlation heatmap
    if len(selected) >= 2:
        st.subheader("Return correlation")
        price_series = {}
        for sym in selected:
            h = get_history(sym)
            if not h.empty:
                price_series[sym] = h.tail(days).set_index("date")["price"]

        if len(price_series) >= 2:
            corr = pd.DataFrame(price_series).dropna().pct_change().corr().round(2)
            fig_corr = go.Figure(go.Heatmap(
                z=corr.values, x=corr.columns.tolist(), y=corr.index.tolist(),
                colorscale=[[0, "#E24B4A"], [0.5, "#F1EFE8"], [1, "#1D9E75"]],
                zmin=-1, zmax=1,
                text=corr.values.round(2), texttemplate="%{text}",
            ))
            fig_corr.update_layout(
                height=320, margin=dict(l=0, r=0, t=10, b=0),
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig_corr, use_container_width=True)
            st.caption("1.0 = perfectly correlated · 0 = uncorrelated · -1.0 = inverse")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: PORTFOLIO TRACKER
# ═══════════════════════════════════════════════════════════════════════════════

elif page == "Portfolio":

    st.markdown("""
    <style>
    .port-header{font-size:26px;font-weight:800;color:#f1f5f9;margin-bottom:4px}
    .port-sub{font-size:13px;color:#475569;margin-bottom:1.5rem}
    .pf-card{background:#0d1117;border:1px solid #1e2d3d;border-radius:14px;padding:18px 22px;margin-bottom:10px}
    .pf-sym{font-size:16px;font-weight:700;color:#f1f5f9}
    .pf-name{font-size:11px;color:#475569;margin-top:2px}
    .pf-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin-top:12px}
    .pf-metric{background:#111827;border-radius:10px;padding:10px 14px}
    .pf-mlbl{font-size:10px;color:#475569;text-transform:uppercase;letter-spacing:.06em;margin-bottom:4px}
    .pf-mval{font-size:15px;font-weight:700;color:#e2e8f0;font-family:monospace}
    .summary-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:1.5rem}
    .sum-card{background:#0d1117;border:1px solid #1e2d3d;border-radius:12px;padding:16px 20px;position:relative;overflow:hidden}
    .sum-card::before{content:"";position:absolute;top:0;left:0;right:0;height:2px}
    .sum-green::before{background:linear-gradient(90deg,#22c55e,#16a34a)}
    .sum-red::before{background:linear-gradient(90deg,#ef4444,#dc2626)}
    .sum-blue::before{background:linear-gradient(90deg,#38bdf8,#0ea5e9)}
    .sum-purple::before{background:linear-gradient(90deg,#a78bfa,#7c3aed)}
    .sum-lbl{font-size:10px;font-weight:700;color:#475569;text-transform:uppercase;letter-spacing:.08em;margin-bottom:6px}
    .sum-val{font-size:24px;font-weight:800;line-height:1}
    </style>""", unsafe_allow_html=True)

    st.markdown('<div class="port-header">💼 Portfolio tracker</div>', unsafe_allow_html=True)
    st.markdown('<div class="port-sub">Track your GSE holdings, monitor P&L and returns in real time</div>', unsafe_allow_html=True)

    # ── Add holding form ──────────────────────────────────────────────────────
    with st.expander("➕ Add new holding", expanded=len(st.session_state.portfolio) == 0):
        c1, c2, c3, c4 = st.columns([2, 2, 2, 1])
        pf_sym   = c1.selectbox("Symbol", symbols, key="pf_sym").upper() if symbols else c1.text_input("Symbol").upper()
        pf_shares = c2.number_input("Shares", min_value=1, value=100, step=1)
        pf_price  = c3.number_input("Buy price (GH₵)", min_value=0.01, value=1.00, step=0.01, format="%.2f")
        pf_date   = c4.date_input("Date", value=pd.Timestamp.today())
        if st.button("Add to portfolio", use_container_width=True):
            st.session_state.portfolio.append({
                "symbol":    pf_sym,
                "shares":    int(pf_shares),
                "buy_price": float(pf_price),
                "date":      str(pf_date),
            })
            st.success(f"Added {int(pf_shares):,} shares of {pf_sym} at GH₵ {pf_price:.2f}")
            st.rerun()

    if not st.session_state.portfolio:
        st.markdown('''<div style="text-align:center;padding:3rem;color:#334155;font-size:14px">
            No holdings yet. Add your first position above.</div>''', unsafe_allow_html=True)
    else:
        # ── Calculate P&L for each holding ───────────────────────────────────
        holdings = []
        for h in st.session_state.portfolio:
            sym         = h["symbol"]
            shares      = h["shares"]
            buy_price   = h["buy_price"]
            live_row    = df_live[df_live["symbol"] == sym]
            curr_price  = float(live_row["price"].values[0]) if not live_row.empty else buy_price
            cost_basis  = shares * buy_price
            curr_value  = shares * curr_price
            pnl         = curr_value - cost_basis
            pnl_pct     = (pnl / cost_basis * 100) if cost_basis > 0 else 0
            day_chg     = float(live_row["change"].values[0]) if not live_row.empty else 0.0
            day_pnl     = curr_value * day_chg / 100
            holdings.append({
                **h,
                "curr_price": curr_price,
                "cost_basis": cost_basis,
                "curr_value": curr_value,
                "pnl":        pnl,
                "pnl_pct":   pnl_pct,
                "day_chg":   day_chg,
                "day_pnl":   day_pnl,
            })

        total_cost  = sum(h["cost_basis"] for h in holdings)
        total_value = sum(h["curr_value"] for h in holdings)
        total_pnl   = total_value - total_cost
        total_pct   = (total_pnl / total_cost * 100) if total_cost > 0 else 0
        day_total   = sum(h["day_pnl"] for h in holdings)

        # ── Portfolio summary cards ───────────────────────────────────────────
        pnl_color = "#4ade80" if total_pnl >= 0 else "#f87171"
        day_color = "#4ade80" if day_total >= 0 else "#f87171"
        pnl_cls   = "sum-green" if total_pnl >= 0 else "sum-red"
        day_cls   = "sum-green" if day_total >= 0 else "sum-red"

        st.markdown(f"""
        <div class="summary-grid">
          <div class="sum-card sum-blue">
            <div class="sum-lbl">Portfolio value</div>
            <div class="sum-val" style="color:#38bdf8">GH₵ {total_value:,.2f}</div>
            <div style="font-size:11px;color:#334155;margin-top:4px">{len(holdings)} positions</div>
          </div>
          <div class="sum-card sum-purple">
            <div class="sum-lbl">Cost basis</div>
            <div class="sum-val" style="color:#a78bfa">GH₵ {total_cost:,.2f}</div>
            <div style="font-size:11px;color:#334155;margin-top:4px">Total invested</div>
          </div>
          <div class="sum-card {pnl_cls}">
            <div class="sum-lbl">Total P&L</div>
            <div class="sum-val" style="color:{pnl_color}">{"+" if total_pnl>=0 else ""}GH₵ {total_pnl:,.2f}</div>
            <div style="font-size:11px;color:{pnl_color};margin-top:4px">{"+" if total_pct>=0 else ""}{total_pct:.2f}% overall</div>
          </div>
          <div class="sum-card {day_cls}">
            <div class="sum-lbl">Today's P&L</div>
            <div class="sum-val" style="color:{day_color}">{"+" if day_total>=0 else ""}GH₵ {day_total:,.2f}</div>
            <div style="font-size:11px;color:#334155;margin-top:4px">Based on today's change</div>
          </div>
        </div>""", unsafe_allow_html=True)

        # ── Portfolio allocation donut chart ──────────────────────────────────
        col_chart, col_list = st.columns([1, 2])

        with col_chart:
            fig_alloc = go.Figure(go.Pie(
                labels=[h["symbol"] for h in holdings],
                values=[h["curr_value"] for h in holdings],
                hole=0.55,
                textinfo="label+percent",
                textfont=dict(size=12, color="#e2e8f0"),
                marker=dict(colors=["#38bdf8","#4ade80","#fb923c","#a78bfa","#f472b6","#34d399","#fbbf24","#f87171"]),
            ))
            fig_alloc.update_layout(
                height=280, margin=dict(l=0,r=0,t=20,b=0),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                showlegend=False,
                annotations=[dict(text="Allocation", x=0.5, y=0.5,
                    font=dict(size=12, color="#475569"), showarrow=False)],
            )
            st.plotly_chart(fig_alloc, use_container_width=True)

        # ── Holdings list ─────────────────────────────────────────────────────
        with col_list:
            for i, h in enumerate(holdings):
                sym      = h["symbol"]
                cname    = _GSE_NAMES.get(sym, sym)
                pnl_c    = "#4ade80" if h["pnl"] >= 0 else "#f87171"
                pnl_bg   = "rgba(34,197,94,0.07)" if h["pnl"] >= 0 else "rgba(239,68,68,0.07)"
                sign     = "+" if h["pnl"] >= 0 else ""
                day_c    = "#4ade80" if h["day_chg"] >= 0 else "#f87171"
                logo     = _load_logo_b64(sym)
                if logo:
                    av_html = f'<img src="{logo}" style="width:36px;height:36px;object-fit:contain;border-radius:7px;background:#0d1117;padding:3px;border:1px solid #1e2d3d">'
                else:
                    sc = _SC_COLORS.get(sym, "#0c2a4a,#38bdf8")
                    bg2, fg2 = sc.split(",")
                    av_html = f'<div style="width:36px;height:36px;border-radius:7px;background:{bg2};color:{fg2};font-size:12px;font-weight:900;display:flex;align-items:center;justify-content:center;flex-shrink:0">{sym[:2]}</div>'

                st.markdown(f"""
                <div class="pf-card">
                  <div style="display:flex;align-items:center;justify-content:space-between">
                    <div style="display:flex;align-items:center;gap:12px">
                      {av_html}
                      <div><div class="pf-sym">{sym}</div><div class="pf-name">{cname}</div></div>
                    </div>
                    <div style="text-align:right">
                      <div style="font-size:14px;font-weight:700;color:#e2e8f0">GH₵ {h["curr_price"]:.2f}</div>
                      <div style="font-size:11px;color:{day_c}">{"+" if h["day_chg"]>=0 else ""}{h["day_chg"]:.2f}% today</div>
                    </div>
                  </div>
                  <div class="pf-grid">
                    <div class="pf-metric"><div class="pf-mlbl">Shares</div><div class="pf-mval">{h["shares"]:,}</div></div>
                    <div class="pf-metric"><div class="pf-mlbl">Avg cost</div><div class="pf-mval">GH₵ {h["buy_price"]:.2f}</div></div>
                    <div class="pf-metric"><div class="pf-mlbl">Value</div><div class="pf-mval">GH₵ {h["curr_value"]:,.0f}</div></div>
                    <div class="pf-metric"><div class="pf-mlbl">P&L</div>
                      <div class="pf-mval" style="color:{pnl_c}">{sign}GH₵ {h["pnl"]:,.2f}</div></div>
                    <div class="pf-metric"><div class="pf-mlbl">Return</div>
                      <div class="pf-mval" style="color:{pnl_c}">{sign}{h["pnl_pct"]:.2f}%</div></div>
                  </div>
                </div>""", unsafe_allow_html=True)

                col_rm, _ = st.columns([1, 5])
                if col_rm.button("Remove", key=f"rm_hold_{i}_{sym}"):
                    st.session_state.portfolio.pop(i)
                    st.rerun()

        # ── Export portfolio as CSV ───────────────────────────────────────────
        st.divider()
        pf_df = pd.DataFrame([{
            "Symbol": h["symbol"], "Company": _GSE_NAMES.get(h["symbol"], h["symbol"]),
            "Shares": h["shares"], "Buy Price": h["buy_price"],
            "Current Price": h["curr_price"], "Cost Basis": round(h["cost_basis"],2),
            "Current Value": round(h["curr_value"],2), "P&L": round(h["pnl"],2),
            "Return (%)": round(h["pnl_pct"],2), "Date": h["date"],
        } for h in holdings])
        csv_bytes = pf_df.to_csv(index=False).encode()
        st.download_button(
            "⬇ Download portfolio CSV", csv_bytes,
            file_name=f"gse_portfolio_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv", use_container_width=True,
        )


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: ADVANCED CHARTS
# ═══════════════════════════════════════════════════════════════════════════════

elif page == "Advanced Charts":

    st.markdown("""
    <style>
    /* ── Robinhood-style chart page ── */
    .rh-header { padding:0 0 1rem; }
    .rh-price  { font-size:42px; font-weight:800; color:#f1f5f9; line-height:1; font-family:monospace; }
    .rh-change { font-size:14px; font-weight:600; padding:4px 12px; border-radius:99px;
                 display:inline-flex; align-items:center; gap:5px; margin-top:6px; }
    .rh-change.up { background:rgba(34,197,94,0.15); color:#4ade80; }
    .rh-change.dn { background:rgba(239,68,68,0.15); color:#f87171; }
    .rh-status { font-size:12px; color:#475569; margin-top:4px; }
    .period-tabs { display:flex; gap:4px; margin:1rem 0 .5rem; }
    .period-tab  { padding:5px 14px; border-radius:99px; font-size:12px; font-weight:700;
                   cursor:pointer; border:none; color:#475569; background:transparent;
                   letter-spacing:.03em; transition:all .15s; }
    .period-tab.active { background:#1e2d3d; color:#38bdf8; }
    .overlay-tabs { display:flex; gap:6px; flex-wrap:wrap; margin-bottom:.75rem; }
    .ov-tab { padding:4px 12px; border-radius:99px; font-size:11px; font-weight:700;
              cursor:pointer; border:1px solid #1e2d3d; color:#475569;
              background:transparent; letter-spacing:.03em; transition:all .15s; }
    .ov-tab.active { border-color:#38bdf8; color:#38bdf8; background:rgba(56,189,248,0.08); }
    .stat-bar { display:grid; grid-template-columns:repeat(6,1fr); gap:8px; margin:1rem 0; }
    .stat-item { background:#0d1117; border:1px solid #1e2d3d; border-radius:10px;
                 padding:10px 12px; }
    .stat-lbl { font-size:9px; font-weight:700; color:#334155; text-transform:uppercase;
                letter-spacing:.08em; margin-bottom:3px; }
    .stat-val { font-size:14px; font-weight:700; color:#e2e8f0; font-family:monospace; }
    </style>""", unsafe_allow_html=True)

    if not symbols:
        st.markdown("""
    <div style="background:#0c1a0c;border:1px solid #166534;border-radius:10px;
         padding:12px 18px;margin-bottom:1rem;display:flex;align-items:center;gap:12px">
      <span style="font-size:20px">📡</span>
      <div>
        <div style="font-size:13px;font-weight:700;color:#4ade80">Connecting to GSE API…</div>
        <div style="font-size:11px;color:#334155;margin-top:3px">
          Run the app locally once during GSE market hours (10:00–15:00 GMT),
          then push <code>gse_history.csv</code> to GitHub — cloud app loads from that file.
          <b>Click Refresh data to retry.</b></div>
      </div>
    </div>""", unsafe_allow_html=True)

    # ── Controls in sidebar ───────────────────────────────────────────────────
    with st.sidebar:
        st.divider()
        st.markdown('<div style="font-size:10px;font-weight:600;color:#475569;text-transform:uppercase;letter-spacing:.08em;margin-bottom:8px">Chart</div>', unsafe_allow_html=True)
        default_ac = st.session_state.get("selected_symbol", symbols[0])
        default_ac_idx = symbols.index(default_ac) if default_ac in symbols else 0
        ac_symbol  = st.selectbox("Symbol", symbols, index=default_ac_idx, key="ac_sym",
            format_func=lambda s: f"{s}  {_GSE_NAMES.get(s,s)[:18]}")
        ac_type    = st.radio("Chart type", ["Line","Area","Candlestick"],
            horizontal=True, key="ac_type", label_visibility="collapsed")
        st.markdown('<div style="font-size:10px;color:#475569;margin:8px 0 4px">Overlays</div>', unsafe_allow_html=True)
        show_bb    = st.checkbox("Bollinger Bands", value=True,  key="ac_bb")
        show_sma20 = st.checkbox("SMA 20",          value=False, key="ac_sma20")
        show_sma50 = st.checkbox("SMA 50",          value=False, key="ac_sma50")
        show_ema   = st.checkbox("EMA 12/26",       value=False, key="ac_ema")
        st.markdown('<div style="font-size:10px;color:#475569;margin:8px 0 4px">Indicators</div>', unsafe_allow_html=True)
        show_vol   = st.checkbox("Volume",   value=True,  key="ac_vol")
        show_rsi   = st.checkbox("RSI (14)", value=True,  key="ac_rsi")
        show_macd  = st.checkbox("MACD",     value=True,  key="ac_macd")

    # Period selector (Robinhood-style tabs)
    ac_period = st.radio("Period", ["1W","1M","3M","6M","1Y","YTD","All"],
        horizontal=True, index=3, key="ac_per", label_visibility="collapsed")

    hist = get_history(ac_symbol)
    if not hist.empty:
        hist = add_indicators(hist)
        period_map = {"1W":7,"1M":30,"3M":90,"6M":180,"1Y":365,"YTD":365,"All":99999}
        hist = hist.tail(period_map.get(ac_period, 180)).reset_index(drop=True)

    live_row   = df_live[df_live["symbol"] == ac_symbol]
    curr_name  = _GSE_NAMES.get(ac_symbol, ac_symbol)
    curr_price = float(live_row["price"].values[0])  if not live_row.empty else None
    curr_chg   = float(live_row["change"].values[0]) if not live_row.empty else 0.0
    chg_col    = "#4ade80" if curr_chg >= 0 else "#f87171"
    chg_bg     = "rgba(34,197,94,0.12)" if curr_chg >= 0 else "rgba(239,68,68,0.12)"
    chg_arrow  = "▲" if curr_chg >= 0 else "▼"
    logo_uri   = _load_logo_b64(ac_symbol)

    # ── Robinhood-style header ─────────────────────────────────────────────────
    logo_html = f'<img src="{logo_uri}" style="width:52px;height:52px;object-fit:contain;border-radius:12px;background:#0d1117;padding:4px;border:1px solid #1e2d3d">' if logo_uri else f'<div style="width:52px;height:52px;border-radius:12px;background:#0c2a4a;display:flex;align-items:center;justify-content:center;font-size:18px;font-weight:900;color:#38bdf8">{ac_symbol[:2]}</div>'

    st.markdown(f"""
    <div style="display:flex;align-items:flex-start;gap:18px;margin-bottom:.5rem">
      {logo_html}
      <div>
        <div style="font-size:13px;font-weight:600;color:#475569;letter-spacing:.5px">{ac_symbol} &nbsp;·&nbsp; {curr_name}</div>
        <div class="rh-price">GH₵ {f"{curr_price:.2f}" if curr_price else "—"}</div>
        <span style="background:{chg_bg};color:{chg_col};font-size:13px;font-weight:700;
            padding:4px 12px;border-radius:99px;display:inline-flex;align-items:center;gap:5px;margin-top:6px">
          {chg_arrow} {"+" if curr_chg>=0 else ""}{curr_chg:.2f}% today
        </span>
        <div style="font-size:11px;color:#334155;margin-top:6px">
          {"● MARKET OPEN" if market_is_open() else "● Market closed"} &nbsp;·&nbsp; {datetime.now(timezone.utc).strftime("%d %b %Y %H:%M GMT")}
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    # ── Stats bar ─────────────────────────────────────────────────────────────
    if not hist.empty:
        rsi_val  = hist["RSI"].dropna().iloc[-1]  if not hist["RSI"].dropna().empty   else None
        macd_val = hist["MACD"].dropna().iloc[-1] if not hist["MACD"].dropna().empty  else None
        sig_val  = hist["Signal"].dropna().iloc[-1] if not hist["Signal"].dropna().empty else None
        hi52 = hist["price"].max(); lo52 = hist["price"].min()
        avg_vol = int(hist["volume"].mean())
        prange  = ((curr_price - lo52)/(hi52-lo52)*100) if (curr_price and hi52!=lo52) else 50
        ms      = "Bullish" if (macd_val and sig_val and macd_val > sig_val) else "Bearish"
        ms_col  = "#4ade80" if ms=="Bullish" else "#f87171"
        rsi_col = "#f87171" if (rsi_val and rsi_val>70) else "#4ade80" if (rsi_val and rsi_val<30) else "#e2e8f0"
        period_ret = ((hist["price"].iloc[-1]-hist["price"].iloc[0])/hist["price"].iloc[0]*100) if len(hist)>1 else 0
        ret_col = "#4ade80" if period_ret>=0 else "#f87171"

        st.markdown(f"""
        <div class="stat-bar">
          <div class="stat-item"><div class="stat-lbl">Period high</div>
            <div class="stat-val">GH₵ {hi52:.2f}</div></div>
          <div class="stat-item"><div class="stat-lbl">Period low</div>
            <div class="stat-val">GH₵ {lo52:.2f}</div></div>
          <div class="stat-item"><div class="stat-lbl">Period return</div>
            <div class="stat-val" style="color:{ret_col}">{"+" if period_ret>=0 else ""}{period_ret:.2f}%</div></div>
          <div class="stat-item"><div class="stat-lbl">Avg volume</div>
            <div class="stat-val">{avg_vol:,}</div></div>
          <div class="stat-item"><div class="stat-lbl">RSI (14)</div>
            <div class="stat-val" style="color:{rsi_col}">{f"{rsi_val:.1f}" if rsi_val else "—"}</div></div>
          <div class="stat-item"><div class="stat-lbl">MACD signal</div>
            <div class="stat-val" style="color:{ms_col}">{ms}</div></div>
        </div>""", unsafe_allow_html=True)

    if hist.empty:
        st.info("No historical data yet — data builds daily when the app runs during market hours.")
        st.stop()

    # ── Build chart ───────────────────────────────────────────────────────────
    n_rows = 1 + (1 if show_rsi else 0) + (1 if show_macd else 0)
    heights = [0.60]
    titles  = [""]
    if show_rsi:  heights.append(0.20); titles.append("RSI (14)")
    if show_macd: heights.append(0.20); titles.append("MACD")
    total = sum(heights)
    heights = [h/total for h in heights]

    fig = make_subplots(rows=n_rows, cols=1, shared_xaxes=True,
        row_heights=heights, vertical_spacing=0.02, subplot_titles=titles)

    # Main chart — Robinhood green area by default
    line_color = "#4ade80" if (len(hist)>1 and hist["price"].iloc[-1] >= hist["price"].iloc[0]) else "#f87171"
    fill_color = "rgba(34,197,94,0.08)" if line_color=="#4ade80" else "rgba(239,68,68,0.08)"

    if ac_type == "Candlestick" and "open" in hist.columns:
        fig.add_trace(go.Candlestick(x=hist["date"],
            open=hist.get("open", hist["price"]), high=hist.get("high", hist["price"]),
            low=hist.get("low", hist["price"]),   close=hist["price"],
            increasing=dict(line_color="#4ade80", fillcolor="rgba(34,197,94,0.7)"),
            decreasing=dict(line_color="#f87171", fillcolor="rgba(239,68,68,0.7)"),
            name="OHLC"), row=1, col=1)
    elif ac_type == "Area":
        fig.add_trace(go.Scatter(x=hist["date"], y=hist["price"], name="Price",
            fill="tozeroy", fillcolor=fill_color,
            line=dict(color=line_color, width=2.5)), row=1, col=1)
    else:  # Line (default — Robinhood style)
        fig.add_trace(go.Scatter(x=hist["date"], y=hist["price"], name="Price",
            fill="tozeroy", fillcolor=fill_color,
            line=dict(color=line_color, width=2.5, shape="spline", smoothing=0.5),
            hovertemplate="GH₵ %{y:.2f}<extra></extra>"), row=1, col=1)

    # Bollinger Bands
    if show_bb and "BB_Upper" in hist.columns:
        for band, name in [("BB_Upper","BB+"), ("BB_Lower","BB-")]:
            fig.add_trace(go.Scatter(x=hist["date"], y=hist[band], name=name,
                line=dict(color="rgba(71,85,105,0.5)", width=1, dash="dot"),
                showlegend=(name=="BB+")), row=1, col=1)
        fig.add_trace(go.Scatter(x=hist["date"], y=hist["BB_Lower"],
            fill="tonexty", fillcolor="rgba(71,85,105,0.05)",
            line=dict(width=0), showlegend=False), row=1, col=1)

    if show_sma20 and "BB_Mid" in hist.columns:
        fig.add_trace(go.Scatter(x=hist["date"], y=hist["BB_Mid"], name="SMA 20",
            line=dict(color="#fbbf24", width=1.5, dash="dot")), row=1, col=1)
    if show_sma50 and "SMA50" in hist.columns:
        fig.add_trace(go.Scatter(x=hist["date"], y=hist["SMA50"], name="SMA 50",
            line=dict(color="#fb923c", width=1.5, dash="dot")), row=1, col=1)
    if show_ema:
        ema12 = hist["price"].ewm(span=12, adjust=False).mean()
        ema26 = hist["price"].ewm(span=26, adjust=False).mean()
        fig.add_trace(go.Scatter(x=hist["date"], y=ema12, name="EMA 12",
            line=dict(color="#a78bfa", width=1.5)), row=1, col=1)
        fig.add_trace(go.Scatter(x=hist["date"], y=ema26, name="EMA 26",
            line=dict(color="#f472b6", width=1.5)), row=1, col=1)

    # Volume bars (colour-matched to price direction per bar)
    if show_vol:
        vol_colors = [line_color if i==0 else
            ("#4ade80" if hist["price"].iloc[i] >= hist["price"].iloc[i-1] else "#f87171")
            for i in range(len(hist))]
        fig.add_trace(go.Bar(x=hist["date"], y=hist["volume"],
            name="Volume", marker_color=vol_colors, opacity=0.35,
            yaxis="y2"), row=1, col=1)

    # RSI row
    rsi_row = 2 if show_rsi else None
    if show_rsi:
        fig.add_trace(go.Scatter(x=hist["date"], y=hist["RSI"], name="RSI",
            line=dict(color="#a78bfa", width=1.8)), row=rsi_row, col=1)
        fig.add_hrect(y0=70, y1=100, fillcolor="rgba(239,68,68,0.04)", line_width=0,
            row=rsi_row, col=1)
        fig.add_hrect(y0=0,  y1=30,  fillcolor="rgba(34,197,94,0.04)", line_width=0,
            row=rsi_row, col=1)
        for lvl, col in [(70,"#f87171"),(50,"#334155"),(30,"#4ade80")]:
            fig.add_hline(y=lvl, line_dash="dot", line_color=col, opacity=0.4,
                row=rsi_row, col=1)

    # MACD row
    macd_row = (3 if show_rsi else 2) if show_macd else None
    if show_macd:
        fig.add_trace(go.Scatter(x=hist["date"], y=hist["MACD"], name="MACD",
            line=dict(color="#38bdf8", width=1.8)), row=macd_row, col=1)
        fig.add_trace(go.Scatter(x=hist["date"], y=hist["Signal"], name="Signal",
            line=dict(color="#fbbf24", width=1.8)), row=macd_row, col=1)
        hc = ["#4ade80" if v>=0 else "#f87171" for v in hist["MACD_Hist"].fillna(0)]
        fig.add_trace(go.Bar(x=hist["date"], y=hist["MACD_Hist"],
            name="Histogram", marker_color=hc, opacity=0.6), row=macd_row, col=1)

    # ── Layout — clean Robinhood-style ────────────────────────────────────────
    fig.update_layout(
        height=620, margin=dict(l=0, r=0, t=10, b=0),
        plot_bgcolor="#080c16", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#475569", family="monospace", size=11),
        hovermode="x unified",
        xaxis_rangeslider_visible=False,
        legend=dict(orientation="h", yanchor="bottom", y=1.01,
            bgcolor="rgba(0,0,0,0)", font=dict(color="#475569", size=10)),
        hoverlabel=dict(bgcolor="#0d1117", bordercolor="#1e2d3d",
            font=dict(color="#e2e8f0", size=12)),
    )
    # Axis styling — minimal gridlines like Robinhood
    for i in range(1, n_rows+1):
        fig.update_yaxes(row=i, col=1,
            showgrid=True, gridcolor="rgba(30,45,61,0.6)", gridwidth=1,
            zeroline=False, showline=False,
            tickfont=dict(color="#334155", size=10),
            tickformat=".2f")
        fig.update_xaxes(row=i, col=1,
            showgrid=False, zeroline=False, showline=False,
            tickfont=dict(color="#334155", size=10))

    st.plotly_chart(fig, use_container_width=True, config={
        "displayModeBar": True,
        "displaylogo": False,
        "modeBarButtonsToRemove": ["select2d","lasso2d","autoScale2d"],
        "modeBarButtonsToAdd": ["drawline","drawopenpath","eraseshape"],
        "toImageButtonOptions": {"format":"png","filename":f"GSE_{ac_symbol}_{ac_period}"},
    })

    # ── RSI interpretation banner ────────────────────────────────────────────
    if not hist.empty and "RSI" in hist.columns:
        rsi_vals = hist["RSI"].dropna()
        if not rsi_vals.empty:
            rv = rsi_vals.iloc[-1]
            if rv > 70:
                st.markdown(f'<div style="background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.3);border-radius:10px;padding:12px 16px;font-size:13px;color:#f87171">⚠️ <b>RSI {rv:.1f}</b> — Overbought. Price may be due for a pullback.</div>', unsafe_allow_html=True)
            elif rv < 30:
                st.markdown(f'<div style="background:rgba(34,197,94,0.08);border:1px solid rgba(34,197,94,0.3);border-radius:10px;padding:12px 16px;font-size:13px;color:#4ade80">✅ <b>RSI {rv:.1f}</b> — Oversold. Potential accumulation zone.</div>', unsafe_allow_html=True)

    # ── Raw data ─────────────────────────────────────────────────────────────
    with st.expander("📋 Raw data"):
        raw = hist[["date","price","volume","RSI","MACD","Signal"]].copy()
        raw["date"] = raw["date"].dt.strftime("%Y-%m-%d")
        for c in ["price","RSI","MACD","Signal"]:
            raw[c] = raw[c].map(lambda x: f"{x:.4f}" if pd.notna(x) else "—")
        raw["volume"] = raw["volume"].map(lambda x: f"{int(x):,}" if pd.notna(x) else "—")
        st.dataframe(raw.iloc[::-1], use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: DAILY MARKET REVIEW  (BlackStar-style)
# ═══════════════════════════════════════════════════════════════════════════════

elif page == "Market Review":

    today_str = datetime.now(timezone.utc).strftime("%d %b %Y")

    st.markdown(f"""
    <style>
    .mr-header{{display:flex;align-items:center;justify-content:space-between;
        padding:20px 24px;background:#0d1117;border:1px solid #1e2d3d;
        border-radius:14px;margin-bottom:1.25rem}}
    .mr-title{{font-size:22px;font-weight:800;color:#f1f5f9;letter-spacing:-.3px}}
    .mr-date {{font-size:14px;color:#475569;margin-top:3px}}
    .mr-brand{{font-size:13px;font-weight:700;color:#38bdf8;letter-spacing:.5px}}
    .mr-section{{font-size:10px;font-weight:800;color:#38bdf8;text-transform:uppercase;
        letter-spacing:.14em;margin:1.5rem 0 .75rem;display:flex;align-items:center;gap:10px}}
    .mr-section::before{{content:"";width:3px;height:14px;background:#38bdf8;border-radius:2px}}
    .mr-section::after{{content:"";flex:1;height:1px;background:linear-gradient(90deg,#1e2d3d,transparent)}}
    .mover-table{{width:100%;border-collapse:collapse;font-size:13px}}
    .mover-table th{{padding:9px 14px;text-align:left;font-size:10px;font-weight:700;
        color:#475569;text-transform:uppercase;letter-spacing:.06em;
        border-bottom:1px solid #1e2d3d;background:#111827}}
    .mover-table td{{padding:10px 14px;border-bottom:1px solid #0d1117;color:#e2e8f0}}
    .mover-table tr:hover td{{background:#111827}}
    .mover-table tr:last-child td{{border-bottom:none}}
    .idx-card{{background:#0d1117;border:1px solid #1e2d3d;border-radius:12px;
        padding:16px 20px;text-align:center;position:relative;overflow:hidden}}
    .idx-card::before{{content:"";position:absolute;top:0;left:0;right:0;height:2px;
        background:linear-gradient(90deg,#22c55e,#16a34a)}}
    .idx-lbl{{font-size:10px;font-weight:700;color:#475569;text-transform:uppercase;
        letter-spacing:.08em;margin-bottom:6px}}
    .idx-val{{font-size:24px;font-weight:800;color:#4ade80;font-family:monospace}}
    .idx-sub{{font-size:11px;color:#334155;margin-top:4px}}
    </style>
    <div class="mr-header">
      <div style="display:flex;align-items:center;gap:14px">
        <div style="width:44px;height:44px;flex-shrink:0">{_B360_MARK_ONLY}</div>
        <div>
          <div class="mr-title">Daily Equity Market Review</div>
          <div class="mr-date">{today_str} &nbsp;·&nbsp; Ghana Stock Exchange</div>
        </div>
      </div>
      <div style="text-align:right">
        <div style="font-size:15px;font-weight:900;color:#38bdf8;
             font-family:Arial Black,sans-serif;letter-spacing:-.2px">
          Bourse<span style="color:#f1f5f9">360</span></div>
        <div style="font-size:10px;color:#334155;margin-top:2px">BismarkDataLab Inc</div>
      </div>
    </div>""", unsafe_allow_html=True)

    if df_live.empty:
        st.markdown("""
    <div style="background:#0c1a0c;border:1px solid #166534;border-radius:10px;
         padding:12px 18px;margin-bottom:1rem;display:flex;align-items:center;gap:12px">
      <span style="font-size:20px">📡</span>
      <div>
        <div style="font-size:13px;font-weight:700;color:#4ade80">Connecting to GSE API…</div>
        <div style="font-size:11px;color:#334155;margin-top:3px">
          Run the app locally once during GSE market hours (10:00–15:00 GMT),
          then push <code>gse_history.csv</code> to GitHub — cloud app loads from that file.
          <b>Click Refresh data to retry.</b></div>
      </div>
    </div>""", unsafe_allow_html=True)

    summary = market_summary(df_live)
    total_vol = summary.get("total_volume", 0)
    vol_bn    = df_live["price"].mul(df_live["volume"]).sum()

    # ── Market standings ───────────────────────────────────────────────────────
    st.markdown('<div class="mr-section">Market standings</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    mktcap_label = "243.85bn"  # Static until API provides it
    c1.markdown(f"""<div class="idx-card" style="border-top-color:#38bdf8">
        <div class="idx-lbl">Market Cap (GHS)</div>
        <div class="idx-val" style="color:#38bdf8">{mktcap_label}</div>
        <div class="idx-sub">Total market capitalisation</div></div>""", unsafe_allow_html=True)
    c2.markdown(f"""<div class="idx-card" style="border-top-color:#a78bfa">
        <div class="idx-lbl">Volume Traded</div>
        <div class="idx-val" style="color:#a78bfa">{total_vol/1e6:.2f}M</div>
        <div class="idx-sub">Shares traded today</div></div>""", unsafe_allow_html=True)
    c3.markdown(f"""<div class="idx-card" style="border-top-color:#fbbf24">
        <div class="idx-lbl">Value Traded (GHS)</div>
        <div class="idx-val" style="color:#fbbf24">{vol_bn/1e6:.2f}M</div>
        <div class="idx-sub">Market turnover</div></div>""", unsafe_allow_html=True)
    c4.markdown(f"""<div class="idx-card">
        <div class="idx-lbl">Advancers / Decliners</div>
        <div class="idx-val"><span style="color:#4ade80">{summary["gainers"]}</span>
          <span style="color:#334155;font-size:16px"> / </span>
          <span style="color:#f87171">{summary["losers"]}</span></div>
        <div class="idx-sub">{summary["unchanged"]} unchanged</div></div>""", unsafe_allow_html=True)

    # ── Day-end market movers ──────────────────────────────────────────────────
    st.markdown('<div class="mr-section">Day-end market movers</div>', unsafe_allow_html=True)

    movers = df_live[df_live["change"] != 0].copy()
    movers["prev_price"] = movers["price"] / (1 + movers["change"]/100)
    movers["price_chg"]  = movers["price"] - movers["prev_price"]
    movers = movers.sort_values("change", key=abs, ascending=False).head(12)

    rows_html = ""
    for _, r in movers.iterrows():
        sym   = str(r["symbol"])
        name  = _GSE_NAMES.get(sym, sym)
        prev  = r["prev_price"]
        close = r["price"]
        pchg  = r["price_chg"]
        pchg_pct = r["change"]
        col   = "#4ade80" if pchg >= 0 else "#f87171"
        arrow = "▲" if pchg >= 0 else "▼"
        logo  = _load_logo_b64(sym)
        av_html = f'<img src="{logo}" style="width:26px;height:26px;object-fit:contain;border-radius:5px;background:#0d1117;padding:2px">' if logo else f'<div style="width:26px;height:26px;border-radius:5px;background:#0c2a4a;display:flex;align-items:center;justify-content:center;font-size:9px;font-weight:900;color:#38bdf8">{sym[:2]}</div>'
        rows_html += f"""<tr>
          <td><div style="display:flex;align-items:center;gap:8px">{av_html}
            <div><div style="font-weight:700;color:#f1f5f9">{sym}</div>
            <div style="font-size:10px;color:#475569">{name[:28]}</div></div></div></td>
          <td style="font-family:monospace;color:#94a3b8">GH₵ {prev:.2f}</td>
          <td style="font-family:monospace;font-weight:700;color:#e2e8f0">GH₵ {close:.2f}</td>
          <td style="font-family:monospace;color:{col}">{arrow} {abs(pchg):.2f}</td>
          <td><span style="background:{"rgba(34,197,94,0.1)" if pchg>=0 else "rgba(239,68,68,0.1)"};
              color:{col};padding:3px 8px;border-radius:99px;font-size:12px;font-weight:700;
              font-family:monospace">{arrow} {abs(pchg_pct):.2f}%</span></td>
          <td style="font-family:monospace;color:#475569">{int(r["volume"]):,}</td>
        </tr>"""

    st.markdown(f"""
    <div style="border:1px solid #1e2d3d;border-radius:14px;overflow:hidden">
    <table class="mover-table">
      <thead><tr>
        <th>Ticker</th><th>Prev close</th><th>Close price</th>
        <th>Price chg</th><th>Chg %</th><th>Volume</th>
      </tr></thead>
      <tbody>{rows_html}</tbody>
    </table></div>""", unsafe_allow_html=True)

    # ── Top 5 Volume & Value ───────────────────────────────────────────────────
    st.markdown('<div class="mr-section">Volume & value leaders</div>', unsafe_allow_html=True)
    col_v, col_val = st.columns(2)

    top_vol = df_live.nlargest(5, "volume")[["symbol","price","volume"]].copy()
    top_val = df_live.copy()
    top_val["value"] = top_val["price"] * top_val["volume"]
    top_val = top_val.nlargest(5, "value")[["symbol","price","volume","value"]]

    with col_v:
        st.markdown("**Top 5 volume traded**")
        max_vol = top_vol["volume"].max()
        for _, r in top_vol.iterrows():
            sym = str(r["symbol"])
            pct = r["volume"] / max_vol
            logo = _load_logo_b64(sym)
            av = f'<img src="{logo}" style="width:22px;height:22px;object-fit:contain;border-radius:4px">' if logo else f'<div style="width:22px;height:22px;border-radius:4px;background:#0c2a4a;display:flex;align-items:center;justify-content:center;font-size:8px;font-weight:900;color:#38bdf8">{sym[:2]}</div>'
            chg_r = df_live[df_live["symbol"]==sym]
            chg_v = float(chg_r["change"].values[0]) if not chg_r.empty else 0
            bar_c = "#4ade80" if chg_v >= 0 else "#f87171"
            vol_str = f"{int(r['volume'])/1000:.1f}K" if r["volume"]>=1000 else str(int(r["volume"]))
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">
              {av}
              <div style="flex:1">
                <div style="display:flex;justify-content:space-between;margin-bottom:3px">
                  <span style="font-size:12px;font-weight:700;color:#e2e8f0">{sym}</span>
                  <span style="font-size:11px;color:#94a3b8;font-family:monospace">{vol_str}</span>
                </div>
                <div style="height:5px;background:#1e2d3d;border-radius:3px">
                  <div style="width:{pct*100:.0f}%;height:5px;background:{bar_c};border-radius:3px"></div>
                </div>
              </div>
            </div>""", unsafe_allow_html=True)

    with col_val:
        st.markdown("**Top 5 value traded (GHS)**")
        max_val = top_val["value"].max()
        for _, r in top_val.iterrows():
            sym = str(r["symbol"])
            pct = r["value"] / max_val
            logo = _load_logo_b64(sym)
            av = f'<img src="{logo}" style="width:22px;height:22px;object-fit:contain;border-radius:4px">' if logo else f'<div style="width:22px;height:22px;border-radius:4px;background:#0c2a4a;display:flex;align-items:center;justify-content:center;font-size:8px;font-weight:900;color:#38bdf8">{sym[:2]}</div>'
            val_str = f"GH₵ {r['value']/1e6:.2f}M" if r["value"]>=1e6 else f"GH₵ {r['value']/1e3:.1f}K"
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">
              {av}
              <div style="flex:1">
                <div style="display:flex;justify-content:space-between;margin-bottom:3px">
                  <span style="font-size:12px;font-weight:700;color:#e2e8f0">{sym}</span>
                  <span style="font-size:11px;color:#94a3b8;font-family:monospace">{val_str}</span>
                </div>
                <div style="height:5px;background:#1e2d3d;border-radius:3px">
                  <div style="width:{pct*100:.0f}%;height:5px;background:#38bdf8;border-radius:3px"></div>
                </div>
              </div>
            </div>""", unsafe_allow_html=True)

    # ── YTD performance area chart ─────────────────────────────────────────────
    st.markdown('<div class="mr-section">YTD market performance</div>', unsafe_allow_html=True)
    csv_hist = load_historical_comparison("MTNGH")
    if not csv_hist.empty and len(csv_hist) > 5:
        all_syms = df_live["symbol"].tolist()
        fin_syms = [s for s in all_syms if _GSE_COMPANIES.get(s,{}).get("sector")=="Financials"]
        nonfin_syms = [s for s in all_syms if _GSE_COMPANIES.get(s,{}).get("sector")!="Financials"]

        fig_ytd = go.Figure()
        fig_ytd.add_trace(go.Scatter(x=csv_hist["date"], y=csv_hist["price"],
            fill="tozeroy", fillcolor="rgba(234,179,8,0.15)",
            line=dict(color="#eab308", width=2), name="Sample (MTNGH)"))
        fig_ytd.update_layout(
            height=240, margin=dict(l=0,r=0,t=10,b=0),
            plot_bgcolor="#080c16", paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False, tickfont=dict(color="#334155", size=10)),
            yaxis=dict(showgrid=True, gridcolor="#1e2d3d", tickfont=dict(color="#334155", size=10)),
            legend=dict(font=dict(color="#475569", size=10), bgcolor="rgba(0,0,0,0)"),
            hovermode="x unified",
        )
        st.plotly_chart(fig_ytd, use_container_width=True)
    else:
        st.markdown('<div style="background:#0d1117;border:1px solid #1e2d3d;border-radius:12px;padding:20px;text-align:center;color:#334155;font-size:13px">YTD chart builds as daily snapshots accumulate in gse_history.csv</div>', unsafe_allow_html=True)

    # ── Footer ─────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="margin-top:2rem;padding:14px 0;border-top:1px solid #1e2d3d;
         font-size:11px;color:#334155;line-height:1.6">
      <i>Sources: Ghana Stock Exchange, dev.kwayisi.org/apis/gse · Compiled by BismarkDataLab Inc</i><br>
      <i>The information has been compiled from sources we believe to be reliable but do not hold ourselves
      responsible for its completeness or accuracy. Not investment advice.</i>
    </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: MARKET HEATMAP
# ═══════════════════════════════════════════════════════════════════════════════

elif page == "Heatmap":

    st.markdown("""
    <style>
    .hm-cell{border-radius:10px;padding:12px 8px;text-align:center;cursor:pointer;
        transition:transform .15s,filter .15s;position:relative;overflow:hidden}
    .hm-cell:hover{transform:scale(1.04);filter:brightness(1.2)}
    .hm-sym{font-size:13px;font-weight:800;color:#f1f5f9;margin-bottom:4px}
    .hm-chg{font-size:12px;font-weight:700;font-family:monospace}
    .hm-price{font-size:10px;color:rgba(255,255,255,0.55);margin-top:3px}
    .hm-vol{font-size:9px;color:rgba(255,255,255,0.35);margin-top:1px}
    .hm-legend{display:flex;align-items:center;gap:8px;font-size:11px;color:#475569}
    .hm-lswatch{width:14px;height:14px;border-radius:3px;flex-shrink:0}
    </style>""", unsafe_allow_html=True)

    st.markdown("### 🟩 Market heatmap")
    st.caption("Block size = trading volume · Colour intensity = % change")

    if df_live.empty:
        st.markdown("""
    <div style="background:#0c1a0c;border:1px solid #166534;border-radius:10px;
         padding:12px 18px;margin-bottom:1rem;display:flex;align-items:center;gap:12px">
      <span style="font-size:20px">📡</span>
      <div>
        <div style="font-size:13px;font-weight:700;color:#4ade80">Connecting to GSE API…</div>
        <div style="font-size:11px;color:#334155;margin-top:3px">
          Run the app locally once during GSE market hours (10:00–15:00 GMT),
          then push <code>gse_history.csv</code> to GitHub — cloud app loads from that file.
          <b>Click Refresh data to retry.</b></div>
      </div>
    </div>""", unsafe_allow_html=True)

    df_hm = df_live.copy()
    df_hm["name"] = df_hm.apply(
        lambda r: _GSE_NAMES.get(str(r["symbol"]), str(r["name"])), axis=1)
    df_hm["sector"] = df_hm["symbol"].map(SECTOR_MAP).fillna("Other")
    df_hm["chg"] = df_hm["change"].fillna(0).astype(float)
    df_hm["vol"] = df_hm["volume"].fillna(0).astype(int)

    # Legend
    st.markdown("""
    <div class="hm-legend" style="margin-bottom:1rem">
      <div class="hm-lswatch" style="background:#16a34a"></div><span>Strong gain</span>
      <div class="hm-lswatch" style="background:#4ade80"></div><span>Gain</span>
      <div class="hm-lswatch" style="background:#1e2d3d"></div><span>Unchanged</span>
      <div class="hm-lswatch" style="background:#f87171"></div><span>Loss</span>
      <div class="hm-lswatch" style="background:#991b1b"></div><span>Strong loss</span>
      <span style="margin-left:12px">Larger block = higher volume</span>
    </div>""", unsafe_allow_html=True)

    # Sector groupings
    sector_order = ["Financials","Telecoms","Oil & Gas","Mining",
                    "Consumer Goods","Agribusiness","Manufacturing",
                    "Healthcare","Insurance","Real Estate","Other"]

    for sector in sector_order:
        stocks = df_hm[df_hm["sector"] == sector]
        if stocks.empty:
            continue

        st.markdown(f'<div style="font-size:10px;font-weight:800;color:#475569;'
                    f'text-transform:uppercase;letter-spacing:.12em;margin:1rem 0 .4rem">'
                    f'{sector}</div>', unsafe_allow_html=True)

        # Dynamic columns — more volume = wider cell (approximate with col count)
        n = len(stocks)
        ncols = min(n, 6)
        cols = st.columns([1]*ncols)

        for ci, (_, row) in enumerate(stocks.sort_values("chg", ascending=False).iterrows()):
            sym  = str(row["symbol"])
            chg  = float(row["chg"])
            pr   = float(row["price"])
            vol  = int(row["vol"])

            # Colour based on intensity
            if   chg >= 5:   bg = "#14532d"; tc = "#4ade80"
            elif chg >= 2:   bg = "#166534"; tc = "#86efac"
            elif chg > 0:    bg = "#052e16"; tc = "#4ade80"
            elif chg == 0:   bg = "#1e2d3d"; tc = "#64748b"
            elif chg > -2:   bg = "#3b0000"; tc = "#f87171"
            elif chg > -5:   bg = "#7f1d1d"; tc = "#fca5a5"
            else:            bg = "#450a0a"; tc = "#fecaca"

            sign = "+" if chg >= 0 else ""
            vol_str = f"{vol/1000:.0f}K" if vol >= 1000 else str(vol)

            with cols[ci % ncols]:
                st.markdown(f"""
                <div class="hm-cell" style="background:{bg}">
                  <div class="hm-sym">{sym}</div>
                  <div class="hm-chg" style="color:{tc}">{sign}{chg:.2f}%</div>
                  <div class="hm-price">GH₵ {pr:.2f}</div>
                  <div class="hm-vol">{vol_str}</div>
                </div>""", unsafe_allow_html=True)
                if st.button("", key=f"hm_{sym}", help=f"View {_GSE_NAMES.get(sym,sym)}"):
                    st.session_state["selected_symbol"] = sym
                    st.session_state.page = "Stock Detail"
                    st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: AI SIGNAL PANEL
# ═══════════════════════════════════════════════════════════════════════════════

elif page == "AI Signals":

    st.markdown("""
    <style>
    .sig-table{width:100%;border-collapse:collapse}
    .sig-table th{padding:10px 16px;font-size:10px;font-weight:700;color:#475569;
        text-transform:uppercase;letter-spacing:.08em;border-bottom:1px solid #1e2d3d;
        background:#111827;text-align:left}
    .sig-table td{padding:11px 16px;border-bottom:1px solid #0d1117;font-size:13px;color:#e2e8f0}
    .sig-table tr:hover td{background:#111827}
    .sig-pill{display:inline-block;padding:3px 12px;border-radius:99px;font-size:11px;font-weight:800;letter-spacing:.5px}
    .conf-bar-bg{height:6px;background:#1e2d3d;border-radius:3px;width:80px;display:inline-block;vertical-align:middle;margin-left:8px}
    .conf-bar{height:6px;border-radius:3px}
    </style>""", unsafe_allow_html=True)

    st.markdown("### 🤖 AI signal panel")
    st.caption("Composite signals from RSI · MACD · Momentum · SMA — updated each session")

    if df_live.empty:
        st.markdown("""
    <div style="background:#0c1a0c;border:1px solid #166534;border-radius:10px;
         padding:12px 18px;margin-bottom:1rem;display:flex;align-items:center;gap:12px">
      <span style="font-size:20px">📡</span>
      <div>
        <div style="font-size:13px;font-weight:700;color:#4ade80">Connecting to GSE API…</div>
        <div style="font-size:11px;color:#334155;margin-top:3px">
          Run the app locally once during GSE market hours (10:00–15:00 GMT),
          then push <code>gse_history.csv</code> to GitHub — cloud app loads from that file.
          <b>Click Refresh data to retry.</b></div>
      </div>
    </div>""", unsafe_allow_html=True)

    # Compute signals for all stocks with a spinner
    with st.spinner("Computing signals for all equities…"):
        signal_rows = []
        for _, row in df_live.iterrows():
            sym  = str(row["symbol"])
            name = _GSE_NAMES.get(sym, str(row["name"]))
            a    = compute_stock_analytics(sym)
            if a["signal"] == "HOLD" and a["signal_score"] == 0:
                continue  # skip stocks with no data
            signal_rows.append({
                "symbol":    sym,
                "name":      name,
                "price":     float(row["price"]),
                "change":    float(row["change"]),
                "signal":    a["signal"],
                "score":     a["signal_score"],
                "rsi":       a["rsi_signal"],
                "macd":      a["macd_signal"],
                "momentum":  a["momentum_5d"],
                "volatility":a["volatility"],
                "ytd":       a["ytd_return"],
            })

    if not signal_rows:
        st.info("Not enough historical data yet to generate signals. Run the app daily during market hours to build history.")
        st.stop()

    
    sig_df = pd.DataFrame(signal_rows).sort_values("score", ascending=False)

    # Summary counts
    counts = sig_df["signal"].value_counts()
    sc1,sc2,sc3,sc4,sc5 = st.columns(5)
    for col, sig, color in [
        (sc1,"STRONG BUY","#4ade80"), (sc2,"BUY","#86efac"),
        (sc3,"HOLD","#94a3b8"),       (sc4,"SELL","#fca5a5"),
        (sc5,"STRONG SELL","#f87171")
    ]:
        col.metric(sig, counts.get(sig, 0))

    st.divider()

    # Filter controls
    f1, f2 = st.columns([2,3])
    sig_filter = f1.multiselect("Filter signals",
        ["STRONG BUY","BUY","HOLD","SELL","STRONG SELL"],
        default=["STRONG BUY","BUY","HOLD","SELL","STRONG SELL"])
    search_sig = f2.text_input("Search symbol", "", placeholder="e.g. GCB",
        label_visibility="collapsed")

    filtered = sig_df[sig_df["signal"].isin(sig_filter)]
    if search_sig:
        filtered = filtered[filtered["symbol"].str.upper().str.contains(search_sig.upper())]

    # Build HTML table
    SIG_STYLE = {
        "STRONG BUY":  ("rgba(34,197,94,0.15)",  "#4ade80",  "●●●●●"),
        "BUY":         ("rgba(34,197,94,0.08)",   "#86efac",  "●●●●○"),
        "HOLD":        ("rgba(71,85,105,0.15)",   "#94a3b8",  "●●●○○"),
        "SELL":        ("rgba(239,68,68,0.08)",   "#fca5a5",  "●●○○○"),
        "STRONG SELL": ("rgba(239,68,68,0.15)",   "#f87171",  "●○○○○"),
    }

    rows_html = ""
    for _, r in filtered.iterrows():
        sym  = r["symbol"]
        sig  = r["signal"]
        sbg, sfg, sdots = SIG_STYLE.get(sig, ("rgba(71,85,105,0.1)","#94a3b8","●●●○○"))
        conf = min(abs(int(r["score"])) * 20 + 40, 95)
        chg  = float(r["change"])
        chg_c= "#4ade80" if chg >= 0 else "#f87171"
        ytd  = r["ytd"]
        ytd_str = (("+" if ytd >= 0 else "") + f"{ytd:.1f}%") if ytd is not None else "—"
        ytd_c = "#4ade80" if (ytd and ytd >= 0) else "#f87171" if ytd else "#475569"
        vol_str = f"{r['volatility']:.1f}%" if r["volatility"] else "—"
        logo = _load_logo_b64(sym)
        av = (f'<img src="{logo}" style="width:28px;height:28px;object-fit:contain;'
              f'border-radius:6px;background:#0d1117;padding:2px;vertical-align:middle;margin-right:8px">'
              if logo else
              f'<span style="display:inline-flex;width:28px;height:28px;border-radius:6px;'
              f'background:#0c2a4a;align-items:center;justify-content:center;font-size:10px;'
              f'font-weight:900;color:#38bdf8;margin-right:8px;vertical-align:middle">{sym[:2]}</span>')

        rows_html += f"""
        <tr>
          <td>{av}<b style="color:#f1f5f9">{sym}</b><br>
              <span style="font-size:10px;color:#475569">{r['name'][:24]}</span></td>
          <td style="font-family:monospace">GH₵ {r['price']:.2f}</td>
          <td style="color:{chg_c};font-family:monospace">{"+" if chg>=0 else ""}{chg:.2f}%</td>
          <td>
            <span class="sig-pill" style="background:{sbg};color:{sfg}">{sig}</span>
          </td>
          <td>
            <span style="font-size:12px;color:#475569;font-family:monospace">{conf}%</span>
            <div class="conf-bar-bg"><div class="conf-bar" style="width:{conf}%;background:{sfg}"></div></div>
          </td>
          <td style="color:{ytd_c};font-family:monospace">{ytd_str}</td>
          <td style="color:#fbbf24;font-family:monospace">{vol_str}</td>
          <td style="font-size:11px;color:#475569">{r['rsi']}</td>
          <td style="font-size:11px;color:#475569">{r['macd']}</td>
        </tr>"""

    st.markdown(f"""
    <div style="border:1px solid #1e2d3d;border-radius:14px;overflow:hidden">
    <table class="sig-table">
      <thead><tr>
        <th>Company</th><th>Price</th><th>Today</th>
        <th>Signal</th><th>Confidence</th>
        <th>YTD</th><th>Volatility</th><th>RSI</th><th>MACD</th>
      </tr></thead>
      <tbody>{rows_html}</tbody>
    </table></div>""", unsafe_allow_html=True)

    st.markdown("""
    <div style="font-size:10px;color:#334155;margin-top:10px;font-style:italic">
    Signals are generated from technical indicators only (RSI, MACD, momentum, SMA).
    Not financial advice. Always conduct your own research before investing.</div>""",
    unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: PORTFOLIO SIMULATOR
# ═══════════════════════════════════════════════════════════════════════════════

elif page == "Portfolio Simulator":

    st.markdown("""
    <style>
    .sim-result{background:#0d1117;border:1px solid #1e2d3d;border-radius:14px;padding:20px}
    .sim-big{font-size:36px;font-weight:900;font-family:monospace;line-height:1}
    .sim-lbl{font-size:10px;font-weight:700;color:#475569;text-transform:uppercase;
        letter-spacing:.08em;margin-bottom:6px}
    .sim-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:1rem}
    .sim-card{background:#111827;border:1px solid #1e2d3d;border-radius:10px;padding:14px}
    .sim-timeline{background:#0d1117;border:1px solid #1e2d3d;border-radius:12px;
        padding:16px;margin-top:1rem}
    </style>""", unsafe_allow_html=True)

    st.markdown("### 💰 Portfolio simulator")
    st.caption("Simulate historical returns for any GSE stock")

    if not symbols:
        st.markdown("""
    <div style="background:#0c1a0c;border:1px solid #166534;border-radius:10px;
         padding:12px 18px;margin-bottom:1rem;display:flex;align-items:center;gap:12px">
      <span style="font-size:20px">📡</span>
      <div>
        <div style="font-size:13px;font-weight:700;color:#4ade80">Connecting to GSE API…</div>
        <div style="font-size:11px;color:#334155;margin-top:3px">
          Run the app locally once during GSE market hours (10:00–15:00 GMT),
          then push <code>gse_history.csv</code> to GitHub — cloud app loads from that file.
          <b>Click Refresh data to retry.</b></div>
      </div>
    </div>""", unsafe_allow_html=True)

    # ── Input form ─────────────────────────────────────────────────────────────
    with st.container():
        c1, c2, c3, c4 = st.columns([3,2,2,1])
        default_s = st.session_state.get("selected_symbol", symbols[0])
        sim_sym   = c1.selectbox("Stock", symbols,
            index=symbols.index(default_s) if default_s in symbols else 0,
            format_func=lambda s: f"{s}  —  {_GSE_NAMES.get(s,s)}")
        sim_amount = c2.number_input("Investment (GH₵)", min_value=100.0,
            max_value=10_000_000.0, value=10_000.0, step=500.0, format="%.2f")
        sim_period = c3.selectbox("Holding period",
            ["All available","1Y","6M","3M","1M"], index=0)
        run_sim = c4.button("Simulate", use_container_width=True, type="primary")

    if run_sim or st.session_state.get("sim_result"):
        hist = load_historical_comparison(sim_sym)

        if hist.empty or len(hist) < 3:
            st.warning("Not enough history for this stock yet. Data builds daily when the app runs during market hours.")
        else:
            # Period filter
            period_days = {"1Y":365,"6M":180,"3M":90,"1M":30,"All available":99999}
            days = period_days.get(sim_period, 99999)
            hist = hist.tail(days).reset_index(drop=True)

            buy_price   = float(hist["price"].iloc[0])
            sell_price  = float(hist["price"].iloc[-1])
            shares      = sim_amount / buy_price if buy_price > 0 else 0
            current_val = shares * sell_price
            total_ret   = current_val - sim_amount
            ret_pct     = (total_ret / sim_amount * 100) if sim_amount > 0 else 0

            # Analytics
            prices       = hist["price"]
            daily_rets   = prices.pct_change().dropna()
            volatility   = float(daily_rets.std() * (252**0.5) * 100) if len(daily_rets) > 1 else 0
            sharpe       = float((daily_rets.mean()*252) / (daily_rets.std()*(252**0.5))) if (len(daily_rets)>1 and daily_rets.std()>0) else 0
            max_price    = float(prices.max())
            min_price    = float(prices.min())
            max_drawdown = float((prices.min() - prices.max()) / prices.max() * 100) if prices.max() > 0 else 0
            best_day     = float(daily_rets.max() * 100) if len(daily_rets) > 0 else 0
            worst_day    = float(daily_rets.min() * 100) if len(daily_rets) > 0 else 0
            days_tracked = len(hist)
            # Estimated dividend (approx 2% annual yield for Ghana stocks)
            est_dividend = sim_amount * 0.02 * (days_tracked / 365)

            ret_color = "#4ade80" if total_ret >= 0 else "#f87171"
            ret_arrow = "▲" if total_ret >= 0 else "▼"
            logo = _load_logo_b64(sim_sym)
            co_name = _GSE_NAMES.get(sim_sym, sim_sym)

            # ── Result header ──────────────────────────────────────────────────
            logo_html = (f'<img src="{logo}" style="width:52px;height:52px;'
                        f'object-fit:contain;border-radius:12px;background:#0d1117;'
                        f'padding:4px;border:1px solid #1e2d3d">' if logo else
                        f'<div style="width:52px;height:52px;border-radius:12px;'
                        f'background:#0c2a4a;display:flex;align-items:center;'
                        f'justify-content:center;font-size:18px;font-weight:900;'
                        f'color:#38bdf8">{sim_sym[:2]}</div>')

            st.markdown(f"""
            <div class="sim-result" style="margin-top:1rem">
              <div style="display:flex;align-items:center;gap:16px;margin-bottom:1.25rem">
                {logo_html}
                <div>
                  <div style="font-size:13px;color:#475569">{sim_sym} · {co_name}</div>
                  <div style="font-size:12px;color:#334155">
                    GH₵ {buy_price:.2f} → GH₵ {sell_price:.2f}
                    &nbsp;·&nbsp; {days_tracked} trading days
                    &nbsp;·&nbsp; {shares:,.0f} shares
                  </div>
                </div>
              </div>

              <div class="sim-grid">
                <div class="sim-card">
                  <div class="sim-lbl">Current value</div>
                  <div class="sim-big" style="color:#38bdf8">GH₵ {current_val:,.2f}</div>
                  <div style="font-size:11px;color:#334155;margin-top:4px">
                    from GH₵ {sim_amount:,.2f} invested</div>
                </div>
                <div class="sim-card">
                  <div class="sim-lbl">Total return</div>
                  <div class="sim-big" style="color:{ret_color}">
                    {ret_arrow} GH₵ {abs(total_ret):,.2f}</div>
                  <div style="font-size:14px;color:{ret_color};font-weight:700;margin-top:4px">
                    {"+" if ret_pct>=0 else ""}{ret_pct:.2f}%</div>
                </div>
                <div class="sim-card">
                  <div class="sim-lbl">Est. dividends</div>
                  <div class="sim-big" style="color:#fbbf24">GH₵ {est_dividend:,.2f}</div>
                  <div style="font-size:11px;color:#334155;margin-top:4px">
                    ~2% annual yield estimate</div>
                </div>
                <div class="sim-card">
                  <div class="sim-lbl">Volatility (ann.)</div>
                  <div class="sim-big" style="color:#a78bfa">{volatility:.1f}%</div>
                  <div style="font-size:11px;color:#334155;margin-top:4px">
                    Sharpe ratio: {sharpe:.2f}</div>
                </div>
              </div>

              <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px">
                <div style="background:#111827;border-radius:8px;padding:10px 12px">
                  <div class="sim-lbl">Max drawdown</div>
                  <div style="font-size:16px;font-weight:700;color:#f87171;font-family:monospace">
                    {max_drawdown:.2f}%</div>
                </div>
                <div style="background:#111827;border-radius:8px;padding:10px 12px">
                  <div class="sim-lbl">Best single day</div>
                  <div style="font-size:16px;font-weight:700;color:#4ade80;font-family:monospace">
                    +{best_day:.2f}%</div>
                </div>
                <div style="background:#111827;border-radius:8px;padding:10px 12px">
                  <div class="sim-lbl">Worst single day</div>
                  <div style="font-size:16px;font-weight:700;color:#f87171;font-family:monospace">
                    {worst_day:.2f}%</div>
                </div>
                <div style="background:#111827;border-radius:8px;padding:10px 12px">
                  <div class="sim-lbl">52-week range</div>
                  <div style="font-size:13px;font-weight:700;color:#e2e8f0;font-family:monospace">
                    {min_price:.2f} – {max_price:.2f}</div>
                </div>
              </div>
            </div>""", unsafe_allow_html=True)

            # ── Price chart ────────────────────────────────────────────────────
            
            fig_sim = go.Figure()
            portfolio_vals = [sim_amount * (p / buy_price) for p in hist["price"]]
            line_color = "#4ade80" if ret_pct >= 0 else "#f87171"
            fill_color = "rgba(34,197,94,0.08)" if ret_pct >= 0 else "rgba(239,68,68,0.08)"

            fig_sim.add_trace(go.Scatter(
                x=hist["date"], y=portfolio_vals,
                fill="tozeroy", fillcolor=fill_color,
                line=dict(color=line_color, width=2.5, shape="spline"),
                name="Portfolio value",
                hovertemplate="GH₵ %{y:,.2f}<extra></extra>",
            ))
            fig_sim.add_hline(y=sim_amount, line_dash="dot",
                line_color="#475569", opacity=0.5,
                annotation_text="Invested", annotation_font_color="#475569")

            fig_sim.update_layout(
                height=280, margin=dict(l=0,r=0,t=20,b=0),
                plot_bgcolor="#080c16", paper_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(showgrid=False, tickfont=dict(color="#334155", size=10)),
                yaxis=dict(showgrid=True, gridcolor="#1e2d3d",
                           tickprefix="GH₵ ", tickfont=dict(color="#334155", size=10)),
                hovermode="x unified",
                hoverlabel=dict(bgcolor="#0d1117", bordercolor="#1e2d3d",
                               font=dict(color="#e2e8f0")),
                legend=dict(font=dict(color="#475569"), bgcolor="rgba(0,0,0,0)"),
            )
            st.plotly_chart(fig_sim, use_container_width=True)

            # ── Verdict ────────────────────────────────────────────────────────
            if ret_pct >= 20:
                verdict = f"🔥 Excellent return of +{ret_pct:.1f}%. This investment significantly outperformed."
                vcolor  = "#4ade80"
            elif ret_pct >= 5:
                verdict = f"✅ Good return of +{ret_pct:.1f}%. Solid positive performance."
                vcolor  = "#86efac"
            elif ret_pct >= -5:
                verdict = f"⚖️ Modest performance of {ret_pct:.1f}%. Roughly flat over this period."
                vcolor  = "#94a3b8"
            else:
                verdict = f"⚠️ Negative return of {ret_pct:.1f}%. Position currently underwater."
                vcolor  = "#f87171"

            st.markdown(f"""
            <div style="background:#0d1117;border:1px solid #1e2d3d;border-radius:12px;
                 padding:14px 18px;margin-top:.75rem">
              <div style="font-size:13px;color:{vcolor}">{verdict}</div>
              <div style="font-size:11px;color:#334155;margin-top:4px;font-style:italic">
                Note: Past performance does not guarantee future results.
                Dividend estimate uses 2% annual yield approximation.
                Not financial advice.</div>
            </div>""", unsafe_allow_html=True)
