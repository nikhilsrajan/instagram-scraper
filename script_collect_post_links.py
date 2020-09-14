import config
from InstagramInterface import InstagramInterface

ii = InstagramInterface(config.chromedrive_executable_path)
ii.go_to('https://instagram.com')

"""
until login is successful, keep trying
wrote this way to not have unnecessary delays
"""
login_success = False 
while not login_success:
    login_success = ii.login(config.username, config.password)

"""
clicks on "not now"
till now it has always been required
but it is possible that this pop up might not appear
"""
post_login_success = False
while not post_login_success:
    post_login_success = ii.post_login()


ii.go_to_account(config.target_username)
posts_count = ii.get_posts_count()

collected_post_links_count = 0
collected_post_links = []

"""
collects all the post links that are available
scrolls down
new post links appear (lazy-load)
repeat
"""
while len(collected_post_links) < posts_count:
    """
    This while loop was added because there
    was a situation when ii.get_available_posts_links()
    threw exception. this happened because requested elements
    were unavailable.
    """
    status = False
    while not status:
        try:
            available_links = ii.get_available_posts_links()
            status = True
        except:
            status = False

    for link in ii.get_available_posts_links():
        if link not in collected_post_links:
            collected_post_links.append(link)
            with open(f'{config.target_username}_post_links.txt', 'a') as fout:
                fout.write(f'{link}\n')
    ii.scroll_down(1080)
