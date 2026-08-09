import urllib.request
import feedparser
import json
import os
import sys

URL_RSS = "https://app.ebando.es/api/v1/rss/esplugadefrancoli"
FITXER_JSON = "noticies.json"

print(f"Iniciant la connexió a: {URL_RSS}")

req = urllib.request.Request(
    URL_RSS, 
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
)

try:
    with urllib.request.urlopen(req, timeout=15) as response:
        contingut_rss = response.read()
    print("✓ Connexió establerta i dades descarregades correctament.")
    
    feed = feedparser.parse(contingut_rss)
    print(f"✓ RSS analitzat. S'han trobat {len(feed.entries)} entrades disponibles.")
    
except urllib.error.HTTPError as e:
    print(f"❌ Error de servidor (HTTP {e.code}): {e.reason}", file=sys.stderr)
    sys.exit(1)
except urllib.error.URLError as e:
    print(f"❌ Error de xarxa o timeout: {e.reason}", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"❌ Error inesperat en descarregar: {e}", file=sys.stderr)
    sys.exit(1)

# Llegir base de dades existent
if os.path.exists(FITXER_JSON):
    with open(FITXER_JSON, "r", encoding="utf-8") as f:
        try:
            noticies_guardades = json.load(f)
            if not isinstance(noticies_guardades, list):
                noticies_guardades = []
        except json.JSONDecodeError:
            noticies_guardades = []
else:
    noticies_guardades = []

guids_existents = {n["guid"] for n in noticies_guardades}
nous_comptats = 0

for entrada in feed.entries:
    if entrada.guid not in guids_existents:
        contingut_html = ""
        if "content" in entrada:
            contingut_html = entrada.content.value
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

with open(FITXER_JSON, "w", encoding="utf-8") as f:
    json.dump(noticies_guardades, f, ensure_ascii=False, indent=4)

print(f"✓ Base de dades actualitzada. Nous bandos afegits: {nous_comptats}")
print(f"Total acumulats: {len(noticies_guardades)}")
