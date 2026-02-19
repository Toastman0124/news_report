import os
import requests
import feedparser

# 讀取推送 Key
SCKEY = os.environ.get("SCKEY")

def get_news_by_category(region_info, category_name, rss_url):
    """抓取特定地區與類別的新聞"""
    try:
        feed = feedparser.parse(rss_url)
        content = f"#### 📍 {region_info} - {category_name}\n"
        # 每個類別抓取前 2 則，避免推播內容過長
        entries = feed.entries[:2]
        if not entries:
            return ""
            
        for entry in entries:
            # 移除標題中多餘的新聞來源後綴 (例如: - Yahoo 新聞)
            title = entry.title.rsplit(' - ', 1)[0]
            content += f"- {title}\n  [查看原文]({entry.link})\n"
        return content + "\n"
    except:
        return ""

def main():
    if not SCKEY:
        print("錯誤：找不到 SCKEY，請檢查 GitHub Secrets")
        return

    # 定義抓取清單：中、台、美、日、韓
    # 這裡使用 Google News 的特定分類 RSS
    sources = [
        # 台灣
        ("台灣", "社會經濟", "https://news.google.com/rss?hl=zh-TW&gl=TW&ceid=TW:zh-Hant"),
        # 中國大陸
        ("中國大陸", "時事熱點", "https://news.google.com/rss?hl=zh-CN&gl=CN&ceid=CN:zh-Hans"),
        # 美國 (中文版方便閱讀)
        ("美國", "國際動態", "https://news.google.com/rss?hl=zh-TW&gl=US&ceid=TW:zh-Hant"),
        # 日本
        ("日本", "社會生活", "https://news.google.com/rss?hl=ja&gl=JP&ceid=JP:ja"),
        # 韓國
        ("韓國", "最新時事", "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko")
    ]
    
    report_body = "📅 今日五地時事快報 (中/台/美/日/韓)\n\n"
    
    for region, cat, url in sources:
        print(f"正在抓取 {region} 新聞...")
        report_body += get_news_by_category(region, cat, url)

    report_body += "---\n💡 溫馨提醒：點擊連結即可閱讀全文。祝您與長輩聊得愉快！"

    # 推送到微信
    push_url = f"https://sctapi.ftqq.com/{SCKEY}.send"
    data = {
        "title": "☀️ 中午時事彙整 (中台美日韓)",
        "desp": report_body
    }
    
    res = requests.post(push_url, data=data)
    if res.status_code == 200:
        print("✅ 任務成功！內容已推送到微信。")
    else:
        print(f"❌ 推送失敗: {res.text}")

if __name__ == "__main__":
    main()
