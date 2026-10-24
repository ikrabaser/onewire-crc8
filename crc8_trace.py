"""
1-Wire CRC-8 adım adım izleme (bit bit görselleştirme)

crc8_1wire.py içindeki algoritmanın her adımını tablo olarak yazdırır:
her bayt için 8 bit sırayla işlenir, CRC'nin ikilik (binary) halinin
nasıl değiştiği görülür.

Kullanım:
    python crc8_trace.py            # Test 1'i izler
    python crc8_trace.py 2          # Test 2'yi izler
    python crc8_trace.py 3          # Test 3'ü (ROM) izler
"""

import sys

from crc8_1wire import POLY_YANSITILMIS, BASLANGIC_CRC, hex_yaz

TESTLER = {
    1: [0x01, 0x23, 0x45, 0x67, 0x89, 0xAB, 0xCD, 0xEF],
    2: [0xFF] * 8,
    3: [0x28, 0xFF, 0x6C, 0x92, 0x91, 0x16, 0x04],
}


def ikilik(sayi):
    """8 bitlik ikilik gösterim: 0x8C -> '10001100'."""
    return format(sayi, "08b")


def crc8_izle(veri):
    """CRC'yi hesaplarken her bit adımını yazdırır ve sonucu döndürür."""
    crc = BASLANGIC_CRC

    print(f"Başlangıç CRC = 0x{crc:02X} ({ikilik(crc)})   "
          f"Yansıtılmış polinom = 0x{POLY_YANSITILMIS:02X} ({ikilik(POLY_YANSITILMIS)})")
    print()
    print(f"{'Bayt':>4} {'Bit':>3} {'Veri biti':>9} {'CRC bit0':>8} "
          f"{'XOR':>3} {'CRC (önce)':>11} {'>> 1':>9} {'Polinom?':>9} {'CRC (sonra)':>12}")
    print("-" * 82)

    for bayt_no, bayt in enumerate(veri):
        for bit_no in range(8):
            crc_once = crc
            veri_biti = bayt & 0x01
            crc_bit0 = crc & 0x01
            karisim = crc_bit0 ^ veri_biti

            crc >>= 1
            kaydirilmis = crc
            if karisim == 1:
                crc ^= POLY_YANSITILMIS
                polinom = "evet"
            else:
                polinom = "hayır"

            bayt >>= 1

            print(f"{bayt_no:>4} {bit_no:>3} {veri_biti:>9} {crc_bit0:>8} "
                  f"{karisim:>3} {ikilik(crc_once):>11} {ikilik(kaydirilmis):>9} "
                  f"{polinom:>9} {ikilik(crc):>12}")

        print(f"     -> Bayt {bayt_no} bitti: CRC = 0x{crc:02X}")
        print("-" * 82)

    return crc


def main():
    secim = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    if secim not in TESTLER:
        print("Geçerli seçimler: 1, 2, 3")
        sys.exit(1)

    veri = TESTLER[secim]
    print(f"Test {secim} verisi: {hex_yaz(veri)}\n")
    crc = crc8_izle(veri)
    print(f"\nSonuç CRC = {crc:02X}")


if __name__ == "__main__":
    main()
