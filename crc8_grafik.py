"""
Tek bit hata algılama grafiği

Her test paketi (veri + CRC baytı) için 72 bit konumunun (9 bayt x 8 bit)
her biri sırayla çevrilir ve paketin CRC sonucu hesaplanır.
Geçerli pakette sonuç 0x00'dır; bozuk pakette sonucun 0x00'dan farklı
çıkması hatanın algılandığı anlamına gelir.

Gereksinim: matplotlib   (pip install matplotlib)
Çıktı     : hata_algilama.png
"""

import matplotlib.pyplot as plt

from crc8_1wire import crc8_hesapla

TESTLER = [
    ("Test 1", [0x01, 0x23, 0x45, 0x67, 0x89, 0xAB, 0xCD, 0xEF]),
    ("Test 2", [0xFF] * 8),
    ("Test 3 (ROM)", [0x28, 0xFF, 0x6C, 0x92, 0x91, 0x16, 0x04]),
]


def tek_bit_taramasi(paket):
    """Paketteki her bit konumunu çevirir, her seferinde CRC sonucunu döndürür."""
    sonuclar = []
    for bayt_no in range(len(paket)):
        for bit_no in range(8):
            bozuk = paket.copy()
            bozuk[bayt_no] ^= (1 << bit_no)
            sonuclar.append(crc8_hesapla(bozuk))
    return sonuclar


def main():
    fig, eksenler = plt.subplots(len(TESTLER), 1, figsize=(11, 8), sharex=False)
    fig.suptitle("Tek bit hatası: bozuk paketin CRC sonucu (geçerli paket = 0x00)",
                 fontsize=13, fontweight="bold")

    for eksen, (ad, veri) in zip(eksenler, TESTLER):
        paket = veri + [crc8_hesapla(veri)]
        sonuclar = tek_bit_taramasi(paket)
        algilanan = sum(1 for s in sonuclar if s != 0)

        eksen.bar(range(len(sonuclar)), sonuclar, color="#2a6f97", width=0.8)
        eksen.axhline(0, color="#c1121f", linewidth=1.5)
        eksen.set_title(f"{ad}: {algilanan}/{len(sonuclar)} hata algılandı", fontsize=10,
                        loc="left")
        eksen.set_ylabel("CRC sonucu")
        eksen.set_ylim(-14, 270)   # alt boşluk: 0x00 çizgisi görünsün

        # Bayt sınırlarını ve bayt etiketlerini göster
        bayt_sayisi = len(paket)
        eksen.set_xticks([b * 8 + 3.5 for b in range(bayt_sayisi)])
        etiketler = [f"B{b}" for b in range(bayt_sayisi - 1)] + ["CRC"]
        eksen.set_xticklabels(etiketler, fontsize=8)
        for b in range(1, bayt_sayisi):
            eksen.axvline(b * 8 - 0.5, color="#bbbbbb", linewidth=0.6, linestyle=":")

    eksenler[-1].set_xlabel("Bozulan bayt (her baytta 8 bit sırayla çevrildi)")
    fig.text(0.01, 0.025,
             "Kırmızı çizgi = 0x00 (geçerli paket). Hiçbir çubuk sıfır olmadığı için "
             "tüm tek bit hataları yakalanır.", fontsize=8, color="#444444")
    fig.text(0.01, 0.005,
             "Not: Tek bit hatasının sonucu veriye değil yalnızca bit konumuna bağlıdır "
             "(CRC doğrusaldır); bu yüzden Test 1 ve Test 2 aynı görünür.",
             fontsize=8, color="#444444")

    fig.tight_layout(rect=[0, 0.045, 1, 0.96])
    fig.savefig("hata_algilama.png", dpi=150)
    print("Kaydedildi: hata_algilama.png")


if __name__ == "__main__":
    main()
