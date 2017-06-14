from application.settings import get_option
import requests
import requests.exceptions


class HackerNewsLoader:

    @staticmethod
    def get_entry_data(item):
        permalink = "https://news.ycombinator.com/item?id=" + str(item["id"])
        url = item.get("url", permalink)
        return {
            "title": item["title"],
            "url": url,
            "digest": str(item["id"]),
            "permalink": permalink,
            "score": item["score"],
            "content": ""
        }

    def load(self, source):
        entries = []

        data = requests.get(
            "https://hacker-news.firebaseio.com/v0/{}stories.json".format(source)
        ).json()

        for item_id in data[:30]:
            item = requests.get(
                "https://hacker-news.firebaseio.com/v0/item/{}.json".format(item_id)
            ).json()
            entry_data = self.get_entry_data(item)
            entries.append(entry_data)

        return entries


def load(sources):
    if not get_option("loaders.hackernews.enabled", False):
        return []

    loader = HackerNewsLoader()
    data = []
    for source in sources:
        try:
            source_entries = loader.load(source)
        except requests.exceptions.RequestException:
            continue

        data.append({
            "source": source,
            "entries": source_entries
        })

    return data
