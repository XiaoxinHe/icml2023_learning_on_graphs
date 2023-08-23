import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from tqdm import tqdm


def get_authors(paper_id):
    url = f"https://icml.cc/virtual/2023/poster/{paper_id}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    script_tag = soup.find("script", type="application/ld+json")
    if script_tag:
        script_text = script_tag.string.strip()
        script_data = json.loads(script_text)
        authors = (', ').join([author['name']
                               for author in script_data['author']])

    return authors


def get_pdf_link_from_prml():
    url = "https://proceedings.mlr.press/v202/"
    response = requests.get(url)
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')

    paper_info = []
    for paper in soup.find_all('div', class_='paper'):
        paper_title = paper.find('p', class_='title').text.strip()
        openreview_link = paper.find('a', text='OpenReview')['href']
        pdf_link = paper.find('a', text='Download PDF')['href']
        paper_info.append((paper_title, openreview_link, pdf_link))
    df = pd.DataFrame(paper_info, columns=[
                      'title', 'openreview_link', 'pdf_link'])
    return df


def get_title_authors_from_icml():
    url = "https://icml.cc/virtual/2023/papers.html?filter=titles"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    paper_info = []
    for link in tqdm(soup.find_all('a', href=True)):
        href = link['href']
        if "/virtual/2023/poster/" in href:
            paper_title = link.text.strip()
            paper_id = int(href.split("/")[-1])
            authors = get_authors(paper_id)
            paper_info.append((paper_id, paper_title, authors))
    df = pd.DataFrame(paper_info, columns=['paper_id', 'title',  'authors'])
    return df


def main():

    df_prml = get_pdf_link_from_prml()
    df_icml = get_title_authors_from_icml()
    df = pd.DataFrame.merge(df_prml, df_icml, on='title')
    df.to_csv('icml2023_full.csv', index=False, columns=[
              'title', 'openreview_link', 'authors'])


if __name__ == "__main__":
    main()
