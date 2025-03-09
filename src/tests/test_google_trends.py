import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
src_path = str(Path(__file__).parent.parent)
sys.path.append(src_path)

from dotenv import load_dotenv
import logging
import json
from tools.api import get_google_trends

def test_get_google_trends():
    """
    # 测试 api.py 中的 get_google_trends 函数
    """
    try:
        query_list = ["vans", "timbs", "otw", "skool"]
        logging.info("\n=== 测试 Google Trends API ===")
        logging.info(f"查询词列表: {query_list}")
        
        trends_results = get_google_trends(query_list)
        
        logging.info("\nTrends 结果:")
        logging.info(f"数据类型: {type(trends_results)}")
        
        # 打印原始返回数据
        logging.info("\n原始数据:")
        logging.info(json.dumps(trends_results, indent=2))
        
        if hasattr(trends_results, 'head'):
            logging.info("\n数据预览:")
            logging.info(trends_results.head())
            logging.info("\n列名:")
            logging.info(trends_results.columns.tolist())
        
        return trends_results

    except Exception as e:
        logging.error(f"Trends API 测试错误: {str(e)}")
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
        test_get_google_trends()
