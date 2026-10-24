"""Supplement PDF discovery using article metadata and official proceedings."""
from pathlib import Path
from urllib.parse import urljoin, urlparse, quote
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from difflib import SequenceMatcher
from io import BytesIO
import requests, re, json, unicodedata, time
from bs4 import BeautifulSoup
from pypdf import PdfReader
OUT=Path('docs/publication-pdf-research.json')
HEADERS={'User-Agent':'AcademicWebsiteLinkCheck/1.0 (+https://github.com/shaoyuanlo/codex_test)'}
def normalized(s):
    s=unicodedata.normalize('NFKD',s).casefold()
    return re.sub(r'[^a-z0-9]+',' ',s).strip()

def similarity(a,b):
    a,b=normalized(a),normalized(b)
    if a==b:return 1.0
    return max(SequenceMatcher(None,a,b).ratio(),len(set(a.split())&set(b.split()))/max(len(set(a.split())),len(set(b.split())),1))

def get(url,**kw):
    return requests.get(url,headers=HEADERS,timeout=(12,35),**kw)

def html(url):
    try:
        r=get(url);r.raise_for_status()
        return BeautifulSoup(r.text,'html.parser')
    except Exception:return None

def validate_pdf(url,title):
    result={'url':url}
    try:
        r=get(url);result.update(status=r.status_code,finalUrl=r.url,contentType=r.headers.get('Content-Type',''))
        if not r.ok:return result
        data=r.content
        result['isPdf']=data[:1024].find(b'%PDF-')>=0
        if not result['isPdf']:return result
        try:
            reader=PdfReader(BytesIO(data));first=' '.join((page.extract_text() or '') for page in list(reader.pages)[:2])
            title_words=set(normalized(title).split());seen=set(normalized(first).split())
            coverage=len(title_words&seen)/max(len(title_words),1)
            result.update(titleCoverage=round(coverage,3),pages=len(reader.pages),bytes=len(data),titleMatches=coverage>=.7)
        except Exception as e:result['textError']=str(e)[:180];result['titleMatches']=False
        result['passed']=result.get('isPdf',False) and result.get('titleMatches',False)
    except Exception as e:result['error']=str(e)[:180]
    return result

data=json.loads(OUT.read_text());papers=data['papers'];tasks=[]
def add(i,url,kind,source):
    if (i,url) not in [(x['index'],x['url']) for x in tasks]:tasks.append({'index':i,'url':url,'kind':kind,'source':source})
# Directly associated PDF after the ECVA title, without collecting unrelated papers.
url='https://www.ecva.net/papers.php';doc=html(url)
if doc:
    for text in doc.find_all(string=lambda t:t and 'follow the rules' in t.casefold()):
        parent=text.parent
        if parent.name=='a' and '.pdf' in parent.get('href',''):add(10,urljoin(url,parent['href']),'proceedings',url)
        a=text.find_next('a',href=lambda u:u and u.endswith('.pdf') and '-supp' not in u)
        if a:add(10,urljoin(url,a['href']),'proceedings',url)
# OpenReview provides the same proceedings PDF through its API.
for ident in ['GSUNPIw7Ad','cw274Eokxt']:
    try:
        r=get('https://api2.openreview.net/notes?id='+ident)
        notes=r.json().get('notes',[])
        if notes:papers[5].setdefault('openReviewDetails',[]).append({k:notes[0].get(k) for k in ['id','content','invitations']})
    except Exception:pass
    add(5,'https://api2.openreview.net/pdf?id='+ident,'proceedings','https://openreview.net/forum?id='+ident)
# Canonical public manuscript and OA-service metadata; no authentication is used.
for url in [
 'https://pmc.ncbi.nlm.nih.gov/articles/instance/12310287/bin/nihms-2095081.pdf',
 'https://pmc.ncbi.nlm.nih.gov/articles/PMC12310287/bin/nihms-2095081.pdf',
 'https://pmc.ncbi.nlm.nih.gov/articles/PMC12310287/pdf/nihms-2095081.pdf?download=1',
 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12310287/pdf/nihms-2095081.pdf',
 'https://europepmc.org/articles/PMC12310287/bin/nihms-2095081.pdf']:
    add(8,url,'manuscript','https://pmc.ncbi.nlm.nih.gov/articles/PMC12310287/')
try:
    r=get('https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id=PMC12310287')
    papers[8]['oaPackage']=r.text[:3000]
except Exception:pass
# Short, distinctive searches avoid requiring every word in a long title.
queries={8:['"Cycle-domain" "CBCT"','"CG-DDPM"','"3556402"'],9:['"TTT-Vnet"','"3047499"'],13:['"Patient-specific" "volumetric" "diffusion"','"3006561"']}
for i,terms in queries.items():
    for term in terms:
        url='https://arxiv.org/search/?searchtype=all&query='+quote(term)
        doc=html(url)
        if not doc:continue
        found=[]
        for row in doc.select('li.arxiv-result'):
            title=row.select_one('p.title');a=row.select_one('p.list-title a')
            if not title or not a:continue
            if similarity(title.get_text(' ',strip=True),papers[i]['title'])<.55:continue
            ident=a['href'].split('/abs/')[-1]
            add(i,'https://arxiv.org/pdf/'+ident,'arxiv',a['href'])
            found.append({'title':title.get_text(' ',strip=True),'id':ident})
        papers[i].setdefault('shortSearches',[]).append({'url':url,'found':found})
# Exact DOI-linked proceedings PDF destinations (can still require subscription).
add(9,'https://www.spiedigitallibrary.org/conference-proceedings-of-spie/13406/134062Y/TTT-Vnet--a-3D-vision-test-time-training-model/10.1117/12.3047499.pdf','publisher','https://doi.org/10.1117/12.3047499')
add(13,'https://www.spiedigitallibrary.org/conference-proceedings-of-spie/12931/129310P/Patient-specific-3D-volumetric-CBCT-image-reconstruction-with-single-x/10.1117/12.3006561.pdf','publisher','https://doi.org/10.1117/12.3006561')
for c in tasks:
    i=c['index']
    # Once a new matching PDF has passed, preserve it rather than repeatedly fetching.
    if papers[i].get('phase3Selected'):continue
    verdict=validate_pdf(c['url'],papers[i]['title']);verdict.update(kind=c['kind'],source=c['source'])
    papers[i].setdefault('phase3Checks',[]).append(verdict)
    print(json.dumps({'index':i,**verdict}),flush=True)
    if verdict.get('passed'):papers[i]['selected']=verdict;papers[i]['phase3Selected']=True
# Keep the research record reviewable; omit the unrelated whole-index candidates.
for p in papers:
    if len(p.get('supplementCandidates',[]))>30:p['supplementCandidatesOmitted']=len(p.pop('supplementCandidates'))
    p.pop('europePmc',None)
data['phase']=3;data['selected']=sum(bool(x['selected']) for x in papers);data['checkedAt']=datetime.now(timezone.utc).isoformat()
OUT.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
print('Selected',data['selected'],'of',len(papers),flush=True)
