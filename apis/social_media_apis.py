import tweepy
import logging
from typing import List, Dict, Optional
from config import Config
from textblob import TextBlob

logger = logging.getLogger(__name__)

class TwitterAPI:
    """واجهة Twitter/X API للحصول على المنشورات والأحاديث"""
    
    def __init__(self):
        self.bearer_token = Config.TWITTER_BEARER_TOKEN
        if self.bearer_token:
            self.client = tweepy.Client(bearer_token=self.bearer_token)
        else:
            self.client = None
            logger.warning("Twitter API key غير مكون")
    
    def search_tweets(self, query: str, max_results: int = 100, 
                     lang: str = 'ar', tweet_fields: List[str] = None) -> Optional[List[Dict]]:
        """البحث عن التغريدات"""
        if not self.client:
            logger.error("Twitter API client غير مهيأ")
            return None
        
        try:
            if tweet_fields is None:
                tweet_fields = ['created_at', 'author_id', 'public_metrics', 'lang']
            
            # إضافة اللغة والحد من النتائج
            search_query = f"{query} lang:{lang} -is:retweet"
            
            tweets = self.client.search_recent_tweets(
                query=search_query,
                max_results=min(max_results, 100),
                tweet_fields=tweet_fields,
                expansions=['author_id'],
                user_fields=['username', 'verified', 'public_metrics']
            )
            
            if tweets.data:
                users = {user.id: user for user in (tweets.includes.get('users', []) if tweets.includes else [])}
                
                results = []
                for tweet in tweets.data:
                    author = users.get(tweet.author_id, None)
                    results.append({
                        'id': tweet.id,
                        'text': tweet.text,
                        'created_at': tweet.created_at,
                        'author_id': tweet.author_id,
                        'author_username': author.username if author else 'unknown',
                        'author_verified': author.verified if author else False,
                        'likes': tweet.public_metrics.get('like_count', 0),
                        'retweets': tweet.public_metrics.get('retweet_count', 0),
                        'replies': tweet.public_metrics.get('reply_count', 0)
                    })
                
                logger.info(f"تم جلب {len(results)} تغريدة عن {query}")
                return results
            
            return []
        
        except Exception as e:
            logger.error(f"خطأ في البحث عن التغريدات: {str(e)}")
            return None
    
    def get_trending_topics(self) -> Optional[List[str]]:
        """الحصول على الموضوعات الرائجة (يتطلب API مدفوع)"""
        logger.info("الحصول على الموضوعات الرائجة يتطلب API مدفوع من Twitter")
        return None
    
    def analyze_sentiment(self, text: str) -> Dict:
        """تحليل المشاعر في النص"""
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            
            if polarity > 0.1:
                sentiment = 'positive'
            elif polarity < -0.1:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            return {
                'sentiment': sentiment,
                'polarity': polarity,
                'subjectivity': blob.sentiment.subjectivity
            }
        
        except Exception as e:
            logger.error(f"خطأ في تحليل المشاعر: {str(e)}")
            return {'sentiment': 'neutral', 'polarity': 0, 'subjectivity': 0}
    
    def track_coin_mentions(self, coin_name: str, symbol: str, 
                           max_results: int = 50) -> Optional[List[Dict]]:
        """تتبع أحاديث العملة على Twitter"""
        try:
            # البحث عن اسم العملة والرمز
            queries = [
                f'"{coin_name}" lang:ar',
                f'#{symbol} lang:ar',
                f'${symbol} lang:ar'
            ]
            
            all_tweets = []
            
            for query in queries:
                tweets = self.search_tweets(query, max_results=max_results)
                if tweets:
                    all_tweets.extend(tweets)
            
            # إزالة التكرارات
            unique_tweets = {t['id']: t for t in all_tweets}
            
            # إضافة تحليل المشاعر
            for tweet in unique_tweets.values():
                sentiment_data = self.analyze_sentiment(tweet['text'])
                tweet.update(sentiment_data)
            
            return list(unique_tweets.values())
        
        except Exception as e:
            logger.error(f"خطأ في تتبع أحاديث العملة: {str(e)}")
            return None


class RedditAPI:
    """واجهة Reddit API للحصول على المناقشات"""
    
    def __init__(self):
        try:
            import praw
            self.reddit = None  # يمكن إضافة مفاتيح Reddit هنا
        except ImportError:
            logger.warning("مكتبة praw غير مثبتة")
    
    def search_subreddit(self, query: str, subreddit: str = 'cryptocurrency') -> Optional[List[Dict]]:
        """البحث في subreddit معينة"""
        if not self.reddit:
            logger.warning("Reddit API غير مهيأة")
            return None
        
        try:
            results = []
            for submission in self.reddit.subreddit(subreddit).search(query, time_filter='day', limit=50):
                results.append({
                    'id': submission.id,
                    'title': submission.title,
                    'text': submission.selftext,
                    'score': submission.score,
                    'comments': submission.num_comments,
                    'created_at': submission.created_utc,
                    'url': submission.url
                })
            
            return results
        
        except Exception as e:
            logger.error(f"خطأ في البحث في Reddit: {str(e)}")
            return None


class DiscordAPI:
    """واجهة Discord للحصول على رسائل الخوادم"""
    
    def __init__(self):
        logger.info("Discord API جاهزة للاستخدام")
    
    def monitor_channel(self, channel_id: str) -> Optional[List[Dict]]:
        """مراقبة قناة Discord"""
        # يتطلب bot token مكون
        logger.info(f"مراقبة القناة {channel_id} تتطلب Discord Bot token")
        return None
