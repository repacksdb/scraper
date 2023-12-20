# Author: NotCoderGuy

from colorama import Fore
from bs4 import BeautifulSoup
from time import sleep
import cfscrape
import html2text
import os
import re
import json
from datetime import datetime
from .utils.database import connect_to_database, post_data

def get_last_page(SITE_URL):
    print(Fore.GREEN + '[+] Getting last page...')
    scraper = cfscrape.create_scraper()
    response = scraper.get(SITE_URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    last_page = soup.select_one('.lcp_paginator > li:nth-child(8) > a:nth-child(1)')
    if last_page:
        last_page = last_page.text.strip()
        print(Fore.GREEN + '[+] Last page found: ' + last_page)
        return last_page
    else:
        print(Fore.RED + '[-] Last page not found.')
        return 0
    
def scrape_all_links(SITE_URL, LAST_PAGE, POSTS_LINKS):
    print(Fore.GREEN + '[+] Preparing to scrape Fitgirl...')
    
    for page in range(1, int(LAST_PAGE) + 1):
        print(Fore.GREEN + '[+] Generating page URL...')
        page_url = SITE_URL + '?lcp_page0=' + str(page) + '#lcp_instance_0'
        print(Fore.GREEN + '[+] Scraping ' + page_url + '...')
        scraper = cfscrape.create_scraper()
        response = scraper.get(page_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        posts = soup.find('ul', {'class': 'lcp_catlist'}).find_all('a')
        for post in posts:
            post_link = post['href']
            print(Fore.GREEN + '[+] Found post link: ' + post_link)
            if post_link not in POSTS_LINKS:
                print(Fore.YELLOW + '[+] Adding post link to list...')
                POSTS_LINKS.append(post_link)
                print(Fore.GREEN + '[+] Added post link to list.')
            else:
                print(Fore.RED + '[-] Post link already exists in list skipping...')
        print(Fore.GREEN + '[+] Scraped ' + str(len(posts)) + ' links from ' + page_url + '.')
        sleep(3)
    return POSTS_LINKS

def load_posts_links():
    print(Fore.GREEN + '[+] Loading posts links...')
    FILE_PATH = os.path.dirname(os.path.realpath(__file__))
    FILE_PATH = os.path.join(FILE_PATH, '../')
    FILE_PATH = os.path.join(FILE_PATH, 'data/fitgirl/links.txt')
    with open(FILE_PATH, 'r') as file:
        links = file.read().splitlines()
    print(Fore.GREEN + '[+] Found ' + str(len(links)) + ' links.')
    return links

def save_posts_links(POSTS_LINKS):
    print(Fore.GREEN + '[+] Saving posts links...')
    FILE_PATH = os.path.dirname(os.path.realpath(__file__))
    FILE_PATH = os.path.join(FILE_PATH, '../')
    FILE_PATH = os.path.join(FILE_PATH, 'data/fitgirl/links.txt')
    with open(FILE_PATH, 'w') as file:
        for link in POSTS_LINKS:
            file.write(link + '\n')
    print(Fore.GREEN + '[+] Saved ' + str(len(POSTS_LINKS)) + ' links.')

def scrape_post(post_link):
    scraper = cfscrape.create_scraper()
    response = scraper.get(post_link)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        try:
            post_title = soup.find('h1', {'class': 'entry-title'}).text.strip()
            print(Fore.GREEN + '[+] Title: ' + post_title)
            
            post_published_date = soup.find('time', class_='entry-date').text
            print(Fore.GREEN + '[+] Post Published Date: ' + post_published_date)

            post_main_poster = soup.find('img', class_='alignleft')['src']
            print(Fore.GREEN + '[+] Main Poster: ' + post_main_poster)

            content = soup.find('div', class_='entry-content')
            post_all_links = [a['href'] for a in content.find_all('a', href=True)]
            post_download_links = [link for link in post_all_links if 'riotpixels.com' not in link.lower()]
            post_images = [img['src'] for img in content.find_all('img', src=True)]
            print(Fore.GREEN + '[+] Found ' + str(len(post_download_links)) + 'download links and ' + str(len(post_images)) + ' images.')

            post_slideshow = []
            for image in post_images:
                if 'riotpixels' in image.lower():
                    post_slideshow.append(image.lower().replace('.jpg.240p.jpg', '.jpg').replace('.jpg.480p.jpg', '.jpg').replace('.jpg.720p.jpg', '.jpg').replace('.jpg.1080p.jpg', '.jpg').replace('.png.240p.png', '.png').replace('.png.480p.png', '.png').replace('.png.720p.png', '.png').replace('.png.1080p.png', '.png').replace('.webp.240p.webp', '.webp').replace('.webp.480p.webp', '.webp').replace('.webp.720p.webp', '.webp').replace('.webp.1080p.webp', '.webp').replace('.gif.240p.gif', '.gif').replace('.gif.480p.gif', '.gif').replace('.gif.720p.gif', '.gif').replace('.gif.1080p.gif', '.gif').replace('.png.240p.jpg', '.jpg').replace('.png.480p.jpg', '.jpg').replace('.png.720p.jpg', '.jpg').replace('.png.1080p.jpg', '.jpg').replace('.webp.240p.jpg', '.jpg').replace('.webp.480p.jpg', '.jpg').replace('.webp.720p.jpg', '.jpg').replace('.webp.1080p.jpg', '.jpg').replace('.gif.240p.jpg', '.jpg').replace('.gif.480p.jpg', '.jpg').replace('.gif.720p.jpg', '.jpg').replace('.gif.1080p.jpg', '.jpg'))

            post_content_html = content.encode_contents()
            post_content_markdown = html2text.html2text(post_content_html.decode('utf-8'))
            post_content_markdown = post_content_markdown.replace('\n\n', '\n')
            print(Fore.GREEN + '[+] Post Content: ' + post_content_markdown)

            repack_genre_tags = ""
            repack_company = ""
            repack_languages = ""
            repack_original_size = ""
            repack_comp_size = ""
            repack_features = []
            repack_game_description = ""
            lines = post_content_markdown.split('\n')
            post_in_game_description_section = False

            for line in lines:
                if line.startswith("Genres/Tags:"):
                    repack_genre_tags = line.replace("Genres/Tags:", "").strip()
                    repack_genre_tags = [genre.strip(' *') for genre in repack_genre_tags.split(',')]
                    print(Fore.GREEN + '[+] Genre Tags: ' + str(repack_genre_tags))
                if line.startswith("Company:"):
                    repack_company = line.replace("Company:", "").strip(' *')
                    print(Fore.GREEN + '[+] Company: ' + repack_company)
                if line.startswith("Languages:"):
                    repack_languages = line.replace("Languages:", "").strip(' *')
                    print(Fore.GREEN + '[+] Languages: ' + repack_languages)
                if line.startswith("Original Size:"):
                    repack_original_size = line.replace("Original Size:", "").strip(' *')
                    print(Fore.GREEN + '[+] Original Size: ' + repack_original_size)
                if line.startswith("Repack Size:"):
                    repack_comp_size = line.replace("Repack Size:", "").strip(' *')
                    print(Fore.GREEN + '[+] Repack Size: ' + repack_comp_size)
                    break

            for line in lines:
                if line.startswith("Game Description"):
                    post_in_game_description_section = True
                    repack_game_description = ""
                elif post_in_game_description_section:
                    if not line.strip() or any(line.startswith(heading) for heading in ["Repack Features", "Screenshots", "Download Mirrors"]):
                        break
                    else:
                        repack_game_description += line + " "

            if repack_game_description:
                repack_game_description = repack_game_description.strip()

            repack_features = []
            repack_features_section = re.search(r'Repack Features(.*?)Game Description', post_content_markdown, re.DOTALL)

            if repack_features_section:
                repack_features_text = repack_features_section.group(1).strip()
                repack_features = re.findall(r'^\s*[*-]\s*(.*?)$', repack_features_text, re.MULTILINE)
            print(Fore.GREEN + '[+] Repack Features Section: ' + str(repack_features))

            # Create a dictionary to store the extracted content
            extracted_content = {
                'url': post_link,
                'title': post_title,
                'published_date': post_published_date,
                'main_poster': post_main_poster,
                'download_links': post_download_links,
                'slideshow': post_slideshow,
                'content': post_content_markdown,
                'genre_tags': repack_genre_tags,
                'company': repack_company,
                'languages': repack_languages,
                'original_size': repack_original_size,
                'comp_size': repack_comp_size,
                'features': repack_features,
                'game_description': repack_game_description,
                'website': 'fitgirl',
            }
            return extracted_content
        except:
            print(Fore.RED + '[-] Failed to extract content from ' + post_link)
            return
    else:
        print(Fore.RED + '[-] Failed to scrape ' + post_link)
        return
    
def save_post(extracted_content):
    print(Fore.GREEN + '[+] Saving post ' + extracted_content['url'] + '...')
    FILE_PATH = os.path.dirname(os.path.realpath(__file__))
    FILE_PATH = os.path.join(FILE_PATH, '../')
    FILE_PATH = os.path.join(FILE_PATH, 'data/fitgirl/')
    FILE_PATH = os.path.join(FILE_PATH, 'repacks.json')
    if os.path.isfile(FILE_PATH):
        with open(FILE_PATH, 'r') as file:
            data = json.load(file)
        data.append(extracted_content)
        with open(FILE_PATH, 'w') as file:
            json.dump(data, file, indent=4)
        print(Fore.GREEN + '[+] Saved post ' + extracted_content['url'] + '.')
    else:
        data = []
        data.append(extracted_content)
        with open(FILE_PATH, 'w') as file:
            json.dump(data, file, indent=4)
        print(Fore.GREEN + '[+] Saved post ' + extracted_content['url'] + '.')


def load_post(post_link):
    print(Fore.GREEN + '[+] Loading post ' + post_link + '...')
    FILE_PATH = os.path.dirname(os.path.realpath(__file__))
    FILE_PATH = os.path.join(FILE_PATH, '../')
    FILE_PATH = os.path.join(FILE_PATH, 'data/fitgirl/')
    FILE_PATH = os.path.join(FILE_PATH, 'repacks.json')
    if os.path.isfile(FILE_PATH):
        with open(FILE_PATH, 'r') as file:
            data = json.load(file)
        for post in data:
            if post['url'] == post_link:
                print(Fore.GREEN + '[+] Loaded post ' + post_link + '.')
                return post
        print(Fore.RED + '[-] Post not found in local file.')
        return
    else:
        data = []
        with open(FILE_PATH, 'w') as file:
            json.dump(data, file, indent=4)
        print(Fore.RED + '[-] Repacks database not found.')
        return

def post_to_database():
    print(Fore.GREEN + '[+] Connecting to MongoDB...')
    client = connect_to_database()
    print(Fore.GREEN + '[+] Successfully connected to MongoDB.')
    print(Fore.GREEN + '[+] Posting data to MongoDB...')
    FILE_PATH = os.path.dirname(os.path.realpath(__file__))
    FILE_PATH = os.path.join(FILE_PATH, '../')
    FILE_PATH = os.path.join(FILE_PATH, 'data/fitgirl/')
    FILE_PATH = os.path.join(FILE_PATH, 'repacks.json')
    with open(FILE_PATH, 'r') as file:
        data = json.load(file)
    for post in data:
        try:
            date = datetime.strptime(post['published_date'], "%B %d, %Y")
            post['published_date'] = date.strftime("%Y-%m-%d")
        except:
            pass
        status = post_data(client, post)
        if status:
            print(Fore.GREEN + '[+] Successfully posted data to MongoDB.')
        else:
            print(Fore.RED + '[-] Failed to post data to MongoDB.')

def main():
    SITE_URL = 'https://fitgirl-repacks.site/all-my-repacks-a-z/'
    print(Fore.GREEN + '[+] Starting Fitgirl Module...')
    LAST_PAGE = get_last_page(SITE_URL)
    POSTS_LINKS = load_posts_links()
    if LAST_PAGE != 0:
        POSTS_LINKS = scrape_all_links(SITE_URL, LAST_PAGE, POSTS_LINKS)
        pass
    else:
        print(Fore.RED + '[-] Could not scrape Fitgirl.')
        return
    save_posts_links(POSTS_LINKS)
    for post_link in POSTS_LINKS:
        extracted_content = load_post(post_link)
        if not extracted_content:    
            extracted_content = scrape_post(post_link)
            if extracted_content:
                save_post(extracted_content)
            else:
                print(Fore.RED + '[-] Failed to save post.')
        else:
            print(Fore.RED + '[+] Post ' + post_link + ' already exists.')
    print(Fore.GREEN + '[+] Posting to database...')
    post_to_database()
    print(Fore.GREEN + '[+] Successfully posted to database.')
    print(Fore.GREEN + '[+] Finished Fitgirl Module.')

if __name__ == '__main__':
    main()