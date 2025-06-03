from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
from mangum import Mangum

app = Flask(__name__)

HEADERS = {'User-Agent': 'Mozilla/5.0'}

def get_filmes(search_term=None, page=1):
    filmes = []

    # URL base
    if search_term:
        url = f"https://megafilmeshdz.cyou/?s={search_term.replace(' ', '+')}&page={page}"
    else:
        url = f"https://megafilmeshdz.cyou/category/terror/page/{page}/"

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        for article in soup.select("article"):
            link_tag = article.find("a", href=True)
            titulo_tag = article.find("h2")
            capa_tag = article.find("img")

            if link_tag and titulo_tag and capa_tag:
                filme_url = link_tag["href"]
                titulo = titulo_tag.get_text(strip=True)
                capa = capa_tag["src"]

                # Obter link de vídeo
                try:
                    filme_page = requests.get(filme_url, headers=HEADERS, timeout=10)
                    filme_soup = BeautifulSoup(filme_page.text, 'html.parser')
                    iframe = filme_soup.find("iframe")
                    video_link = iframe["src"] if iframe else None
                except Exception:
                    video_link = None

                tmdb_link = f"https://www.themoviedb.org/search?query={requests.utils.quote(titulo)}"

                filmes.append({
                    "titulo": titulo,
                    "url": video_link,
                    "capa": capa,
                    "tmdb_link": tmdb_link
                })

    except Exception as e:
        filmes.append({
            "titulo": "Erro ao buscar filmes",
            "url": None,
            "capa": None,
            "tmdb_link": None,
            "error": str(e)
        })

    return filmes

@app.route('/', methods=["GET"])
def index():
    search = request.args.get("search", "").strip()
    page = int(request.args.get("page", 1))
    filmes = get_filmes(search_term=search if search else None, page=page)
    return render_template("index.html", filmes=filmes, search=search, page=page)

@app.route('/favoritos')
def favoritos():
    return render_template('favoritos.html')

handler = Mangum(app)

if __name__ == "__main__":
    app.run(debug=True)







