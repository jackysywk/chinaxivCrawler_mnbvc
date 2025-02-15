import requests
import re
import os
import time
import jsonlines
from tqdm import tqdm
from bs4 import BeautifulSoup
import json
TIME_INTERVAL = 5

def get_html_from_url(url):

    headers = {
        # "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.6943.99 Safari/537.36",
        "User-Agent":"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Mobile Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "DNT": "1",  # Do Not Track Request Header
        # "Cookies":'JSESSIONID=4A4E9E34461F6BAB8360A3274A64A483; Hm_lvt_e0ffa85682c12db0afd8f95090cd9c7e=1737854413,1739257298,1739372401,1739589385; HMACCOUNT=7FB98E0B1A29A254; Hm_lpvt_e0ffa85682c12db0afd8f95090cd9c7e=1739590002',
        "Connection": "keep-alive",
    }
    response = requests.get(url, headers=headers)
    time.sleep(TIME_INTERVAL)
    # 确保请求成功
    if response.status_code == 200:
        # 获取页面HTML内容
        html_text = response.text
        return html_text  # 或者进行其他的处理
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
    
    return ""

def get_chinaxiv_category(html_text):

    cate_link = []
    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(html_text, 'html.parser')

    # 找到所有的<div class="box part1">标签
    divs = soup.find_all('div', class_='box part1')

    # 从这些<div>标签中提取所有的<a>标签
    a_tags = []
    for div in divs:
        a_tags.extend(div.find_all('a'))

    # 打印提取的<a>标签
    for a in a_tags:
        cate_link.append("https://chinaxiv.org" + a["href"])
        print(f'URL: {a["href"]}, Text: {a.text}')

    return cate_link

def get_time_link(html_text):
    time_links = []
    dedup_set = set()
    soup = BeautifulSoup(html_text, 'html.parser')

    # 找到ID为ulfieid1的<ul>标签
    ul_tag = soup.find('ul', id='ulfield1')

    # 从这个<ul>标签中提取所有的<a>标签
    a_tags = ul_tag.find_all('a') if ul_tag else []

    # 打印提取的<a>标签链接
    for a in a_tags:
        time_links.append("https://chinaxiv.org" + a["href"])
        print(f'URL: {a["href"]}')

    for tmp_link in time_links:
        dedup_set.add(tmp_link)
    
    return list(dedup_set)

def get_download_link(html_text):
    pdf_links = []

   
    soup = BeautifulSoup(html_text, 'html.parser')
    list_div = soup.find('div', class_='list')
    li_tags = list_div.find_all('li')
    
    for li in li_tags:
        pdf_dict = {}
        a_tag = li.find_all('a')
        download_links = ["https://chinaxiv.org" + a['href'] for a in a_tag if "下载全文" in a.text]

        h3_tags = li.find_all('h3')
        for h3_tag in h3_tags:
            title = h3_tag.text
        
        author_tags = li.find_all('div', class_='name')
        for author_tag in author_tags:
            author = author_tag.text
        
        pdf_dict['link'] = download_links
        pdf_dict['title'] = title
        pdf_dict['author'] = author
        
        pdf_links.append(pdf_dict)

    return pdf_links

