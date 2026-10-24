"""
1-Wire CRC-8 otomatik testleri (yalnızca standart kütüphane: unittest)

Çalıştırma:
    python -m unittest -v test_crc8
"""

import random
import unittest
from itertools import combinations

from crc8_1wire import crc8_hesapla, paket_gecerli_mi, hex_oku
from crc8_tablo import crc8_tablo, TABLO

TEST1 = [0x01, 0x23, 0x45, 0x67, 0x89, 0xAB, 0xCD, 0xEF]
TEST2 = [0xFF] * 8
TEST3 = [0x28, 0xFF, 0x6C, 0x92, 0x91, 0x16, 0x04]   # 1-Wire ROM (7 bayt + CRC)


class ZorunluTestler(unittest.TestCase):
    """Ödev PDF'indeki beklenen CRC değerleri."""

    def test_1(self):
        self.assertEqual(crc8_hesapla(TEST1), 0xDD)

    def test_2(self):
        self.assertEqual(crc8_hesapla(TEST2), 0xC9)

    def test_3_rom(self):
        self.assertEqual(crc8_hesapla(TEST3), 0x3A)


class PaketDogrulama(unittest.TestCase):
    """Veri + CRC baytı birlikte işlenince sonuç 0x00 olmalı."""

    def test_gecerli_paketler(self):
        for veri in (TEST1, TEST2, TEST3):
            paket = veri + [crc8_hesapla(veri)]
            self.assertEqual(crc8_hesapla(paket), 0x00)
            self.assertTrue(paket_gecerli_mi(paket))

    def test_yanlis_crc_reddedilir(self):
        paket = TEST1 + [0xDD ^ 0x01]
        self.assertFalse(paket_gecerli_mi(paket))


class HataAlgilama(unittest.TestCase):
    """Paketteki herhangi bir TEK bit değişirse hata algılanmalı."""

    def test_her_tek_bit_hatasi_yakalanir(self):
        for veri in (TEST1, TEST2, TEST3):
            paket = veri + [crc8_hesapla(veri)]
            for bayt_no in range(len(paket)):
                for bit_no in range(8):
                    bozuk = paket.copy()
                    bozuk[bayt_no] ^= (1 << bit_no)
                    with self.subTest(veri=veri, bayt=bayt_no, bit=bit_no):
                        self.assertFalse(paket_gecerli_mi(bozuk))

    def test_her_cift_bit_hatasi_yakalanir(self):
        """Bu kısa paketlerde (en çok 72 bit) iki bitlik hataların hepsi yakalanır."""
        for veri in (TEST1, TEST2, TEST3):
            paket = veri + [crc8_hesapla(veri)]
            for a, b in combinations(range(len(paket) * 8), 2):
                bozuk = paket.copy()
                bozuk[a // 8] ^= (1 << (a % 8))
                bozuk[b // 8] ^= (1 << (b % 8))
                self.assertFalse(paket_gecerli_mi(bozuk), f"kaçan çift: {a}, {b}")


class KenarDurumlari(unittest.TestCase):
    def test_bos_veri_baslangic_crc(self):
        self.assertEqual(crc8_hesapla([]), 0x00)

    def test_tek_sifir_bayt(self):
        self.assertEqual(crc8_hesapla([0x00]), 0x00)

    def test_hex_oku(self):
        self.assertEqual(hex_oku(["01", "ab", "0xFF"]), [0x01, 0xAB, 0xFF])

    def test_hex_oku_gecersiz(self):
        with self.assertRaises(ValueError):
            hex_oku(["ZZ"])
        with self.assertRaises(ValueError):
            hex_oku(["1FF"])


class TabloVersiyonu(unittest.TestCase):
    """Tablo tabanlı versiyon, bit bit versiyonla aynı sonucu vermeli."""

    def test_tablo_boyutu(self):
        self.assertEqual(len(TABLO), 256)

    def test_zorunlu_testler(self):
        self.assertEqual(crc8_tablo(TEST1), 0xDD)
        self.assertEqual(crc8_tablo(TEST2), 0xC9)
        self.assertEqual(crc8_tablo(TEST3), 0x3A)

    def test_tum_tek_baytlar(self):
        for b in range(256):
            self.assertEqual(crc8_tablo([b]), crc8_hesapla([b]))

    def test_rastgele_veriler(self):
        rng = random.Random(1)
        for _ in range(500):
            veri = [rng.randrange(256) for _ in range(rng.randrange(0, 40))]
            self.assertEqual(crc8_tablo(veri), crc8_hesapla(veri))


if __name__ == "__main__":
    unittest.main(verbosity=2)
