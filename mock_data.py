import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

random.seed(42)
np.random.seed(42)

brands = ["Lenovo", "HP", "Dell", "Asus", "Acer", "Samsung", "Microsoft"]
domains = ["amazon.it", "amazon.de", "amazon.fr", "amazon.es"]
segments = ["Laptop", "Tablet", "Monitor", "Accessori", "Desktop"]
sellers = ["Amazon", "MediaWorld", "Unieuro", "TechStore", "other"]
keywords = [
    "laptop 15 pollici", "notebook gaming", "laptop ufficio",
    "ultrabook sottile", "laptop economico", "notebook studenti",
    "laptop professionale", "tablet windows", "monitor 4k", "pc portatile"
]

def generate_asin():
    return "B0" + "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=8))

asins = [generate_asin() for _ in range(100)]
brand_map = {}
for asin in asins:
    if random.random() < 0.25:
        brand_map[asin] = "Lenovo"
    else:
        brand_map[asin] = random.choice([b for b in brands if b != "Lenovo"])

scan_dates = [
    datetime(2024, 1, 15),
    datetime(2024, 4, 10),
    datetime(2024, 7, 22),
    datetime(2024, 10, 5),
    datetime(2025, 1, 18),
    datetime(2025, 3, 12),
]

rows = []
for asin in asins:
    brand = brand_map[asin]
    domain = random.choice(domains)
    segment = random.choice(segments)
    keyword = random.choice(keywords)
    seller = random.choice(sellers)
    base_price = round(random.uniform(199, 1899), 2)
    base_position = random.randint(1, 55)
    base_rating = round(random.uniform(3.0, 5.0), 1)
    base_ratings_total = random.randint(10, 5000)
    base_images = random.randint(3, 10)
    base_title_length = random.randint(40, 200)
    base_desc_length = random.randint(200, 2000)
    base_bullet_count = random.randint(3, 7)
    base_bullet_length = random.randint(100, 600)
    base_aplus = random.choice([0, 1])
    base_sponsored = random.choice([0, 1])
    search_freq = random.randint(1, 100)
    search_vol = random.randint(1000, 500000)

    prev_images = base_images
    prev_title_length = base_title_length
    prev_aplus = base_aplus

    for i, scan_date in enumerate(scan_dates):
        position = max(1, base_position + random.randint(-5, 5))
        price = round(base_price * random.uniform(0.9, 1.1), 2)
        rating = min(5.0, max(1.0, round(base_rating + random.uniform(-0.2, 0.2), 1)))
        ratings_total = base_ratings_total + i * random.randint(0, 100)

        if i > 0 and random.random() < 0.15:
            images = prev_images + random.choice([-1, 1, 2])
            images = max(1, images)
        else:
            images = prev_images

        if i > 0 and random.random() < 0.12:
            title_length = prev_title_length + random.randint(-30, 50)
            title_length = max(20, title_length)
        else:
            title_length = prev_title_length

        if i > 0 and random.random() < 0.10:
            aplus = 1 - prev_aplus
        else:
            aplus = prev_aplus

        rows.append({
            "asin_prodotto": asin,
            "nome_brand": brand,
            "dominio": domain,
            "segmento_categoria": segment,
            "posizione": position,
            "range_posizione": "1-4" if position <= 4 else ("5-8" if position <= 8 else "9-60"),
            "posizione_avg": base_position,
            "posizione_best": max(1, base_position - 5),
            "sponsorizzato": base_sponsored,
            "ricerca": keyword,
            "titolo": f"{brand} {segment} {asin[:6]}",
            "owner_competitor": "LENOVO" if brand == "Lenovo" else "competitor",
            "prezzo": price,
            "venditore": seller,
            "rating": rating,
            "rating_totali": ratings_total,
            "n_immagini": images,
            "n_video": random.randint(0, 3),
            "lunghezza_titolo": title_length,
            "lunghezza_descrizione": base_desc_length,
            "n_bullet_points": base_bullet_count,
            "lunghezza_bullet_points": base_bullet_length,
            "conto_brand": random.choice(["1-4", "5-9", "10-29", "30-99", "100+"]),
            "search_frequency": search_freq,
            "search_volume": search_vol,
            "presenza_a_plus": aplus,
            "data_scansione": scan_date,
            "anno_scansione": str(scan_date.year),
        })

        prev_images = images
        prev_title_length = title_length
        prev_aplus = aplus

df = pd.DataFrame(rows)

def get_mock_data():
    return df.copy()
