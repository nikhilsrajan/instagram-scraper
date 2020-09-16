import config
from instagram_interface import InstagramInterface

class ScriptBase(object):
    def __init__(self):
        self.ii = InstagramInterface(config.chromedrive_executable_path)
    
    def perform_login(self, username, password):
        """
        until login is successful, keep trying
        wrote this way to not have unnecessary delays
        """
        self.ii.go_to('https://instagram.com')
        login_success = False 
        while not login_success:
            login_success = self.ii.login(username, password)

        """
        clicks on "not now"
        till now it has always been required
        but it is possible that this pop up might not appear
        """
        post_login_success = False
        while not post_login_success:
            post_login_success = self.ii.post_login()