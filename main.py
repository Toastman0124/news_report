import os
import requests
import feedparser
from deep_translator import GoogleTranslator

# 從環境變數讀取推送 Key
SCKEY = os.environ.get("SCKEY")

def get_region_news(region_name, icon, rss_url, translate_to_chinese=False):
    """抓取新聞並翻譯標題"""
    try:
        feed = feedparser.parse(rss_url)
        content = f"### {icon} {region_name} 重要時事\n"
        
        # 每個地區抓取 6 則
        entries = feed.entries[:6]
        if not entries:
            return f"#### {icon} {region_name}：暫時無法取得新聞\n"
            
        translator = GoogleTranslator(source='auto', target='zh-TW')
        
        for i, entry in enumerate(entries, 1):
            original_title = entry.title.rsplit(' - ', 1)[0]
            
            if translate_to_chinese:
                try:
                    # 直接翻譯標題
                    display_title = translator.translate(original_title)
                    content += f"{i}. {display_title}\n   🔗 [閱讀原文]({entry.link})\n"
                except:
                    content += f"{i}. {original_title}\n   🔗 [閱讀原文]({entry.link})\n"
            else:
                content += f"{i}. {original_title}\n   🔗 [閱讀原文]({entry.link})\n"
        return content + "\n"
    except Exception as e:
        return f"#### {icon} {region_name} 抓取出錯: {str(e)}\n"

def main():
    if not SCKEY:
        print("錯誤：找不到 SCKEY，請檢查 GitHub Secrets 設定")
        return

    # 定義抓取清單：地區, 圖示, RSS網址, 是否翻譯
    sources = [
        ("台灣", "🇹🇼", "https://news.google.com/rss?hl=zh-TW&gl=TW&ceid=TW:zh-Hant", False),
        ("中國大陸", "🇨🇳", "https://news.google.com/rss?hl=zh-CN&gl=CN&ceid=CN:zh-Hans", False),
        ("美國 (國際)", "🇺🇸", "https://news.google.com/rss?hl=zh-TW&gl=US&ceid=TW:zh-Hant", False),
        ("日本", "🇯🇵", "https://news.google.com/rss?hl=ja&gl=JP&ceid=JP:ja", True),
        ("韓國", "🇰🇷", "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko", True)
    ]
    
    report_body = "📅 今日五地時事快報 (12:00)\n\n"
    
    for region, icon, url, translate in sources:
        print(f"正在處理 {region} 新聞...")
        report_body += get_region_news(region, icon, url, translate)

    report_body += "---\n💡 溫馨提醒：日韓新聞標題已自動翻譯為繁體中文。祝您今日愉快！"

    # 推送到微信 (Server 醬)
    push_url = f"https://sctapi.ftqq.com/{SCKEY}.send"
    data = {
        "title": "📰 今日五地重要時事 (共 30 則)",
        "desp": report_body
    }
    
    try:
        res = requests.post(push_url, data=data)
        if res.status_code == 200:
            print("✅ 任務成功！內容已推送到微信。")
        else:
            print(f"❌ 推送失敗，請檢查 SCKEY 是否正確。")
    except Exception as e:
        print(f"❌ 網路請求失敗: {str(e)}")

if __name__ == "__main__":
    main()
