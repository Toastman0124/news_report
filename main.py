import os
import requests
import feedparser
from deep_translator import GoogleTranslator
import urllib.parse

# 從環境變數讀取推送 Key
SCKEY = os.environ.get("SCKEY")

def get_categorized_news(region_name, icon, lang_config, translate_to_chinese=False):
    """使用關鍵字搜尋方式抓取分類新聞"""
    translator = GoogleTranslator(source='auto', target='zh-TW')
    region_content = f"## {icon} {region_name}\n"
    
    # 分類與對應搜尋關鍵字 (針對不同語言調整)
    categories = [
        ("政治", "⚖️", lang_config['politics']),
        ("經濟", "💰", lang_config['finance']),
        ("社會", "🏠", lang_config['society']),
        ("娛樂", "🎭", lang_config['entertainment'])
    ]
    
    for cat_name, cat_icon, keyword in categories:
        try:
            # 將關鍵字進行 URL 編碼
            encoded_key = urllib.parse.quote(keyword)
            # 使用 Google News 搜尋 RSS 網址
            rss_url = f"https://news.google.com/rss/search?q={encoded_key}&hl={lang_config['hl']}&gl={lang_config['gl']}&ceid={lang_config['ceid']}"
            
            feed = feedparser.parse(rss_url)
            region_content += f"#### {cat_icon} {cat_name}\n"
            
            entries = feed.entries[:3]
            if not entries:
                region_content += "- (暫無消息)\n"
                continue
                
            for i, entry in enumerate(entries, 1):
                title = entry.title.rsplit(' - ', 1)[0]
                if translate_to_chinese:
                    try:
                        title = translator.translate(title)
                    except: pass
                
                region_content += f"{i}. {title} [🔗]({entry.link})\n"
            region_content += "\n"
        except:
            region_content += "- (讀取失敗)\n"
            
    return region_content

def main():
    if not SCKEY:
        print("錯誤：找不到 SCKEY")
        return

    # 各國語言與搜尋關鍵字配置
    configs = {
        "TW": {"hl": "zh-TW", "gl": "TW", "ceid": "TW:zh-Hant", 
               "politics": "政治", "finance": "財經", "society": "社會", "entertainment": "娛樂"},
        "CN": {"hl": "zh-CN", "gl": "CN", "ceid": "CN:zh-Hans", 
               "politics": "政治", "finance": "財經", "society": "社會", "entertainment": "娛樂"},
        "US": {"hl": "zh-TW", "gl": "US", "ceid": "US:zh-Hant", 
               "politics": "US Politics", "finance": "Economy", "society": "US News", "entertainment": "Entertainment"},
        "JP": {"hl": "ja", "gl": "JP", "ceid": "JP:ja", 
               "politics": "政治", "finance": "経済", "society": "社会", "entertainment": "エンタメ"},
        "KR": {"hl": "ko", "gl": "KR", "ceid": "KR:ko", 
               "politics": "정치", "finance": "경제", "society": "사회", "entertainment": "연예"}
    }

    report_body = "📅 今日五地各類新聞精華 (12:00)\n\n"
    report_body += get_categorized_news("台灣", "🇹🇼", configs["TW"], False)
    report_body += get_categorized_news("中國大陸", "🇨🇳", configs["CN"], False)
    report_body += get_categorized_news("美國 (國際)", "🇺🇸", configs["US"], False)
    report_body += get_categorized_news("日本", "🇯🇵", configs["JP"], True)
    report_body += get_categorized_news("韓國", "🇰🇷", configs["KR"], True)

    report_body += "---\n💡 點擊 [🔗] 即可閱讀詳情。祝您與長輩聊得愉快！"

    # 推送至微信
    push_url = f"https://sctapi.ftqq.com/{SCKEY}.send"
    requests.post(push_url, data={"title": "📰 五地時事分類報 (共 60 則)", "desp": report_body})

if __name__ == "__main__":
    main()
