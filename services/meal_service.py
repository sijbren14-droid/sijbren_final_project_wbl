#-----------------------------------------------------------------------------------
#Request: afbeelding gebruiken en linken in datasset
#https://requests.readthedocs.io/en/latest/
#https://scrapeops.io/python-web-scraping-playbook/python-how-to-download-images/
#-----------------------------------------------------------------------------------
import requests

WIKI_API_URL = "https://en.wikipedia.org/w/api.php"
HEADERS = {
    "User-Agent": "WhoWillBeLunch/1.0 (educational project)"
}

def get_meal_image(meal):
    """
    Return local image if present,
    otherwise fetch first Wikipedia thumbnail using meal['wiki']
    """

    # lokale afbeelding
    if meal.get("image"):
        return f"/static/images/meals/{meal['image']}"

    # wikipedia afbeelding
    wiki_query = meal.get("wiki")
    if not wiki_query:
        return "/static/images/placeholder.png"

    return get_wikipedia_image(wiki_query)


def get_wikipedia_image(query):
    print("Wikipedia lookup:", query)

    params = {
        "action": "query",
        "titles": query,
        "prop": "pageimages",
        "format": "json",
        "pithumbsize": 400,
        "redirects": 1
    }

    try:
        r = requests.get(
            WIKI_API_URL,
            params=params,
            headers=HEADERS,
            timeout=5
        )

        if r.status_code != 200:
            print("Wikipedia HTTP error:", r.status_code)
            return "/static/images/placeholder.jpg"

        data = r.json()
        pages = data.get("query", {}).get("pages", {})

        if not pages:
            return "/static/images/placeholder.jpg"

        page = next(iter(pages.values()))
        return page.get("thumbnail", {}).get(
            "source",
            "/static/images/placeholder.jpg"
        )

    except Exception as e:
        print("Wikipedia error:", e)
        return "/static/images/placeholder.jpg"
