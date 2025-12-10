import csv
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE = "https://www.dominanz.rs"
START_URL = BASE + "/sr/services/tuning"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; DominanzScraper/1.0)"
}

session = requests.Session()
session.headers.update(HEADERS)


def get_soup(url: str) -> BeautifulSoup:
    resp = session.get(url, timeout=20)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")


def parse_mapping_info(card):
    mapped = total = percent = None

    row = card.find("div", class_="flex justify-between text-sm")
    if row:
        spans = row.find_all("span")
        if len(spans) >= 2:
            ratio_text = spans[-1].get_text(strip=True)
            if "/" in ratio_text:
                left, right = ratio_text.split("/", 1)
                mapped = left.strip()
                total = right.strip()

    badge = card.find("span", string=lambda t: t and "%" in t and "Dostupno" in t)
    if badge:
        percent = badge.get_text(strip=True).split()[0]

    return mapped, total, percent


def scrape_brands():
    """Sa /sr/services/tuning pokupi sve marke."""
    soup = get_soup(START_URL)
    brands = []

    for card in soup.select("div.flex.flex-col.relative.overflow-hidden"):
        name_el = card.select_one("h3.text-lg.font-semibold")
        subtitle_el = card.select_one("p.text-sm")
        if not name_el or not subtitle_el:
            continue

        # marka ima logo (img alt="Audi logo", "Alfa Romeo logo", itd.)
        img = card.select_one("img[alt$='logo']")
        if not img:
            continue

        brand_name = name_el.get_text(strip=True)
        models_count = subtitle_el.get_text(strip=True)
        mapped, total, percent = parse_mapping_info(card)

        a = card.find_parent("a", href=True)
        if not a:
            continue
        href = a["href"]
        if not href.startswith("/sr/services/tuning/"):
            continue

        brands.append(
            {
                "brand_name": brand_name,
                "brand_url": href,
                "brand_models_count": models_count,
                "brand_mapped": mapped,
                "brand_total": total,
                "brand_percent": percent,
            }
        )

    return brands


def scrape_models(brand_url: str):
    """Sa /sr/services/tuning/<brand> pokupi sve modele tog brenda."""
    url = urljoin(BASE, brand_url)
    soup = get_soup(url)
    models = []

    for card in soup.select("div.flex.flex-col.relative.overflow-hidden"):
        name_el = card.select_one("h3.text-lg.font-semibold")
        subtitle_el = card.select_one("p.text-sm")
        if not name_el or not subtitle_el:
            continue

        # preskoči karticu sa logom (na stranici brenda ima jedan logo gore)
        if card.select_one("img[alt$='logo']"):
            continue

        model_name = name_el.get_text(strip=True)
        model_info = subtitle_el.get_text(strip=True)
        mapped, total, percent = parse_mapping_info(card)

        a = card.find_parent("a", href=True)
        if not a:
            continue
        model_href = a["href"]

        models.append(
            {
                "model_name": model_name,
                "model_url": model_href,
                "model_info": model_info,
                "model_mapped": mapped,
                "model_total": total,
                "model_percent": percent,
            }
        )

    return models


def scrape_years(model_url: str):
    """Sa /sr/services/tuning/<brand>/<model> pokupi sve generacije/godine."""
    url = urljoin(BASE, model_url)
    soup = get_soup(url)
    years = []

    for a in soup.select('a[href^="/sr/services/tuning/"]'):
        href = a.get("href", "")
        if not href.startswith(model_url.rstrip("/")):
            continue

        card = a.select_one("div.flex.flex-col.relative.overflow-hidden")
        if not card:
            continue

        name_el = card.select_one("h3.text-lg.font-semibold")
        subtitle_el = card.select_one("p.text-sm")
        if not name_el or not subtitle_el:
            continue

        year_label = name_el.get_text(strip=True)
        year_info = subtitle_el.get_text(strip=True)
        mapped, total, percent = parse_mapping_info(card)

        years.append(
            {
                "year_label": year_label,
                "year_url": href,
                "year_info": year_info,
                "year_mapped": mapped,
                "year_total": total,
                "year_percent": percent,
            }
        )

    return years


