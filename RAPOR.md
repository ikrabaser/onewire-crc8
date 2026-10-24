# 1-Wire CRC-8 Ödevi — Kısa Rapor

**Ders:** Gömülü Sistemler  
**Konu:** 1-Wire protokolünde CRC-8 hesaplama ve doğrulama

## 1. Amaç

1-Wire haberleşmesinde (ör. DS18B20 sıcaklık sensörü, iButton) her ROM kodunun
ve veri paketinin sonunda bir CRC-8 baytı bulunur. Alıcı, gelen veriyi aynı
algoritmadan geçirerek iletim sırasında bit hatası olup olmadığını anlar.
Bu ödevde algoritma, hazır bir CRC kütüphanesi kullanılmadan **bit düzeyinde**
geliştirilmiş ve verilen test vektörleriyle doğrulanmıştır.

## 2. Algoritma

| Parametre | Değer |
|---|---|
| Başlangıç CRC | `0x00` |
| Polinom (normal) | `0x31` → x⁸ + x⁵ + x⁴ + 1 |
| Bit yönü | LSB önce |
| Yansıtılmış polinom | `0x8C` |
| Son XOR | `0x00` |

Her veri baytı için 8 bit, en düşük anlamlı bitten başlayarak işlenir:

1. CRC'nin en düşük biti ile veri biti XOR'lanır.
2. CRC bir bit sağa kaydırılır.
3. 1. adımın sonucu 1 ise CRC, `0x8C` ile XOR'lanır.
4. Veri bir bit sağa kaydırılıp sıradaki bite geçilir.

**Neden `0x8C`?** Normal gösterimdeki `0x31` polinomu (`00110001`) bit sırası ters
çevrilince `10001100` = `0x8C` olur. Veri LSB önce işlendiği için sağa kaydırmalı
(yansıtılmış) biçim kullanılır; böylece bit sırasını ayrıca çevirmek gerekmez.

**Paket doğrulama:** CRC baytı, verinin sonuna eklenip tüm paket aynı algoritmadan
geçirilirse doğru pakette sonuç `0x00` çıkar. Alıcının ayrıca CRC'yi karşılaştırmasına
gerek kalmaz, tek bir hesapla doğrulama yapılır.

## 3. Sonuçlar

| Test | Veri | Hesaplanan | Beklenen | Paket sonucu | Tek bit bozulunca |
|---|---|---|---|---|---|
| 1 | `01 23 45 67 89 AB CD EF` | `DD` | `DD` | `00` (geçerli) | `A4` (hata algılandı) |
| 2 | `FF FF FF FF FF FF FF FF` | `C9` | `C9` | `00` (geçerli) | `A4` (hata algılandı) |
| 3 (ROM) | `28 FF 6C 92 91 16 04` | `3A` | `3A` | `00` (geçerli) | `43` (hata algılandı) |

Üç testte de hesaplanan değer beklenenle eşleşmiştir.

**Hata algılama:** Her paketteki (veri + CRC) tüm bitler sırayla çevrilmiştir.
Test 1 ve 2'de 72 bitin, Test 3'te 64 bitin **hepsinde** hata yakalanmıştır
(`hata_algilama.png`). Ayrıca bu üç pakette iki bitin aynı anda bozulduğu **tüm
çiftler** (2556, 2556 ve 2016 çift) denenmiş ve hiçbiri kaçmamıştır.

Test 1 ve 2'nin grafikleri aynıdır: CRC doğrusal bir işlem olduğu için tek bit
hatasının sonucu veriye değil yalnızca bit konumuna bağlıdır.

## 4. Yapılanlar

| Dosya | Açıklama |
|---|---|
| `crc8_1wire.py` | Ana program (A-D maddeleri) ve komut satırından HEX veri alma modu |
| `crc8_trace.py` | Algoritmanın bit bit adım adım tablosu |
| `crc8_tablo.py` | 256 elemanlı arama tablosuyla hızlı versiyon, bit bit sonuçla karşılaştırma |
| `crc8_1wire.c` | Aynı algoritmanın C versiyonu (mikrodenetleyiciye taşınabilir) |
| `test_crc8.py` | 15 otomatik test (`python -m unittest -v test_crc8`) |
| `crc8_grafik.py` | Tek bit hata algılama grafiği |

Python ve C versiyonları aynı çıktıyı üretir. Tablo versiyonu, 0-255 arasındaki
tüm tek baytlarda ve 500 rastgele veri dizisinde bit bit versiyonla aynı sonucu
vermiştir.

## 5. Bit bit ve tablo versiyonu karşılaştırması

| | Bit bit | Tablo tabanlı |
|---|---|---|
| Bayt başına işlem | 8 adım (kaydırma + koşullu XOR) | 1 tablo okuması + 1 XOR |
| Ek bellek | Yok | 256 bayt |
| Uygun olduğu yer | Belleğin kısıtlı olduğu küçük MCU'lar | Hızın önemli olduğu, 256 baytın harcanabildiği yerler |

## 6. Öğrenilenler

- CRC, polinom bölmesinin kalanıdır; bit düzeyinde kaydırma ve XOR ile hesaplanır.
- Yansıtılmış polinom, LSB-önce iletimde bit sırası çevirme işini ortadan kaldırır.
- Doğru pakette "veri + CRC" sonucunun `0x00` olması doğrulamayı basitleştirir.
- Denenen kısa paketlerde (en çok 72 bit) bu CRC-8 tüm tek ve çift bit hatalarını yakalamıştır;
  ancak CRC bir güvenlik önlemi değil, yalnızca rastgele iletim hatalarına karşı bir
  koruma yöntemidir.
