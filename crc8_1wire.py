"""
1-Wire (Dallas/Maxim) CRC-8 hesaplama ve doğrulama

Parametreler:
  - Başlangıç CRC : 0x00
  - Polinom       : 0x31 (x^8 + x^5 + x^4 + 1)
  - Bit yönü      : LSB önce  -> yansıtılmış polinom 0x8C
  - Son XOR       : 0x00

Hazır CRC kütüphanesi kullanılmamıştır; algoritma bit bit elle yazılmıştır.
"""

POLY_YANSITILMIS = 0x8C   # 0x31 polinomunun bit sırası ters çevrilmiş hali
BASLANGIC_CRC = 0x00


def crc8_hesapla(veri):
    """Bayt listesinin 1-Wire CRC-8 değerini döndürür."""
    crc = BASLANGIC_CRC

    for bayt in veri:                      # her bayt için
        for _ in range(8):                 # 8 bit işle (LSB önce)
            # CRC'nin en düşük biti ile veri bitini XOR'la
            karisim = (crc ^ bayt) & 0x01

            crc >>= 1                      # CRC'yi sağa kaydır
            if karisim == 1:
                crc ^= POLY_YANSITILMIS    # bit 1 ise polinomla XOR'la

            bayt >>= 1                     # sıradaki veri bitine geç

    return crc


def paket_gecerli_mi(paket):
    """Veri + CRC baytı birlikte işlenirse geçerli pakette sonuç 0x00 çıkar."""
    return crc8_hesapla(paket) == 0x00


def hex_yaz(veri):
    return " ".join(f"{b:02X}" for b in veri)


def main():
    # (test adı, veri baytları, beklenen CRC)
    testler = [
        ("Test 1", [0x01, 0x23, 0x45, 0x67, 0x89, 0xAB, 0xCD, 0xEF], 0xDD),
        ("Test 2", [0xFF] * 8, 0xC9),
        ("Test 3 (ROM)", [0x28, 0xFF, 0x6C, 0x92, 0x91, 0x16, 0x04], 0x3A),
    ]

    for ad, veri, beklenen in testler:
        print("=" * 60)
        print(f"{ad}")
        print(f"Veri            : {hex_yaz(veri)}")

        # A) CRC hesapla
        crc = crc8_hesapla(veri)

        # D) Hesaplanan ve beklenen değeri yazdır
        durum = "EŞLEŞTİ" if crc == beklenen else "EŞLEŞMEDİ"
        print(f"Hesaplanan CRC  : {crc:02X}")
        print(f"Beklenen CRC    : {beklenen:02X}  -> {durum}")

        # B) Veri + CRC baytını tekrar işle
        paket = veri + [crc]
        sonuc = crc8_hesapla(paket)
        print(f"Paket           : {hex_yaz(paket)}")
        print(f"Paket CRC sonucu: {sonuc:02X}  -> "
              f"{'GEÇERLİ' if paket_gecerli_mi(paket) else 'GEÇERSİZ'}")

        # C) Tek bir veri bitini boz ve hatanın yakalandığını göster
        bozuk = paket.copy()
        bozuk[0] ^= 0x01                   # ilk baytın en düşük bitini çevir
        sonuc_bozuk = crc8_hesapla(bozuk)
        print(f"Bozuk paket     : {hex_yaz(bozuk)}  (bayt 0, bit 0 değişti)")
        print(f"Bozuk CRC sonucu: {sonuc_bozuk:02X}  -> "
              f"{'GEÇERLİ' if paket_gecerli_mi(bozuk) else 'GEÇERSİZ (hata algılandı)'}")

    print("=" * 60)


if __name__ == "__main__":
    main()
