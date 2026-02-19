import os
import requests
import feedparser
import google.generativeai as genai

# 配置 API Key
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
SCKEY = os.environ.get("SCKEY")

# 初始化 Gemini AI
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_region_news(url):
    """抓取 RSS 標題與連結"""
    feed = feedparser.parse(url)
    news_list = []
    for entry in feed.entries[:5]: # 每個地區取前 5 條
        news_list.append(f"標題: {entry.title}\n連結: {entry.link}")
    return "\n".join(news_list)

def main():
    # 1. 定義 RSS 來源
    sources = {
        "台灣": "https://news.google.com/rss?hl=zh-TW&gl=TW&ceid=TW:zh-Hant",
        "中國大陸": "https://news.google.com/rss?hl=zh-CN&gl=CN&ceid=CN:zh-Hans",
        "美國 (中文)": "https://news.google.com/rss?hl=zh-TW&gl=US&ceid=TW:zh-Hant",
        "日本 (日文)": "https://news.google.com/rss?hl=ja&gl=JP&ceid=JP:ja"
    }

    # 2. 彙整原始新聞
    raw_news_text = ""
    for region, url in sources.items():
        raw_news_text += f"\n【{region}重要新聞】\n{get_region_news(url)}\n"

    # 3. 呼叫 Gemini AI 進行重點整理
    prompt = f"""
    你是一位專業的新聞秘書。請針對以下來自台灣、中國大陸、美國、日本的原始新聞標題，
    進行分類摘要（社會、經濟、娛樂、運動）。
    
    要求：
    1. 內容要精簡，每條新聞用一句話總結重點。
    2. 必須保留原本的[連結]。
    3. 用溫暖、客觀的語氣呈現。
    4. 總結這些新聞對讀者的重要意義。

    原始新聞資料：
    {raw_news_text}
    """
    
    response = model.generate_content(prompt)
    ai_summary = response.text

    # 4. 推送到微信 (Server 醬)
    push_url = f"https://sctapi.ftqq.com/{SCKEY}.send"
    payload = {
        "title": "📍 中午時事 AI 摘要報告",
        "desp": ai_summary
    }
    
    res = requests.post(push_url, data=payload)
    if res.status_code == 200:
        print("AI 新聞摘要推送成功！")
    else:
        print(f"推送失敗: {res.text}")

if __name__ == "__main__":
    main()
