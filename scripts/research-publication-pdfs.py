"""One-off source discovery; the final publication content remains manual Markdown."""
from pathlib import Path
from urllib.parse import urljoin, urlparse, quote
from concurrent.futures import ThreadPoolExecutor
from collections import Counter
from difflib import SequenceMatcher
from datetime import datetime, timezone
from io import BytesIO
import requests, re, json, unicodedata, time, xml.etree.ElementTree as ET
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

def read_records():
    text=Path('src/publications.md').read_text().split('---',2)[2]
    records=[];year=None
    for block in re.split(r'(?=^##(?:#)? )',text,flags=re.M):
        if block.startswith('## '):year=re.search(r'## (\d+)',block).group(1)
        if not block.startswith('### '):continue
        lines=block.splitlines();title=lines[0][4:]
        resource=next(x for x in lines if x.startswith('[Paper](') or x.startswith('[arXiv]('))
        paper=re.search(r'\[(?:Paper|arXiv)\]\((https?://[^)]+)\)',resource).group(1)
        records.append({'title':title,'year':year,'paper':paper,'venue':next(x for x in lines if x.startswith('*') and not x.startswith('**'))})
    return records
records=read_records()

# Official, openly readable proceedings index pages are the strongest source.
indexes={}
def index_one(item):
    key,url=item;doc=html(url)
    return key,[(a.get_text(' ',strip=True),urljoin(url,a.get('href',''))) for a in doc.find_all('a',href=True)] if doc else []
index_urls={
 'CVPR2025':'https://openaccess.thecvf.com/CVPR2025?day=all',
 'CVPR2024':'https://openaccess.thecvf.com/CVPR2024?day=all',
 'CVPR2023':'https://openaccess.thecvf.com/CVPR2023?day=all',
 'WACV2026':'https://openaccess.thecvf.com/WACV2026?day=all',
 'ACCV2022':'https://openaccess.thecvf.com/ACCV2022?day=all',
 'ICML2025':'https://proceedings.mlr.press/v267/',
 'ECCV2024':'https://www.ecva.net/papers.php',
}
with ThreadPoolExecutor(max_workers=5) as pool:
    indexes=dict(pool.map(index_one,index_urls.items()))

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

def crossref(title):
    try:
        r=get('https://api.crossref.org/works',params={'query.title':title,'rows':3});r.raise_for_status()
        return [{'title':x.get('title',[''])[0],'doi':x.get('DOI'),'url':x.get('URL'),'links':x.get('link',[]),'score':round(similarity(title,x.get('title',[''])[0]),3)} for x in r.json()['message']['items'] if similarity(title,x.get('title',[''])[0])>=.78]
    except Exception as e:return [{'error':str(e)[:150]}]

def arxiv_search(title):
    terms=title.split(':')[0] if ':' in title else ' '.join(title.split()[:9])
    for host in ['https://export.arxiv.org/api/query','https://arxiv.org/api/query']:
        try:
            r=get(host,params={'search_query':'ti:"'+terms+'"','max_results':6});r.raise_for_status()
            root=ET.fromstring(r.text);ns={'a':'http://www.w3.org/2005/Atom'}
            found=[]
            for entry in root.findall('a:entry',ns):
                candidate=entry.findtext('a:title','',ns);ident=entry.findtext('a:id','',ns)
                if '/abs/' in ident and similarity(title,candidate)>=.65:found.append({'title':candidate,'id':ident.split('/abs/')[-1],'score':similarity(title,candidate)})
            if found:return sorted(found,key=lambda x:x['score'],reverse=True)
        except Exception:pass
    return []

