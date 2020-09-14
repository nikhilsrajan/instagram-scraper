import config
from InstagramInterface import InstagramInterface

"""
it was observed that when from as account a lot of posts
are tried to be opened, instagram blocks that account temporarily
but it also turns out, if one has a link to a post by a public account,
you don't need to login to view the post, consequently collect datetime
thus,
"""

target_file = f'{config.target_username}_post_links.txt'

ii = InstagramInterface(config.chromedrive_executable_path)

datetime_strings = []
with open(target_file, 'r+') as fin:
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
            