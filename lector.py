name: Execució Diària eBando Espluga

on:
  schedule:
    - cron: '0 9 * * *'  # S'executa cada dia a les 09:00 UTC
  workflow_dispatch:     # Permet provar-ho manualment amb el botó "Run workflow"

permissions:
  contents: write        # Permet que l'script guardi el fitxer noticies.json al repositori
  pages: write           # Permet activar GitHub Pages
  id-token: write

jobs:
  run-agent:
    runs-on: ubuntu-latest
    steps:
      - name: Baixar el codi del repositori
        uses: actions/checkout@v4

      - name: Configurar Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Instal·lar llibreries de Python
        run: pip install feedparser

      - name: Executar l'agent de l'eBando
        run: python agent.py  # Assegura't que el teu fitxer de Python es diu exactament així

      # DESA ELS CANVIS DE LES NOTÍCIES AL TEU GITHUB
      - name: Guardar noticies.json al repositori
        run: |
          git config --global user.name "GitHub Actions"
          git config --global user.email "actions@github.com"
          git add noticias.json || true
          git commit -m "Actualització automàtica de bandos (JSON)" || true
          git push || true

      # ENVIAMENT A LA WEB PÚBLICA
      - name: Configurar GitHub Pages
        uses: actions/configure-pages@v5

      - name: Pujar fitxers a internet
        uses: actions/upload-pages-artifact@v3
        with:
          path: '.'      # Això publica l'index.html i el noticies.json a la teva URL pública

      - name: Desplegar el lloc web oficial
        uses: actions/deploy-pages@v4
