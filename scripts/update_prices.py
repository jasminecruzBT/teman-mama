"""Turn the government's PriceCatcher files into small JSON files for the prices page.

Usage:
    python scripts/update_prices.py <folder with the .parquet files>

The folder must contain lookup_item.parquet, lookup_premise.parquet and one or more
pricecatcher_YYYY-MM.parquet files, all from https://storage.data.gov.my/pricecatcher/
(open data from KPDN via data.gov.my).

Writes:
    site-data/prices-summary.json        typical prices per item for Malaysia / each state / each district
    site-data/shops/<state-slug>.json    the cheapest shops per item in each district
    site-data/districts.json             every state and district (used by the taska/tadika finder)
build.py copies site-data/ into the site.
"""
import glob
import json
import os
import re
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "site-data")

BABY_CATEGORIES = {"SUSU BAYI", "LAMPIN PAKAI BUANG", "MAKANAN BAYI"}
MUM_MILK = {336: "Anmum Materna", 843: "Anmum Lacta"}  # pregnancy / breastfeeding milk

# Clean display names (product names stay as sold in Malaysia).
NAMES = {
    299: "Lactogen 1", 300: "Lactogen 2", 303: "Enfagrow A+ Mind Pro 3 (vanilla)",
    1512: "Mamex 1", 1513: "Sustagen Kid 3+ (vanilla)", 1514: "Sustagen Junior 1+ (vanilla)",
    1623: "S-26 SMA 1", 1624: "S-26 Gold SMA 1", 1874: "Dutch Lady 123 (plain)",
    1904: "Dumex Dugro 3 (1-3 yrs)", 1956: "NAN PRO 1", 1957: "NAN PRO 2",
    1958: "NANKID OPTIPRO 3", 1961: "Anmum Essential 4 (tin)", 1963: "Anmum Essential 4 (box)",
    1965: "PediaSure (vanilla)", 2001: "Dumex Dupro 2", 2009: "Dutch Lady 123",
    2010: "Dutch Lady 456", 2014: "Enfagrow A+ Mind Pro 3", 2027: "NAN 1", 2030: "NAN 2",
    2031: "S-26 1", 2062: "S-26 SMA 1", 2097: "Sustagen All-in-One",
    2104: "Fernleaf 1-3 yrs", 2105: "Fernleaf 4-6 yrs",
    1522: "Drypers Wee Wee Dry", 1967: "PetPet Gold+", 1968: "Drypers Wee Wee Dry",
    1969: "Huggies Dry Diapers", 1970: "Diapex Easy", 1971: "Fitti", 1972: "MamyPoko Extra Dry",
    1973: "PetPet Day Night Pants", 1974: "Drypers Drypantz", 1975: "Huggies Dry Pants",
    2015: "PetPet Pants Gold+", 2032: "PetPet Gold+", 2042: "PetPet Pants Gold+",
    2098: "Drypers Wee Wee Dry", 2099: "Huggies Dry (tape)", 2100: "Drypers Drypantz",
    2101: "Huggies Dry Pants",
    1145: "Nestle Cerelac Rice (tin)", 1515: "Heinz Farley's Rusks", 1517: "Heinz Apple Puree",
    1628: "Nestle Cerelac Wheat & Honey", 1629: "Nestle Cerelac Brown Rice & Milk",
    1966: "Milna Rusks",
    **MUM_MILK,
}

MIN_SHOPS_NATIONAL = 20  # skip items that too few shops reported this month


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", str(s).lower()).strip("-")


def grams(unit):
    u = str(unit).lower().replace(" ", "")
    m = re.match(r"^([\d.]+)(kg|g)$", u)
    if not m:
        return None
    v = float(m.group(1))
    return round(v * 1000) if m.group(2) == "kg" else round(v)


def pieces_m(unit):
    """Pieces in the size-M pack, e.g. 'S80, M60, L58' -> 60, 'M74' -> 74."""
    m = re.search(r"\bM(\d+)", str(unit).upper())
    return int(m.group(1)) if m else None


def group_of(row):
    code, item, cat = row["item_code"], str(row["item"]).upper(), row["item_category"]
    if code in MUM_MILK:
        return "mum"
    if cat == "LAMPIN PAKAI BUANG":
        return "diaper"
    if cat == "MAKANAN BAYI":
        return "food"
    if "LANGKAH 1" in item or "RUMUSAN BAYI" in item:
        return "infant"
    if "LANGKAH 2" in item or "SUSULAN" in item:
        return "followon"
    return "growing"


