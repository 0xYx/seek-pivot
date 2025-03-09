# src/tests/test_apify.py
import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
src_path = str(Path(__file__).parent.parent)
sys.path.append(src_path)

from dotenv import load_dotenv
import logging
import json
from tools.api import get_instagram_trends

def test_get_instagram_trends():
    """
    测试 Instagram 趋势数据获取
    """
    try:
        hashtags = ['vans', 'nike', 'adidas']
        logging.info("\n=== 测试 Instagram Trends API ===")
        logging.info(f"查询标签: {hashtags}")
        
        results = get_instagram_trends(hashtags)
        
        if results:
            logging.info(f"\n成功获取 {len(results)} 个标签的数据")
            
            for idx, stat in enumerate(results, 1):
                logging.info(f"\n{idx}. 标签详细信息:")
                logging.info(f"   名称: #{stat.name}")
                logging.info(f"   URL: {stat.url}")
                logging.info(f"   帖子总数: {stat.post_count:,}")
                logging.info(f"   日均帖子数: {stat.posts_per_day:,.2f}")
                
                if stat.related:
                    logging.info(f"   相关标签 (全部):")
                    for related in stat.related:
                        logging.info(f"   - #{related.hash} ({related.info})")
                if stat.top_posts:
                    logging.info(f"   最新帖子数: {len(stat.top_posts)}")
                    logging.info(f"   最新帖子示例:")
                    for post in stat.top_posts[:3]:  # 只显示前3条
                        logging.info(f"   - 点赞: {post.get('likesCount', 'N/A')}")
                        logging.info(f"   - 评论: {post.get('commentsCount', 'N/A')}")
                        caption = post.get('caption', '')[:100]  # 限制显示长度
                        logging.info(f"   - 描述: {caption}...")
        
        return results

    except Exception as e:
        logging.error(f"测试错误: {str(e)}")
        logging.error("错误详情:", exc_info=True)
        return None

if __name__ == "__main__":
    # 设置详细的日志格式
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    load_dotenv()
    
    if not os.getenv("APIFY_API_KEY"):
        logging.error("请先设置 APIFY_API_KEY 环境变量")
    else:
        test_get_instagram_trends()