def chinaxiv_empty(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')

    # 查找所有<span>标签
    span_tags = soup.find_all('span')

    # 判断是否存在符合条件的<span>标签
    found = any("没有查找" in span.text for span in span_tags)

    # 打印结果
    if found:
        return True
    else:
        return False

def get_start_url(html_text, raw_url):
    soup = BeautifulSoup(html_text, 'html.parser')

    # 查找所有class为"last"的<a>标签
    a_tags = soup.find_all('a', class_='last')

    # 从这些<a>标签中筛选出文本包含"尾页"的链接
    last_page_links = [a['href'] for a in a_tags if "尾页" in a.text]

    question_mark_index = raw_url.find('?')

    # 如果找到'?'，则替换它及其后面的内容；否则，直接附加新的查询字符串
    if question_mark_index != -1:
        # 替换原始URL中'?'及其后面的所有内容
        new_url = raw_url[:question_mark_index] + last_page_links[0]
    
    match = re.search(r'Page=(\d+)', new_url)

    # 检查是否找到匹配项并提取值
    last_page_value = match.group(1) if match else None
    
    new_current_page=0
    traverse_url = re.sub(r'(Page=)\d+', r'\g<1>{}'.format(new_current_page), new_url)
    return traverse_url, last_page_value

# def traverse_category_link(url):
#     pdf_links = []
#     match = re.search(r'pageId=(\d+)', url)
#     if match:
#         pageId = match.group(1)
#     page_text = get_html_from_url(url)

#     traverse_url, page_nums = get_start_url(page_text, url)
#     page_nums = int(page_nums)
#     ##
#     page_nums = 2
#     for idx in tqdm(range(page_nums)):
#         print(f"{idx}/{page_nums}")
#         traverse_url = re.sub(r'(Page=)\d+', r'\g<1>{}'.format(idx), traverse_url)
#         page_text = get_html_from_url(traverse_url)
#         yield get_download_link(page_text)
#         # if not chinaxiv_empty(page_text):
#         #     pdf_links += get_download_link(page_text)
#         # else:
#         #     return pdf_links
        
#     return pdf_links

def process_time_link(url):
    page_text = get_html_from_url(url)
    traverse_url, page_nums = get_start_url(page_text, url)
    page_nums = int(page_nums)
    return page_nums

def process_single_page(url, page_num):
    url = re.sub(r'(Page=)\d+', r'\g<1>{}'.format(page_num), url)
    page_text = get_html_from_url(url)
    return get_download_link(page_text)

def save_stage_link_res(links, file_name):
    with open(f"{file_name}", "w") as f:
        for link in links:
            f.write(link+'\n')


def save_stage_link_jsonl(links, file_name):
    with open(f"{file_name}", "w") as f:
        for link in links:
            json.dump({'url': link, 'done': False, 'page':None, 'total_page':None}, f)
            f.write('\n')

def load_links(file_name):
    links = []
    with open(f"./{file_name}", "r") as f:
        tmp = f.readlines()
    for t in tmp:
        links.append(t)
    return links

def load_jsonl(file_name):
    links = []
    with jsonlines.open(f"./{file_name}", "r") as reader:
        link_objs = [obj for obj in reader]
    return link_objs
def save_pdf_res(file_name, items):
    with jsonlines.open(f"{file_name}", "a") as writer:
        for item in items:
            writer.write(item)

def update_jsonl(file, index,done, page, total_page=None):
    # Read all lines
    with open(file, 'r') as f:
        lines = f.readlines()

    # Update the specific line
    if 0 <= index < len(lines):
        data = json.loads(lines[index])
        data['done'] = done
        data['page'] = page
        if total_page != None:
            data['total_page'] = total_page
        lines[index] = json.dumps(data) + '\n'
    
    # Write back all lines
    with open(file, 'w') as f:
        f.writelines(lines)
    

if __name__ == "__main__":

    if os.path.exists("./chinaxiv_cate_link.txt"):
        cate_links = load_links("chinaxiv_cate_link.txt")
    else:
        index = "https://chinaxiv.org/home.htm"
        html_text = get_html_from_url(index)
        cate_links = get_chinaxiv_category(html_text)
        save_stage_link_res(cate_links, "chinaxiv_cate_link.txt")

    
    time_links_files = os.listdir("./time_links")
    ###### testing mode######
    # cate_links  = cate_links[0:2]
    # if len(time_links_files)> 2:
    #     time_links_files = time_links_files[0:2]
    ###### Tesintg ###########
    if len(time_links_files) != len(cate_links):
        for idx, link in enumerate(cate_links):
            html_text = get_html_from_url(link.replace('\n',''))
            time_links = get_time_link(html_text)
            save_stage_link_jsonl(time_links, f"./time_links/chinaxiv_time_link_{idx}.jsonl")
    
    time_links_files = os.listdir("./time_links")

    # Scrap no of page 
    for idx, file in tqdm(enumerate(time_links_files), total=len(time_links_files)):
        time_links = load_jsonl(f"./time_links/{file}")

        for i,link_obj in enumerate(time_links):
            if link_obj['url'] is None or (len(link_obj['url']) < 5) or (link_obj['total_page']!=None):
                break
            page_num = process_time_link(link['url'])
            update_jsonl(f"./time_links/{file}",i, done=False, page=0, total_page=page_num)

    print("Start scrapping single page")
    # Scraping page
    for idx, file in tqdm(enumerate(time_links_files), total=len(time_links_files)):
        time_links = load_jsonl(f"./time_links/{file}")
        for i,link_obj in enumerate(time_links):
            last_page = link_obj['page']
            total_page = link_obj['total_page']
            url = link_obj['url']
            done = link_obj['done']
            if done == False:
                for current_page in range(last_page, total_page):
                    pdf_links = process_single_page(url, current_page)
                    if len(pdf_links) >0:
                        save_pdf_res(f"./pdf_links/pdf_links_{idx}.jsonl", pdf_links)
                        current_page+=1
                        if current_page > total_page:
                            done= True
                        update_jsonl(f"./time_links/{file}",i, done=done, page=current_page)
