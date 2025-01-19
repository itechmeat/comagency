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