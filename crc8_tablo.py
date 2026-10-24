"""
1-Wire CRC-8, tablo tabanlı (lookup table) versiyon

Bit bit versiyon (crc8_1wire.py) her bayt için 8 adım yapar.
Tablo versiyonu aynı sonucu bayt başına TEK adımda verir:

    crc = TABLO[crc ^ bayt]

Tablonun 256 elemanı, "CRC=0 iken tek baytı bit bit işlemenin sonucu"
olarak önceden hesaplanır. Gömülü sistemlerde bu, bellek (256 bayt)
karşılığında hız kazandırır.

Bu dosya da hazır CRC kütüphanesi kullanmaz.
"""

from crc8_1wire import POLY_YANSITILMIS, BASLANGIC_CRC, crc8_hesapla, hex_yaz


def tablo_olustur():
    """0..255 için tek baytın bit bit CRC sonucunu hesaplayıp tablo üretir."""
    tablo = []
    for bayt in range(256):
        crc = bayt
        for _ in range(8):
            if crc & 0x01:
                crc = (crc >> 1) ^ POLY_YANSITILMIS
            else:
                crc >>= 1
        tablo.append(crc)
    return tablo


TABLO = tablo_olustur()


def crc8_tablo(veri):
    """Tablo kullanarak bayt listesinin 1-Wire CRC-8 değerini döndürür."""
    crc = BASLANGIC_CRC
    for bayt in veri:
        crc = TABLO[crc ^ bayt]
    return crc


def tabloyu_yazdir():
    """Tabloyu 16x16 HEX olarak yazdırır (C kodunda dizi olarak kullanılabilir)."""
    print("      " + " ".join(f"{s:02X}" for s in range(16)))
    for satir in range(16):
        degerler = TABLO[satir * 16:(satir + 1) * 16]
        print(f"{satir * 16:02X} : " + " ".join(f"{d:02X}" for d in degerler))


def main():
    print("256 elemanlı CRC tablosu (satır başı = ilk indeks):\n")
    tabloyu_yazdir()

    print("\nBit bit versiyon ile karşılaştırma:")
    testler = [
        ("Test 1", [0x01, 0x23, 0x45, 0x67, 0x89, 0xAB, 0xCD, 0xEF], 0xDD),
        ("Test 2", [0xFF] * 8, 0xC9),
        ("Test 3 (ROM)", [0x28, 0xFF, 0x6C, 0x92, 0x91, 0x16, 0x04], 0x3A),
    ]
    for ad, veri, beklenen in testler:
        bit_bit = crc8_hesapla(veri)
        tablolu = crc8_tablo(veri)
        durum = "AYNI" if bit_bit == tablolu == beklenen else "FARKLI"
        print(f"{ad:<13} {hex_yaz(veri):<26} bit bit={bit_bit:02X}  "
              f"tablo={tablolu:02X}  beklenen={beklenen:02X}  -> {durum}")


if __name__ == "__main__":
    main()