def scrape_engines(year_url: str):
    """Sa /sr/services/tuning/<brand>/<model>/<year> pokupi sve motore (bez linkova)."""
    url = urljoin(BASE, year_url)
    soup = get_soup(url)
    engines = []

    cards = soup.select("section .grid > div.flex.flex-col.relative.overflow-hidden")
    for card in cards:
        name_el = card.select_one("h4.text-lg.font-semibold")
        if not name_el:
            continue
        engine_name = name_el.get_text(strip=True)

        stock_hp = tuned_hp = stock_nm = tuned_nm = None

        power_block = card.find("h4", string=lambda t: t and "Snaga" in t)
        if power_block:
            rows = power_block.find_all_next(
                "div", class_="flex justify-between text-sm", limit=2
            )
            for row in rows:
                spans = row.find_all("span")
                if len(spans) < 2:
                    continue
                label = spans[0].get_text(strip=True)
                val = spans[-1].get_text(strip=True)
                if "Fabrički" in label:
                    stock_hp = val
                elif "Mapiran" in label:
                    tuned_hp = val

        torque_block = card.find("h4", string=lambda t: t and "Obrtni moment" in t)
        if torque_block:
            rows = torque_block.find_all_next(
                "div", class_="flex justify-between text-sm", limit=2
            )
            for row in rows:
                spans = row.find_all("span")
                if len(spans) < 2:
                    continue
                label = spans[0].get_text(strip=True)
                val = spans[-1].get_text(strip=True)
                if "Fabrički" in label:
                    stock_nm = val
                elif "Mapiran" in label:
                    tuned_nm = val

        engines.append(
            {
                "engine_name": engine_name,
                "stock_hp": stock_hp,
                "tuned_hp": tuned_hp,
                "stock_nm": stock_nm,
                "tuned_nm": tuned_nm,
            }
        )

    return engines


def main():
    with open("dominanz_tuning_all.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "brand_name",
                "brand_url",
                "brand_models_count",
                "brand_mapped",
                "brand_total",
                "brand_percent",
                "model_name",
                "model_url",
                "model_info",
                "model_mapped",
                "model_total",
                "model_percent",
                "year_label",
                "year_url",
                "year_info",
                "year_mapped",
                "year_total",
                "year_percent",
                "engine_name",
                "stock_hp",
                "tuned_hp",
                "stock_nm",
                "tuned_nm",
            ]
        )

        brands = scrape_brands()
        print("Brendova:", len(brands))

        rows = 0
        for b in brands:
            print(f"\nBRAND: {b['brand_name']} ({b['brand_url']})")
            time.sleep(1)

            models = scrape_models(b["brand_url"])
            print("  Modela:", len(models))

            for m in models:
                print(f"  Model: {m['model_name']} ({m['model_url']})")
                time.sleep(0.5)

                years = scrape_years(m["model_url"])
                print("    Godina:", len(years))

                for y in years:
                    print(f"    Year: {y['year_label']} ({y['year_url']})")
                    time.sleep(0.5)

                    engines = scrape_engines(y["year_url"])
                    print("      Motora:", len(engines))

                    for e in engines:
                        w.writerow(
                            [
                                b["brand_name"],
                                urljoin(BASE, b["brand_url"]),
                                b["brand_models_count"],
                                b["brand_mapped"],
                                b["brand_total"],
                                b["brand_percent"],
                                m["model_name"],
                                urljoin(BASE, m["model_url"]),
                                m["model_info"],
                                m["model_mapped"],
                                m["model_total"],
                                m["model_percent"],
                                y["year_label"],
                                urljoin(BASE, y["year_url"]),
                                y["year_info"],
                                y["year_mapped"],
                                y["year_total"],
                                y["year_percent"],
                                e["engine_name"],
                                e["stock_hp"],
                                e["tuned_hp"],
                                e["stock_nm"],
                                e["tuned_nm"],
                            ]
                        )
                        rows += 1
        print("\nUkupno redova upisano:", rows)


if __name__ == "__main__":
    main()
