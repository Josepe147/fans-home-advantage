"""Scrape Transfermarkt matchday pages: home, away, score, date, referee, attendance."""
import urllib.request, re, html, csv, time, sys, os
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36'}
SLUG={'GB1':'premier-league','GB2':'championship','L1':'bundesliga','ES1':'laliga','IT1':'serie-a','FR1':'ligue-1'}
NMD={'GB1':38,'GB2':46,'L1':34,'ES1':38,'IT1':38,'FR1':38}
pat=re.compile(r'\|(?:\([^|]*\)\|)?(?P<home>[^|()]+)\|(?:\([^|]*\)\|)?[A-Z0-9]{2,8}\|(?P<score>\d+:\d+)\|(?P<away>[^|()]+)\|(?:\([^|]*\)\|)?[A-Z0-9]{2,8}\|(?:\([^|]*\)\|)?[^|]*\|[^|]*\|(?P<date>\d\d/\d\d/\d{4})\s*\|[^|]*\|Referee: \|(?P<ref>[^|]+)\|(?P<nxt>[^|]*)\|')
def parse(t):
    s=html.unescape(re.sub(r'<[^>]+>','|',t)); s=re.sub(r'\s+',' ',s); s=re.sub(r'\|[\s|]*','|',s)
    out=[]
    for m in pat.finditer(s):
        nx=m.group('nxt').strip()
        att=int(nx.replace('.','')) if re.fullmatch(r'\d{1,3}(\.\d{3})*',nx) else ''
        out.append([m.group('home').strip(),m.group('away').strip(),m.group('score'),m.group('date'),m.group('ref').strip(),att])
    return out
comp=sys.argv[1]; seasons=[int(x) for x in sys.argv[2].split(',')]
os.makedirs('tm',exist_ok=True)
for sea in seasons:
    fn=f'tm/{comp}_{sea}.csv'
    if os.path.exists(fn): continue
    rows=[]
    for md in range(1,NMD[comp]+1):
        url=f'https://www.transfermarkt.co.uk/{SLUG[comp]}/spieltag/wettbewerb/{comp}/saison_id/{sea}/spieltag/{md}'
        for a in range(3):
            try: t=urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=30).read().decode('utf8','ignore'); break
            except Exception as e: t=''; time.sleep(5)
        r=parse(t); rows+= [[sea,md]+x for x in r]
        time.sleep(1.0)
    with open(fn,'w',newline='') as f:
        w=csv.writer(f); w.writerow(['season','matchday','home','away','score','date','referee','attendance']); w.writerows(rows)
    print(comp,sea,len(rows),'matches',sum(1 for x in rows if x[-1]==''),'no attendance',flush=True)
