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

## Aşama 1 - Minimax Algoritması

### İstek 12

Minimax algoritmasının derinlik sınırı ile
oluşturulması konusunda ChatGPT'den yardım aldım.

Kullanılan kısım:
search.py dosyasındaki Minimax sınıfı,
max_value(), min_value(), choose_move(),
evaluate() ve ordered_actions() fonksiyonlarının
kodları ve açıklamaları.

Düğüm sayacı, terminal kontrolü, eşit değerli
hamlelerde seçim kuralı ve geçici değerlendirme
fonksiyonu için verilen kodlardan yararlanıldı.

Boş tahta, kazanma, rakibi engelleme ve
tekrarlanabilirlik için test kodları kullanıldı.
### İstek 13

Minimax algoritmasının farklı oyun konumlarında
ve farklı derinliklerde performansının ölçülmesi
konusunda ChatGPT'den yardım aldım.

Kullanılan kısım:
minimax_olcum.py dosyasının kodları,
beş örnek oyun konumu, çalışma süresi ölçümü,
etkin dallanma çarpanı hesabı ve sonuçların
CSV dosyasına kaydedilmesi.

Ölçümler kendi bilgisayarımda gerçekleştirildi.
Öğretmenin vereceği konumlar için ölçümler
ayrıca tekrarlanacaktır.
### İstek 14

Minimax algoritmasının doğruluğunu kontrol
etmek için birim testlerinin hazırlanması
konusunda ChatGPT'den yardım aldım.

Kullanılan kısım:
test_search.py dosyasındaki 10 birim testinin
kodları ve açıklamaları.

Kazanma, rakibi engelleme, düğüm sayısı,
tekrarlanabilirlik, terminal durum, derinlik
sınırı ve oyun durumunun değişmemesi için
hazırlanan testlerden yararlanıldı.

### İstek 15

Minimax performans ölçümlerinin raporlanması,
grafiklerin oluşturulması ve sonuçların
yorumlanması konusunda ChatGPT'den yardım aldım.

Kullanılan kısım:
Rapor metni, performans tablosu ve
grafik_olustur.py dosyasına eklenen
Minimax grafik kodları.

Grafiklerin CSV dosyasındaki ölçümlerden
otomatik olarak oluşturulması sağlandı.

Rapordaki ölçümler ve test süreleri kendi
bilgisayarımda elde ettiğim sonuçlardan alındı.

### İstek 16

Minimax algoritması için kontrol noktası 1
hazırlığı ve öğretmenin vereceği hamle
dizilerinin test edilmesi konusunda
ChatGPT'den yardım aldım.

Kullanılan kısım:
kontrol1.py dosyasının kodları,
kazanma ve rakibi engelleme konumları,
derinlik bazlı ölçüm tablosu ve
sözlü kontrol sorularının açıklamaları.

## Aşama 2 - Alfa-Beta Budaması

### İstek 17

Alfa-beta budaması algoritmasının oluşturulması
ve Minimax ile karşılaştırılması konusunda
ChatGPT'den yardım aldım.

Kullanılan kısım:
search.py dosyasına eklenen AlphaBeta sınıfı,
alpha ve beta sınırları, max_value(),
min_value() ve choose_move() fonksiyonlarının
kodları ve açıklamaları.

alphabeta_ilk_test.py dosyasındaki beş örnek
konum, düğüm azalması hesabı, kök değerinin
ve seçilen hamlenin doğruluk kontrolleri
için verilen kodlar kullanıldı.

İlk aşamada hamle sıralaması uygulanmadı.

### İstek 18

Alfa-beta ve Minimax algoritmalarının
karşılaştırılabilmesi için 50 rastgele oyun
konumunun oluşturulması konusunda
ChatGPT'den yardım aldım.

Kullanılan kısım:
rastgele_konumlar.py dosyasının kodları,
seed kullanımı, benzersiz konum kontrolü,
terminal durumların elenmesi ve JSON
dosyasına veri kaydetme işlemleri.

Seed değeri olarak öğrenci numaramın
son iki hanesi olan 27 kullanıldı.

