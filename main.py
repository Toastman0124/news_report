import os
import requests
import feedparser
from deep_translator import GoogleTranslator
import urllib.parse

# 從環境變數讀取推送 Key
SCKEY = os.environ.get("SCKEY")

def get_categorized_news(region_name, icon, lang_config, translate_to_chinese=False):
    """使用關鍵字搜尋方式抓取分類新聞，並根據設定進行翻譯"""
    # 初始化翻譯器 (從自動偵測轉為繁體中文)
    translator = GoogleTranslator(source='auto', target='zh-TW')
    region_content = f"## {icon} {region_name}\n"
    
    # 分類與對應搜尋關鍵字
    categories = [
        ("政治", "⚖️", lang_config['politics']),
        ("經濟", "💰", lang_config['finance']),
        ("社會", "🏠", lang_config['society']),
        ("娛樂", "🎭", lang_config['entertainment'])
    ]
    
    for cat_name, cat_icon, keyword in categories:
        try:
            encoded_key = urllib.parse.quote(keyword)
            # 建立搜尋 URL
            rss_url = f"https://news.google.com/rss/search?q={encoded_key}&hl={lang_config['hl']}&gl={lang_config['gl']}&ceid={lang_config['ceid']}"
            
            feed = feedparser.parse(rss_url)
            region_content += f"#### {cat_icon} {cat_name}\n"
            
            entries = feed.entries[:3]
            if not entries:
                region_content += "- (暫無消息)\n"
                continue
                
            for i, entry in enumerate(entries, 1):
                title = entry.title.rsplit(' - ', 1)[0]
                
                # 如果該地區設定為需要翻譯 (美、日、韓)
                if translate_to_chinese:
                    try:
                        title = translator.translate(title)
                    except:
                        pass # 翻譯失敗則保留原標題
                
                region_content += f"{i}. {title} [🔗]({entry.link})\n"
            region_content += "\n"
        except Exception as e:
            print(f"抓取 {region_name} {cat_name} 出錯: {e}")
            region_content += "- (讀取失敗)\n"
            
    return region_content

def main():
    if not SCKEY:
        print("錯誤：找不到 SCKEY")
        return

    # 各國配置：現在 US, JP, KR 都設定為 True (翻譯)
    configs = {
        "TW": {"hl": "zh-TW", "gl": "TW", "ceid": "TW:zh-Hant", 
               "politics": "政治", "finance": "財經", "society": "社會", "entertainment": "娛樂", "translate": False},
        "CN": {"hl": "zh-CN", "gl": "CN", "ceid": "CN:zh-Hans", 
               "politics": "政治", "finance": "財經", "society": "社會", "entertainment": "娛樂", "translate": False},
        "US": {"hl": "en-US", "gl": "US", "ceid": "US:en", 
               "politics": "US Politics", "finance": "Economy", "society": "US Society", "entertainment": "Hollywood", "translate": True},
        "JP": {"hl": "ja", "gl": "JP", "ceid": "JP:ja", 
               "politics": "政治", "finance": "経済", "society": "社会", "entertainment": "エンタメ", "translate": True},
        "KR": {"hl": "ko", "gl": "KR", "ceid": "KR:ko", 
               "politics": "정치", "finance": "경제", "society": "사회", "entertainment": "연예", "translate": True}
    }

    report_body = "📅 今日五地各類新聞精華 (12:00)\n\n"
    # 執行各國抓取
    report_body += get_categorized_news("台灣", "🇹🇼", configs["TW"], configs["TW"]["translate"])
    report_body += get_categorized_news("中國大陸", "🇨🇳", configs["CN"], configs["CN"]["translate"])
    report_body += get_categorized_news("美國 (國際)", "🇺🇸", configs["US"], configs["US"]["translate"])
    report_body += get_categorized_news("日本", "🇯🇵", configs["JP"], configs["JP"]["translate"])
    report_body += get_categorized_news("韓國", "🇰🇷", configs["KR"], configs["KR"]["translate"])

    report_body += "---\n💡 溫馨提醒：美、日、韓新聞已自動翻譯為繁體中文。"

    # 推送至微信
    push_url = f"https://sctapi.ftqq.com/{SCKEY}.send"
    requests.post(push_url, data={"title": "📰 五地時事分類報 (繁體中文版)", "desp": report_body})
    print("✅ 任務執行完畢")

if __name__ == "__main__":
    main()
