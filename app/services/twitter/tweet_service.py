import asyncio
import os

from loguru import logger
from twikit import Client

from app.config import get_twitter_credentials
from app.models.schemas.tweet import DBTweet, TwitterTweet

USE_TWITTER_MOCKS = os.getenv("USE_TWITTER_MOCKS", "false").lower() == "true"

ExecutionStopError = (asyncio.CancelledError, KeyboardInterrupt, SystemError)

class TwitterClient:
    def __init__(self):
        self.client = Client('en-US')
        self.client.load_cookies('cookies.json')
        self.credentials = get_twitter_credentials()
        self.is_authenticated = False
        self.auth_retries = 0
        self.max_retries = 3
        self.retry_delay = 30 # seconds
        logger.info(f'🙍‍♂️  Username: {self.credentials["username"]}')

    async def ensure_authenticated(self):
        if USE_TWITTER_MOCKS:
            logger.info("📙  Mock mode is enabled; skipping authentication.")
            self.is_authenticated = True
            return True

        if self.is_authenticated:
            return True
            
        while self.auth_retries < self.max_retries:
            try:
                await self.authenticate()
                return True
            except Exception as e:
                self.auth_retries += 1
                logger.error(f'Authentication attempt {self.auth_retries} failed: {str(e)}')
                
                if self.auth_retries < self.max_retries:
                    delay = self.retry_delay * (2 ** (self.auth_retries - 1))  # Exponential backoff
                    logger.info(f'⏳  Waiting {delay} seconds before retry...')
                    await asyncio.sleep(delay)
                else:
                    logger.error('Max authentication retries reached')
                    raise
        
        return False

    async def authenticate(self):
        logger.info(f'🔑  Authenticating as {self.credentials["username"]}...')
        try:
            # First try to verify if existing cookies are valid
            if await self._verify_existing_session():
                logger.info('✅  Using existing session')
                self.is_authenticated = True
                return

            # If not, perform full authentication
            await self._perform_full_authentication()
            
        except ExecutionStopError:
            raise
        except Exception as e:
            self.is_authenticated = False
            logger.error(f'❌  Authentication failed: {str(e)}')
            raise

    async def _verify_existing_session(self) -> bool:
        """Verify if existing cookies are valid"""
        try:
            # Try a simple API call to verify session
            await self.client.get_timeline(count=1)
            return True
        except ExecutionStopError:
            raise
        except Exception:
            return False

    async def _perform_full_authentication(self):
        """Perform full authentication process"""
        self.client = Client('en-US')
        
        # Perform login
        await self.client.login(
            auth_info_1=self.credentials['username'],
            auth_info_2=self.credentials['email'],
            password=self.credentials['password']
        )
        
        # Save new cookies
        self.client.save_cookies('cookies.json')
        self.is_authenticated = True
        self.auth_retries = 0  # Reset retry counter on success
        logger.info('✅  Authentication successful')

    @staticmethod
    def get_photo_urls(media_list):
        if not media_list:
            return []
        
        return [
            item['media_url_https'] 
            for item in media_list 
            if item.get('type') == 'photo' 
            and item.get('ext_media_availability', {}).get('status') == 'Available'
        ]

    def process_tweet(self, tweet, tweet_count):
        if USE_TWITTER_MOCKS:
            photo_urls = self.get_photo_urls(tweet['media'] if 'media' in tweet else [])
            result = {
                'tweet_id': tweet['id'],
                'tweet_user_name': tweet['user']['name'],
                'tweet_user_nick': tweet['user']['screen_name'],
                'text': tweet['text'],
                'created_at': str(tweet['created_at']),
                'retweets': tweet['retweet_count'],
                'likes': tweet['favorite_count'],
                'photo_urls': photo_urls,
                'tweet_lang': tweet['lang'],
            }
        else:
            photo_urls = self.get_photo_urls(tweet.media if hasattr(tweet, 'media') else [])
            result = {
                'tweet_id': tweet.id,
                'tweet_user_name': tweet.user.name,
                'tweet_user_nick': tweet.user.screen_name,
                'text': tweet.text,
                'created_at': str(tweet.created_at),
                'retweets': tweet.retweet_count,
                'likes': tweet.favorite_count,
                'photo_urls': photo_urls,
                'tweet_lang': tweet.lang,
            }
        
        return result

async def save_twitter_tweet(supabase: Client, tweet_data: dict) -> DBTweet:
    try:
        twitter_tweet = TwitterTweet.model_validate(tweet_data)
        db_tweet = twitter_tweet.to_db_tweet()

        existing = supabase.table('tweets')\
            .select('*')\
            .eq('id', db_tweet.id)\
            .execute()

        if existing.data:
            logger.debug(f"Updating tweet {db_tweet.id}")
            update_data = {
                'id': db_tweet.id,
                'text': db_tweet.text,
                'author_id': db_tweet.author_id,
                'author_name': db_tweet.author_name,
                'author_username': db_tweet.author_username,
                'author_photo': db_tweet.author_photo,
                'lang': db_tweet.lang,
                'retweets_count': db_tweet.retweets_count,
                'likes_count': db_tweet.likes_count,
                'photo_urls': db_tweet.photo_urls,
                'media': db_tweet.media,
                'meta_data': db_tweet.meta_data,
                'updated_at': 'now()'
            }

            result = supabase.table('tweets')\
                .upsert(update_data, on_conflict='id')\
                .execute()
        else:
            logger.debug(f"Creating new tweet {db_tweet.id}")
            result = supabase.table('tweets')\
                .insert(db_tweet.model_dump())\
                .execute()

        if not result.data:
            raise Exception("No data returned from database operation")

        return DBTweet.model_validate(result.data[0])

    except Exception as e:
        logger.error(f"Error saving tweet: {str(e)}")
        raise Exception(f"Error saving tweet: {str(e)}") from e