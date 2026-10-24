/*
 * 1-Wire (Dallas/Maxim) CRC-8 hesaplama ve dogrulama - C versiyonu
 *
 * Parametreler:
 *   - Baslangic CRC : 0x00
 *   - Polinom       : 0x31 (x^8 + x^5 + x^4 + 1)
 *   - Bit yonu      : LSB once -> yansitilmis polinom 0x8C
 *   - Son XOR       : 0x00
 *
 * Hazir CRC kutuphanesi kullanilmamistir; algoritma bit bit yazilmistir.
 * Yalnizca standart kutuphane (stdio, stdint, stddef) kullanilir; bu nedenle
 * crc8_hesapla() fonksiyonu oldugu gibi bir mikrodenetleyiciye tasinabilir.
 *
 * Derleme ve calistirma:
 *   gcc -Wall -Wextra -o crc8 crc8_1wire.c
 *   ./crc8            (Windows: crc8.exe)
 */

#include <stdint.h>
#include <stddef.h>
#include <stdio.h>

#define POLY_YANSITILMIS 0x8C
#define BASLANGIC_CRC    0x00

/* Verilen baytlarin 1-Wire CRC-8 degerini dondurur. */
uint8_t crc8_hesapla(const uint8_t *veri, size_t uzunluk)
{
    uint8_t crc = BASLANGIC_CRC;

    for (size_t i = 0; i < uzunluk; i++) {          /* her bayt icin */
        uint8_t bayt = veri[i];

        for (int bit = 0; bit < 8; bit++) {         /* 8 bit isle (LSB once) */
            /* CRC'nin en dusuk biti ile veri bitini XOR'la */
            uint8_t karisim = (crc ^ bayt) & 0x01;

            crc >>= 1;                              /* CRC'yi saga kaydir */
            if (karisim) {
                crc ^= POLY_YANSITILMIS;            /* bit 1 ise polinomla XOR'la */
            }

            bayt >>= 1;                             /* siradaki veri bitine gec */
        }
    }

    return crc;
}

/* Veri + CRC bayti birlikte islenirse gecerli pakette sonuc 0x00 cikar. */
int paket_gecerli_mi(const uint8_t *paket, size_t uzunluk)
{
    return crc8_hesapla(paket, uzunluk) == 0x00;
}

static void hex_yaz(const uint8_t *veri, size_t uzunluk)
{
    for (size_t i = 0; i < uzunluk; i++) {
        printf("%s%02X", i ? " " : "", veri[i]);
    }
}

/* Bir test icin odevin A-D maddelerini calistirir. 0 = basarili, 1 = hata. */
static int test_calistir(const char *ad, const uint8_t *veri, size_t uzunluk,
                         uint8_t beklenen)
{
    uint8_t paket[16];

    printf("============================================================\n");
    printf("%s\n", ad);
    printf("Veri            : ");
    hex_yaz(veri, uzunluk);
    printf("\n");

    /* A) CRC hesapla */
    uint8_t crc = crc8_hesapla(veri, uzunluk);

    /* D) Hesaplanan ve beklenen degeri yazdir */
    int eslesti = (crc == beklenen);
    printf("Hesaplanan CRC  : %02X\n", crc);
    printf("Beklenen CRC    : %02X  -> %s\n", beklenen,
           eslesti ? "ESLESTI" : "ESLESMEDI");

    /* B) Veri + CRC baytini tekrar isle */
    for (size_t i = 0; i < uzunluk; i++) {
        paket[i] = veri[i];
    }
    paket[uzunluk] = crc;
    size_t paket_uzunluk = uzunluk + 1;

    printf("Paket           : ");
    hex_yaz(paket, paket_uzunluk);
    printf("\n");
    printf("Paket CRC sonucu: %02X  -> %s\n", crc8_hesapla(paket, paket_uzunluk),
           paket_gecerli_mi(paket, paket_uzunluk) ? "GECERLI" : "GECERSIZ");

    /* C) Tek bir veri bitini boz ve hatanin yakalandigini goster */
    paket[0] ^= 0x01;                               /* ilk baytin en dusuk biti */
    printf("Bozuk paket     : ");
    hex_yaz(paket, paket_uzunluk);
    printf("  (bayt 0, bit 0 degisti)\n");
    printf("Bozuk CRC sonucu: %02X  -> %s\n", crc8_hesapla(paket, paket_uzunluk),
           paket_gecerli_mi(paket, paket_uzunluk) ? "GECERLI"
                                                  : "GECERSIZ (hata algilandi)");

    return eslesti ? 0 : 1;
}

int main(void)
{
    const uint8_t test1[] = {0x01, 0x23, 0x45, 0x67, 0x89, 0xAB, 0xCD, 0xEF};
    const uint8_t test2[] = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF};
    const uint8_t test3[] = {0x28, 0xFF, 0x6C, 0x92, 0x91, 0x16, 0x04};

    int hata = 0;
    hata += test_calistir("Test 1", test1, sizeof test1, 0xDD);
    hata += test_calistir("Test 2", test2, sizeof test2, 0xC9);
    hata += test_calistir("Test 3 (ROM)", test3, sizeof test3, 0x3A);
    printf("============================================================\n");

    return hata ? 1 : 0;                            /* basarisiz test varsa 1 dondur */
}
