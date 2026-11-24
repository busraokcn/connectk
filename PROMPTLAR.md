# Yapay Zekâ Kullanım Tutanağı

## 24.11.2026 - Hazırlık Aşaması

Kullanılan araç: ChatGPT

### İstek 1
Ödev föyünün incelenmesini ve projenin adım adım
nasıl yapılacağının açıklanmasını istedim.

Kullanılan kısım:
Proje geliştirme sırası ve yapılacak görevlerin
açıklamaları.

### İstek 2
Öğrenci numaramın son iki hanesi olan 27'ye göre
oyun varyantımın hesaplanmasını istedim.

Kullanılan kısım:
R=5, C=6, K=5, V=1, d=27 parametreleri.

### İstek 3
Proje dosyalarının oluşturulması, Git ayarlarının
yapılması ve rapor iskeletinin hazırlanması
konusunda yardım istedim.

Kullanılan kısım:
Terminal komutları, klasör yapısı, gitignore
dosyası, rapor ve kullanım tutanağı taslağı.
## Aşama 0 - Oyun Modeli

### İstek 4

Oyun tahtasının ve başlangıç durumunun nasıl
oluşturulacağı konusunda ChatGPT'den yardım aldım.

Kullanılan kısım:
State sınıfı, Game sınıfı, oyun parametreleri,
initial_state ve print_board fonksiyonlarının
kodları ve açıklamaları.

Veri yapısı olarak iki boyutlu tuple kullanıldı.
### İstek 5

Yasal hamlelerin belirlenmesi, taşların oyun
tahtasına yerleştirilmesi ve oyuncu sırasının
değiştirilmesi konusunda ChatGPT'den yardım aldım.

Kullanılan kısım:
_landing_row(), actions() ve result()
fonksiyonlarının kodları ve açıklamaları.

Dolu sütun kontrolü, orijinal tahtanın
değişmemesi ve taşların doğru konuma
yerleştirilmesi için test kodlarından yararlanıldı.

Kodların birleştirilmesinde eksiklik olabileceği
için game.py dosyasının güncel ve eksiksiz
hali tekrar istendi.

### İstek 6

Yatay, dikey, çapraz ve silindir varyantına
özel kazanma kontrolünün nasıl yapılacağı
konusunda ChatGPT'den yardım aldım.

Kullanılan kısım:
line_player() ve state_from_moves()
fonksiyonlarının kodları, modulo işleminin
açıklaması ve kazanma kontrolü test kodları.

### İstek 7

Oyunun bitiş durumunun kontrol edilmesi ve
fayda değerinin hesaplanması konusunda
ChatGPT'den yardım aldım.

Kullanılan kısım:
is_terminal() ve utility() fonksiyonlarının
kodları ve açıklamaları.

actions() ve result() fonksiyonları terminal
durumlara uygun şekilde güncellendi.

MAX ve MIN kazanması, Misere varyantı,
beraberlik ve oyun bittikten sonra hamle
yapılmaması için hazırlanan test kodları
ve örnek hamle dizileri kullanıldı.
### İstek 8

Perft algoritmasının oluşturulması ve oyun
modelinin doğruluğunun ölçülmesi konusunda
ChatGPT'den yardım aldım.

Kullanılan kısım:
perft() ve measure_perft() fonksiyonlarının
kodları ve açıklamaları.

Boş tahta, dolu sütun, bir hamlede kazanma
ve terminal durum için test kodları kullanıldı.

5 satırlı oyun tahtasında derinlik 6 için
Perft değerinin neden 46650 olması gerektiği
incelendi.

Performans ölçümleri kendi bilgisayarımda
program çalıştırılarak elde edildi.
### İstek 9

Oyun modelinin doğruluğunu kontrol etmek için
birim testlerinin hazırlanması konusunda
ChatGPT'den yardım aldım.

Kullanılan kısım:
unittest kütüphanesinin kullanımı,
tests klasörünün düzenlenmesi ve
test_game.py dosyasındaki 16 birim
testinin kodları ve açıklamaları.

Yatay, dikey, çapraz, silindir, Misere,
engelli varyant, beraberlik, geçersiz
hamleler ve Perft durumları için
testlerden yararlanıldı.
### İstek 10

Perft ölçümlerinin raporlanması, grafiklerin
oluşturulması ve birim testi sonuçlarının
yorumlanması konusunda ChatGPT'den yardım aldım.

Kullanılan kısım:
Rapor metni, ölçüm tabloları, Matplotlib
kurulum komutları ve grafik_olustur.py
dosyasının kodları.

Tablolarda ve grafiklerde kendi bilgisayarımda
elde ettiğim gerçek ölçüm sonuçları kullanıldı.
### İstek 11

Kontrol noktası 0 için öğretmenin vereceği
hamle dizilerinin terminalden girilmesi ve
Perft değerlerinin hesaplanması konusunda
ChatGPT'den yardım aldım.

Kullanılan kısım:
kontrol0.py dosyasının kodları, örnek
hamle dizileri ve sözlü kontrol soruları.