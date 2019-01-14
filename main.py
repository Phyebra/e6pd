import re
import requests
import urllib.request
import sys
import pathlib
import os
import copy
import time
import hashlib
import pathlib

# Colour terminal support check
try:
    import colorama
    from colorama import init
    init()
    from colorama import Fore, Back, Style
except ImportError:
    print("Colorama not installed on your computer. Switching to compatibility mode.")
    class Fore:
        BLACK = ''
        BLUE = ''
        CYAN = ''
        RED = ''
        YELLOW = ''
        GREEN = ''
        RESET = ''
    class Back:
        BLACK = ''
        BLUE = ''
        CYAN = ''
        RED = ''
        YELLOW = ''
        GREEN = ''
        RESET = ''

# Requests headers
headers = {'user-agent': 'e6pd/0.1a-devel -> github/phyebra'}

# Startup help menu
print(Back.BLUE + "For the integrated help menu, type --help" + Back.RESET)

# Check if integer
def isInteger(string):
    try:
        int(string)
        return True
    except ValueError:
        return False

# Temporary parsing out of commands, to be replaced with actual command processing system later
def rmCommand(string):
    string = string.split()
    string.pop(0)
    string = ' '.join(string)
    return string

# Memory efficient hashing [22058048]
def get_md5(filename):
    md5 = hashlib.md5()
    b = bytearray(128*1024)
    mv = memoryview(b)
    with open(filename, 'rb', buffering=0) as f:
        for n in iter(lambda : f.readinto(mv), 0):
            md5.update(mv[:n])
    return md5.hexdigest()

# Prefer SI (Posix) or Binary (Windows)?
mbyte = 1024*1024

# Add items to blacklist. wip
blacklist = set()

# Convert title underscores to space characters
convert_spaces = True

# Request urls
show_url = 'https://e621.net/pool/show.json?id='
index_url = 'https://e621.net/pool/index.json?query='

# Change this parameter to automatically startup in raw input mode
raw_mode = False

