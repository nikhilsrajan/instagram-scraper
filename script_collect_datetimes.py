import config
from script_base import ScriptBase
import os.path

class ScriptCollectDatetimes(ScriptBase):
    def __init__(self, 
                 target_username, 
                 datetimes_file, 
                 post_links_file, 
                 must_perform_login=False, 
                 username=None, 
                 password=None):
        ScriptBase.__init__(self)
        
        self.POST_COUNT = -1
        self.datetime_strings = []

        self.target_username = target_username
        self.datetimes_file = datetimes_file
        self.post_links_file = post_links_file
        self.must_perform_login = must_perform_login

        if must_perform_login:
            if username is None:
                raise Exception('username required when perform login is True')
            if password is None:
                raise Exception('password required when perform login is True')

        self.username = username
        self.password = password

    def print_progress(self):
        if len(self.datetime_strings) > 0:
            print(self.datetime_strings[-1], end='', sep='')
            if self.POST_COUNT == -1:
                print('\n')
            else:
                print(f' -- {len(self.datetime_strings)} / {self.POST_COUNT} [ {len(self.datetime_strings)/self.POST_COUNT*100} % ]')

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
        with open(self.post_links_file, 'r+') as fin:
            for line in fin:
                link = line.replace('\n', '')
                self.ii.go_to(link)

                if first_run:
                    if(self.ii.check_if_at_private_account_page()):
                        raise Exception('At private account, cannot proceed.')
                    first_run = False

                status = False
                datetime_string = ''
                """
                two cases are tried to be handelled.
                it is possible that I am still in the previously loaded page
                in that case the collected datetime would already be in the list
                it is also possible that datetime collection is attempted while a page is loading
                in that case exception would be raise when element is sought, status remains False
                """
                while not status and datetime_string not in self.datetime_strings:
                    try:
                        print('try')
                        datetime_string = self.ii.get_datetime_string()
                        status = True
                        print('success')
                    except:
                        print('fail')
                        status = False
                        
                print('dump-date')
                self.datetime_strings.append(datetime_string)
                with open(config.datetimes_file, 'a') as fout:
                    fout.write(f'{datetime_string}\n')
                self.print_progress()

        self.ii.quit()
