import os
import requests
import feedparser
import json

# 從 GitHub Secrets 讀取環境變數 (請確保 GitHub 上的 GEMINI_API_KEY 已更新)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
SCKEY = os.environ.get("SCKEY")

def get_region_news(url):
    """抓取 RSS 標題與連結"""
    try:
        feed = feedparser.parse(url)
        news_list = []
        # 抓取前 5 則提供給 AI 篩選
        for entry in feed.entries[:5]:
            news_list.append(f"- 標題: {entry.title}\n  連結: {entry.link}")
        return "\n".join(news_list)
    except:
        return "抓取失敗"

def main():
    if not GEMINI_API_KEY or not SCKEY:
        print("錯誤：找不到 API Key，請檢查 GitHub Secrets")
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
        raw_news += f"\n【{region}重要時事資料】\n{get_region_news(url)}\n"

    # 2. 設定 API 網址 (使用最新的 v1 穩定路徑)
    api_url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    # 3. 準備給 AI 的指令 (Prompt)
    prompt = f"""
    你是一位專業新聞秘書。請將以下新聞資料彙整為一份精美的中文報告。
    
    格式要求：
    1. 💰 經濟與科技：重點摘要 + 原文連結
    2. 🏠 社會與生活：重點摘要 + 原文連結
    3. 🏆 運動與娛樂：重點摘要 + 原文連結
    4. 💡 聊天話題點：針對以上時事，提供 2-3 個適合與「長輩朋友」聊天開啟話題的建議。

    規則：
    - 每則摘要不超過 30 字。
    - 內容涵蓋中、台、美、日。外文新聞(日/英)請翻譯為繁體中文。
    - 必須保留連結以便閱讀全文。

    新聞原始資料：
    {raw_news}
    """

    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    # 4. 呼叫 Gemini API
    print("正在生成 AI 摘要...")
    try:
        res = requests.post(api_url, headers={'Content-Type': 'application/json'}, data=json.dumps(payload))
        res_json = res.json()
        
        if "candidates" in res_json:
            final_text = res_json['candidates'][0]['content']['parts'][0]['text']
            print("✅ AI 摘要生成成功")
        else:
            final_text = f"⚠️ AI 處理異常，回傳：{json.dumps(res_json, ensure_ascii=False)}"
            
    except Exception as e:
        final_text = f"❌ 系統錯誤: {str(e)}\n\n原始新聞內容：\n{raw_news}"

    # 5. 推送到微信
    push_url = f"https://sctapi.ftqq.com/{SCKEY}.send"
    requests.post(push_url, data={"title": "📰 今日中午 AI 時事精華報告", "desp": final_text})
    print("✅ 已發送推送")

if __name__ == "__main__":
    main()
