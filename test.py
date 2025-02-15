from chinaixv_crawl import get_html_from_url, get_start_url, get_download_link

url = "https://chinaxiv.org/user/search.htm?type=filter&filterField=domain&value=2"
html_text = get_html_from_url(url)
print(html_text)