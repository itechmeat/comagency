from app.models.schemas.tweet import TweetDetails, TweetAuthor
from loguru import logger

def process_tweet_details(tweet) -> TweetDetails:
    """Convert Twitter API tweet object to TweetDetails model"""
    try:
        if not tweet:
            raise ValueError("Tweet object is None")
            
        # Get text and display text
        text = getattr(tweet, 'text', '')
        display_text = text
        
        # Process author information
        author = None
        if hasattr(tweet, 'user'):
            user = getattr(tweet, 'user', None)
            author = TweetAuthor(
                id=str(getattr(user, 'id', '0')),
                name=getattr(user, 'name', ''),
                username=getattr(user, 'screen_name', ''),
                profile_image_url=getattr(user, 'profile_image_url_https', None)
            )
        elif hasattr(tweet, 'author'):
            author = tweet.author

        if not author:
            raise ValueError("Tweet author information is missing")
            
        # Get media information - с дополнительными проверками
        media = []
        tweet_media = getattr(tweet, 'media', None)
        if tweet_media is not None:
            if isinstance(tweet_media, (list, tuple)):
                media = list(tweet_media)  # Преобразуем в список для безопасности
            else:
                logger.warning(f"Unexpected media type: {type(tweet_media)}")

        # Extract photo URLs from media safely
        photo_urls = []
        for item in media:
            if not isinstance(item, dict):
                continue
            if item.get('type') == 'photo' and item.get('ext_media_availability', {}).get('status') == 'Available':
                media_url = item.get('media_url_https')
                if media_url:
                    photo_urls.append(media_url)
        
        # Get base tweet attributes
        tweet_id = str(getattr(tweet, 'id', '0'))
        created_at = str(getattr(tweet, 'created_at', ''))
        lang = getattr(tweet, 'lang', '')
        retweet_count = getattr(tweet, 'retweet_count', 0)
        favorite_count = getattr(tweet, 'favorite_count', 0)
        
        # Get reply information
        in_reply_to_status_id = getattr(tweet, 'in_reply_to_status_id', None)
        in_reply_to_user_id = getattr(tweet, 'in_reply_to_user_id', None)
        in_reply_to_screen_name = getattr(tweet, 'in_reply_to_screen_name', None)
        in_reply_to = getattr(tweet, 'in_reply_to', None)
        
        # Handling display text for replies
        if in_reply_to_status_id:
            words = text.split()
            non_mention_words = [w for w in words if not w.startswith('@')]
            display_text = ' '.join(non_mention_words) if non_mention_words else text

        return TweetDetails(
            id=tweet_id,
            text=text,
            display_text=display_text.strip(),
            created_at=created_at,
            lang=lang,
            retweet_count=retweet_count,
            favorite_count=favorite_count,
            author=author,
            in_reply_to_status_id=str(in_reply_to_status_id) if in_reply_to_status_id else None,
            in_reply_to_user_id=str(in_reply_to_user_id) if in_reply_to_user_id else None,
            in_reply_to_screen_name=in_reply_to_screen_name,
            in_reply_to=str(in_reply_to) if in_reply_to else None,
            photo_urls=photo_urls,
            media=media
        )
    except Exception as e:
        logger.error(f"Error processing tweet details: {str(e)}")
        logger.debug(f"Tweet object: {tweet}")
        raise