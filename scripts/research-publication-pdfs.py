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

from playwright.sync_api import sync_playwright
import shutil
D=json.loads(OUT.read_text());paper=D['papers'][8]
pdf='https://pmc.ncbi.nlm.nih.gov/articles/PMC12310287/pdf/nihms-2095081.pdf'
status={}
try:
    with sync_playwright() as pw:
        chrome=shutil.which('google-chrome') or shutil.which('chromium')
        browser=pw.chromium.launch(executable_path=chrome,args=['--no-sandbox'])
        context=browser.new_context(accept_downloads=True);page=context.new_page()
        response=page.goto('https://pmc.ncbi.nlm.nih.gov/articles/PMC12310287/',wait_until='domcontentloaded',timeout=40000)
        page.wait_for_timeout(1500)
        text=page.locator('body').inner_text(timeout=10000)
        status.update(articleStatus=response.status if response else None,articleTitle=page.title(),articleText=text[:900])
        # Do not interact with CAPTCHA or human-verification challenges.
        blocked=any(s in text.lower() for s in ['verify you are human','captcha','pardon our interruption','access denied'])
        if not blocked:
            links=page.locator('a[href*="/pdf/"]')
            if links.count():
                href=links.first.get_attribute('href');pdf=urljoin(page.url,href)
            try:
                with page.expect_download(timeout=20000) as pending:
                    page.goto(pdf,wait_until='domcontentloaded',timeout=20000)
                download=pending.value;path=download.path();blob=Path(path).read_bytes()
                reader=PdfReader(BytesIO(blob));first=' '.join(x.extract_text() or '' for x in list(reader.pages)[:2])
                title=normalized(paper['title']);coverage=len(set(title.split())&set(normalized(first).split()))/len(set(title.split()))
                status.update(pdf=pdf,isPdf=b'%PDF-' in blob[:1024],titleCoverage=coverage,downloadedBytes=len(blob))
                if b'%PDF-' in blob[:1024] and coverage>=.9:
                    paper['selected']={'url':pdf,'finalUrl':pdf,'kind':'author-manuscript','source':'https://pmc.ncbi.nlm.nih.gov/articles/PMC12310287/','passed':True,'isPdf':True,'titleMatches':True,'titleCoverage':coverage,'browserDownload':True}
            except Exception as e:
                status['downloadError']=str(e)[:1200]
                try:status['pdfPageText']=page.locator('body').inner_text(timeout=5000)[:1000]
                except Exception:pass
        else:status['blockedByHumanVerification']=True
        browser.close()
except Exception as e:status['error']=str(e)[:1500]
paper['browserCheck']=status
D['phase']=6;D['selected']=sum(bool(x['selected']) for x in D['papers']);D['checkedAt']=datetime.now(timezone.utc).isoformat()
OUT.write_text(json.dumps(D,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(status),flush=True)
