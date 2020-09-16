import config
from script_base import ScriptBase

class ScriptCollectPostlinks(ScriptBase):
    def __init__(self, 
                 target_username,
                 post_links_file,
                 account_info_file,
                 username, 
                 password,
                 MAX_POSTLINK_FAILS = 100):
        ScriptBase.__init__(self)
        
        self.collected_post_links = []

        self.target_username = target_username
        self.post_links_file = post_links_file
        self.account_info_file = account_info_file
        self.username = username
        self.password = password

        self.MAX_POSTLINK_FAILS = MAX_POSTLINK_FAILS

    def run(self):
        """
        logging in is required as scrolling gets halted
        """
        self.perform_login(self.username, self.password)

        """
        go to the account
        collect and dump header info to config.account_info_file
        """
        self.ii.go_to_account(self.target_username)
        header_info = self.ii.get_header_info(self.account_info_file)
        posts_count = header_info['posts']

        """
        collects all the post links that are available
        scrolls down
        new post links appear (lazy-load)
        repeat
        --
        if step one fails MAX_POSTLINK_FAILS, resize  window
        """
        fail_counts = 0
        while len(self.collected_post_links) < posts_count:
            """
            This while loop was added because there
            was a situation when ii.get_available_posts_links()
            threw exception. this happened because requested elements
            were unavailable.
            """
            print('new-loop-starting')
            status = False
            while not status:
                try:
                    print('try')
                    available_links = self.ii.get_available_posts_links()
                    status = True
                    print('success')
                except:
                    print('fail')
                    status = False
                    fail_counts += 1
                    if fail_counts >= self.MAX_POSTLINK_FAILS:
                        print('resizing window')
                        self.ii.resize_window_by_preset()
                        fail_counts = 0
            
            print('dump-links')
            for link in available_links:
                if link not in self.collected_post_links:
                    self.collected_post_links.append(link)
                    with open(config.post_links_file, 'a') as fout:
                        fout.write(f'{link}\n')
            self.ii.scroll_down(1080)

        self.ii.quit()
