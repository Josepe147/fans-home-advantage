"""Transfermarkt matchday scraper for any competition code. Usage: python tm_any.py NL1 2020,2021
Writes tm2/<comp>_<season>.csv. Stops when two matchdays in a row come back empty."""
import urllib.request, re, html, csv, time, sys, os
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36'}
pat=re.compile(r'\|(?:\([^|]*\)\|)?(?P<home>[^|()]+)\|(?:\([^|]*\)\|)?[^|]{1,30}\|(?P<score>\d+:\d+)\|(?P<away>[^|()]+)\|(?:\([^|]*\)\|)?[^|]{1,30}\|(?:\([^|]*\)\|)?[^|]*\|[^|]*\|(?P<date>\d\d/\d\d/\d{4})\s*\|(?:-[^|]*\|)?Referee: \|(?P<ref>[^|]+)\|(?P<nxt>[^|]*)\|(?P<nxt2>[^|]*)\|')
num=re.compile(r'\d{1,3}(\.\d{3})*')
def parse(t):
    s=html.unescape(re.sub(r'<[^>]+>','|',t)); s=re.sub(r'\s+',' ',s); s=re.sub(r'\|[\s|]*','|',s); out=[]
    for m in pat.finditer(s):
        nx=m.group('nxt').strip(); n2=m.group('nxt2').strip()
        if 'sold' in nx.lower() and num.fullmatch(n2): nx=n2
        att=int(nx.replace('.','')) if num.fullmatch(nx) else ''
        out.append([m.group('home').strip(),m.group('away').strip(),m.group('score'),m.group('date'),m.group('ref').strip(),att])
    return out
NMD={'L1':34,'L2':34,'BE1':34,'SC1':38,'IT1':38,'ES1':38,'GB3':46,'GB4':46,'NL1':34,'FR1':38,'PO1':34,'TR1':42,'GR1':26,'IT2':38,'ES2':42,'FR2':38,'A1':32,'DK1':26,'PL1':37,'RO1':30,'RU1':30,'C1':36,'SE1':30,'NO1':30,'FI1':22,'IR1':36,'JAP1':38}
comp=sys.argv[1]; seasons=[int(x) for x in sys.argv[2].split(',')]; os.makedirs('tm2',exist_ok=True)
for sea in seasons:
    fn=f'tm2/{comp}_{sea}.csv'
    if os.path.exists(fn): continue
    rows=[]; empty=0
    for md in range(1,NMD.get(comp,46)+1):
        url=f'https://www.transfermarkt.co.uk/x/spieltag/wettbewerb/{comp}/saison_id/{sea}/spieltag/{md}'; r=[]
        for a in range(5):
            try: t=urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=30).read().decode('utf8','ignore'); r=parse(t)
            except Exception as e: r=[]
            if r: break
            time.sleep(4+6*a)
        if not r:
            empty+=1
            if empty>=2: break
            continue
        empty=0; rows+=[[sea,md]+x for x in r]; time.sleep(1.3)
    with open(fn,'w',newline='') as f:
        w=csv.writer(f); w.writerow(['season','matchday','home','away','score','date','referee','attendance']); w.writerows(rows)
    print(comp,sea,len(rows),'matches',sum(1 for x in rows if x[-1]==''),'no attendance',flush=True)
