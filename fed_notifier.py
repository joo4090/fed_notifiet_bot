import os, time, requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# 각 항목마다 로그로 중복 방지
def already_sent(file, content):
    if not os.path.exists(file): return False
    with open(file, 'r', encoding='utf-8') as f:
        return content in f.read()

def log_sent(file, content):
    with open(file, 'a', encoding='utf-8') as f:
        f.write(content + '\n')

# 텔레그램 전송
def send_telegram(message):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    data = {'chat_id': CHAT_ID, 'text': message}
    requests.post(url, data=data)

# 사이트 모니터링 (예시: Investing.com 미국 경제지표 캘린더)
def check_fomc():
    url = "https://www.investing.com/central-banks/fed-interest-rate-decision"
    res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(res.text, 'html.parser')
    if "Federal Reserve" in soup.text and "interest rate" in soup.text:
        line = "[FOMC] 기준금리 관련 뉴스 감지"
        if not already_sent('logs/sent_fomc.txt', line):
            send_telegram("📢 FOMC 기준금리 뉴스 발견됨!\n📎 https://www.investing.com/central-banks/fed-interest-rate-decision")
            log_sent('logs/sent_fomc.txt', line)

def check_cpi():
    url = "https://www.investing.com/economic-calendar/cpi-733"
    res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(res.text, 'html.parser')
    if "CPI" in soup.text:
        line = "[CPI] 인플레이션 뉴스 감지"
        if not already_sent('logs/sent_inflation.txt', line):
            send_telegram("📊 CPI 관련 뉴스 발견됨!\n📎 https://www.investing.com/economic-calendar/cpi-733")
            log_sent('logs/sent_inflation.txt', line)

def check_jobs():
    url = "https://www.investing.com/economic-calendar/nonfarm-payrolls-227"
    res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(res.text, 'html.parser')
    if "Nonfarm Payrolls" in soup.text or "unemployment" in soup.text:
        line = "[고용지표] 고용 뉴스 감지"
        if not already_sent('logs/sent_jobs.txt', line):
            send_telegram("💼 NFP 또는 고용 뉴스 감지!\n📎 https://www.investing.com/economic-calendar/nonfarm-payrolls-227")
            log_sent('logs/sent_jobs.txt', line)

def check_fed_speech():
    url = "https://www.investing.com/news/central-banks"
    res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(res.text, 'html.parser')
    names = ["Powell", "Waller", "Bowman"]
    for name in names:
        if name in soup.text:
            line = f"[연준 발언] {name} 발언 감지"
            if not already_sent('logs/sent_fed_speech.txt', line):
                send_telegram(f"🗣️ 연준 인사 {name} 발언 관련 뉴스 감지!\n📎 https://www.investing.com/news/central-banks")
                log_sent('logs/sent_fed_speech.txt', line)
                break

if __name__ == "__main__":
    while True:
        print("[🔍] 모니터링 중...")

        check_fomc()
        check_cpi()
        check_jobs()
        check_fed_speech()

        time.sleep(60 * 60)  # 1시간 간격