while True:
    
    # Startup title
    os.system("title e6pd v0.1a")
    
    # Input
    if raw_mode == True:
        print(Back.BLUE + 'Exit raw input mode: --smode' + Back.RESET)
        x = input(Fore.CYAN + "r-> " + Fore.RESET)
        if x == '--smode':
            raw_mode = False
            os.system('cls')
            continue
        x = '--raw ' + str(x)
    else:
        x = input("--> ")
    
    # Exit program
    if x == '--' or x == '--exit':
        sys.exit()
    
    # Clear screen
    if x == '--cls':
        os.system('cls')
        continue

    # Raw input mode
    if x == '--rmode':
        raw_mode = True
        os.system('cls')
        continue

    # Cache all pools
    if x == '--cache':
        # To be implemented, download a cache of comic names for fast searching
        print("Currently not implemented, sorry!")
        
    # Integrated help menu
    elif x == '--help':
        print("\n" + Back.BLUE + "GENERAL SEARCH HELP" + Back.RESET)
        print("To preview the content of a pool before downloading, type in its ID.\\n>>> Typing in '123' will return all posts from the pool 123, if it exists.")
        print("To search for pools by name, simply type in a search query.\n>>> Typing 'cute' will query (20 at a time) all the pools containing 'cute' in any form.")
        print("Note: If you want to specifically search for" + Fore.YELLOW + " numbers only" + Fore.RESET + ", you can type in --raw before your search query:\n>>> For example, to search for '1' instead of the pool #1, " + Fore.YELLOW + "--raw 1" + Fore.RESET + ". You can even escape commands e.g. " + Fore.YELLOW + "--raw -- 1" + Fore.RESET)
        print("Searching for numbers often? You can bypass the default behavior by typing in --rmode to switch to raw input. Return by typing --smode")
        print(Back.BLUE + "POOL DOWNLOAD OPERATIONS" + Back.RESET)
        print("download\t...download all images in full quality.\ntags\t...view image tags\n--src\t...search for specific tags matching criteria e.g. --src female")
    
    # Check if the supplied input is an ID. If so, we assume it's a pool id, and search accordingly.
    # Unless the user explicity escapes the numbers by typing 'raw'.
    elif (isInteger(x) and '--raw' not in x):
        
        # Get first 24 pages and associated data.
        resp = requests.get(show_url + str(x), headers=headers)
        
        # Check if there's a response. Currently there's no timeout programmed. Wip
        if resp.ok:
            
            # Get first page of requests to fill some metadata
            data = resp.json()
            print(Fore.GREEN +'<--->\t', len(resp.content), ' bytes recieved.' + Fore.RESET, sep='') 
            
            # Convert spaces if specified earlier
            if convert_spaces == True: 
                pool_name = re.sub(r'[^\w\-_\. ]', ',', str(data['name'].replace('_', ' ')))
            else:
                pool_name = re.sub(r'[^\w\-_\. ]', ',', str(data['name']))

            # Get number of pages
            pool_pages = data['post_count']
            
            # Show current pool in title
            command = 'title e6pd: ' + pool_name
            os.system(command)
            print(Back.BLUE + 'Pool: ', pool_name, '. ', pool_pages, ' pages.' + Back.RESET, sep='')
            
            # If there is a description available, print it out.
            # May add processing from BeautifulSoup later to filter Markdown.
            if data['description'] != "":
                print("="*80)
                print(data['description'])
                print("="*80)
            all_tags = set()
            for page in data['posts']:
                all_tags = all_tags | set(page['tags'].split(' '))

            # Main loop, multithreading planned soon
            while True:
                
                # Get user input
                print("\nPool operation - 'exit' to exit")
                user = input("> ")
                
                if user == 'download':
                    
                    print("Finding links. Depending on your pool, this may take a while...")

                    # Download cap is 24 pages per request, so calculate how many requests must be made.
                    if pool_pages % 24 == 0:
                        total_req = pool_pages // 24
                    else:
                        total_req = pool_pages // 24 + 1

                    # Tell the user
                    # print("# of requests to make:", total_req)

                    # Before downloading, create a list of download links.
                    download_req = 0
                    
                    # Dictonary containing the metadata of every page, including tags, download link, etc.
                    pool_meta = list()
                    pool_artists = set()
                    
                    for current_page in range(1, total_req+1, 1): 
                        if current_page == 1:
                            print("", end='')
                        print("\rFetching data:", current_page, "of", total_req, end='')
                        req = show_url + str(x) + '&page=' + str(current_page)
                        
                        # Prevent fast requests from hitting the API request limit
                        last_req = copy.copy(time.time())
                        
                        resp = requests.get(req, headers=headers)
                        if resp.ok:   
                            # Look through all the posts in the returned data
                            for page in data['posts']:
                                all_tags = all_tags | set(page['tags'].split())     # Compile the list of tags in this particular pool
                                pool_artists = pool_artists | set(page['artist'])   # Compile the list of artists in the entire pool
                                download_req += page['file_size']                   # Add the next file to the total download size count in bytes

                                # Make a copy of the current page json data as a list entry in pool_meta.
                                pool_meta += [copy.deepcopy(page)]

                        # Delay if 600ms have not yet passed
                        if time.time() - last_req < 0.6:
                            time.sleep(0.5)

                    # Convert sets to list
                    all_tags = list(all_tags)
                    pool_artists = list(pool_artists)

                    # Completion, warning about possibly very large file sizes.
                    print()
                    print(Fore.GREEN + '<--->\tMetadata for', len(pool_meta), 'posts cached.' + Fore.RESET)
                    print(Back.BLUE + " LARGE FILE WARNING " + Back.RESET)
                    print("This download will consume approximately " + Back.BLUE + str(round(download_req/mbyte, 2)) + " MB" + Back.RESET + " of disk space.")
                    user = input("Press Enter to continue or type 'n'> ")
                    
                    if user != '':
                        continue
                    else:
                        
                        # Check if there's only one artist. If so, put it in the folder name.
                        if len(pool_artists) == 1:
                            # Check if the artist name is already mentioned.
                            if pool_artists[0].lower() in pool_name.lower():
                                pool_path = pathlib.Path(os.getcwd(), (str(x) + " - " + str(pool_name)))
                            else:
                                pool_path = pathlib.Path(os.getcwd(), (str(x) + " (" + str(pool_artists[0]) + ") " + str(pool_name)))
                        else:
                            pool_path = pathlib.Path(os.getcwd(), (str(x) + " - " + str(pool_name)))
                        
                        # Prepare folders for download. To change the name of the containing folder, modify pool_path.
                        pathlib.Path(pool_path).mkdir(parents=True, exist_ok=True)
                        
                        downloaded = 0
                        
                        # Iterate through every entry created earlier to download the entire pool.
                        for page in pool_meta:
                                    
                                    # Expected hash
                                    expected_hash = page['md5']
                                    
                                    # Actual page # for pools not uploaded in time order
                                    page_num = pool_meta.index(page)
                                    
                                    # Change these values to modify the final filename.
                                    # Default is written as follows: <page> - <name> - <hash>.<ext>
                                    # For instance, 1 - Generic Comic - e9cea3ec8a2cf43e053d9971910f84b2.png
                                    filename = str(page_num + 1) + " - " + str(pool_name) + " - " + str(expected_hash) + "." + str(page['file_ext'])
                                    save_path = pathlib.Path(pool_path, filename)
                                    
                                    # print("Expected MD5:", expected_hash)
                                    print()
                                    msg = ''

                                    for i in range(3):
                                        try:
                                            print("Fetching", round(page['file_size']/mbyte, 2), "Mb - File:", filename, end='')
                                            # print(pool_path, save_path)
                                            urllib.request.urlretrieve(page['file_url'], save_path)
                                            
                                            if get_md5(save_path) == expected_hash:
                                                print(" " + Back.GREEN + " OK " + Back.RESET, end='')
                                            else:
                                                print(" " + Back.RED + " Hash Error " + Back.RESET, end='')
                                                
                                                continue

                                        except urllib.error.URLError:
                                            print(" " + Back.RED + " Con. Error " + Back.RESET, end='')
                                            continue
                                        break
                                    
                                    # For progress bar
                                    downloaded += 1

                                    # Change title
                                    title = 'title e6pd: Downloading: ' + str(round((downloaded/pool_pages)*100)) + '%'
                                    os.system(title)
                
                if user == 'tags':
                    # print a list of all tags found on the first (up to 24) pages.
                    print('Tags:' + ', '.join(all_tags))
                if '--src' in user:
                    # print a list of all tags matching the given search criteria
                    search = user.split()
                    search.pop(0)
                    for tag in all_tags:
                        for item in search:
                            if item in tag:
                                print(tag, end=' | ')
                    print('\n--end tag list--\n')
                if user == 'exit':
                    os.system('cls')
                    break
                else:
                    continue
        else:
            print("No pool found with the id", x)
    
    # Standard search for pools
    else:
        if '--raw' in x:
            x = x.split()
            x.pop(0)
            x = ' '.join(x)
        search_page = 1
        while True:
            resp = requests.get(index_url + str(x) + '&page=' + str(search_page), headers=headers)
            if resp.ok:
                
                data = resp.json()
                if len(data) == 0:
                    # If the response is empty there probably aren't any more results to show.
                    print("No data to show.")
                    break
                if len(data) == 20:
                    # If there are 20 responses there can be more data, so add "or more."
                    print(Fore.GREEN + '<--->\t', len(resp.content), ' bytes recieved. ', len(data), ' or more matches.' + Fore.RESET, sep='')
                else:
                    # If there are less than 20 responses, we can break immediately.
                    print(Fore.GREEN + '<--->\t', len(resp.content), ' bytes recieved. ', len(data), ' matches.', sep='' + Fore.RESET)
                print(Back.BLUE + 'ID #\tPages\tPool / Comic Name' + Back.RESET)
                
                for item in data:
                    if convert_spaces == True:
                        print(item['id'], '\t', item['post_count'], '\t', item['name'].replace('_', ' '), sep='')
                    else:
                        print(item['id'], '\t', item['post_count'], '\t', item['name'], sep='')
                
                if len(data) == 20:
                    print(Fore.YELLOW + "...press Enter to keep searching or type anything to cancel.", end='' + Fore.RESET)
                    user = input(" > ")
                    if user != '':
                        break
                    else:
                        search_page += 1

                else:
                    print(Back.RED + "No more data to show." + Back.RESET)
                    break
