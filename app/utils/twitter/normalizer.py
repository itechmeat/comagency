from typing import Any, Dict

def normalize_tweet_data(tweet_data: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize tweet data to a consistent format for TwitterTweet model"""
    return {
        'id': tweet_data['id'],
        'text': tweet_data['text'],
        'display_text': tweet_data['display_text'],
        'retweet_count': tweet_data['retweet_count'],
        'favorite_count': tweet_data['favorite_count'],
        'author': {
            'id': tweet_data['author']['id'],
            'name': tweet_data['author']['name'],
            'username': tweet_data['author']['username'],
            'profile_image_url': tweet_data['author']['profile_image_url']
        },
        'lang': tweet_data['lang'],
        'photo_urls': tweet_data.get('photo_urls', []),
        'media': tweet_data.get('media', []),
        'in_reply_to_status_id': tweet_data.get('in_reply_to_status_id'),
        'in_reply_to_user_id': tweet_data.get('in_reply_to_user_id'),
        'in_reply_to_screen_name': tweet_data.get('in_reply_to_screen_name'),
        'in_reply_to': tweet_data.get('in_reply_to')
    }

def normalize_search_tweet_data(tweet_data: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize tweet data from search results to a consistent format"""

    entities = tweet_data.get('entities') or {}
    media = entities.get('media') or []
    media = media if isinstance(media, list) else []

    photo_urls = [
        item['media_url_https']
        for item in media
        if isinstance(item, dict) and item.get('type') == 'photo'
    ]

    return {
        'id': tweet_data['tweet_id'],
        'text': tweet_data['text'],
        'display_text': tweet_data['text'],
        'retweet_count': tweet_data['retweets'],
        'favorite_count': tweet_data['likes'],
        'author': {
            'id': tweet_data['tweet_user_nick'],
            'name': tweet_data['tweet_user_name'],
            'username': tweet_data['tweet_user_nick'],
            'profile_image_url': ''
        },
        'lang': tweet_data['tweet_lang'],
        'photo_urls': photo_urls,
        'media': media,
        'in_reply_to_status_id': None,
        'in_reply_to_user_id': None,
        'in_reply_to_screen_name': None,
        'in_reply_to': None
    }