import os
import requests
import feedparser
import json

# 從 GitHub Secrets 讀取環境變數
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
SCKEY = os.environ.get("SCKEY")

def get_region_news(url):
    """抓取 RSS 標題與連結"""
    try:
        feed = feedparser.parse(url)
        news_list = []
        for entry in feed.entries[:5]:
            news_list.append(f"- 標題: {entry.title} (連結: {entry.link})")
        return "\n".join(news_list)
    except Exception as e:
        return f"無法抓取新聞: {str(e)}"

def main():
    if not GEMINI_API_KEY or not SCKEY:
        print("錯誤：找不到 API Key")
        return

    # 1. 抓取新聞
    sources = {
        "台灣": "https://news.google.com/rss?hl=zh-TW&gl=TW&ceid=TW:zh-Hant",
        "中國大陸": "https://news.google.com/rss?hl=zh-CN&gl=CN&ceid=CN:zh-Hans",
        "美國": "https://news.google.com/rss?hl=zh-TW&gl=US&ceid=TW:zh-Hant",
        "日本": "https://news.google.com/rss?hl=ja&gl=JP&ceid=JP:ja"
    }
    raw_news_text = ""
    for region, url in sources.items():
        raw_news_text += f"\n【{region}重要時事】\n{get_region_news(url)}\n"

    # 2. 直接使用 requests 呼叫 Google Gemini API (避開 SDK)
    # 使用 v1beta 版本路徑
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    prompt = f"""
    你是一位新聞祕書。請針對以下新聞內容進行跨國時事重點整理（社會、經濟、運動、娛樂）。
    要求：
    1. 內容精簡，每則新聞總結約 30 字並保留[連結]。
    2. 如果是日本或美國新聞請翻譯成繁體中文。
    3. 提供 2 個適合與長輩聊天的話題點。

    新聞資料：
    {raw_news_text}
    """

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    headers = {'Content-Type': 'application/json'}

    print("正在透過 REST API 呼叫 Gemini...")
    try:
        response = requests.post(api_url, headers=headers, data=json.dumps(payload))
        res_json = response.json()
        
        # 提取 AI 回傳內容
        if "candidates" in res_json:
            ai_summary = res_json['candidates'][0]['content']['parts'][0]['text']
            print("✅ AI 摘要生成成功")
        else:
            # 如果 API 回傳錯誤訊息，直接顯示出來
            ai_summary = f"⚠️ AI 生成失敗，API 回傳內容：\n{json.dumps(res_json, ensure_ascii=False)}"
            
    except Exception as e:
        ai_summary = f"⚠️ 網路請求出錯：{str(e)}\n\n原始新聞備份：\n{raw_news_text}"

    # 3. 推送到微信
    push_url = f"https://sctapi.ftqq.com/{SCKEY}.send"
    requests.post(push_url, data={"title": "☀️ 中午時事 AI 報告 (REST版)", "desp": ai_summary})

if __name__ == "__main__":
    main()
