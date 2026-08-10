#!/usr/bin/env python3
""" 
Agent d'actualitat municipal per Esplugues de Francolí
Recull notícies de l'RSS oficial i les guarda en format JSON
"""

import requests
import feedparser
import json
import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

# Configuració de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuració
RSS_URL = "https://app.ebando.es/api/v1/rss/esplugadefrancoli"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
HEADERS = {
    'User-Agent': USER_AGENT,
    'Accept': 'application/rss+xml, application/xml, text/xml, */*',
    'Accept-Language': 'ca,es;q=0.9,en;q=0.8',
    'Cache-Control': 'no-cache'
}
JSON_FILE = "noticies.json"
MAX_NOTICIES = 200  # 🆕 Límit per evitar que el fitxer creixi indefinidament

def obtenir_noticies_rss() -> List[Dict[str, Any]]:
    """Obté les notícies de l'RSS amb headers per evitar bloquejos"""
    try:
        logger.info(f"Descarregant RSS de: {RSS_URL}")
        response = requests.get(RSS_URL, headers=HEADERS, timeout=30)
        response.raise_for_status()
        
        # Parsejar el contingut RSS
        feed = feedparser.parse(response.content)
        
        if feed.bozo:
            # No tots els errors bozo són crítics
            logger.warning(f"Problema menor amb el parseig del RSS: {feed.bozo_exception}")
        
        noticies = []
        for entry in feed.entries:
            # 🆕 Millor generació de GUID
            guid = entry.get('guid', '')
            if not guid:
                # Fallback: link + title com a identificador compost
                guid = f"{entry.get('link', '')}_{entry.get('title', '')}"
                if not guid or guid == "_":
                    continue
            
            # Extreure data de publicació
            published = entry.get('published', entry.get('pubDate', ''))
            if published:
                try:
                    from email.utils import parsedate_to_datetime
                    pub_date = parsedate_to_datetime(published)
                    published_iso = pub_date.isoformat()
                except (ValueError, TypeError):
                    # Si no es pot parsejar, guardar com a text
                    published_iso = published
            else:
                published_iso = datetime.now().isoformat()
            
            noticia = {
                'guid': guid,
                'title': entry.get('title', 'Sense títol'),
                'link': entry.get('link', ''),
                'published': published_iso,
                'summary': entry.get('summary', entry.get('description', 'Sense resum')),
                'fetched_at': datetime.now().isoformat()
            }
            noticies.append(noticia)
        
        logger.info(f"Obtingudes {len(noticies)} notícies de l'RSS")
        return noticies
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error descarregant RSS: {e}")
        return []
    except Exception as e:
        logger.error(f"Error inesperat: {e}")
        return []

def carregar_noticies_existents() -> List[Dict[str, Any]]:
    """Carrega les notícies existents del fitxer JSON"""
    if os.path.exists(JSON_FILE):
        try:
            with open(JSON_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.error(f"Error decodificant {JSON_FILE}, començant de nou")
            return []
        except Exception as e:
            logger.error(f"Error carregant {JSON_FILE}: {e}")
            return []
    return []

def guardar_noticies(noticies: List[Dict[str, Any]]) -> bool:
    """Guarda les notícies al fitxer JSON"""
    try:
        # Ordenar per data de publicació (més recent primer)
        noticies.sort(key=lambda x: x.get('published', ''), reverse=True)
        
        # 🆕 Limitar el nombre de notícies
        if len(noticies) > MAX_NOTICIES:
            logger.info(f"Truncant notícies de {len(noticies)} a {MAX_NOTICIES}")
            noticies = noticies[:MAX_NOTICIES]
        
        with open(JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(noticies, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Guardades {len(noticies)} notícies a {JSON_FILE}")
        return True
    except Exception as e:
        logger.error(f"Error guardant {JSON_FILE}: {e}")
        return False

def actualitzar_noticies(force: bool = False) -> None:
    """Funció principal: obté notícies noves i actualitza el fitxer JSON"""
    # 🆕 Paràmetre force per recarregar totes les notícies
    if force:
        noticies_existents = []
        guids_existents = set()
        logger.info("Mode FORCE: recarregant totes les notícies")
    else:
        noticies_existents = carregar_noticies_existents()
        guids_existents = {n.get('guid') for n in noticies_existents if n.get('guid')}
        logger.info(f"Carregades {len(noticies_existents)} notícies existents")
    
    # Obtenir noves notícies
    noves_noticies = obtenir_noticies_rss()
    if not noves_noticies:
        logger.warning("No s'han obtingut notícies noves")
        return
    
    # Filtrar notícies noves
    noticies_per_afegir = []
    for noticia in noves_noticies:
        if noticia['guid'] not in guids_existents:
            noticies_per_afegir.append(noticia)
            logger.info(f"Nova notícia: {noticia['title'][:50]}...")
    
    if not noticies_per_afegir:
        logger.info("No hi ha notícies noves per afegir")
        return
    
    # Combinar i guardar
    noticies_totals = noticies_per_afegir + noticies_existents
    if guardar_noticies(noticies_totals):
        logger.info(f"Afegides {len(noticies_per_afegir)} notícies noves")
    else:
        logger.error("Error guardant les notícies")

if __name__ == "__main__":
    actualitzar_noticies()
