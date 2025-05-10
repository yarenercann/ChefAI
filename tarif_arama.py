import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# 1. Tarif verisini yükle
with open("dataset.json", "r", encoding="utf-8") as f:
    tarifler = json.load(f)

# 2. Başlık ve malzeme metinleri ve hazırlama metinleri hazırla
basliklar = [tarif["Başlık"] for tarif in tarifler]
malzeme_metinleri = [" ".join(tarif["İçindekiler"]) for tarif in tarifler]
hazırlama_metinleri = [tarif["Hazirlanis"] for tarif in tarifler]


# 3. Vektörleştirme
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(malzeme_metinleri)

# Basliktan tarif bulan fonksiyon
def tarif_bul(baslik):
    for tarif in tarifler:
        if tarif["Başlık"].strip().lower() == baslik.strip().lower():
            return tarif
    return None


# 4. Kullanıcıdan giriş al
kullanici_input = input("Malzemeleri aralarına boşluk koyarak girin (örn: un süt yumurta şeker):\n> ")
kullanici_malzemeleri = kullanici_input.strip().split()
query = " ".join(kullanici_malzemeleri)
query_vec = vectorizer.transform([query])

# 5. Benzerlik hesapla
benzerlik = cosine_similarity(query_vec, X)

# 6. En benzer 5 tarifi sırala
en_benzer_indisler = benzerlik[0].argsort()[::-1][:5]

# 7. Sonuçları göster
print("\n📌 Girdiğiniz malzemelere en uygun 5 tarif:\n")
secenekler = [] # sunulan secenekleri bir listeeye ekleme
for i, k in enumerate(en_benzer_indisler, start=1):
    print(f"{i}. {basliklar[k]} (Benzerlik Skoru: {benzerlik[0][k]:.2f})")
    secenekler.append(basliklar[k])

#kullanıcıdan secim alma
secim = input("\nBir tarif seçin (1-5): \n")
if secim.isdigit() and 1 <= int(secim) <= 5:
    secilen_tarif = secenekler[int(secim) - 1]
    detayli_tarif = tarif_bul(secilen_tarif)
    if detayli_tarif:
        print(f"\nSecilen tarif: {detayli_tarif['Başlık']}")
        print("\nMalzemeler: ")
        for malzeme in detayli_tarif["İçindekiler"]:
            print(f"- {malzeme}")
        print("\nHazırlama: ")
        for hazirlama in detayli_tarif["Hazirlanis"]:
            print(f"- {hazirlama}")
        #print(detayli_tarif["Hazirlanis"])
    else:
        print("Tarif bulunamadı.")
else:
    print("Geçersiz seçim.")

