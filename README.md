# e6pd
Script to search for and download pools off of e621/e926.

### Requirements
- Python 3
- Modules `requests`, `colorama` (optional but highly recommended)

### Setup
- Install Python  
**Ubuntu:** Python should already be installed. Type `apt install python3-pip`  
**Windows:** Install Python from [here](https://www.python.org/downloads/) and tick `Add Python to PATH`
- Download this repository's files and move them into a folder you want to use for downloads.
- If you don't have the modules, install them by typing:  
**Ubuntu:** `pip3 install requests` and `pip3 install colorama`  
**Windows:** `pip install requests` and `pip install colorama`

### Usage
- Start `main.py` in a pool folder
- To search for a pool, type in your search term directly in the command line to get a list of results.
- To download a pool, type in its ID, then type 'download', confirming the prompts.

### Features
- Low memory footprint
- Automatic naming of folders with pool name

### WIP Features
- Multithreaded downloading
- Markdown filtering (requires `BeautifulSoup`)
- Blacklist hit warnings
- Existing file detection
- User-accessible file renaming settings
- Checksum verification
- Single-command download
