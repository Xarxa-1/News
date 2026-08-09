import urllib.request
import feedparser
import json
import os

URL_RSS = "https://app.ebando.es/api/v1/rss/esplugadefrancoli"
FITXER_JSON = "noticies.json"

print(f"Descarregant dades de l'eBando: {URL_RSS}")

# Forçar la capçalera de navegador per seguretat contra bloquejos
req = urllib.request.Request(
    URL_RSS, 
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
)

try:
    with urllib.request.urlopen(req, timeout=20) as response:
        contingut_rss = response.read()
    feed = feedparser.parse(contingut_rss)
    print(f"RSS llegit. S'han detectat {len(feed.entries)} entrades.")
except Exception as e:
    print(f"Avís: No s'ha pogut baixar l'RSS actual: {e}")
    feed = None

# Llegir base de dades existent de manera segura
noticies_guardades = []
if os.path.exists(FITXER_JSON):
    try:
        with open(FITXER_JSON, "r", encoding="utf-8") as f:
            noticies_guardades = json.load(f)
            if not isinstance(noticies_guardades, list):
                noticies_guardades = []
    except Exception:
        print("El fitxer JSON antic estava buit o corrupte. Es reiniciarà de zero.")
        noticies_guardades = []

guids_existents = {n["guid"] for n in noticies_guardades if "guid" in n}

# Integrar les noves entrades trobades
nous_comptats = 0
if feed and feed.entries:
    for entrada in feed.entries:
        if getattr(entrada, "guid", None) and entrada.guid not in guids_existents:
            contingut_html = ""
            if "content" in entrada:
                contingut_html = entrada.content[0].value if isinstance(entrada.content, list) else entrada.content.value
            elif "summary" in entrada:
                contingut_html = entrada.summary

            nou_bando = {
                "guid": entrada.guid,
                "title": entrada.title,
                "pubDate": getattr(entrada, "published", "Sense data"),
                "link": entrada.link,
                "content": contingut_html
            }
            noticies_guardades.append(nou_bando)
            nous_comptats += 1

# Desar la base de dades actualitzada a l'arrel
with open(FITXER_JSON, "w", encoding="utf-8") as f:
    json.dump(noticies_guardades, f, ensure_ascii=False, indent=4)

print(f"Procés completat. Nous bandos afegits: {nous_comptats}. Total: {len(noticies_guardades)}")
