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