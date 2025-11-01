import requests, os, time, re, textwrap
from bs4 import BeautifulSoup
from collections import Counter
from tabulate import tabulate

class ElPaisScraper:
    def __init__(self):
        self.base_url = "https://elpais.com"
        self.opinion_url = f"{self.base_url}/opinion/"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept-Language": "es-ES,es;q=0.9"
        })
        # RapidAPI (Translation API) configuration
        self.rapidapi_key = "Your rapid api key"  # replace with your key
        self.translate_url = "https://rapid-translate-multi-traduction.p.rapidapi.com/t"

    def scrape_opinion_articles(self):
        print("Fetching the first 5 articles from Opinion section of El País...")
        r = self.session.get(self.opinion_url)
        soup = BeautifulSoup(r.text, "html.parser")

        # Trying multiple css selectors - using this as El pais sometimes uses h2 and h3 instead of article tags 
        selectors = ['article a[href*="/opinion/"]', 'h2 a[href*="/opinion/"]', 'h3 a[href*="/opinion/"]']
        links = []
        for s in selectors:
            links += [a.get("href") for a in soup.select(s) if "/opinion/" in a.get("href", "")]
        links = [self.base_url + l if not l.startswith("http") else l for l in dict.fromkeys(links)]
        
        # Visit each article and scrape content
        articles = []
        for i, href in enumerate(links[:8], 1):
            print(f"\nArticle {i}: {href}")
            art = self.scrape_article(href)
            if art: articles.append(art)
            if len(articles) >= 5: break
            time.sleep(1) # small delay to avoid rate-limiting
        return articles

    def scrape_article(self, url):
        try:
            r = self.session.get(url)
            soup = BeautifulSoup(r.text, "html.parser")
            # Extract title and main content
            title = next((t.get_text(strip=True) for t in soup.select("h1, .a_t, header h1") if t), "Sin título")
            content = next((c.get_text(strip=True) for c in soup.select(".a_c, .articulo-contenido, div[class*='content'], div[class*='body']") if c), "Sin contenido")
            img_tag = next((img for img in soup.select("figure img, .a_m img, img[src*='jpg'], img[src*='jpeg'], img[src*='png']") if img.get("src")), None)
            img_url = None
            if img_tag:
                src = img_tag.get("src")
                if src.startswith("//"): img_url = "https:" + src
                elif src.startswith("http"): img_url = src
                else: img_url = self.base_url + src
            return {"title": title, "content": (content[:500] + "...") if len(content) > 500 else content, "image_url": img_url, "url": url}
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None

    def download_image(self, url, name):  # function to download image and save in images directory 
        if not url: return None
        try:
            os.makedirs("images", exist_ok=True)
            r = self.session.get(url)
            if r.status_code == 200:
                path = f"images/{name}"
                with open(path, "wb") as f: f.write(r.content)
                return path
        except Exception as e:
            print(f"Error downloading image: {e}")
        return None

    def translate_titles(self, articles): # Trnslate titles using Rapid API
        headers = {
            "X-RapidAPI-Key": self.rapidapi_key,
            "X-RapidAPI-Host": "rapid-translate-multi-traduction.p.rapidapi.com",
            "Content-Type": "application/json"
        }
        titles = [a["title"] for a in articles]
        payload = {"from": "es", "to": "en", "q": titles}
        try:
            resp = self.session.post(self.translate_url, json=payload, headers=headers, timeout=15)
            data = resp.json()
            if isinstance(data, list):
                translated = [d.get("translatedText", t) if isinstance(d, dict) else str(d) for d, t in zip(data, titles)]
            else:
                translated = titles
            return translated
        except Exception as e:
            print(f"Translation failed: {e}")
            return titles

    def analyze_repeated_words(self, translated_titles):
        words = re.findall(r'\b[a-zA-Z]+\b', " ".join(translated_titles).lower()) 
        counter = Counter(words)
        repeated = {w: c for w, c in counter.items() if c >= 2}  # repeated words
        repeated = dict(sorted(repeated.items(), key=lambda x: x[1], reverse=True))  # sort by frequency
        print("\n Repeated Words :")
        print(tabulate(repeated.items(), headers=["Word", "Count"], tablefmt="fancy_grid")) if repeated else print("None found.")
        return repeated


def main():
    scraper = ElPaisScraper()
    arts = scraper.scrape_opinion_articles()
    if not arts:
        print("No articles found. Site structure may have changed.")
        return

    translated = scraper.translate_titles(arts)

    table = []
    for i, a in enumerate(arts):
        img_path = scraper.download_image(a["image_url"], f"article_{i+1}.jpg") if a["image_url"] else "None"
        table.append([
            textwrap.fill(a["title"], 60),
            textwrap.fill(translated[i], 60),
            textwrap.fill(a["content"], 80),
            textwrap.fill(a["url"], 60),
            img_path or "None"
        ])

    print("\nTable showing Original Title (ES), Translated Title (EN), Content, URL, and Image Path\n")
    print(tabulate(
        table,
        headers=["Original Title in Spanish", "Translated Title in English", "Content", "URL", "Image Path"],
        tablefmt="fancy_grid",
        maxcolwidths=[30, 30, 50, 30, 20],
        stralign="left"
    ))

    scraper.analyze_repeated_words(translated)


if __name__ == "__main__":
    main()