def discover(record):
    title=record['title'];candidates=[];sources=[]
    def add(url,kind,source):
        if url and url not in [x['url'] for x in candidates]:candidates.append({'url':url,'kind':kind,'source':source})
    for key,links in indexes.items():
        for label,url in links:
            if similarity(title,label)<.83:continue
            if 'thecvf.com' in url and '/html/' in url:
                add(url.replace('/html/','/papers/').replace('_paper.html','_paper.pdf'),'proceedings',url)
            elif 'mlr.press' in url and url.endswith('.html'):
                doc=html(url)
                if doc:
                    for a in doc.find_all('a',href=True):
                        if '.pdf' in a['href']:add(urljoin(url,a['href']),'proceedings',url)
            elif 'ecva.net' in url and url.endswith('.pdf'):add(url,'proceedings',url)
    # Project pages can supply an official OpenReview or proceedings PDF.
    text=Path('src/publications.md').read_text()
    section=text.split('### '+title,1)[1].split('\n### ',1)[0].split('\n## ',1)[0]
    for project in re.findall(r'\[(?:Project|Code)\]\((https?://[^)]+)\)',section):
        if 'github.com/' in project and 'github.io/' not in project:continue
        doc=html(project)
        if not doc:continue
        for a in doc.find_all('a',href=True):
            u=urljoin(project,a['href'])
            if 'openreview.net/forum?id=' in u:u=u.replace('/forum?','/pdf?')
            if ('openreview.net/pdf?' in u or ('thecvf.com' in u and '.pdf' in u) or ('mlr.press' in u and '.pdf' in u)):add(u,'proceedings',project)
    works=crossref(title)
    for work in works:
        if 'error' in work:continue
        for link in work['links']:
            u=link.get('URL','')
            if link.get('content-type')=='application/pdf' or '.pdf' in u or '/pdf/' in u:add(u,'publisher',work['url'])
        doi=work.get('doi','')
        if doi.startswith('10.1007/'):
            add('https://link.springer.com/content/pdf/'+doi+'.pdf','publisher',work['url'])
        if doi.startswith('10.1145/'):
            add('https://dl.acm.org/doi/pdf/'+doi,'publisher',work['url'])
        if doi.startswith('10.1117/'):
            add('https://www.spiedigitallibrary.org/conference-proceedings-of-spie/'+doi+'/pdf','publisher',work['url'])
    if 'ieeexplore.ieee.org/document/' in record['paper']:
        ident=record['paper'].rstrip('/').split('/')[-1]
        add('https://ieeexplore.ieee.org/stampPDF/getPDF.jsp?tp=&arnumber='+ident,'publisher',record['paper'])
    # Prefer verified published versions, then a verified arXiv PDF.
    checked=[];selected=None
    for c in candidates[:8]:
        verdict=validate_pdf(c['url'],title);verdict.update(kind=c['kind'],source=c['source']);checked.append(verdict)
        if verdict.get('passed'):selected=verdict;break
    arxiv=[]
    if not selected:
        m=re.search(r'arxiv.org/abs/([^?#]+)',record['paper'])
        arxiv=[{'id':m.group(1),'title':title,'score':1}] if m else arxiv_search(title)
        for item in arxiv:
            u='https://arxiv.org/pdf/'+item['id']
            verdict=validate_pdf(u,title);verdict.update(kind='arxiv',source='https://arxiv.org/abs/'+item['id']);checked.append(verdict)
            if verdict.get('passed'):selected=verdict;break
    result={**record,'crossref':works,'arxivSearch':arxiv,'candidates':candidates,'checks':checked,'selected':selected}
    print(json.dumps({'title':title,'selected':selected and selected['url'],'kind':selected and selected['kind'],'checked':len(checked)}),flush=True)
    return result

results=[]
with ThreadPoolExecutor(max_workers=4) as pool:
    for result in pool.map(discover,records):
        results.append(result)
OUT.parent.mkdir(exist_ok=True)
OUT.write_text(json.dumps({'checkedAt':datetime.now(timezone.utc).isoformat(),'count':len(results),'selected':sum(bool(x['selected']) for x in results),'indexCounts':{k:len(v) for k,v in indexes.items()},'papers':results},ensure_ascii=False,indent=2)+'\n')
print('Selected',sum(bool(x['selected']) for x in results),'of',len(results),flush=True)
