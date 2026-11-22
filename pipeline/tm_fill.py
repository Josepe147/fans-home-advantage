"""Re-fetch any matchdays missing from the Transfermarkt files."""
import pandas as pd, glob, time, urllib.request, csv, os
src = open('analysis_tm_scrape.py').read().split("comp=sys.argv[1]")[0]
exec(src)
for f in sorted(glob.glob('tm/GB[12]_*.csv')):
    comp, sea = os.path.basename(f)[:3], int(os.path.basename(f)[4:8])
    t = pd.read_csv(f)
    have = set(t.matchday.unique()); per = 10 if comp == 'GB1' else 12
    short = set(t.groupby('matchday').size()[lambda s: s < per].index) if sea < 2026 else set()
    missing = sorted((set(range(1, NMD[comp] + 1)) - have) | short)
    if sea == 2026: missing = [x for x in missing if x <= max(have)]
    if not missing: continue
    add = []
    for md in missing:
        url = f'https://www.transfermarkt.co.uk/{SLUG[comp]}/spieltag/wettbewerb/{comp}/saison_id/{sea}/spieltag/{md}'
        r = []
        for a in range(3):
            try:
                r = parse(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read().decode('utf8', 'ignore'))
                if r: break
            except Exception as e: time.sleep(4)
        add += [[sea, md] + x for x in r]; time.sleep(1.0)
    if add:
        a = pd.DataFrame(add, columns=t.columns)
        t = pd.concat([t[~t.matchday.isin(a.matchday.unique())], a]).sort_values('matchday')
        t.to_csv(f, index=False)
    print(comp, sea, 'missing', missing, '->', len(t), 'matches', flush=True)
