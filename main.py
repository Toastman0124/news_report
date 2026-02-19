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
        for entry in feed.entries[:3]: # 縮減條數以防內容過長
            news_list.append(f"- {entry.title}\n  連結: {entry.link}")
        return "\n".join(news_list)
    except: return "抓取失敗"

def main():
    sources = {
        "台灣": "https://news.google.com/rss?hl=zh-TW&gl=TW&ceid=TW:zh-Hant",
        "大陸": "https://news.google.com/rss?hl=zh-CN&gl=CN&ceid=CN:zh-Hans",
        "美國": "https://news.google.com/rss?hl=zh-TW&gl=US&ceid=TW:zh-Hant",
        "日本": "https://news.google.com/rss?hl=ja&gl=JP&ceid=JP:ja"
    }
    raw_news = ""
    for k, v in sources.items():
        raw_news += f"\n📍【{k}時事】\n{get_region_news(v)}\n"

    # 嘗試 v1 版本路徑
    api_url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    prompt = f"你是新聞秘書，請將以下新聞總結為繁體中文分類摘要（社會、經濟、娛樂、運動），保留連結，並給2個聊天話題點：\n{raw_news}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        res = requests.post(api_url, headers={'Content-Type': 'application/json'}, data=json.dumps(payload))
        res_json = res.json()
        if "candidates" in res_json:
            final_content = res_json['candidates'][0]['content']['parts'][0]['text']
        else:
            # 保底機制：AI 失敗就給標題
            final_content = f"⚠️ AI 摘要暫時不可用(錯誤:{res.status_code})\n今日原始資訊如下：\n{raw_news}"
    except Exception as e:
        final_content = f"❌ 系統錯誤: {str(e)}\n\n{raw_news}"

    requests.post(f"https://sctapi.ftqq.com/{SCKEY}.send", data={"title": "☀️ 今日時事彙整", "desp": final_content})

if __name__ == "__main__":
    main()
