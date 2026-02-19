import os
import requests
import feedparser
import google.generativeai as genai

# 從環境變數讀取 Key
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
SCKEY = os.environ.get("SCKEY")

def get_region_news(url):
    """抓取 RSS 標題與連結"""
    try:
        feed = feedparser.parse(url)
        news_list = []
        # 每個地區取前 5 條重要新聞
        for entry in feed.entries[:5]:
            news_list.append(f"標題: {entry.title}\n連結: {entry.link}")
        return "\n".join(news_list)
    except Exception as e:
        return f"無法抓取新聞: {str(e)}"

def main():
    # 1. 檢查必要的 Key
    if not GEMINI_API_KEY or not SCKEY:
        print("錯誤：找不到 API Key，請檢查 GitHub Secrets 設定 (GEMINI_API_KEY, SCKEY)")
        return

    # 2. 定義 RSS 來源 (中、台、美、日)
    sources = {
        "台灣": "https://news.google.com/rss?hl=zh-TW&gl=TW&ceid=TW:zh-Hant",
        "中國大陸": "https://news.google.com/rss?hl=zh-CN&gl=CN&ceid=CN:zh-Hans",
        "美國": "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en",
        "日本": "https://news.google.com/rss?hl=ja&gl=JP&ceid=JP:ja"
    }

    # 3. 先彙整原始新聞內容 (這是解決 UnboundLocalError 的關鍵)
    print("正在抓取各國新聞...")
    raw_news_text = ""
    for region, url in sources.items():
        news_content = get_region_news(url)
        raw_news_text += f"\n【{region}重要新聞】\n{news_content}\n"

    # 4. 初始化 Gemini AI
    genai.configure(api_key=GEMINI_API_KEY)
    
    # 嘗試使用 1.5-flash，若失敗則退回 gemini-pro
    model_name = 'models/gemini-1.5-flash'
    try:
        model = genai.GenerativeModel(model_name)
    except Exception:
        model = genai.GenerativeModel('models/gemini-pro')

    # 5. 準備 AI 提示詞 (Prompt)
    prompt = f"""
    你是一位專業的新聞秘書。請針對以下新聞內容，進行分類摘要（包含：社會、經濟、娛樂、運動）。
    
    要求：
    1. 內容精簡，每條新聞用一句話總結重點，並保留原始[連結]。
    2. 必須涵蓋中、台、美、日四個地區的消息。
    3. 如果新聞是外文(日文/英文)，請翻譯並總結為繁體中文。
    4. 最後請加一段「今日觀點」，總結這些時事對讀者的意義。

    原始資料：
    {raw_news_text}
    """

    # 6. 呼叫 AI 生成摘要
    print("正在呼叫 Gemini AI 生成摘要...")
    try:
        response = model.generate_content(
            prompt,
            safety_settings={
                "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
                "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE",
                "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_NONE",
                "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE",
            }
        )
        ai_summary = response.text
    except Exception as e:
        ai_summary = f"⚠️ AI 摘要生成失敗，原因：{str(e)}\n\n--- 原始新聞備份 ---\n{raw_news_text}"

    # 7. 推送到微信 (Server 醬)
    push_url = f"https://sctapi.ftqq.com/{SCKEY}.send"
    payload = {
        "title": "📰 中午 12 點時事 AI 秘書報告",
        "desp": ai_summary
    }
    
    res = requests.post(push_url, data=payload)
    if res.status_code == 200:
        print("✅ 任務完成！新聞已推送至微信。")
    else:
        print(f"❌ 推送失敗: {res.text}")

if __name__ == "__main__":
    main()
