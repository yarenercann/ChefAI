import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# 1. Tarif verisini yükle
with open("dataset.json", "r", encoding="utf-8") as f:
    tarifler = json.load(f)

# 2. Başlık ve malzeme metinleri hazırla
basliklar = [tarif["Başlık"] for tarif in tarifler]
malzeme_metinleri = [" ".join(tarif["İçindekiler"]) for tarif in tarifler]

# 3. Vektörleştirme
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(malzeme_metinleri)

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
for i in en_benzer_indisler:
    print(f"- {basliklar[i]} (Benzerlik Skoru: {benzerlik[0][i]:.2f})")
