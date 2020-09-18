import config
from script_base import ScriptBase
import time

class ScriptCollectPostlinks(ScriptBase):
    def __init__(self, 
                 target_username,
                 post_links_file,
                 account_info_file,
                 username, 
                 password,
                 SCROLL_DOWN_PIXELS=500,
                 MAX_POSTLINK_FAILS=25,
                 PAUSE_AFTER_POSTS_COUNT=1000,
                 PAUSE_FOR_SECS=60*5,
                 USELESS_SCROLLS_LIMIT=100):
        ScriptBase.__init__(self)
        
        self.collected_post_links = []

        self.target_username = target_username
        self.post_links_file = post_links_file
        self.account_info_file = account_info_file
        self.username = username
        self.password = password

        self.SCROLL_DOWN_PIXELS = SCROLL_DOWN_PIXELS
        self.MAX_POSTLINK_FAILS = MAX_POSTLINK_FAILS
        self.PAUSE_AFTER_POSTS_COUNT = PAUSE_AFTER_POSTS_COUNT
        self.PAUSE_FOR_SECS = PAUSE_FOR_SECS
        self.USELESS_SCROLLS_LIMIT = USELESS_SCROLLS_LIMIT

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
        count_to_pause = 0
        useless_scrolls_count = 0
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
            
            has_collected_new_links = False
            for link in available_links:
                if link not in self.collected_post_links:
                    print('dump-link')
                    useless_scrolls_count = 0
                    has_collected_new_links = True
                    count_to_pause += 1
                    self.collected_post_links.append(link)
                    with open(config.post_links_file, 'a') as fout:
                        fout.write(f'{link}\n')
            
            if not has_collected_new_links:
                print('useless scroll')
                useless_scrolls_count += 1
                if useless_scrolls_count >= self.USELESS_SCROLLS_LIMIT:
                    print('too many useless scrolls')
                    print('abrupt termination.')
                    break

            if count_to_pause >= self.PAUSE_AFTER_POSTS_COUNT:
                print(f'cooling down, {self.PAUSE_FOR_SECS} secs...')
                time.sleep(self.PAUSE_FOR_SECS)
                count_to_pause = 0

            self.ii.scroll_down(self.SCROLL_DOWN_PIXELS)

        self.ii.quit()
