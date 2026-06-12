import requests
import re

url = 'https://www.xiaohongshu.com/search_result?keyword=%25E7%25A6%258F%25E4%25BA%2595&source=web_search_result_notes'
headers = {'User-Agent': 'Mozilla/5.0'}
res = requests.get(url, headers=headers, timeout=20)
html = res.text
print('status', res.status_code)
print('len', len(html))
print('head', html[:500])
patterns = [r'__INITIAL_STATE__=\\{', r'window\\.__INITIAL_STATE__', r'"notes"', r'var\\s+data\\s*=']
for p in patterns:
    print(p, bool(re.search(p, html)))
