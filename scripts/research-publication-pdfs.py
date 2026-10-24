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

data=json.loads(OUT.read_text())
papers=data['papers'];supplement=[]
def add_candidate(index,url,kind,source):
    if url and url.startswith(('https://','http://')):
        supplement.append({'index':index,'url':url.replace('http://arxiv.org','https://arxiv.org'),'kind':kind,'source':source})

def pdf_metadata(index,url):
    doc=html(url)
    if not doc:return
    title=doc.find('meta',attrs={'name':'citation_title'})
    for meta in doc.find_all('meta'):
        name=(meta.get('name','') or meta.get('property','')).lower()
        value=meta.get('content','')
        if name in ['citation_pdf_url','eprints.document_url','wkhealth_pdf_url']:
            add_candidate(index,urljoin(url,value),'publisher',url)
    for a in doc.find_all('a',href=True):
        u=urljoin(url,a['href'])
        if 'arxiv.org/abs/' in u:add_candidate(index,u.replace('/abs/','/pdf/'),'arxiv',url)
        elif '.pdf' in u or 'openreview.net/pdf?' in u:
            if 'supp' not in a.get_text(' ',strip=True).lower():add_candidate(index,u,'publisher',url)
    data['papers'][index].setdefault('landingPages',[]).append({'url':url,'title':str(title) if title else doc.title and doc.title.get_text(),'text':doc.get_text(' ',strip=True)[:1800]})

# A proceedings title can be plain text, with PDF links in adjacent elements.
for index,url,keyword in [
 (2,'https://proceedings.mlr.press/v267/','Overcoming Multi-step'),
 (10,'https://www.ecva.net/papers.php','Follow the Rules')]:
    doc=html(url)
    if not doc:continue
    for text in doc.find_all(string=lambda t: t and keyword.casefold() in t.casefold()):
        parent=text.parent
        for _ in range(4):
            for a in parent.find_all('a',href=True):
                u=urljoin(url,a['href'])
                if '.pdf' in u:add_candidate(index,u,'proceedings',url)
                elif u.endswith('.html') and ('mlr.press' in u or 'ecva.net' in u):pdf_metadata(index,u)
            if parent.name in ['div','tr']:break
            parent=parent.parent
        # ECVA associates each title <dt> with subsequent <dd> resources.
        dt=text.find_parent('dt')
        if dt:
            for sibling in dt.find_next_siblings():
                if sibling.name=='dt':break
                for a in sibling.find_all('a',href=True):
                    u=urljoin(url,a['href'])
                    if '.pdf' in u:add_candidate(index,u,'proceedings',url)

# OpenReview's final paper title can differ from its original arXiv title.
for term in ['ComNeck','Bridging Compressed Image Latents']:
    url='https://api2.openreview.net/notes/search?term='+quote(term)+'&limit=20'
    try:
        r=get(url);notes=r.json().get('notes',[])
        for note in notes:
            raw=note.get('content',{}).get('title',{})
            title=raw.get('value','') if isinstance(raw,dict) else raw
            if similarity(title,papers[5]['title'])>=.55:
                add_candidate(5,'https://openreview.net/pdf?id='+note['id'],'proceedings',url)
                papers[5].setdefault('openReview',[]).append({'title':title,'id':note['id']})
    except Exception as e:papers[5].setdefault('searchErrors',[]).append(str(e))

for index,doi in [(8,'10.1109/TMI.2025.3556402'),(9,'10.1117/12.3047499'),(13,'10.1117/12.3006561')]:
    title=papers[index]['title']
    pdf_metadata(index,'https://doi.org/'+doi)
    pdf_metadata(index,papers[index]['paper'])
    try:
        url='https://api.openalex.org/works/https://doi.org/'+doi
        r=get(url);r.raise_for_status();work=r.json()
        papers[index]['openAlex']={'title':work.get('title'),'locations':work.get('locations'),'ids':work.get('ids')}
        for loc in work.get('locations',[]):
            u=loc.get('pdf_url')
            if u:add_candidate(index,u,'arxiv' if 'arxiv' in u else 'publisher',url)
            landing=loc.get('landing_page_url')
            if landing and any(host in landing for host in ['pmc.ncbi.nlm.nih.gov','arxiv.org','europepmc.org']):pdf_metadata(index,landing)
    except Exception as e:papers[index].setdefault('searchErrors',[]).append('OpenAlex: '+str(e))
    try:
        url='https://api.semanticscholar.org/graph/v1/paper/DOI:'+doi+'?fields=title,openAccessPdf,externalIds'
        r=get(url);r.raise_for_status();work=r.json();papers[index]['semanticScholar']=work
        u=(work.get('openAccessPdf') or {}).get('url')
        if u:add_candidate(index,u,'arxiv' if 'arxiv' in u else 'publisher',url)
        ident=work.get('externalIds',{}).get('ArXiv')
        if ident:add_candidate(index,'https://arxiv.org/pdf/'+ident,'arxiv',url)
    except Exception as e:papers[index].setdefault('searchErrors',[]).append('SemanticScholar: '+str(e))
    try:
        url='https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:'+doi+'&format=json&resultType=core'
        r=get(url);r.raise_for_status();work=r.json();papers[index]['europePmc']=work
        for result in work.get('resultList',{}).get('result',[]):
            for link in result.get('fullTextUrlList',{}).get('fullTextUrl',[]):
                if link.get('documentStyle')=='pdf':add_candidate(index,link.get('url'),'publisher',url)
            if result.get('pmcid'):pdf_metadata(index,'https://pmc.ncbi.nlm.nih.gov/articles/'+result['pmcid']+'/')
    except Exception as e:papers[index].setdefault('searchErrors',[]).append('EuropePMC: '+str(e))
    # Search pages also expose arXiv IDs when the API is unavailable.
    for endpoint in ['https://arxiv.org/search/?searchtype=all&query=','https://www.google.com/search?q=','https://www.bing.com/search?q=']:
        url=endpoint+quote(title+' arxiv' if 'arxiv.org/search' not in endpoint else title)
        doc=html(url)
        if not doc:continue
        for match in re.findall(r'https?://(?:www\.)?arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5}(?:v\d+)?)',str(doc)):
            add_candidate(index,'https://arxiv.org/pdf/'+match,'arxiv',url)
        papers[index].setdefault('searchPages',[]).append({'url':url,'text':doc.get_text(' ',strip=True)[:2500]})
    time.sleep(1)

# Validated arXiv fallback for the original SPIE proceedings entry (if metadata provides it).
seen=set();selected_by={}
for candidate in supplement:
    key=(candidate['index'],candidate['url'])
    if key not in seen:seen.add(key);selected_by.setdefault(candidate['index'],[]).append(candidate)
for index,candidates in selected_by.items():
    # Check publisher/proceedings before preprint repositories.
    candidates.sort(key=lambda x:x['kind']=='arxiv')
    for c in candidates[:16]:
        verdict=validate_pdf(c['url'],papers[index]['title']);verdict.update(kind=c['kind'],source=c['source'])
        papers[index].setdefault('supplementChecks',[]).append(verdict)
        print(json.dumps({'index':index,**verdict}),flush=True)
        if verdict.get('passed'):
            papers[index]['selected']=verdict;break
    papers[index]['supplementCandidates']=candidates

data['checkedAt']=datetime.now(timezone.utc).isoformat();data['phase']=2
data['selected']=sum(bool(x['selected']) for x in papers)
OUT.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
print('Selected',data['selected'],'of',len(papers),flush=True)
