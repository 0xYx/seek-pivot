from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class Price(BaseModel):
    open: float
    close: float
    high: float
    low: float
    volume: int
    time: str


class PriceResponse(BaseModel):
    ticker: str
    prices: list[Price]


class FinancialMetrics(BaseModel):
    ticker: str
    calendar_date: str | None = None
    report_period: str
    period: str
    currency: str
    market_cap: float | None
    enterprise_value: float | None
    price_to_earnings_ratio: float | None
    price_to_book_ratio: float | None
    price_to_sales_ratio: float | None
    enterprise_value_to_ebitda_ratio: float | None
    enterprise_value_to_revenue_ratio: float | None
    free_cash_flow_yield: float | None
    peg_ratio: float | None
    gross_margin: float | None
    operating_margin: float | None
    net_margin: float | None
    return_on_equity: float | None
    return_on_assets: float | None
    return_on_invested_capital: float | None
    asset_turnover: float | None
    inventory_turnover: float | None
    receivables_turnover: float | None
    days_sales_outstanding: float | None
    operating_cycle: float | None
    working_capital_turnover: float | None
    current_ratio: float | None
    quick_ratio: float | None
    cash_ratio: float | None
    operating_cash_flow_ratio: float | None
    debt_to_equity: float | None
    debt_to_assets: float | None
    interest_coverage: float | None
    revenue_growth: float | None
    earnings_growth: float | None
    book_value_growth: float | None
    earnings_per_share_growth: float | None
    free_cash_flow_growth: float | None
    operating_income_growth: float | None
    ebitda_growth: float | None
    payout_ratio: float | None
    earnings_per_share: float | None
    book_value_per_share: float | None
    free_cash_flow_per_share: float | None


class FinancialMetricsResponse(BaseModel):
    financial_metrics: list[FinancialMetrics]


class LineItem(BaseModel):
    ticker: str
    report_period: str
    period: str
    currency: str

    # Allow additional fields dynamically
    model_config = {"extra": "allow"}


class LineItemResponse(BaseModel):
    search_results: list[LineItem]


class InsiderTrade(BaseModel):
    ticker: str
    issuer: str | None
    name: str | None
    title: str | None
    is_board_director: bool | None
    transaction_date: str | None
    transaction_shares: float | None
    transaction_price_per_share: float | None
    transaction_value: float | None
    shares_owned_before_transaction: float | None
    shares_owned_after_transaction: float | None
    security_title: str | None
    filing_date: str


class InsiderTradeResponse(BaseModel):
    insider_trades: list[InsiderTrade]


class CompanyNews(BaseModel):
    ticker: str
    title: str
    author: str
    source: str
    date: str
    url: str
    sentiment: str | None = None


class CompanyNewsResponse(BaseModel):
    news: list[CompanyNews]


class Position(BaseModel):
    cash: float = 0.0
    shares: int = 0
    ticker: str


class Portfolio(BaseModel):
    positions: dict[str, Position]  # ticker -> Position mapping
    total_cash: float = 0.0


class AnalystSignal(BaseModel):
    signal: str | None = None
    confidence: float | None = None
    reasoning: dict | str | None = None
    max_position_size: float | None = None  # For risk management signals
    target_price_range: str | None = None


class TickerAnalysis(BaseModel):
    ticker: str
    analyst_signals: dict[str, AnalystSignal]  # agent_name -> signal mapping


class AgentStateData(BaseModel):
    tickers: list[str]
    portfolio: Portfolio
    start_date: str
    end_date: str
    ticker_analyses: dict[str, TickerAnalysis]  # ticker -> analysis mapping


class AgentStateMetadata(BaseModel):
    show_reasoning: bool = False
    model_config = {"extra": "allow"}

class InstagramTrend(BaseModel):
    name: str
    postsCount: int
    related: list[dict[str, str]]


class GoogleNews(BaseModel):
    title: str  # News article title
    source: str  # Source/publisher of the news
    date: str  # Publication date
    link: str  # URL link to the article
    snippet: str  # Brief excerpt/summary of the article

# Model for Google Trends data point values
class TrendValue(BaseModel):
    query: str
    value: str
    extracted_value: int

# Model for a single timestamp's trend data
class TrendDataPoint(BaseModel):
    date: str
    timestamp: str
    partial_data: bool = False
    values: list[TrendValue]

# Model for trend averages
class TrendAverage(BaseModel):
    query: str
    value: int

# Model for complete Google Trends response
class GoogleTrends(BaseModel):
    timeline_data: list[TrendDataPoint]
    averages: list[TrendAverage]

# Model for individual Instagram post
class InstagramPost(BaseModel):
    id: Optional[str] = None
    caption: Optional[str] = None
    url: str = ""
    timestamp: Optional[str] = None
    likes_count: Optional[int] = None
    comments_count: Optional[int] = None
    display_url: Optional[str] = None
    dimensions_height: Optional[int] = None
    dimensions_width: Optional[int] = None
    is_sponsored: Optional[bool] = None
    product_type: Optional[str] = None
    first_comment: Optional[str] = None
    latest_comments: Optional[List[str]] = None

class RelatedHashtag(BaseModel):
    hash: str
    info: Optional[str] = None

class InstagramHashtagStats(BaseModel):
    name: str
    post_count: int  # 改为 int 类型
    url: str
    id: str
    posts: str
    top_posts: List[InstagramPost] = []
    posts_per_day: float = 0
    related: List[RelatedHashtag] = []
    collection_timestamp: str

    def log_stats(self):
        """Log the statistics for this hashtag"""
        logging.info(f"Hashtag #{self.name} stats:")
        logging.info(f"- Total posts: {self.post_count:,}")
        logging.info(f"- Posts per day: {self.posts_per_day:,.2f}")
        logging.info(f"- Related hashtags: {len(self.related)}")