MAX ve MIN sırasındaki konumların dengeli
olması için her oyuncuya 25 konum ayrıldı.

### İstek 19

50 rastgele oyun konumunda Minimax ve
alfa-beta algoritmalarının derinlik 6 için
karşılaştırılması konusunda ChatGPT'den
yardım aldım.

Kullanılan kısım:
alphabeta_dogruluk.py dosyasının kodları,
JSON dosyasından konumların okunması,
kök değeri karşılaştırması, düğüm sayısı
kontrolü ve seçilen hamlenin düz Minimax
ile doğrulanması.

Çalışma süresi, ortalama düğüm sayısı,
düğüm azalması hesapları ve CSV dosyasına
sonuçların kaydedilmesi için verilen
kodlardan yararlanıldı.

Ölçümler kendi bilgisayarımda gerçekleştirildi.

### İstek 20

Alfa-beta algoritmasında üç farklı hamle
sıralama yönteminin geliştirilmesi konusunda
ChatGPT'den yardım aldım.

Kullanılan kısım:
AlphaBeta sınıfının güncellenmesi,
center_distance(), ordered_actions()
ve priority() fonksiyonlarının kodları.

Sıralamasız, merkezden dışarı ve önce
kazanma/engelleme yöntemleri oluşturuldu.

Misere varyantında kaybettiren hamlelerin
son sıraya alınması sağlandı.

siralama_test.py dosyasındaki doğruluk
ve hamle sıralaması testlerinden yararlanıldı.

### İstek 21

Uc farkli hamle siralama yonteminin 50 rastgele
oyun konumunda performansinin olculmesi
konusunda ChatGPT'den yardim aldim.

Kullanilan kisim:
siralama_olcum.py dosyasinin kodlari,
MeasuredAlphaBeta sinifi, siralama suresinin
olculmesi ve 150 aramanin karsilastirilmasi.

Kok degeri, secilen hamlenin dogrulugu,
dugum sayisi, calisma suresi ve siralama
maliyeti icin verilen kodlar kullanildi.

En az budama yapilan konumun belirlenmesi,
ortalama degerlerin hesaplanmasi ve CSV
dosyalarinin olusturulmasindan yararlanildi.

Olcumler kendi bilgisayarimda gerceklestirildi.
### İstek 22

Alfa-beta algoritmasinin birim testlerinin
hazirlanmasi ve beta kesme kosulundaki
hatalarin yakalanmasi konusunda ChatGPT'den
yardim aldim.

Kullanilan kisim:
test_alphabeta.py dosyasindaki 9 birim
testinin kodlari ve aciklamalari.

Beta kesme kosulunun >= yerine > ve <=
olarak degistirilmesiyle olusan performans
ve dogruluk sorunlarinin test edilmesi
icin verilen adimlardan yararlanildi.

Deneylerden sonra orijinal beta kesme
kosulu geri yuklendi ve tum birim
testleri yeniden calistirildi.

### İstek 23

Alfa-beta budaması ve hamle sıralama
sonuçlarının raporlanması konusunda
ChatGPT'den yardım aldım.

Kullanılan kısım:
Aşama 2 rapor metni, karşılaştırma
tabloları, performans yorumları ve
grafik_olustur.py dosyasına eklenen
dört grafik için verilen kodlar.

Minimax ve alfa-beta karşılaştırması,
üç sıralama yönteminin değerlendirilmesi
ve beta kesme koşulu deneylerinin
raporlanmasından yararlanıldı.

Rapordaki bütün ölçümler kendi
bilgisayarımda elde ettiğim gerçek
sonuçlardan alınmıştır.

### İstek 24

Alfa-beta kontrol noktası ve sözlü sınav
hazırlığı konusunda ChatGPT'den yardım aldım.

Kullanılan kısım:
kontrol2.py dosyasının kodları, kullanıcıdan
hamle dizisinin alınması, Minimax ve üç
alfa-beta yönteminin karşılaştırılması,
düğüm azalması ve çalışma süresi hesapları.

Seçilen hamlelerin doğrulanması ve sözlü
kontrol sorularının açıklamalarından
yararlanıldı.