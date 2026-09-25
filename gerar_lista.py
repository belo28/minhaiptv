import requests
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin

API_URL = "https://futmax.lat/wp-admin/admin-ajax.php?action=fav_home_schedule"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "X-Requested-With": "XMLHttpRequest"
}


def obter_players(url):
    if not url:
        return []

    try:
        res = requests.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0",
                "Referer": "https://futmax.lat/"
            },
            timeout=20
        )

        res.raise_for_status()

        soup = BeautifulSoup(res.text, "html.parser")

        players = []

        for player in soup.select("#players a[data-url]"):
            endereco = player.get("data-url")

            if endereco:
                players.append({
                    "opcao": player.get("data-slot", ""),
                    "url": urljoin(url, endereco)
                })

        return players

    except Exception as e:
        print(f"Erro ao obter players: {e}")
        return []


def atualizar_jogos():
    try:
        res = requests.get(
            API_URL,
            headers=HEADERS,
            timeout=15
        )

        res.raise_for_status()

        data = res.json().get("data", {})

        soup = BeautifulSoup(
            data.get("upcoming_html", ""),
            "html.parser"
        )

        links = soup.find_all("a")

        jogos = []

        for j in links:
            partes = [
                x.strip()
                for x in j.get_text(separator="|").split("|")
                if x.strip()
            ]

            if len(partes) >= 7:
                pagina_jogo = j.get("href")

                jogo_info = {
                    "title": f"{partes[2]} vs {partes[6]} ({partes[0]})",
                    "campeonato": partes[0],
                    "horario": partes[1],
                    "time_casa": partes[2],
                    "data": partes[3],
                    "time_fora": partes[6],
                    "canal": partes[7] if len(partes) > 7 else "",
                    "url": pagina_jogo,
                    "disponivel": False,
                    "players": []
                }

                print(f"Processando: {jogo_info['title']}")

                jogo_info["players"] = obter_players(pagina_jogo)
                jogo_info["disponivel"] = len(jogo_info["players"]) > 0

                print(
                    f"  Players encontrados: "
                    f"{len(jogo_info['players'])}"
                )

                jogos.append(jogo_info)

        with open(
            "jogos_futmax.json",
            "w",
            encoding="utf-8"
        ) as f:
            json.dump(
                jogos,
                f,
                indent=2,
                ensure_ascii=False
            )

        print(f"\nSucesso! {len(jogos)} jogos salvos.")

    except Exception as e:
        print(f"Erro ao atualizar jogos: {e}")


if __name__ == "__main__":
    atualizar_jogos()
