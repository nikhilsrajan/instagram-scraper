import config
from script_base import ScriptBase
import os.path

class ScriptCollectPostInfo(ScriptBase):
    def __init__(self, 
                 target_username, 
                 post_info_file, 
                 post_links_file, 
                 must_perform_login=False, 
                 username=None, 
                 password=None,
                 SCROLL_DOWN_PIXELS=20,
                 MAX_TRIES=25):
        ScriptBase.__init__(self)
        
        self.POST_COUNT = -1

        self.last_datetime_string = 'NO-DATE-COLLECTED'
        self.last_likes = -1
        self.last_views = -1
        self.last_case = -1
        self.post_info_collected_count = 0

        self.target_username = target_username
        self.post_info_file = post_info_file
        self.post_links_file = post_links_file
        self.must_perform_login = must_perform_login

        if must_perform_login:
            if username is None:
                raise Exception('username required when perform login is True')
            if password is None:
                raise Exception('password required when perform login is True')

        self.username = username
        self.password = password

        self.SCROLL_DOWN_PIXELS = SCROLL_DOWN_PIXELS
        self.MAX_TRIES = MAX_TRIES

    def print_progress(self):
        if self.post_info_collected_count > 0:
            print(f'datetime_string: {self.last_datetime_string}')
            print(f'likes: {self.last_likes}')
            print(f'views: {self.last_views}')
            if self.POST_COUNT == -1:
                print('\n')
            else:
                whole, decimal = str(self.post_info_collected_count/self.POST_COUNT*100).split('.')
                percentage = whole + '.' + decimal[0:3]
                print(f'{self.post_info_collected_count} / {self.POST_COUNT} [ {percentage} % ]')
                print('---')

    def run(self):
        """
        it was observed that when from as account a lot of posts
        are tried to be opened, instagram blocks that account temporarily
        but it also turns out, if one has a link to a post by a public account,
        you don't need to login to view the post, consequently collect datetime
        thus,
        """
        if self.must_perform_login:
            self.perform_login(self.username, self.password)

        if os.path.exists(config.account_info_file):
            self.POST_COUNT = self.ii.load_header_info(config.account_info_file)['posts']
        else:
            print('Warning: Cannot display progress.')

        first_run = True
        # SKIP_LINKS = 36
        # links_skipped = 0

        with open(self.post_links_file, 'r+') as fin:
            with open(self.post_info_file, 'a') as fout:
                fout.write(f'link, datetime_string, likes, views, case\n')

            for line in fin:

                # if links_skipped < SKIP_LINKS:
                #     self.post_info_collected_count += 1
                #     links_skipped += 1
                #     continue

                link = line.replace('\n', '')
                self.ii.go_to(link)

                if first_run:
                    if(self.ii.check_if_at_private_account_page()):
                        raise Exception('At private account, cannot proceed.')
                    first_run = False

                status = False
                datetime_string = ''
                likes = -1
                views = -1
                case = -1  # InstagramInterface.get_likes()

                fails = 0

                """
                two cases are tried to be handelled.
                it is possible that I am still in the previously loaded page
                in that case the collected datetime would already be in the list
                it is also possible that datetime collection is attempted while a page is loading
                in that case exception would be raise when element is sought, status remains False
                """
                while not status:
                    try:
                        print('try')
                        datetime_string = self.ii.get_datetime_string()
                        likes, views, case = self.ii.get_likes()
                        status = True
                        print(f'success, case {case} encountered')
                    except:
                        print('fail')
                        
                        fails += 1
                        if fails >= self.MAX_TRIES:
                            """
                            Possibly encountered the case where a post has 0 likes.
                            0 likes results in absence of any element that contains likes or views.
                            """
                            likes = 0
                            break

                        status = False
                        """
                        sometimes failure happens because the element is not loaded yet (lazy load)
                        and scrolling down BIT BY BIT helps
                        if scrolled down too much, we lose information
                        """
                        self.ii.scroll_down(self.SCROLL_DOWN_PIXELS)

                if datetime_string == '':
                    raise Exception('datetime_string is empty.')

                print('dump-info')
                self.post_info_collected_count += 1
                self.last_datetime_string = datetime_string
                self.last_likes = likes
                self.last_views = views
                self.last_case = case
                with open(self.post_info_file, 'a') as fout:
                    fout.write(f'{link}, {datetime_string}, {likes}, {views}, {case}\n')
                self.print_progress()

        self.ii.quit()
