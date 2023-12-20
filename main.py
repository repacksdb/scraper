# Author: NotCoderGuy
# Import necessary modules
import threading
from colorama import Fore
from dotenv import dotenv_values

# Import individual website scraping modules
from sites.cpg import main as cpg_main
from sites.dodi import main as dodi_main
from sites.elamigos import main as elamigos_main
from sites.fitgirl import main as fitgirl_main
from sites.kaoskrew import main as kaoskrew_main
from sites.kapitalsin import main as kapitalsin_main
from sites.m4ckd0ge import main as m4ckd0ge_main
from sites.tiny import main as tiny_main
from sites.xatab import main as xatab_main

# Function to retrieve the list of enabled websites from the .env file
def get_website_list():
    config = dotenv_values('.env')
    website_list = config['ENABLED_WEBSITES'].split(',')
    website_list = [website.strip() for website in website_list]  # Remove extra spaces
    print(Fore.GREEN + '[+] Found ' + str(len(website_list)) + ' enabled repack websites.')
    print(website_list)
    return website_list

# Function to load a specific website
def load_website(website):
    print(Fore.GREEN + '[+] Loading ' + website + '...')
    
    # Call the appropriate main function for the website
    if website == 'cpg':
        cpg_main()
    elif website == 'dodi':
        dodi_main()
    elif website == 'elamigos':
        elamigos_main()
    elif website == 'fitgirl':
        fitgirl_main()
    elif website == 'kaoskrew':
        kaoskrew_main()
    elif website == 'kapitalsin':
        kapitalsin_main()
    elif website == 'm4ckd0ge':
        m4ckd0ge_main()
    elif website == 'tiny':
        tiny_main()
    elif website == 'xatab':
        xatab_main()
    else:
        print(Fore.RED + '[-] Invalid website: ' + website)

# Main function to start the scraper
def main():
    print(Fore.GREEN + '[+] Starting RepacksDB Scraper...')
    print(Fore.GREEN + '[+] Getting all enabled repack websites...')
    ENABLED_WEBSITES = get_website_list()
    print(Fore.GREEN + '[+] Loading all enabled repack websites...')
    
    # Create and start a thread for each website
    threads = []
    for website in ENABLED_WEBSITES:
        website = website.lower()
        thread = threading.Thread(target=load_website, args=(website,))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    print(Fore.GREEN + '[+] All the functions have completed execution.')
    print(Fore.GREEN + '[+] Exiting RepacksDB Scraper...')
# Entry point of the script
if __name__ == '__main__':
    main()
