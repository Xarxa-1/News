import feedparser
import json
import os

URL_RSS = "https://ebando.es"
FITXER_JSON = "noticies.json"

# 1. Descarregar i analitzar el canal RSS
feed = feedparser.parse(URL_RSS)

# 2. Carregar la base de dades JSON si ja existeix
if os.path.exists(FITXER_JSON):
    with open(FITXER_JSON, "r", encoding="utf-8") as f:
        noticies_guardades = json.load(f)
else:
    noticies_guardades = []

# Guardem els ID per no repetir bandos
guids_existents = {n["guid"] for n in noticies_guardades}

# 3. Recórrer els bandos
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

# 4. Desar la base de dades JSON
with open(FITXER_JSON, "w", encoding="utf-8") as f:
    json.dump(noticies_guardades, f, ensure_ascii=False, indent=4)

print(f"Procés finalitzat. Total de bandos: {len(noticies_guardades)}")
