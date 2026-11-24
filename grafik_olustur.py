import matplotlib.pyplot as plt
from pathlib import Path


# Grafik klasörünü oluştur
Path("grafikler").mkdir(exist_ok=True)

# Kendi bilgisayarımda elde ettiğim Perft ölçümleri
depths_empty = [1, 2, 3, 4, 5, 6]
times_empty = [
    0.059, 0.198, 1.324,
    8.149, 50.304, 266.164
]

depths_other = [1, 2, 3, 4]

times_full = [
    0.070, 0.167, 0.778, 3.889
]

times_win = [
    0.067, 0.281, 1.021, 5.100
]

# Çalışma süresi grafiği
plt.figure(figsize=(9, 5))

plt.plot(
    depths_empty,
    times_empty,
    marker="o",
    label="Boş tahta"
)

plt.plot(
    depths_other,
    times_full,
    marker="s",
    label="Dolu sütun"
)

plt.plot(
    depths_other,
    times_win,
    marker="^",
    label="Kazanma konumu"
)

plt.title("Perft - Derinlik ve Çalışma Süresi")
plt.xlabel("Derinlik")
plt.ylabel("Çalışma süresi (ms)")
plt.xticks(depths_empty)
plt.yscale("log")
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()

plt.savefig(
    "grafikler/perft_sure.png",
    dpi=300
)

plt.close()


# Yaprak sayısı grafiği
nodes_empty = [6, 36, 216, 1296, 7776, 46650]
nodes_full = [5, 25, 125, 625]
nodes_win = [6, 31, 175, 882]

plt.figure(figsize=(9, 5))

plt.plot(
    depths_empty,
    nodes_empty,
    marker="o",
    label="Boş tahta"
)

plt.plot(
    depths_other,
    nodes_full,
    marker="s",
    label="Dolu sütun"
)

plt.plot(
    depths_other,
    nodes_win,
    marker="^",
    label="Kazanma konumu"
)

plt.title("Perft - Derinlik ve Yaprak Sayısı")
plt.xlabel("Derinlik")
plt.ylabel("Yaprak sayısı")
plt.xticks(depths_empty)
plt.yscale("log")
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()

plt.savefig(
    "grafikler/perft_yaprak.png",
    dpi=300
)

plt.close()

print("Grafikler basariyla olusturuldu!")
print("grafikler/perft_sure.png")
print("grafikler/perft_yaprak.png")

# ==========================================
# ASAMA 1 - MINIMAX GRAFIKLERI
# ==========================================

import csv


# Minimax ölçümlerini CSV dosyasından oku
with open(
    "minimax_sonuclar.csv",
    "r",
    encoding="utf-8-sig"
) as file:

    reader = csv.DictReader(file)
    minimax_results = list(reader)


# Konum isimlerini belirle
positions = list(dict.fromkeys(
    row["Konum"] for row in minimax_results
))


# 1. Grafik: Derinlik ve düğüm sayısı
plt.figure(figsize=(9, 5))

for position in positions:

    rows = [
        row for row in minimax_results
        if row["Konum"] == position
    ]

    depths = [
        int(row["Derinlik"]) for row in rows
    ]

    nodes = [
        int(row["Dugum Sayisi"]) for row in rows
    ]

    plt.plot(
        depths,
        nodes,
        marker="o",
        label=position
    )

plt.title("Minimax - Derinlik ve Düğüm Sayısı")
plt.xlabel("Arama derinliği")
plt.ylabel("Düğüm sayısı")
plt.xticks([2, 4, 6])
plt.yscale("log")
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()

plt.savefig(
    "grafikler/minimax_dugum.png",
    dpi=300
)

plt.close()


# 2. Grafik: Derinlik ve çalışma süresi
plt.figure(figsize=(9, 5))

for position in positions:

    rows = [
        row for row in minimax_results
        if row["Konum"] == position
    ]

    depths = [
        int(row["Derinlik"]) for row in rows
    ]

    times = [
        float(row["Sure (ms)"]) for row in rows
    ]

    plt.plot(
        depths,
        times,
        marker="o",
        label=position
    )

plt.title("Minimax - Derinlik ve Çalışma Süresi")
plt.xlabel("Arama derinliği")
plt.ylabel("Çalışma süresi (ms)")
plt.xticks([2, 4, 6])
plt.yscale("log")
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()

plt.savefig(
    "grafikler/minimax_sure.png",
    dpi=300
)

plt.close()


# 3. Grafik: Etkin dallanma çarpanı
plt.figure(figsize=(9, 5))

for position in positions:

    rows = [
        row for row in minimax_results
        if row["Konum"] == position
    ]

    depths = [
        int(row["Derinlik"]) for row in rows
    ]

    branching = [
        float(row["Etkin Dallanma Carpani"])
        for row in rows
    ]

    plt.plot(
        depths,
        branching,
        marker="o",
        label=position
    )

# Sütun sayısı için referans çizgisi
plt.axhline(
    y=6,
    linestyle="--",
    color="black",
    label="C = 6"
)

plt.title("Minimax - Etkin Dallanma Çarpanı")
plt.xlabel("Arama derinliği")
plt.ylabel("Etkin dallanma çarpanı")
plt.xticks([2, 4, 6])
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()

plt.savefig(
    "grafikler/minimax_dallanma.png",
    dpi=300
)

plt.close()

print("\nMinimax grafikleri olusturuldu!")
print("grafikler/minimax_dugum.png")
print("grafikler/minimax_sure.png")
print("grafikler/minimax_dallanma.png")