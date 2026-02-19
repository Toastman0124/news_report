import os
import requests
import feedparser
import google.generativeai as genai

# 從 GitHub Secrets 讀取環境變數
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
SCKEY = os.environ.get("SCKEY")

def get_region_news(url):
    """抓取 RSS 標題與連結"""
    try:
        # 使用 Google News RSS 抓取
        feed = feedparser.parse(url)
        news_list = []
        # 每個地區取前 5 條重要新聞，確保資訊量足夠讓 AI 篩選
        for entry in feed.entries[:5]:
            news_list.append(f"- 標題: {entry.title}\n  連結: {entry.link}")
        return "\n".join(news_list)
    except Exception as e:
        return f"無法抓取此來源新聞: {str(e)}"

def main():
    # 1. 檢查必要的 API Key
    if not GEMINI_API_KEY or not SCKEY:
        print("錯誤：找不到 API Key，請檢查 GitHub Secrets 設定 (GEMINI_API_KEY, SCKEY)")
        return

    # 2. 定義 RSS 來源 (涵蓋中、台、美、日)
    sources = {
        "台灣": "https://news.google.com/rss?hl=zh-TW&gl=TW&ceid=TW:zh-Hant",
        "中國大陸": "https://news.google.com/rss?hl=zh-CN&gl=CN&ceid=CN:zh-Hans",
        "美國 (國際)": "https://news.google.com/rss?hl=zh-TW&gl=US&ceid=TW:zh-Hant",
        "日本": "https://news.google.com/rss?hl=ja&gl=JP&ceid=JP:ja"
    }

    # 3. 彙整原始新聞內容
    print("正在抓取各國新聞標題...")
    raw_news_text = ""
    for region, url in sources.items():
        news_content = get_region_news(url)
        raw_news_text += f"\n### 【{region}新聞來源】\n{news_content}\n"

    # 4. 初始化 Gemini AI (修正 404 問題的寫法)
    genai.configure(api_key=GEMINI_API_KEY)
    
    # 嘗試使用最通用的名稱，避免 v1beta 路由錯誤
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        print("嘗試調用 gemini-1.5-flash...")
    except Exception:
        model = genai.GenerativeModel('gemini-pro')
        print("切換至備用模型 gemini-pro...")

    # 5. 準備 AI 提示詞 (專為您的需求優化)
    prompt = f"""
    你是一位專業的新聞秘書。請針對以下新聞內容，進行跨國時事的重點整理。
    你的目標是讓使用者能快速掌握重點，並能與身邊長輩或朋友交談。

    請將內容歸類為：
    1. 💰 經濟與科技 (重點摘要+連結)
    2. 🏠 社會與生活 (重點摘要+連結)
    3. 🏆 運動與娛樂 (重點摘要+連結)
    4. 💡 聊天話題點：提供 2-3 個適合與長輩聊天、開啟話題的時事小撇步。

    要求：
    - 內容必須簡練，每則新聞總結不超過 30 字，並保留原始[連結]。
    - 必須包含中、台、美、日四個地區的綜合消息。
    - 日本與美國的新聞若為外文，請翻譯並總結為「繁體中文」。

    原始資料如下：
    {raw_news_text}
    """

    # 6. 呼叫 AI 生成摘要
    print("正在呼叫 Gemini AI 生成精簡摘要...")
    try:
        response = model.generate_content(
            prompt,
            # 安全設定：避免社會新聞因包含暴力文字而被擋掉
            safety_settings={
                "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
                "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE",
                "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_NONE",
                "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE",
            }
        )
        ai_summary = response.text
    except Exception as e:
        # 如果 AI 失敗，則發送原始抓取的標題作為保底
        ai_summary = f"⚠️ AI 摘要生成失敗 ({str(e)})\n以下為今日原始新聞：\n{raw_news_text}"

    # 7. 推送到微信 (Server 醬)
    push_url = f"https://sctapi.ftqq.com/{SCKEY}.send"
    payload = {
        "title": "☀️ 中午時事 AI 摘要報告",
        "desp": ai_summary
    }
    
    res = requests.post(push_url, data=payload)
    if res.status_code == 200:
        print("✅ 任務成功！內容已推送到微信。")
    else:
        print(f"❌ 推送失敗: {res.text}")

if __name__ == "__main__":
    main()
