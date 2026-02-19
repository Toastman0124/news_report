import os
import requests
import feedparser
import google.generativeai as genai

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
SCKEY = os.environ.get("SCKEY")

def get_region_news(url):
    try:
        feed = feedparser.parse(url)
        news_list = []
        for entry in feed.entries[:5]:
            news_list.append(f"- 標題: {entry.title}\n  連結: {entry.link}")
        return "\n".join(news_list)
    except Exception as e:
        return f"無法抓取新聞: {str(e)}"

def main():
    if not GEMINI_API_KEY or not SCKEY:
        print("錯誤：找不到 API Key，請檢查 GitHub Secrets 設定")
        return

    # 1. 抓取新聞
    sources = {
        "台灣": "https://news.google.com/rss?hl=zh-TW&gl=TW&ceid=TW:zh-Hant",
        "中國大陸": "https://news.google.com/rss?hl=zh-CN&gl=CN&ceid=CN:zh-Hans",
        "美國": "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en",
        "日本": "https://news.google.com/rss?hl=ja&gl=JP&ceid=JP:ja"
    }
    raw_news_text = ""
    for region, url in sources.items():
        raw_news_text += f"\n### 【{region}新聞】\n{get_region_news(url)}\n"

    # 2. 初始化與模型診斷
    genai.configure(api_key=GEMINI_API_KEY)
    
    # 嘗試清單
    model_candidates = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']
    model = None
    error_logs = []

    print("開始診斷 API 狀態...")
    for name in model_candidates:
        try:
            m = genai.GenerativeModel(name)
            # 測試極簡生成
            m.generate_content("Hi", generation_config={"max_output_tokens": 1})
            model = m
            print(f"✅ 成功找到可用模型: {name}")
            break
        except Exception as e:
            error_msg = str(e)
            error_logs.append(f"模型 {name} 失敗原因: {error_msg}")
            print(f"❌ {name} 測試失敗")

    # 3. 處理結果
    if not model:
        diagnostic_report = "\n".join(error_logs)
        ai_summary = f"⚠️ Gemini API 診斷失敗\n\n【詳細報錯如下】\n{diagnostic_report}\n\n請根據報錯檢查 AI Studio 設定。"
    else:
        prompt = f"請將以下新聞做分類摘要（經濟、社會、運動），保留連結，並提供2個與長輩聊天的話題點。語系：繁體中文。\n\n資料：{raw_news_text}"
        try:
            response = model.generate_content(prompt)
            ai_summary = response.text
        except Exception as e:
            ai_summary = f"⚠️ 生成過程出錯: {str(e)}"

    # 4. 推送
    push_url = f"https://sctapi.ftqq.com/{SCKEY}.send"
    requests.post(push_url, data={"title": "☀️ 新聞 AI 診斷報告", "desp": ai_summary})

if __name__ == "__main__":
    main()
