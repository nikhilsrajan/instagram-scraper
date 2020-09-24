import config
from script_base import ScriptBase
import time
import os.path

class ScriptCollectFollowing(ScriptBase):
    def __init__(self, target_usernames, folder_path, username, password):
        ScriptBase.__init__(self)
        self.target_usernames = target_usernames
        self.folder_path = folder_path
        self.username = username
        self.password = password

    def run(self):
        if not os.path.exists(self.folder_path):
            raise Exception(f'{self.folder_path} doesn\'t exist.')

        self.perform_login(self.username, self.password)
        for target_username in self.target_usernames:
            following_file = os.path.join(self.folder_path, f'{target_username}_following.csv')
            self.run_one(target_username, following_file)
        self.ii.quit()

    def run_one(self, target_username, following_file):
        self.ii.go_to_account(target_username)
        accessible = True
        if not self.ii.check_if_at_private_account_page():
            self.ii.get_following(following_file)
        else:
            print('at private account')
            accessible = False
        return accessible

# ScriptCollectFollowing(['upsdwn'], './test_root/following', config.username, config.password).run()