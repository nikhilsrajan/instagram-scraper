from selenium import webdriver
import time

class InstagramInterface(object):
    def __init__(self, chromedriver_executable_path):
        self.driver = webdriver.Chrome(executable_path=chromedriver_executable_path)
        self.resize_options = [
            (400, 563),
            (1080, 720),
        ]
        self.resize_index = 0

    def resize_window(self, width, height):
        self.driver.set_window_size(width, height)

    def resize_window_by_preset(self):
        if self.resize_index == len(self.resize_options):
            raise Exception('Ran out of resize options. Must rest resize index.')
        dim = self.resize_options[self.resize_index]
        self.resize_window(dim[0], dim[1])
        self.resize_index += 1

    def reset_resize_index(self):
        self.resize_index = 0

    def close(self):
        self.driver.close()

    def quit(self):
        self.driver.quit()

    def go_to(self, url):
        status = True
        try:
            self.driver.get(url)
        except:
            status = False
        return status

    def login(self, username, password):
        status = True
        try:
            username_textbox = self.driver.find_element_by_xpath('/html/body/div[1]/section/main/article/div[2]/div[1]/div/form/div/div[1]/div/label/input')
            password_textbox = self.driver.find_element_by_xpath('/html/body/div[1]/section/main/article/div[2]/div[1]/div/form/div/div[2]/div/label/input')
            login_button = self.driver.find_element_by_xpath('/html/body/div[1]/section/main/article/div[2]/div[1]/div/form/div/div[3]/button')
            username_textbox.send_keys(username)
            password_textbox.send_keys(password)
            login_button.click()
        except:
            status = False
        return status

    def post_login(self):
        status = True
        try:
            not_now_button = self.driver.find_element_by_xpath('/html/body/div[1]/section/main/div/div/div/div/button')
            not_now_button.click()
        except:
            status = False
        return status

    def get_header_info(self, filepath=None):
        header_info = {
            'username' : self.get_username(),
            'posts' : self.get_posts_count(),
            'followers' : self.get_followers_count(),
            'following' : self.get_following_count(),
            'given name' : self.get_given_name(),
            'bio' : self.get_bio(),
            'website' : self.get_website()
        }
        if filepath is not None:
            with open(filepath, 'w+') as fout:
                for k, v in header_info.items():
                    fout.write(f'{k}: ')
                    if k in ['bio', 'given name']:
                        for c in v:
                            try:
                                fout.write(c)
                            except:
                                fout.write('[?]')
                    else:
                        fout.write(f'{v}')
                    fout.write('\n')
        return header_info        
    
    @staticmethod
    def load_header_info(filepath):
        header_info = {}
        with open(filepath, 'r') as fin:
            for line in fin:
                line = line.replace('\n', '')
                splits = line.split(': ')
                if splits[0] in ['posts', 'followers', 'following']:
                    header_info[splits[0]] = int(splits[1])
                else:
                    header_info[splits[0]] = splits[1]
        return header_info

    def check_if_at_private_account_page(self):
        try:
            at_private_account_page = str(self.driver.find_element_by_xpath('/html/body/div[1]/section/main/div/div/article/div/div/h2').get_attribute('innerHTML')) == 'This Account is Private'
        except:
            at_private_account_page = False
        return at_private_account_page

    def get_username(self):
        try:
            username = str(self.driver.find_element_by_xpath('/html/body/div[1]/section/main/div/header/section/div[1]/h2').get_attribute('innerHTML'))
        except:
            """
            case when probably there is no given name
            """
            username = str(self.driver.find_element_by_xpath('/html/body/div[1]/section/main/div/header/section/div[1]/h1').get_attribute('innerHTML'))
        return username

    def get_posts_count(self):
        return int(self.driver.find_element_by_xpath('/html/body/div[1]/section/main/div/header/section/ul/li[1]/span/span').get_attribute('innerHTML').replace(',', ''))

    def get_followers_count(self):
        return int(self.driver.find_element_by_xpath('/html/body/div[1]/section/main/div/header/section/ul/li[2]/a/span').get_attribute('title').replace(',', ''))

    def get_following_count(self):
        return int(self.driver.find_element_by_xpath('/html/body/div[1]/section/main/div/header/section/ul/li[3]/a/span').get_attribute('innerHTML').replace(',', ''))
    
    def get_given_name(self):
        try:
            given_name = str(self.driver.find_element_by_xpath('/html/body/div[1]/section/main/div/header/section/div[2]/h1').get_attribute('innerHTML'))
        except:
            given_name = ''
        return given_name

    def get_bio(self):
        bio = ''
        try:
            bio = str(self.driver.find_element_by_xpath('/html/body/div[1]/section/main/div/header/section/div[2]/span').get_attribute('innerHTML'))
        except:
            print('Warning: bio element not found.')
        return bio
    
    def get_website(self):
        website = ''
        try:
            website = str(self.driver.find_element_by_xpath('/html/body/div[1]/section/main/div/header/section/div[2]/a').get_attribute('innerHTML'))
        except:
            print('Warning: website element not found.')
        return website

    def go_to_account(self, username):
        return self.go_to(f'https://www.instagram.com/{username}')

    def get_available_posts_links(self):
        posts_links = []
        contents_element = self.driver.find_element_by_xpath('/html/body/div[1]/section/main/div/div[3]/article/div[1]/div')
        elements_tag_name_a = contents_element.find_elements_by_tag_name('a')
        for a_element in elements_tag_name_a:
            posts_links.append(a_element.get_attribute('href'))
        return posts_links
    
    def get_pageYOffset(self):
        return int(self.driver.execute_script('return window.pageYOffset'))

    def scroll_down(self, by):
        self.driver.execute_script(f'window.scrollTo(0, {self.get_pageYOffset() + by})')

    def get_first_comment(self):
        return str(self.driver.find_element_by_xpath('/html/body/div[1]/section/main/div/div[1]/article/div[3]/div[1]/ul/div/li/div/div/div[2]/span').get_attribute('innerHTML'))
    
    def get_datetime_string(self):
        return str(self.driver.find_element_by_xpath('/html/body/div[1]/section/main/div/div[1]/article/div[3]/div[2]/a/time').get_attribute('datetime'))

    def get_likes(self):
        likes = -1
        views = -1
        case = -1
        try:
            """
            case 1: N likes
            """
            likes = int(self.driver.find_element_by_xpath('/html/body/div[1]/section/main/div/div[1]/article/div[3]/section[2]/div/div/button/span').get_attribute('innerHTML').replace(',', ''))
            case = 1
        except:
            try:
                """
                case 2: Liked by SOMEONE and N others
                """
                likes = int(self.driver.find_element_by_xpath('/html/body/div[1]/section/main/div/div[1]/article/div[3]/section[2]/div/div[2]/button/span').get_attribute('innerHTML').replace(',', '')) + 1
                case = 2
            except:
                try:
                    """
                    case 3: M views -> <click> -> N likes
                    """
                    views = int(self.driver.find_element_by_xpath('/html/body/div[1]/section/main/div/div[1]/article/div[3]/section[2]/div/span/span').get_attribute('innerHTML').replace(',', ''))
                    self.driver.find_element_by_xpath('/html/body/div[1]/section/main/div/div[1]/article/div[3]/section[2]/div/span').click()
                    likes = int(self.driver.find_element_by_xpath('/html/body/div[1]/section/main/div/div[1]/article/div[3]/section[2]/div/div/div[4]/span').get_attribute('innerHTML').replace(',', ''))
                    case = 3
                except:
                    """
                    case 4: 1 view
                    """
                    try:
                        view_button = self.driver.find_element_by_xpath('/html/body/div[1]/section/main/div/div[1]/article/div[3]/section[2]/div/span')
                        views = int(view_button.get_attribute('innerHTML').split(' ')[0].replace(',', ''))
                        view_button.click()
                        likes = int(self.driver.find_element_by_xpath('/html/body/div[1]/section/main/div/div[1]/article/div[3]/section[2]/div/div/div[4]/span').get_attribute('innerHTML').replace(',', ''))
                        case = 4
                    except:
                        """
                        case 5: 1 like
                        """
                        try:
                            likes = int(self.driver.find_element_by_xpath('/html/body/div[1]/section/main/div/div/article/div[3]/section[2]/div/div/button').get_attribute('innerHTML').split(' ')[0].replace(',', ''))
                            case = 5
                        except:
                            raise Exception('Error: Encountered case not addressed.')

        return likes, views, case
    
    def get_following(self, following_file):
        following_count = self.get_following_count()
        following_set = set()
        following = self.driver.find_elements_by_class_name("-nal3")[2]
        following.click()
        time.sleep(2)
        initialise_vars = 'elem = document.getElementsByClassName("isgrP")[0]; followers = parseInt(document.getElementsByClassName("g47SY")[1].innerText); times = parseInt(followers * 0.14); followersInView1 = document.getElementsByClassName("FPmhX").length'
        initial_scroll = 'elem.scrollTop += 500'
        next_scroll = 'elem.scrollTop += 1500'
        
        with open('./jquery-3.3.1.min.js', 'r') as jquery_js:
            # 3) Read the jquery from a file
            jquery = jquery_js.read()
            # 4) Load jquery lib
            self.driver.execute_script(jquery)
            # scroll down the page
            self.driver.execute_script(initialise_vars)
            self.driver.execute_script(initial_scroll)
            time.sleep(3)

            li_index = 0

            li_elems_not_found_fails = 0
            MAX_LI_ELEMS_NOT_FOUND_FAILS = 10
            useless_scrolls = 0
            MAX_USELESS_SCROLLS = 10

            next = True
            while next:
                was_useless_scroll = True
                found_li_elements = False
                while not found_li_elements:
                    try:
                        li_elements = self.driver.find_element_by_class_name('PZuss').find_elements_by_tag_name('li')
                        found_li_elements = True
                    except:
                        li_elems_not_found_fails += 1
                        if li_elems_not_found_fails > MAX_LI_ELEMS_NOT_FOUND_FAILS:
                            raise Exception('too many li_elems_not_found fails')
                        time.sleep(2)

                li_elems_not_found_fails = 0
                while li_index < len(li_elements):
                    was_useless_scroll = False
                    profile_link = li_elements[li_index].find_element_by_xpath('div/div[1]/div[2]/div[1]/span/a').get_attribute('href')
                    li_index += 1
                    following_set.add(profile_link)
                    print(f'{profile_link}, {li_index+1} / {following_count} [ {(li_index+1) / following_count * 100} % ]')
                    with open(following_file, 'a') as fout:
                        fout.write(f'{profile_link}\n')
                
                if was_useless_scroll:
                    useless_scrolls += 1
                else:
                    useless_scrolls = 0
                
                if useless_scrolls > MAX_USELESS_SCROLLS:
                    print('too many useless scrolls')
                    next = False

                self.driver.execute_script(next_scroll)
                time.sleep(3)
                if len(li_elements) >= following_count:
                    next = False

            return list(following_set)
