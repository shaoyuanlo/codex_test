"""Check publication resource URLs without changing manually maintained content."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json, re, urllib.request, urllib.error, subprocess

headers={'User-Agent':'AcademicWebsiteLinkCheck/1.0 (+https://github.com/shaoyuanlo/codex_test)'}
resources=[];title=None
for line in Path('src/publications.md').read_text().splitlines():
    if line.startswith('### '):title=line[4:]
    if not title or not line.startswith(('[Paper](','[arXiv](')):continue
    for label,url in re.findall(r'\[([^\]]+)\]\((https?://[^)]+|\{\{[^}]+\}\})\)',line):
        restriction = ('institutional-access' if 'Institutional access may be required' in line else 'browser-verification' if 'Browser verification may be required' in line else None) if label == 'PDF' else None
        resources.append({'title':title,'label':label,'url':url,**({'expectedRestriction':restriction} if restriction else {})})

def check(item):
    result=dict(item)
    if item['url'].startswith('{{'):
        path=re.search(r"'(/[^']+)'",item['url']).group(1).lstrip('/')
        local=Path(path);result['localPath']=path
        result['passed']=local.is_file()
        if local.is_file() and (item['label']=='PDF' or local.suffix.lower()=='.pdf'):
            with local.open('rb') as f:result['isPdf']=b'%PDF-' in f.read(1024)
            result['passed'] &= result['isPdf']
        return result
    try:
        req=urllib.request.Request(item['url'],headers=headers)
        with urllib.request.urlopen(req,timeout=25) as response:
            chunk=response.read(8192)
            result.update(status=response.status,finalUrl=response.url,contentType=response.headers.get('Content-Type',''),passed=response.status==200)
            if item['label']=='PDF':
                result['isPdf']=b'%PDF-' in chunk[:1024]
                result['passed'] &= result['isPdf']
            challenge=any(marker in chunk.lower() for marker in [b'pardon our interruption',b'checking your browser',b'verify you are human'])
            if challenge:result.update(passed=False,reason='browser-verification')
            if not result['passed'] and item.get('expectedRestriction'):result['reason']=item['expectedRestriction']
    except urllib.error.HTTPError as e:result.update(status=e.code,passed=False,error=str(e),reason=item.get('expectedRestriction','http-error'))
    except Exception as e:result.update(passed=False,error=str(e))
    print(json.dumps(result),flush=True)
    return result
with ThreadPoolExecutor(max_workers=4) as pool:checks=list(pool.map(check,resources))
result={'sourceCommit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'checkedAt':datetime.now(timezone.utc).isoformat(),'passed':all(x['passed'] for x in checks),'count':len(checks),'verifiedCount':sum(x['passed'] for x in checks),'expectedRestrictions':sum(not x['passed'] and bool(x.get('expectedRestriction')) for x in checks),'checks':checks}
Path('docs').mkdir(exist_ok=True)
Path('docs/publication-link-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'count':len(checks),'passed':sum(x['passed'] for x in checks),'failed':sum(not x['passed'] for x in checks)}),flush=True)
