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

import xml.etree.ElementTree as ET
D=json.loads(OUT.read_text());p=D['papers'][8]
# A similar limited-angle CBCT paper is not the original single-projection paper.
p['rejectedArxivCandidate']={'url':'https://arxiv.org/pdf/2506.13545','reason':'Different title and reconstruction task; not the DOI-linked publication.'}
p['selected']=None
log=[];candidates=[]
for url in [
 'https://pmc-oa-opendata.s3.amazonaws.com/?list-type=2&max-keys=5',
 'https://pmc-oa-opendata.s3.amazonaws.com/?list-type=2&prefix=PMC12310287&max-keys=50',
 'https://pmc-oa-opendata.s3.amazonaws.com/?list-type=2&prefix=oa_comm/&max-keys=5',
 'https://pmc-oa-opendata.s3.amazonaws.com/?list-type=2&prefix=oa_noncomm/&max-keys=5',
 'https://pmc-oa-opendata.s3.amazonaws.com/?list-type=2&prefix=manuscript/&max-keys=5']:
    try:
        r=get(url);log.append({'url':url,'status':r.status_code,'text':r.text[:12000]})
        if 's3.amazonaws' in url:
            xml=ET.fromstring(r.text)
            for el in xml.iter():
                if el.tag.endswith('Key') and el.text.endswith('.pdf') and '12310287' in el.text:
                    candidates.append('https://pmc-oa-opendata.s3.amazonaws.com/'+el.text)
        else:
            for u in re.findall(r'(?:href|href)=["\']([^"\']+\.pdf)["\']',r.text):candidates.append(urljoin(url,u))
    except Exception as e:log.append({'url':url,'error':str(e)})
for url in dict.fromkeys(candidates):
    verdict=validate_pdf(url,p['title']);verdict.update(kind='author-manuscript',source='https://pmc.ncbi.nlm.nih.gov/articles/PMC12310287/')
    p.setdefault('phase4Checks',[]).append(verdict)
    if verdict.get('passed'):p['selected']=verdict;break
p['publicArchiveDiscovery']=log
D['phase']=5;D['selected']=sum(bool(x['selected']) for x in D['papers']);D['checkedAt']=datetime.now(timezone.utc).isoformat()
OUT.write_text(json.dumps(D,ensure_ascii=False,indent=2)+'\n')
print('Selected',D['selected'],'of',D['count'],flush=True)
