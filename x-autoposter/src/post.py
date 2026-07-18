"""Post to X via the official API: v1.1 media upload + v2 create tweet."""

import os

import tweepy


def _credentials() -> dict:
    creds = {
        "consumer_key": os.environ["X_API_KEY"],
        "consumer_secret": os.environ["X_API_SECRET"],
        "access_token": os.environ["X_ACCESS_TOKEN"],
        "access_token_secret": os.environ["X_ACCESS_TOKEN_SECRET"],
    }
    return creds


def post_to_x(text: str, image_path: str) -> str:
    """Upload the image, publish the post, and return the new post's URL."""
    creds = _credentials()
    auth = tweepy.OAuth1UserHandler(
        creds["consumer_key"],
        creds["consumer_secret"],
        creds["access_token"],
        creds["access_token_secret"],
    )
    media = tweepy.API(auth).media_upload(image_path)

    client = tweepy.Client(**creds)
    response = client.create_tweet(text=text, media_ids=[media.media_id])
    return f"https://x.com/i/status/{response.data['id']}"
