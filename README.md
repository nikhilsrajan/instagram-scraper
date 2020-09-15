# Instagram Scrapper
Python 3.7 tool to scrape information from Instagram using Selenium.

## How to run

A better "How to run" would be written later, but for now, I would just explain how to run some scripts I wrote.

- First, download chromedriver.

- Create a `config.py` file which contains the following informations:
    - path to the chromedriver executable in `chromedriver_executable_path`, 
    - `username` and `password` to login into Instagram, 
    - the username whose information you wish to scrape through in `target_username`, 
    - boolean `login_for_datetimes_collection` which is `True` if `target_username` is a private account, else can be set `False` (recommended)
    - path to the file where you wish to store the links to the posts in `post_links_file`, and 
    - path to the file where you wish to store the datetimes of each post in `datetimes_file`


Finally,
```
pipenv install
pipenv shell
python script_collect_post_links.py
python script_collect_datetimes.py
python analysis.py
```

## What does each script do?

- `script_collect_post_links.py` collects links to each post by `target_username` to `post_links_file`.
- `script_collect_datetimes.py` reads and goes to each link in `post_links_file` and writes it to `datetimes_file`.
- `analysis.py` reads `datetimes_file` and plots graphs for analysis.

