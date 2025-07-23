import os, requests, time
from bs4 import BeautifulSoup
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})

def fetch_top_news():
    res = requests.get("https://www.investing.com/news/economy", headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(res.text, "html.parser")
    headlines = soup.select(".textDiv a.title")
    news_list = []
    for headline in headlines[:5]:  # 상위 5개 뉴스만
        title = headline.get_text(strip=True)
        link = "https://www.investing.com" + headline["href"]
        news_list.append(f"{title}\n{link}")
    return "\n\n".join(news_list)

def summarize_with_openai(news_text):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    messages = [
        {"role": "system", "content": "뉴스를 한국어로 간결하게 요약해줘."},
        {"role": "user", "content": news_text}
    ]
    data = {
        "model": "gpt-4o",
        "messages": messages,
        "temperature": 0.5
    }
    response = requests.post(url, headers=headers, json=data)
    result = response.json()
    return result["choices"][0]["message"]["content"]

if __name__ == "__main__":
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    try:
        raw_news = fetch_top_news()
        summary = summarize_with_openai(raw_news)
        final_message = f"📢 {now} 경제 뉴스 요약 🇰🇷\n\n{summary}"
        send_telegram(final_message)
    except Exception as e:
        send_telegram(f"[에러 발생] {str(e)}")
