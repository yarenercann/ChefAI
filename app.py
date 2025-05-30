from flask import Flask, render_template, request
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

# Dataset'i yükle
with open("dataset.json", "r", encoding="utf-8") as f:
    tarifler = json.load(f)

basliklar = [tarif["Başlık"] for tarif in tarifler]
malzeme_metinleri = [" ".join(tarif["İçindekiler"]) for tarif in tarifler]

# TF-IDF vektörleştirme
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(malzeme_metinleri)

@app.route("/", methods=["GET", "POST"])
def index():
    oneriler = []

    if request.method == "POST":
        girilen_malzeme = request.form["malzemeler"]
        query = " ".join(girilen_malzeme.strip().split())
        query_vec = vectorizer.transform([query])
        benzerlik = cosine_similarity(query_vec, X)
        en_benzer_inds = benzerlik[0].argsort()[::-1][:5]

        for i in en_benzer_inds:
            tarif = tarifler[i]

            # 'Hazirlanis' verisini düzgün kontrol et
            hazirlanis = (
                tarif.get("hazırlanis")
                or tarif.get("hazırlanış")
                or tarif.get("Hazirlanis")
                or ["Hazırlanış bilgisi bulunamadı."]
            )

            if isinstance(hazirlanis, str):
                hazirlanis = [hazirlanis]
            elif not isinstance(hazirlanis, list):
                hazirlanis = ["Hazırlanış bilgisi bulunamadı."]

            oneriler.append({
                "baslik": tarif["Başlık"],
                "malzemeler": tarif["İçindekiler"],
                "hazirlanis": hazirlanis,
                "skor": f"{benzerlik[0][i]:.2f}"
            })

    return render_template("index.html", onerilen_tarifler=oneriler)

if __name__ == "__main__":
    app.run(debug=True)