def main(raw):
    items = pd.read_parquet(os.path.join(raw, "lookup_item.parquet"))
    prem = pd.read_parquet(os.path.join(raw, "lookup_premise.parquet"))
    files = sorted(glob.glob(os.path.join(raw, "pricecatcher_*.parquet")))
    if not files:
        sys.exit("no pricecatcher_*.parquet files in " + raw)
    prices = pd.concat([pd.read_parquet(f) for f in files], ignore_index=True)
    prices["date"] = pd.to_datetime(prices["date"])

    # Last 30 days of data only.
    end = prices["date"].max()
    prices = prices[prices["date"] >= end - pd.Timedelta(days=29)]
    start = prices["date"].min()

    want = items[items["item_category"].isin(BABY_CATEGORIES) | items["item_code"].isin(MUM_MILK)].copy()
    want["group"] = want.apply(group_of, axis=1)
    p = prices[prices["item_code"].isin(want["item_code"])]

    # Latest price per shop per item.
    p = p.sort_values("date").groupby(["premise_code", "item_code"], as_index=False).last()

    # Drop obvious typing errors: below half or above double the national median.
    med = p.groupby("item_code")["price"].transform("median")
    p = p[(p["price"] >= med * 0.5) & (p["price"] <= med * 2)]

    p = p.merge(prem, on="premise_code", how="left")
    p = p[p["state"].notna() & p["district"].notna()]

    counts = p.groupby("item_code")["premise_code"].nunique()
    keep = set(counts[counts >= MIN_SHOPS_NATIONAL].index)
    p = p[p["item_code"].isin(keep)]
    want = want[want["item_code"].isin(keep)]

    def stats(df):
        out = {}
        for code, g in df.groupby("item_code"):
            out[str(code)] = [round(float(g["price"].median()), 2),
                              round(float(g["price"].quantile(0.1)), 2),
                              int(g["premise_code"].nunique())]
        return out

    areas = {"MY": stats(p)}
    for st, g in p.groupby("state"):
        areas["S|" + st] = stats(g)
    for (st, di), g in p.groupby(["state", "district"]):
        areas["D|" + st + "|" + di] = stats(g)

    meta = {}
    for _, r in want.iterrows():
        code = int(r["item_code"])
        meta[str(code)] = {
            "n": NAMES.get(code, str(r["item"]).title()),
            "u": str(r["unit"]),
            "g": r["group"],
            "gr": grams(r["unit"]) if r["group"] != "diaper" else None,
            "pc": pieces_m(r["unit"]) if r["group"] == "diaper" else None,
            "t": ("pants" if re.search(r"PANT", str(r["item"]).upper()) else "tape") if r["group"] == "diaper" else None,
        }

    os.makedirs(os.path.join(OUT, "shops"), exist_ok=True)
    summary = {
        "from": start.strftime("%Y-%m-%d"),
        "to": end.strftime("%Y-%m-%d"),
        "shops": int(p["premise_code"].nunique()),
        "items": meta,
        "areas": areas,
    }
    with open(os.path.join(OUT, "prices-summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, separators=(",", ":"))

    # Cheapest 5 shops per item per district, one file per state.
    for f in glob.glob(os.path.join(OUT, "shops", "*.json")):
        os.remove(f)
    for st, g in p.groupby("state"):
        shops, dist = {}, {}
        for (di, code), h in g.groupby(["district", "item_code"]):
            top = h.nsmallest(5, "price")
            rows = []
            for _, r in top.iterrows():
                pc = str(int(r["premise_code"]))
                shops[pc] = [str(r["premise"]).strip(), str(r["premise_type"]).strip(), str(r["address"]).strip()]
                rows.append([pc, round(float(r["price"]), 2), r["date"].strftime("%Y-%m-%d")])
            dist.setdefault(di, {})[str(int(code))] = rows
        with open(os.path.join(OUT, "shops", slug(st) + ".json"), "w", encoding="utf-8") as f:
            json.dump({"p": shops, "d": dist}, f, ensure_ascii=False, separators=(",", ":"))

    allp = prem[prem["state"].notna() & prem["district"].notna()]
    districts = {st: sorted(g["district"].unique().tolist()) for st, g in allp.groupby("state")}
    with open(os.path.join(OUT, "districts.json"), "w", encoding="utf-8") as f:
        json.dump(districts, f, ensure_ascii=False, separators=(",", ":"))

    print(f"{len(meta)} items, {summary['shops']} shops, {summary['from']} to {summary['to']}, "
          f"{len(areas)} areas, {len(districts)} states")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
