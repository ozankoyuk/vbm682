# Hacettepe Üniversitesi
## Veri ve Bilgi Mühendisliği Yüksek Lisans Programı
### VBM 682 Doğal Dil İşleme Dersi Proje Ödevi (Sonbahar 2021)


## Amaç
* Verilen verileri kullanarak HMM modeli oluşturup, her kelime için POSTag tahmini üretimi.

## Kurulum
* Python 3.8 sürümu ile bir sanal ortam yaratılır ve aktif hale getirilir.
```
python -m venv venv
. venv/bin/activate
```

* venv aktif olduktan sonra, gerekli kütüphanelerin kurulması gerekmektedir. 
```
pip install -r requirements.txt
```

* Kurulum tamamlandıktan sonra ilgili kodu çalıştırmak yeterlidir.
```
python hmm_algorithm.py
```

* İşlemlerin tamamlanmasının ardından, terminalde ilgili çıktılar kontrol edilebilir.

* Verilerin (`Train` ve `Test` klasörlerinin) doğru konumda olduklarından emin olunuz.

## Sonuçlar
* Ilgili kodun çalışmasının ardından, içinde bulunulan dizin içerisine gerekli dosyaların oluşturulduğunu görebilirsiniz.
* Daha detaylı sonuç dosyalarını oluşturmak için, kodun ilk satırlarındaki açıklama kısmını okumanız yeterli olacaktır.
