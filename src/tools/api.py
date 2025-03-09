import os
import pandas as pd
import requests
from serpapi import GoogleSearch
from dotenv import load_dotenv
from apify_client import ApifyClient
import logging
import json
from datetime import datetime  # 添加这行


from data.cache import get_cache
from data.models import (
    CompanyNews,
    CompanyNewsResponse,
    FinancialMetrics,
    FinancialMetricsResponse,
    Price,
    PriceResponse,
    LineItem,
    LineItemResponse,
    InsiderTrade,
    InsiderTradeResponse,
    InstagramHashtagStats,
    GoogleNews,
    InstagramPost,
    RelatedHashtag,
)

# Global cache instance
_cache = get_cache()
load_dotenv()

def get_prices(ticker: str, start_date: str, end_date: str) -> list[Price]:
    """Fetch price data from cache or API."""
    # Check cache first
    if cached_data := _cache.get_prices(ticker):
        # Filter cached data by date range and convert to Price objects
        filtered_data = [Price(**price) for price in cached_data if start_date <= price["time"] <= end_date]
        if filtered_data:
            return filtered_data

    # If not in cache or no data in range, fetch from API
    headers = {}
    if api_key := os.environ.get("FINANCIAL_DATASETS_API_KEY"):
        headers["X-API-KEY"] = api_key

    url = f"https://api.financialdatasets.ai/prices/?ticker={ticker}&interval=day&interval_multiplier=1&start_date={start_date}&end_date={end_date}"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Error fetching data: {response.status_code} - {response.text}")

    # Parse response with Pydantic model
    price_response = PriceResponse(**response.json())
    prices = price_response.prices

    if not prices:
        return []

    # Cache the results as dicts
    _cache.set_prices(ticker, [p.model_dump() for p in prices])
    return prices


def get_financial_metrics(
    ticker: str,
    end_date: str,
    period: str = "ttm",
    limit: int = 10,
) -> list[FinancialMetrics]:
    """Fetch financial metrics from cache or API."""
    # Check cache first
    if cached_data := _cache.get_financial_metrics(ticker):
        # Filter cached data by date and limit
        filtered_data = [FinancialMetrics(**metric) for metric in cached_data if metric["report_period"] <= end_date]
        filtered_data.sort(key=lambda x: x.report_period, reverse=True)
        if filtered_data:
            return filtered_data[:limit]

    # If not in cache or insufficient data, fetch from API
    headers = {}
    if api_key := os.environ.get("FINANCIAL_DATASETS_API_KEY"):
        headers["X-API-KEY"] = api_key

    url = f"https://api.financialdatasets.ai/financial-metrics/?ticker={ticker}&report_period_lte={end_date}&limit={limit}&period={period}"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Error fetching data: {response.status_code} - {response.text}")

    # Parse response with Pydantic model
    metrics_response = FinancialMetricsResponse(**response.json())
    # Return the FinancialMetrics objects directly instead of converting to dict
    financial_metrics = metrics_response.financial_metrics

    if not financial_metrics:
        return []

    # Cache the results as dicts
    _cache.set_financial_metrics(ticker, [m.model_dump() for m in financial_metrics])
    return financial_metrics


def search_line_items(
    ticker: str,
    line_items: list[str],
    end_date: str,
    period: str = "ttm",
    limit: int = 10,
) -> list[LineItem]:
    """Fetch line items from API."""
    # If not in cache or insufficient data, fetch from API
    headers = {}
    if api_key := os.environ.get("FINANCIAL_DATASETS_API_KEY"):
        headers["X-API-KEY"] = api_key

    url = "https://api.financialdatasets.ai/financials/search/line-items"

    body = {
        "tickers": [ticker],
        "line_items": line_items,
        "end_date": end_date,
        "period": period,
        "limit": limit,
    }
    response = requests.post(url, headers=headers, json=body)
    if response.status_code != 200:
        raise Exception(f"Error fetching data: {response.status_code} - {response.text}")
    data = response.json()
    response_model = LineItemResponse(**data)
    search_results = response_model.search_results
    if not search_results:
        return []

    # Cache the results
    return search_results[:limit]


