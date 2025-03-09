import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
src_path = str(Path(__file__).parent.parent)
sys.path.append(src_path)

from dotenv import load_dotenv
import logging
import json
from tools.api import get_google_news

def test_get_google_news():
    """
    # 测试 api.py 中的 get_google_news 函数
    """
    try:
        query_list = ["vans"]
        logging.info("\n=== 测试 Google News API ===")
        logging.info(f"查询词列表: {query_list}")
        
        # 修改 API 调用参数
        news_results = get_google_news(query_list)
        
        logging.info("\n新闻结果:")
        logging.info(json.dumps(news_results, indent=2))
        
        if news_results:
            logging.info(f"\n获取到 {len(news_results)} 条新闻")
            
            logging.info("\n新闻摘要:")
            for idx, news in enumerate(news_results, 1):
                logging.info(f"\n{idx}. {news.get('title', 'No title')}")
                logging.info(f"   日期: {news.get('date', 'No date')}")
                logging.info(f"   来源: {news.get('source', 'No source')}")
        
        return news_results

    except Exception as e:
        logging.error(f"News API 测试错误: {str(e)}")
        logging.error("错误详情:", exc_info=True)
        return None

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    load_dotenv()
    
    if not os.getenv("SERPAPI_API_KEY"):
        logging.error("请先设置 SERPAPI_API_KEY 环境变量")
    else:
        test_get_google_news()
