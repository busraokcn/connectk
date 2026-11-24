import csv
import matplotlib.pyplot as plt

from pathlib import Path


Path("grafikler").mkdir(exist_ok=True)


def read_csv(filename):

    with open(
        filename,
        "r",
        encoding="utf-8-sig"
    ) as file:

        return list(csv.DictReader(file))


def grouped_graph(
    labels, first, second,
    first_name, second_name,
    title, ylabel, filename
):

    plt.figure(figsize=(10, 5))

    x = list(range(len(labels)))
    width = 0.35

    bars1 = plt.bar(
        [i - width / 2 for i in x],
        first,
        width,
        label=first_name,
        color="#64748b"
    )

    bars2 = plt.bar(
        [i + width / 2 for i in x],
        second,
        width,
        label=second_name,
        color="#16a34a"
    )

    plt.bar_label(
        bars1, fmt="%.2f", fontsize=8
    )

    plt.bar_label(
        bars2, fmt="%.2f", fontsize=8
    )

    plt.xticks(x, labels)

    plt.title(title)
    plt.ylabel(ylabel)

    plt.ylim(
        0,
        max(first + second) * 1.25
    )

    plt.legend()
    plt.grid(axis="y", alpha=0.2)
    plt.tight_layout()

    plt.savefig(
        f"grafikler/{filename}",
        dpi=300
    )

    plt.close()

    print(f"grafikler/{filename}")


# ==========================================
# 1. ZOBRIST PERFORMANSI
# ==========================================

rows = read_csv("zobrist_performans.csv")

grouped_graph(
    [f"V{r['Varyant']}" for r in rows],

    [float(r["Tam Hash (us)"]) for r in rows],

    [float(r["Artimli Hash (us)"]) for r in rows],

    "Tam hash",
    "Artımlı hash",

    "Zobrist Hash Performansı",

    "Süre (mikrosaniye)",

    "zobrist_performans.png"
)


# ==========================================
# 2. TT DERINLIK KARSILASTIRMASI
# ==========================================

rows = read_csv(
    "tt_performans_sonuclar.csv"
)

off = sorted(
    [r for r in rows if r["TT"] == "KAPALI"],
    key=lambda r: int(r["Konum"])
)

on = sorted(
    [r for r in rows if r["TT"] == "ACIK"],
    key=lambda r: int(r["Konum"])
)

grouped_graph(
    [r["Konum"] for r in off],

    [int(r["Derinlik"]) for r in off],

    [int(r["Derinlik"]) for r in on],

    "TT kapalı",
    "TT açık",

    "Bir Saniyelik Aramada TT Etkisi",

    "Tamamlanan derinlik",

    "tt_derinlik.png"
)


# ==========================================
# 3. UFUK ETKISI VE TEHDIT UZATMA
# ==========================================

rows = read_csv(
    "tehdit_uzatma_sonuclar.csv"
)

normal = [
    r for r in rows
    if r["Yontem"] == "Normal"
]

extended = [
    r for r in rows
    if r["Yontem"] == "Tehdit Uzatma"
]

grouped_graph(
    [r["Derinlik"] for r in normal],

    [int(r["Dugum"]) for r in normal],

    [int(r["Dugum"]) for r in extended],

    "Normal arama",
    "Tehdit uzatma",

    "Tehdit Uzatmanın Düğüm Maliyeti",

    "Düğüm sayısı",

    "tehdit_uzatma.png"
)


# ==========================================
# 4. SON PERFORMANS KARSILASTIRMASI
# ==========================================

rows = read_csv(
    "son_performans_sonuclar.csv"
)

normal = sorted(
    [r for r in rows if r["Yontem"] == "Normal TT"],
    key=lambda r: int(r["Konum"])
)

extended = sorted(
    [r for r in rows if r["Yontem"] == "Tehdit Uzatma"],
    key=lambda r: int(r["Konum"])
)

grouped_graph(
    [r["Konum"] for r in normal],

    [int(r["Derinlik"]) for r in normal],

    [int(r["Derinlik"]) for r in extended],

    "Normal TT",
    "Tehdit uzatma",

    "Son Performans - Arama Derinlikleri",

    "Tamamlanan derinlik",

    "son_performans.png"
)


print("\nAsama 4 grafikleri basariyla olusturuldu!")