def get_insider_trades(
    ticker: str,
    end_date: str,
    start_date: str | None = None,
    limit: int = 1000,
) -> list[InsiderTrade]:
    """Fetch insider trades from cache or API."""
    # Check cache first
    if cached_data := _cache.get_insider_trades(ticker):
        # Filter cached data by date range
        filtered_data = [InsiderTrade(**trade) for trade in cached_data 
                        if (start_date is None or (trade.get("transaction_date") or trade["filing_date"]) >= start_date)
                        and (trade.get("transaction_date") or trade["filing_date"]) <= end_date]
        filtered_data.sort(key=lambda x: x.transaction_date or x.filing_date, reverse=True)
        if filtered_data:
            return filtered_data

    # If not in cache or insufficient data, fetch from API
    headers = {}
    if api_key := os.environ.get("FINANCIAL_DATASETS_API_KEY"):
        headers["X-API-KEY"] = api_key

    all_trades = []
    current_end_date = end_date
    
    while True:
        url = f"https://api.financialdatasets.ai/insider-trades/?ticker={ticker}&filing_date_lte={current_end_date}"
        if start_date:
            url += f"&filing_date_gte={start_date}"
        url += f"&limit={limit}"
        
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise Exception(f"Error fetching data: {response.status_code} - {response.text}")
        
        data = response.json()
        response_model = InsiderTradeResponse(**data)
        insider_trades = response_model.insider_trades
        
        if not insider_trades:
            break
            
        all_trades.extend(insider_trades)
        
        # Only continue pagination if we have a start_date and got a full page
        if not start_date or len(insider_trades) < limit:
            break
            
        # Update end_date to the oldest filing date from current batch for next iteration
        current_end_date = min(trade.filing_date for trade in insider_trades).split('T')[0]
        
        # If we've reached or passed the start_date, we can stop
        if current_end_date <= start_date:
            break

    if not all_trades:
        return []

    # Cache the results
    _cache.set_insider_trades(ticker, [trade.model_dump() for trade in all_trades])
    return all_trades


def get_company_news(
    ticker: str,
    end_date: str,
    start_date: str | None = None,
    limit: int = 1000,
) -> list[CompanyNews]:
    """Fetch company news from cache or API."""
    # Check cache first
    if cached_data := _cache.get_company_news(ticker):
        # Filter cached data by date range
        filtered_data = [CompanyNews(**news) for news in cached_data 
                        if (start_date is None or news["date"] >= start_date)
                        and news["date"] <= end_date]
        filtered_data.sort(key=lambda x: x.date, reverse=True)
        if filtered_data:
            return filtered_data

    # If not in cache or insufficient data, fetch from API
    headers = {}
    if api_key := os.environ.get("FINANCIAL_DATASETS_API_KEY"):
        headers["X-API-KEY"] = api_key

    all_news = []
    current_end_date = end_date
    
    while True:
        url = f"https://api.financialdatasets.ai/news/?ticker={ticker}&end_date={current_end_date}"
        if start_date:
            url += f"&start_date={start_date}"
        url += f"&limit={limit}"
        
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise Exception(f"Error fetching data: {response.status_code} - {response.text}")
        
        data = response.json()
        response_model = CompanyNewsResponse(**data)
        company_news = response_model.news
        
        if not company_news:
            break
            
        all_news.extend(company_news)
        
        # Only continue pagination if we have a start_date and got a full page
        if not start_date or len(company_news) < limit:
            break
            
        # Update end_date to the oldest date from current batch for next iteration
        current_end_date = min(news.date for news in company_news).split('T')[0]
        
        # If we've reached or passed the start_date, we can stop
        if current_end_date <= start_date:
            break

    if not all_news:
        return []

    # Cache the results
    _cache.set_company_news(ticker, [news.model_dump() for news in all_news])
    return all_news



def get_market_cap(
    ticker: str,
    end_date: str,
) -> float | None:
    """Fetch market cap from the API."""
    financial_metrics = get_financial_metrics(ticker, end_date)
    market_cap = financial_metrics[0].market_cap
    if not market_cap:
        return None

    return market_cap


