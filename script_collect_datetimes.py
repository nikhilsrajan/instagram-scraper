import config
from InstagramInterface import InstagramInterface

"""
it was observed that when from as account a lot of posts
are tried to be opened, instagram blocks that account temporarily
but it also turns out, if one has a link to a post by a public account,
you don't need to login to view the post, consequently collect datetime
thus,
"""
ii = InstagramInterface(config.chromedrive_executable_path)

if config.login_for_datetimes_collection:
    """
    see script_collect_post_links
    """
    ii.go_to('https://instagram.com')
    login_success = False 
    while not login_success:
        login_success = ii.login(config.username, config.password)
    post_login_success = False
    while not post_login_success:
        post_login_success = ii.post_login()

datetime_strings = []
with open(config.post_links_file, 'r+') as fin:
    for line in fin:
        link = line.replace('\n', '')
        ii.go_to(link)
        status = False
        datetime_string = ''
        """
        two cases are tried to be handelled.
        it is possible that I am still in the previously loaded page
        in that case the collected datetime would already be in the list
        it is also possible that datetime collection is attempted while a page is loading
        in that case exception would be raise when element is sought, status remains False
        """
        while not status and datetime_string not in datetime_strings:
            try:
                datetime_string = ii.get_datetime_string()
                status = True
            except:
                status = False
        datetime_strings.append(datetime_string)
        with open(config.datetimes_file, 'a') as fout:
            fout.write(f'{datetime_string}\n')
            
ii.quit()
