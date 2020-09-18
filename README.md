# Instagram Scrapper
Python 3.7 tool to scrape information from Instagram using Selenium.

## How to run

A better "How to run" would be written later, but for now, I would just explain how to run some scripts I wrote.

- First, download [ChromeDriver](https://chromedriver.chromium.org/).

- Create a `config.py` file which contains the following informations:
    - path to the ChromeDriver executable in `chromedriver_executable_path`, 
    - `username` and `password` to login into Instagram, 
    - the username whose information you wish to scrape through in `target_username`, 
    - boolean `login_for_datetimes_collection` which is `True` if `target_username` is a private account, else can be set `False` (recommended)
    - path to the file where you wish to store the basic information of an account in `account_info_file`,
    - path to the file where you wish to store the links to the posts in `post_links_file`, and 
    - path to the file where you wish to store information of each post in `post_info_file`. Information is stored in a CSV format with header "`link, datetime_string, likes, views, case`"

        ```
        # sample-config.py

        chromedriver_executable_path = 'path/to/chromedriver.exe'

        username = 'instagram-username'
        password = 'instagram-password'

        target_username = 'instagram-username-whose-info-you-want-to-scrape'
        login_for_post_info_collection = False   # False if target_username is a public profile, else True

        account_info_file = f'./data/{target_username}_account_info.txt'
        post_links_file = f'./data/{target_username}_post_links.txt'
        post_info_file = f'./data/{target_username}_post_info.csv'
        ```


- Finally,
    ```
    pipenv install
    pipenv shell
    python run.py
    python analysis.py [WIP]
    ```

## What does each script do?

- `run.py`, first, goes through the `target_username` profile and collects links to each post. Then it goes to each post and collects information - date-time, views, likes, and dumps them into `post_info_file`
- `analysis.py` reads `post_info_file` and plots graphs for analysis. [WIP]

