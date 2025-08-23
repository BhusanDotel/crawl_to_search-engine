import schedule, time

from crawl import start_crawl

def job():
    start_crawl()

schedule.every().monday.at("09:00").do(job)

while True:
    schedule.run_pending()
    time.sleep(3600)
