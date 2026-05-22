import time, json
from urllib.request import urlopen

def check():
    try:
        r = urlopen('http://127.0.0.1:9090/api/challenges/stats')
        stats = json.loads(r.read())
        r2 = urlopen('http://127.0.0.1:9090/api/challenges')
        all_ch = json.loads(r2.read())
        solving = [c for c in all_ch if c.get('status') == 'solving']

        print(f'[{time.strftime("%H:%M:%S")}] Total:{stats["total"]} Solved:{stats["solved"]} Failed:{stats["failed"]} Solving:{stats["solving"]}', flush=True)

        if solving:
            cid = solving[0]['id']
            name = solving[0]['name']
            attempts = solving[0]['attempt_count']
            print(f'  -> Current: [{cid}] {name[:40]} (attempt {attempts})', flush=True)

            r3 = urlopen(f'http://127.0.0.1:9090/api/challenges/{cid}')
            ch = json.loads(r3.read())
            if ch.get('recent_stdout'):
                last_line = ch['recent_stdout'][-1]['text']
                print(f'  -> Last: {last_line[:120]}', flush=True)

    except Exception as e:
        print(f'Error: {e}')

while True:
    check()
    time.sleep(600)