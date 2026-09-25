import requests
import json
from bs4 import BeautifulSoup

def atualizar_jogos():
    url = "https://futmax.lat/wp-admin/admin-ajax.php?action=fav_home_schedule"
    headers = {"X-Requested-With": "XMLHttpRequest"}
    
    try:
        res = requests.get(url, headers=headers, timeout=15)
        data = res.json().get("data", {})
        soup = BeautifulSoup(data.get("upcoming_html", ""), "html.parser")
        links = soup.find_all("a")
        
        jogos = []
        for j in links:
            partes = [x.strip() for x in j.get_text(separator="|").split("|") if x.strip()]
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
                    "url": pagina_jogo 
                }
                jogos.append(jogo_info)

        with open("jogos_futmax.json", "w", encoding="utf-8") as f:
            json.dump(jogos, f, indent=2, ensure_ascii=False)
            
        print(f"Sucesso! {len(jogos)} jogos salvos.")
    except Exception as e:
        print(f"Erro ao atualizar jogos: {e}")

if __name__ == "__main__":
    atualizar_jogos()
