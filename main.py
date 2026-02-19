import os
import requests
import feedparser
import json

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
SCKEY = os.environ.get("SCKEY")

def get_region_news(url):
    try:
        feed = feedparser.parse(url)
        news_list = []
        for entry in feed.entries[:5]:
            news_list.append(f"- 標題: {entry.title}\n  連結: {entry.link}")
        return "\n".join(news_list)
    except:
        return "抓取失敗"

def main():
    if not GEMINI_API_KEY or not SCKEY:
        print("錯誤：找不到 API Key")
        return

    # 1. 抓取四地新聞
    sources = {
        "台灣": "https://news.google.com/rss?hl=zh-TW&gl=TW&ceid=TW:zh-Hant",
        "中國大陸": "https://news.google.com/rss?hl=zh-CN&gl=CN&ceid=CN:zh-Hans",
        "美國": "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en",
        "日本": "https://news.google.com/rss?hl=ja&gl=JP&ceid=JP:ja"
    }
    
    raw_news = ""
    for region, url in sources.items():
        raw_news += f"\n【{region}時事資料】\n{get_region_news(url)}\n"

    # 2. 終極相容網址：v1beta + gemini-1.5-flash-latest
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_API_KEY}"
    
    # 3. Prompt (保持您的偏好：分類 + 話題點)
    prompt = f"""
    你是一位專業新聞秘書。請將以下新聞資料彙整為一份精美的中文報告。
    格式：
    1. 💰 經濟與科技：摘要 + 連結
    2. 🏠 社會與生活：摘要 + 連結
    3. 🏆 運動與娛樂：摘要 + 連結
    4. 💡 聊天話題點：提供 2-3 個適合與長輩朋友聊天的話題建議。
    要求：每則摘要約 30 字，外文翻譯為繁體中文，保留連結。

    新聞資料：
    {raw_news}
    """

    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    print("正在透過 v1beta API 生成摘要...")
    try:
        res = requests.post(api_url, headers={'Content-Type': 'application/json'}, data=json.dumps(payload))
        res_json = res.json()
        
        if "candidates" in res_json:
            final_text = res_json['candidates'][0]['content']['parts'][0]['text']
            print("✅ 摘要成功生成")
        else:
            # 這裡會印出更詳細的錯誤，方便我們診斷
            final_text = f"⚠️ AI 生成失敗。API 回傳：{json.dumps(res_json, ensure_ascii=False)}"
            
    except Exception as e:
        final_text = f"❌ 請求失敗: {str(e)}\n\n原始新聞備份：\n{raw_news}"

    # 4. 推送到微信
    requests.post(f"https://sctapi.ftqq.com/{SCKEY}.send", data={"title": "📰 今日中午 AI 時事精華報告", "desp": final_text})

if __name__ == "__main__":
    main()
