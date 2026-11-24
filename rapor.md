# Connect-K Arena Proje Raporu

**Ders:** Yapay Zekâ
**Öğrenci:** Büşra Okcan
**Öğrenci numarasının son iki hanesi:** 27

## Oyun Varyantı

- R = 5
- C = 6
- K = 5
- V = 1
- d = 27

(R, C, K, V, d) = (5, 6, 5, 1, 27)

Oyun varyantım silindir modelidir. Oyun tahtası
5 satır ve 6 sütundan oluşmaktadır. Kazanmak için
5 taşın yatay, dikey veya çapraz olarak dizilmesi
gerekmektedir. Tahtanın sağ ve sol kenarları
birbirine bağlıdır.

## Aşama 0: Oyun Modeli ve Perft
Oyun modeli iki boyutlu tuple veri yapısı
kullanılarak oluşturuldu. Her hamlede mevcut
tahtayı değiştirmek yerine yeni bir oyun durumu
oluşturuldu.

Silindir varyantında sütunların birbirine
bağlanması modulo işlemiyle sağlandı.
Kazanma kontrolünde son yerleştirilen taşın
yatay, dikey ve iki çapraz doğrultusu incelendi.

### Perft Ölçümleri

| Derinlik | Boş tahta | Dolu sütun | Kazanma konumu |
|---|---:|---:|---:|
| 1 | 6 | 5 | 6 |
| 2 | 36 | 25 | 31 |
| 3 | 216 | 125 | 175 |
| 4 | 1296 | 625 | 882 |
| 5 | 7776 | - | - |
| 6 | 46650 | - | - |

### Perft Çalışma Süreleri (ms)

| Derinlik | Boş tahta | Dolu sütun | Kazanma konumu |
|---|---:|---:|---:|
| 1 | 0.059 | 0.070 | 0.067 |
| 2 | 0.198 | 0.167 | 0.281 |
| 3 | 1.324 | 0.778 | 1.021 |
| 4 | 8.149 | 3.889 | 5.100 |
| 5 | 50.304 | - | - |
| 6 | 266.164 | - | - |

![Perft çalışma süreleri](grafikler/perft_sure.png)

### Sonuçların Değerlendirilmesi

Derinlik arttıkça yaprak sayısının ve çalışma
süresinin arttığı gözlemlendi.

İlk beş derinlikte boş tahta için beklenen
6 üzeri n değerleri elde edildi. Altıncı
derinlikte ise tahta 5 satırlı olduğu için
aynı sütuna altıncı taş yerleştirilemez.
Bu nedenle 46656 yerine 46650 yaprak elde edildi.

Dolu sütun bulunan konumda yasal hamle sayısı
azaldığı için daha az yaprak oluştu.
Kazanma konumunda ise terminal durumlarda
arama durdurulduğu için yaprak sayısı azaldı.

### Birim Testleri

Python unittest kütüphanesi kullanılarak
16 birim testi çalıştırıldı.

- Toplam test: 16
- Başarılı test: 16
- Başarısız test: 0
- Başarı oranı: %100
- Toplam test süresi: 0.335 saniye

Dört oyun varyantına ilişkin hazırlanan testler,
taş yerleştirme, kazanma, beraberlik, geçersiz
hamleler ve Perft kontrolleri başarılı oldu.

## Aşama 1: Minimax

## Aşama 2: Alfa-Beta Budaması ve Hamle Sıralaması

## Aşama 3: Değerlendirme Fonksiyonu ve Ağırlık Ayarı

## Aşama 4: Zaman Sınırlı Arama ve Ufuk Etkisi

## Aşama 5: Turnuva ve Yenilgi Analizi

## Sonuç