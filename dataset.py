import requests
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
import nltk
import json

nltk.download('stopwords')
turkish_stopword=set(stopwords.words('turkish'))

cokluIfadeler = [
    "su bardağı", "çay bardağı", "yemek kaşığı", "tatlı kaşığı", "çay kaşığı",
    "orta boy", "küçük boy", "büyük boy", "ince yemeklik doğranmış",
    "küçük doğranmış", "yemeklik doğranmış", "taze sıkılmış",
    "ince kıyılmış", "piyazlık doğranmış"
]

tekliOlcuBirimleri = set([
    "adet", "tane", "gr", "gr.", "kg", "kg.", "litre", "ml", "ml.", "küp",
    "dilim", "diş", "–", "tutam", "haşlanmış", "rendelenmiş", "½", "¼",
    "tepeleme", "¾", "haşlamak", "için", "dal", "küçük", "büyük", "iri",
    "boy", "rende", "pişirmek", "avuç", "kızartmak", "haşlamış", "doğranmış",
    "közlenmiş", "ezilmiş", "bağ", "yaprak", "dolu", "hafif", "ince", "didiklenmiş"
])

def sayi(k): #Tarif içerisinde sayısal ifadeler varsa onları bulup temizler
    try:
        float(k.replace(",","."))
        return True
    except ValueError:
        return False
    
def temizlenmisMalzemeCumlesi(cumle):
    cumle=cumle.lower() #Cümleyi küçük harflere dönüştürür
    
    for ifade in cokluIfadeler:
        cumle=cumle.replace(ifade,"")
    
    kelimeler=cumle.split() # Cümleyi bosluklara göre parçalar
    
    anlamli_kelimeler=[
        k for k in kelimeler
        if k not in turkish_stopword and #ile,ve,bir gibi bağlaçlar çıkarılır
           k not in tekliOlcuBirimleri and 
           not sayi(k) #Sayılar çıkartılır
    ]
    
    sonuc=" "
    for kelime in anlamli_kelimeler:
        sonuc+= kelime +" "
    sonuc=sonuc.strip()
    return sonuc
    

        
def veriCekme(url):
    tarifDetaylari=[]
    try:
        response=requests.get(url)
        soup=BeautifulSoup(response.text,"html.parser")
        
        baslik_tag=soup.find("h1",{"class":"entry-title"})
        baslik=baslik_tag.text.strip() if baslik_tag else "Başlık Bulunamadı!"
        
        malzeme_div=soup.find("div",{"class":"mlz"})
        icindekiler= []
        
        if malzeme_div: # Yemek tarifi malzemeleri kısmı doluysa aşağıdaki işlemler yapılır
            for htmlOgesi in malzeme_div.children: #children html ögesinin altındaki etiketlere(span,br gibi etiketlere) erişimi sağlar
                if htmlOgesi.name=='br':
                    continue
                if isinstance(htmlOgesi,str) and htmlOgesi.strip(): #Eğer html ögesi içerisindeki string text ise ve boş değilse bu metin icindekiler[] kısmına eklenir
                    icindekiler.append(htmlOgesi.strip().strip('"'))
                #Metin başında ve sonunda çift tırnak varsa onları da kaldırır  
                elif hasattr(htmlOgesi,'text') and htmlOgesi.text.strip(): #Eğer html ögesi bir metin içerimiyorsa (br,span) içerisindeki metin içeriğini alır
                    icindekiler.append(htmlOgesi.text.strip().strip('"'))
        
        temizlenmisMalzeme=[temizlenmisMalzemeCumlesi(item) for item in icindekiler if item.strip()]
         
        tarifDetaylari.append({
            "Başlık": baslik,
            "İçindekiler":temizlenmisMalzeme
        })   
    
    except Exception as e:
        print(f"Hata!") 
    return tarifDetaylari   


def kategoriDetaylari(kategoriURL,sayfaSayisi=1):
    
    tarifDetaylari=[]
    for sayfa in range(1,sayfaSayisi+1):
        url=f"{kategoriURL.rstrip('/')}/page/{sayfa}"
        response=requests.get(url) #sayfa içeriği çekilir
        soup=BeautifulSoup(response.text,"html.parser")
        
        tarifLink=[]
        for tarif in soup.find_all("article",{"class":"post"}): #<article> içerisindeki bağlantılar bulunur
            link=tarif.find("a")["href"]
            if link not in tarifLink:
                tarifLink.append(link)
                
        for link in tarifLink: #her link için veriCekme() fonksiyonu çağrılır
            tarifler=veriCekme(link) 
            tarifDetaylari.extend(tarifler)
    
    return tarifDetaylari


if __name__ == "__main__":
    kategoriler={
        "corbalar": ("https://www.ardaninmutfagi.com/category/corbalar",3),
        "et-yemekleri":("https://www.ardaninmutfagi.com/category/et-yemekleri",3),
        "balik-yemekleri":("https://www.ardaninmutfagi.com/category/balik-yemekleri",2),
        "tavuk-yemekleri":("https://www.ardaninmutfagi.com/category/tavuk-yemekleri",3),
        "sebze-yemekleri":("https://www.ardaninmutfagi.com/category/sebze-yemekleri",3),
        "salatalar":("https://www.ardaninmutfagi.com/category/salatalar",3),
        "hamurlular":("https://www.ardaninmutfagi.com/category/hamurlular",6),
        "mezeler":("https://www.ardaninmutfagi.com/category/mezeler",3),
        "soslar":("https://www.ardaninmutfagi.com/category/soslar",2),
        "tatlilar":("https://www.ardaninmutfagi.com/category/tatlilar",3),
        "icecekler":("https://www.ardaninmutfagi.com/category/icecekler",3),
        "makarna-pilav":("https://www.ardaninmutfagi.com/category/makarnalar-pilavlar",3)
    }               
    
    tumTarifler=[]
    
    for isim,(url,sayfaSayisi) in kategoriler.items():
        print(f"\nKategori: {isim} işleniyor ({sayfaSayisi} sayfa)...")
        tumTarifler.extend(kategoriDetaylari(url,sayfaSayisi=sayfaSayisi))
        
    with open("dataset.json", "w", encoding="utf-8") as f:
        json.dump(tumTarifler, f, ensure_ascii=False, indent=2)
        
    print(f"\n Toplam tarif sayısı: {len(tumTarifler)} adet. 'dataset.json' dosyasına kaydedildi.")
   #ilk commit