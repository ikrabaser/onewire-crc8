# 1-Wire CRC-8 (Dallas/Maxim) — Python

Gömülü Sistemler dersi programlama ödevi. 1-Wire haberleşmesinde kullanılan
CRC-8 algoritması, **hazır CRC kütüphanesi kullanılmadan** bit bit elle yazılmıştır.

## Algoritma parametreleri

| Parametre | Değer |
|---|---|
| Algoritma | Dallas/Maxim CRC-8 (1-Wire) |
| Başlangıç CRC | `0x00` |
| Polinom (normal gösterim) | `0x31` (x⁸ + x⁵ + x⁴ + 1) |
| Bit işleme yönü | LSB önce |
| Yansıtılmış işlem polinomu | `0x8C` |
| Son XOR | `0x00` |

## Algoritma nasıl çalışır?

Her veri baytı için 8 bit, en düşük anlamlı bitten başlayarak işlenir:

1. CRC'nin en düşük biti ile veri bitini XOR'la.
2. CRC'yi bir bit sağa kaydır.
3. 1. adımın sonucu `1` ise CRC'yi `0x8C` ile XOR'la.
4. Veriyi bir bit sağa kaydırıp sıradaki bite geç.

```python
for bayt in veri:
    for _ in range(8):
        karisim = (crc ^ bayt) & 0x01
        crc >>= 1
        if karisim == 1:
            crc ^= 0x8C
        bayt >>= 1
```

Veri + CRC baytı birlikte aynı algoritmadan geçirilirse, **doğru pakette sonuç
`0x00`** çıkar. Paket doğrulama bu özelliğe dayanır.

## Dosyalar

| Dosya | Ne işe yarar? |
|---|---|
| `crc8_1wire.py` | Ödevin ana programı: CRC hesaplama, paket doğrulama, üç zorunlu test, tek bit hata algılama; komut satırından HEX veri de alır |
| `crc8_1wire.c` | Aynı algoritmanın C versiyonu (mikrodenetleyiciye taşınabilir) |
| `crc8_tablo.py` | 256 elemanlı arama tablosuyla hızlı versiyon, bit bit sonuçla karşılaştırma |
| `crc8_trace.py` | Algoritmayı bit bit adım adım tablo olarak gösterir |
| `test_crc8.py` | 15 otomatik test (`unittest`) |
| `crc8_grafik.py` | Tek bit hatası taramasını grafiğe döker (`hata_algilama.png`) |
| `hata_algilama.png` | Üretilmiş grafik |
| `RAPOR.md` | Kısa ödev raporu |

## Çalıştırma

```bash
python crc8_1wire.py                 # ödevin istediği çıktı (A, B, C, D)
python crc8_1wire.py 01 23 45 67 89 AB CD EF   # kendi verinin CRC'sini hesapla
python crc8_1wire.py --paket 28 FF 6C 92 91 16 04 3A   # son bayt CRC: paketi doğrula

python crc8_trace.py 1               # Test 1'in bit bit izlemesi (2 ve 3 de olur)
python crc8_tablo.py                 # tablo versiyonu + bit bit karşılaştırma
python -m unittest -v test_crc8      # otomatik testler

gcc -Wall -Wextra -o crc8 crc8_1wire.c && ./crc8   # C versiyonu (Windows: crc8.exe)

pip install matplotlib               # yalnızca grafik için gerekli
python crc8_grafik.py                # hata_algilama.png üretir
```

Matplotlib dışındaki tüm Python dosyaları yalnızca standart kütüphane kullanır.
`--paket` modu, paket geçersizse `2` çıkış koduyla biter.

## Test sonuçları

| Test | Veri baytları | Hesaplanan | Beklenen | Paket kontrolü | Tek bit bozulunca |
|---|---|---|---|---|---|
| 1 | `01 23 45 67 89 AB CD EF` | `DD` | `DD` | `00` → geçerli | `A4` → hata algılandı |
| 2 | `FF FF FF FF FF FF FF FF` | `C9` | `C9` | `00` → geçerli | `A4` → hata algılandı |
| 3 (ROM) | `28 FF 6C 92 91 16 04` | `3A` | `3A` | `00` → geçerli | `43` → hata algılandı |

Örnek çıktı (Test 1):

```
Veri            : 01 23 45 67 89 AB CD EF
Hesaplanan CRC  : DD
Beklenen CRC    : DD  -> EŞLEŞTİ
Paket           : 01 23 45 67 89 AB CD EF DD
Paket CRC sonucu: 00  -> GEÇERLİ
Bozuk paket     : 00 23 45 67 89 AB CD EF DD  (bayt 0, bit 0 değişti)
Bozuk CRC sonucu: A4  -> GEÇERSİZ (hata algılandı)
```

## Bit bit izleme

`crc8_trace.py 1` çıktısından ilk bayt (`0x01`):

```
Bayt Bit Veri biti CRC bit0 XOR  CRC (önce)      >> 1  Polinom?  CRC (sonra)
   0   0         1        0   1    00000000  00000000      evet     10001100
   0   1         0        0   0    10001100  01000110     hayır     01000110
   0   2         0        0   0    01000110  00100011     hayır     00100011
   0   3         0        1   1    00100011  00010001      evet     10011101
   0   4         0        1   1    10011101  01001110      evet     11000010
   0   5         0        0   0    11000010  01100001     hayır     01100001
   0   6         0        1   1    01100001  00110000      evet     10111100
   0   7         0        0   0    10111100  01011110     hayır     01011110
     -> Bayt 0 bitti: CRC = 0x5E
```

Sütunlar: o bitte işlenen veri biti, CRC'nin en düşük biti, ikisinin XOR'u,
kaydırmadan önceki CRC, sağa kaydırılmış hali, `0x8C` ile XOR uygulanıp
uygulanmadığı ve adım sonundaki CRC.

## Hata algılama grafiği

Her test paketinin (veri + CRC) her bir biti sırayla çevrilip paketin CRC sonucu
hesaplanmıştır. Geçerli paket `0x00` verir; kırmızı çizgi bu değerdir.
Hiçbir çubuk sıfır olmadığı için **tüm tek bit hataları yakalanmıştır**
(Test 1 ve 2: 72/72, Test 3: 64/64).

![Tek bit hata algılama](hata_algilama.png)

Tek bit hatasının sonucu veriye değil yalnızca bit konumuna bağlıdır
(CRC doğrusaldır); bu yüzden Test 1 ve Test 2'nin grafikleri aynıdır.
