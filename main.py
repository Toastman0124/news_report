import os
import requests
import feedparser

# 從環境變數讀取推送 Key
SCKEY = os.environ.get("SCKEY")

def get_region_news(region_name, rss_url, need_translate=False):
    """抓取特定地區的前 6 則新聞，若需要翻譯則標註"""
    try:
        feed = feedparser.parse(rss_url)
        content = f"### 📍 {region_name} 重要時事\n"
        
        entries = feed.entries[:6]
        if not entries:
            return f"#### {region_name}：暫時無法取得新聞\n"
            
        for i, entry in enumerate(entries, 1):
            title = entry.title.rsplit(' - ', 1)[0]
            
            if need_translate:
                # 這裡利用 Google 翻譯的 Web 連結作為輔助，點擊即可看翻譯版全文
                translate_link = f"https://translate.google.com/translate?sl=auto&tl=zh-TW&u={entry.link}"
                content += f"{i}. {title}\n   [閱讀原文]({entry.link}) | [繁體翻譯說明]({translate_link})\n"
            else:
                content += f"{i}. {title}\n   [閱讀全文]({entry.link})\n"
        return content + "\n"
    except Exception as e:
        return f"#### {region_name} 抓取出錯: {str(e)}\n"

def main():
    if not SCKEY:
        print("錯誤：找不到 SCKEY，請檢查 GitHub Secrets")
        return

    # 定義抓取清單：中、台、美、日、韓
    # 日本與韓國設定為需要翻譯說明 (need_translate=True)
    sources = [
        ("台灣", "https://news.google.com/rss?hl=zh-TW&gl=TW&ceid=TW:zh-Hant", False),
        ("中國大陸", "https://news.google.com/rss?hl=zh-CN&gl=CN&ceid=CN:zh-Hans", False),
        ("美國 (國際)", "https://news.google.com/rss?hl=zh-TW&gl=US&ceid=TW:zh-Hant", False),
        ("日本", "https://news.google.com/rss?hl=ja&gl=JP&ceid=JP:ja", True),
        ("韓國", "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko", True)
    ]
    
    report_body = "📅 今日五地重要新聞彙整 (12:00)\n\n"
    
    for region, url, translate in sources:
        print(f"正在抓取 {region} 新聞...")
        report_body += get_region_news(region, url, translate)

    report_body += "---\n💡 溫馨提醒：日韓新聞點擊「繁體翻譯說明」可直接開啟翻譯網頁。祝您與長輩聊得愉快！"

    # 推送到微信
    push_url = f"https://sctapi.ftqq.com/{SCKEY}.send"
    data = {
        "title": "☀️ 今日五地時事精選 (共 30 則)",
        "desp": report_body
    }
    
    try:
        res = requests.post(push_url, data=data)
        if res.status_code == 200:
            print("✅ 任務成功！內容已推送到微信。")
        else:
            print(f"❌ 推送失敗")
    except Exception as e:
        print(f"❌ 網路請求失敗: {str(e)}")

if __name__ == "__main__":
    main()
