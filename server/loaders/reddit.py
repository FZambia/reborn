from application.settings import get_option
import praw
import prawcore.exceptions


DEFAULT_USER_AGENT = 'Reborn Loader v0.1'


class RedditLoader:

    def __init__(self, client_id, client_secret, user_agent=None):
        self.r = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent or DEFAULT_USER_AGENT
        )

    @staticmethod
    def get_entry_data(submission):
        title = submission.title
        url = submission.url
        permalink = submission.permalink
        score = submission.score
        return {
            "title": title,
            "url": url,
            "digest": submission.id,
            "permalink": "https://reddit.com" + permalink,
            "score": score,
            "content": submission.media_embed['content'] if submission.media_embed else ""
        }

    def load(self, source):
        entries = []
        submissions = self.r.subreddit(source).hot(limit=20)
        for submission in submissions:
            entry_data = self.get_entry_data(submission)
            entries.append(entry_data)
        return entries


def load(sources):
    if not get_option("loaders.reddit.enabled", False):
        return []

    loader = RedditLoader(
        get_option("loaders.reddit.client_id", ""),
        get_option("loaders.reddit.secret", ""),
        user_agent=get_option("loaders.reddit.user_agent", "")
    )
    data = []
    for source in sources:
        try:
            source_entries = loader.load(source)
        except prawcore.exceptions.NotFound:
            continue

        data.append({
            "source": source,
            "entries": source_entries
        })

    return data
