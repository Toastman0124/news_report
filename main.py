import os
import requests
import feedparser
from deep_translator import GoogleTranslator

# 從環境變數讀取推送 Key
SCKEY = os.environ.get("SCKEY")

def get_categorized_news(region_name, icon, topics, translate_to_chinese=False):
    """根據分類抓取新聞"""
    translator = GoogleTranslator(source='auto', target='zh-TW')
    region_content = f"## {icon} {region_name}\n"
    
    for topic_name, topic_icon, rss_url in topics:
        try:
            feed = feedparser.parse(rss_url)
            region_content += f"#### {topic_icon} {topic_name}\n"
            
            # 每個分類抓取 3 則
            entries = feed.entries[:3]
            if not entries:
                region_content += "- (暫無消息)\n"
                continue
                
            for i, entry in enumerate(entries, 1):
                original_title = entry.title.rsplit(' - ', 1)[0]
                if translate_to_chinese:
                    try:
                        display_title = translator.translate(original_title)
                    except:
                        display_title = original_title
                else:
                    display_title = original_title
                
                region_content += f"{i}. {display_title} [🔗]({entry.link})\n"
            region_content += "\n"
        except:
            continue
            
    return region_content

def main():
    if not SCKEY:
        print("錯誤：找不到 SCKEY")
        return

    # 定義各國各分類的 RSS URL (Google News Topic IDs)
    # 台灣
    tw_topics = [
        ("政治", "⚖️", "https://news.google.com/rss/topics/CAAqIQgKIhtDQkFTRGdvSUwyMHZNRzV6Y0hjU0FtdHZHZ0pKUVNnQVAB?hl=zh-TW&gl=TW&ceid=TW:zh-Hant"),
        ("經濟", "💰", "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVd4b1NBUmxHZ0pKUVNnQVAB?hl=zh-TW&gl=TW&ceid=TW:zh-Hant"),
        ("社會", "🏠", "https://news.google.com/rss/topics/CAAqIQgKIhtDQkFTRGdvSUwyMHZNRzV6Y0hjU0FtdHZHZ0pKUVNnQVAB?hl=zh-TW&gl=TW&ceid=TW:zh-Hant"), # 台灣社會常用本地主題
        ("娛樂", "🎭", "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNREpxYW5RU0FtdHZHZ0pKUVNnQVAB?hl=zh-TW&gl=TW&ceid=TW:zh-Hant")
    ]
    # 中國大陸
    cn_topics = [
        ("政治", "⚖️", "https://news.google.com/rss/topics/CAAqJQgKIh5DQkFTRVdvSkwyMHZNR1ptZHpWbUVnSnJieWdBUVAB?hl=zh-CN&gl=CN&ceid=CN:zh-Hans"),
        ("經濟", "💰", "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVd4b1NBUmxHZ0pKckJ5Z0FQAQ?hl=zh-CN&gl=CN&ceid=CN:zh-Hans"),
        ("社會", "🏠", "https://news.google.com/rss/topics/CAAqJQgKIh5DQkFTRVdvSkwyMHZNR1ptZHpWbUVnSnJieWdBUVAB?hl=zh-CN&gl=CN&ceid=CN:zh-Hans"),
        ("娛樂", "🎭", "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNREpxYW5RU0FtdHZHZ0pKckJ5Z0FQAQ?hl=zh-CN&gl=CN&ceid=CN:zh-Hans")
    ]
    # 美國 (國際版中文)
    us_topics = [
        ("政治", "⚖️", "https://news.google.com/rss/topics/CAAqIggKIhtDQkFTRGdvSkwyMHZNRGxqTkhZNFNBUmxHZ0pLVVNB0gEAKhAIByoICiIGYm9sdWNoMAA?hl=zh-TW&gl=US&ceid=US:zh-Hant"),
        ("經濟", "💰", "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVd4b1NBUmxHZ0pLVVNB0gEAKhAIByoICiIGYm9sdWNoMAA?hl=zh-TW&gl=US&ceid=US:zh-Hant"),
        ("社會", "🏠", "https://news.google.com/rss/topics/CAAqIggKIhtDQkFTRGdvSkwyMHZNRGxqTkhZNFNBUmxHZ0pLVVNB0gEAKhAIByoICiIGYm9sdWNoMAA?hl=zh-TW&gl=US&ceid=US:zh-Hant"),
        ("娛樂", "🎭", "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNREpxYW5RU0FtdHZHZ0pLVVNB0gEAKhAIByoICiIGYm9sdWNoMAA?hl=zh-TW&gl=US&ceid=US:zh-Hant")
    ]
    # 日本
    jp_topics = [
        ("政治", "⚖️", "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFZ4ZERidUVndHdaU2dCS0Flb0FBUAE?hl=ja&gl=JP&ceid=JP:ja"),
        ("經濟", "💰", "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVd4b1NBUmxHZ0pLU2dCS0Flb0FBUAE?hl=ja&gl=JP&ceid=JP:ja"),
        ("社會", "🏠", "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRzV6Y0hjU0FtdHZHZ0pLU2dCS0Flb0FBUAE?hl=ja&gl=JP&ceid=JP:ja"),
        ("娛樂", "🎭", "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNREpxYW5RU0FtdHZHZ0pLU2dCS0Flb0FBUAE?hl=ja&gl=JP&ceid=JP:ja")
    ]
    # 韓國
    kr_topics = [
        ("政治", "⚖️", "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFZ4ZERidUVndHdaU2dCS0Flb0FBUAE?hl=ko&gl=KR&ceid=KR:ko"),
        ("經濟", "💰", "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVd4b1NBUmxHZ0pLU2dCS0Flb0FBUAE?hl=ko&gl=KR&ceid=KR:ko"),
        ("社會", "🏠", "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRzV6Y0hjU0FtdHZHZ0pLU2dCS0Flb0FBUAE?hl=ko&gl=KR&ceid=KR:ko"),
        ("娛樂", "🎭", "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNREpxYW5RU0FtdHZHZ0pLU2dCS0Flb0FBUAE?hl=ko&gl=KR&ceid=KR:ko")
    ]

    report_body = "📅 今日五地各類新聞精華 (12:00)\n\n"
    report_body += get_categorized_news("台灣", "🇹🇼", tw_topics, False)
    report_body += get_categorized_news("中國大陸", "🇨🇳", cn_topics, False)
    report_body += get_categorized_news("美國 (國際)", "🇺🇸", us_topics, False)
    report_body += get_categorized_news("日本", "🇯🇵", jp_topics, True)
    report_body += get_categorized_news("韓國", "🇰🇷", kr_topics, True)

    report_body += "---\n💡 溫馨提醒：點擊連結圖示 [🔗] 即可閱讀詳情。"

    # 推送至微信
    push_url = f"https://sctapi.ftqq.com/{SCKEY}.send"
    res = requests.post(push_url, data={"title": "📰 五地時事分類報 (共 60 則)", "desp": report_body})
    if res.status_code == 200:
        print("✅ 推送成功！")

if __name__ == "__main__":
    main()