def prices_to_df(prices: list[Price]) -> pd.DataFrame:
    """Convert prices to a DataFrame."""
    df = pd.DataFrame([p.model_dump() for p in prices])
    df["Date"] = pd.to_datetime(df["time"])
    df.set_index("Date", inplace=True)
    numeric_cols = ["open", "close", "high", "low", "volume"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df.sort_index(inplace=True)
    return df


# Update the get_price_data function to use the new functions
def get_price_data(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    prices = get_prices(ticker, start_date, end_date)
    return prices_to_df(prices)


# Get Google Trends data for a list of queries
# from serpapi import GoogleSearch

# params = {
#   "engine": "google_trends",
#   "q": "coffee,milk,bread,pasta,steak",
#   "data_type": "TIMESERIES",
#   "api_key": "d9f287f256744fac5911e54e72298cda45a489e77a14c2ceeedac4819eac5d31"
# }

# search = GoogleSearch(params)
# results = search.get_dict()
# interest_over_time = results["interest_over_time"]
def get_google_trends(querylist: list[str]) -> pd.DataFrame:
    search = GoogleSearch(
        {
            "engine": "google_trends",
            "api_key": os.getenv("SERPAPI_API_KEY"),
            "q": ",".join(querylist),
            "data_type": "TIMESERIES",
            "date": "now 7-d"
        }
    )
    results = search.get_dict()
    print(results)
    interest_over_time = results["interest_over_time"]
    return interest_over_time

# Get Google News data for a list of queries
# from serpapi import GoogleSearch

# params = {
#   "engine": "google_news",
#   "q": "pizza",
#   "gl": "us",
#   "hl": "en",
#   "api_key": "d9f287f256744fac5911e54e72298cda45a489e77a14c2ceeedac4819eac5d31"
# }

# search = GoogleSearch(params)
# results = search.get_dict()
# news_results = results["news_results"]

def get_google_news(querylist: list[str]) -> pd.DataFrame:
    search = GoogleSearch(
        {
            "engine": "google_news",
            "api_key": os.getenv("SERPAPI_API_KEY"),
            "q": ",".join(querylist),
            "gl": "us",
            "hl": "en",
            "data_type": "NEWS"
        }
    )
    results = search.get_dict()
    print(results)
    news_results = results["news_results"]  
    return news_results

# Get Instagram Trends data for a list of hashtags
# from apify_client import ApifyClient

# # Initialize the ApifyClient with your API token
# client = ApifyClient("<YOUR_API_TOKEN>")

# # Prepare the Actor input
# run_input = { "hashtags": ["webscraping"] }

# # Run the Actor and wait for it to finish
# run = client.actor("cHedUknx10dsaavpI").call(run_input=run_input)

# # Fetch and print Actor results from the run's dataset (if there are any)
# for item in client.dataset(run["defaultDatasetId"]).iterate_items():
#     print(item)
def get_instagram_trends(hashtags: list[str]) -> list[InstagramHashtagStats]:
    """
    Fetch Instagram hashtag statistics and trends data
    Args:
        hashtags: List of hashtag names to analyze
    Returns:
        List of InstagramHashtagStats objects with parsed data
    """
    try:
        # Initialize ApifyClient with API key
        client = ApifyClient(os.getenv("APIFY_API_KEY"))
        
        logging.info(f"开始获取 Instagram 数据，标签: {hashtags}")
        
        # Set input parameters for the actor
        run_input = { 
            "hashtags": hashtags,
            "resultsLimit": 100
        }

        # Check if in debug mode
        debug_mode = os.getenv("DEBUG", "false").lower() == "true"
        
        if debug_mode:
            # For testing, load data from local file
            logging.info("Debug mode: Using local test data file")
            with open('src/apify/dataset_instagram-hashtag-stats_2025-03-09_12-05-31-336.json', 'r') as f:
                data_items = json.load(f)
        else:
            # Run the actor and get results from API
            logging.info("Production mode: Fetching data from Instagram API")
            # run = client.actor("cHedUknx10dsaavpI").call(run_input=run_input)
            # data_items = client.dataset(run["defaultDatasetId"]).iterate_items()
        
        # Parse results into data model
        instagram_data = []
        for item in data_items:
            # Parse top posts
            top_posts = []
            for post in item.get('top_posts', []):
                post_obj = InstagramPost(
                    id=str(post.get('id', '')),
                    caption=post.get('caption'),
                    url=post.get('url', ''),
                    timestamp=post.get('timestamp'),
                    likes_count=int(post.get('likesCount', 0)),
                    comments_count=int(post.get('commentsCount', 0)),
                    display_url=post.get('displayUrl'),
                    dimensions_height=post.get('dimensionsHeight'),
                    dimensions_width=post.get('dimensionsWidth'),
                    is_sponsored=bool(post.get('isSponsored')),
                    product_type=post.get('productType'),
                    first_comment=post.get('firstComment'),
                    latest_comments=post.get('latestComments', [])
                )
                top_posts.append(post_obj)
            
            # Parse related hashtags
            related_hashtags = []
            for related in item.get('related', []):
                if isinstance(related, str):
                    related_hashtags.append(RelatedHashtag(hash=related))
                elif isinstance(related, dict):
                    related_hashtags.append(RelatedHashtag(
                        hash=related.get('hash', ''),
                        info=related.get('info', '')
                    ))
                
            # Create InstagramHashtagStats object
            hashtag_stats = InstagramHashtagStats(
                name=str(item.get('name', '')),
                post_count=int(item.get('postsCount', 0)),
                url=str(item.get('url', '')),
                id=str(item.get('id', '')),
                posts=item.get('posts', ''),
                top_posts=top_posts,
                posts_per_day=float(item.get('postsPerDay', 0)),
                related=related_hashtags,
                collection_timestamp=datetime.now().isoformat()
            )
            
            instagram_data.append(hashtag_stats)
            
            # Log individual hashtag stats
            logging.info(f"\n标签 #{hashtag_stats.name} 统计:")
            logging.info(f"- 帖子总数: {hashtag_stats.post_count:,}")
            logging.info(f"- 日均帖子: {hashtag_stats.posts_per_day:,.2f}")
            logging.info(f"- 相关标签数: {len(hashtag_stats.related)}")
        
        return instagram_data

    except Exception as e:
        logging.error(f"Instagram 数据获取错误: {str(e)}")
        logging.error("错误详情:", exc_info=True)
        return []