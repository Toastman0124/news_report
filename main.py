import os
import requests
import feedparser

# 從環境變數讀取推送 Key
SCKEY = os.environ.get("SCKEY")

def get_region_news(region_name, rss_url):
    """抓取特定地區的前 6 則重要新聞"""
    try:
        feed = feedparser.parse(rss_url)
        content = f"### 📍 {region_name} 重要時事\n"
        
        # 抓取前 6 則新聞
        entries = feed.entries[:6]
        if not entries:
            return f"#### {region_name}：暫時無法取得新聞\n"
            
        for i, entry in enumerate(entries, 1):
            # 移除標題中冗長的新聞來源後綴
            title = entry.title.rsplit(' - ', 1)[0]
            content += f"{i}. {title}\n   [閱讀全文]({entry.link})\n"
        return content + "\n"
    except Exception as e:
        return f"#### {region_name} 抓取出錯: {str(e)}\n"

def main():
    if not SCKEY:
        print("錯誤：找不到 SCKEY，請檢查 GitHub Secrets")
        return

    # 定義抓取清單：中、台、美、日 (移除韓國)
    sources = [
        ("台灣", "https://news.google.com/rss?hl=zh-TW&gl=TW&ceid=TW:zh-Hant"),
        ("中國大陸", "https://news.google.com/rss?hl=zh-CN&gl=CN&ceid=CN:zh-Hans"),
        ("美國 (國際)", "https://news.google.com/rss?hl=zh-TW&gl=US&ceid=TW:zh-Hant"),
        ("日本", "https://news.google.com/rss?hl=ja&gl=JP&ceid=JP:ja")
    ]
    
    report_body = "📅 今日四地重要新聞彙整 (12:00)\n\n"
    
    for region, url in sources:
        print(f"正在抓取 {region} 新聞...")
        report_body += get_region_news(region, url)

    report_body += "---\n💡 溫馨提醒：點擊連結即可查看詳情。祝您與長輩朋友們聊得愉快！"

    # 推送到微信 (Server 醬)
    push_url = f"https://sctapi.ftqq.com/{SCKEY}.send"
    data = {
        "title": "☀️ 今日四地時事精選 (共 24 則)",
        "desp": report_body
    }
    
    try:
        res = requests.post(push_url, data=data)
        if res.status_code == 200:
            print("✅ 任務成功！內容已推送到微信。")
        else:
            print(f"❌ 推送失敗，狀態碼: {res.status_code}")
    except Exception as e:
        print(f"❌ 網路請求失敗: {str(e)}")

if __name__ == "__main__":
    main()
