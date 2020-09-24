import config
from script_base import ScriptBase
import time
import os.path
import os

class ScriptRecursiveFollowing(ScriptBase):
    """
    script to:
    1. go to a target account and collect the links to accounts it is following
    2. filter out in-accessible accounts
    3. repeat (1) and (2) for every account in the filtered list
    4. repeat once again
    5. repeat once again
    """
    def __init__(self, username, password, target_username, root_folder, MAX_DEPTH=2):
        if not os.path.exists(root_folder):
            raise Exception(f'{root_folder} not found')
        
        ScriptBase.__init__(self)

        self.username = username
        self.password = password

        root_folder = os.path.normpath(root_folder)

        self.visited_file = os.path.join(root_folder, 'visited.csv')
        self.following_folder = os.path.join(root_folder, 'following')

        self.mkdir(self.following_folder)
        self.visited = set()
        self.queue = []
        
        self.profile = target_username  # username, as opposed to urls
        self.accessible = None
        self.scraped = None
        self.process_incomplete = True  # if the recursive scrapping is incomplete
        self.depth = 0
        self.MAX_DEPTH = MAX_DEPTH

        """
        visited_file stores the state of BFS
        when read line by line, BFS needs to be simulated
        """
                            #  0        1       2         3          4           5
        visited_file_header = 'profile, posts, followers, following, accessible, scraped\n'
        last_line = None
        if not os.path.exists(self.visited_file):
            with open(self.visited_file, 'w+') as fout:
                fout.write(visited_file_header)
        else:
            """
            BFS
            ---
            queue.push(start)
            while queue is not empty:
                top = queue.pop()
                for child in top.children:
                    if child not in visited:
                        queue.push(child)
                visited.push(top)
            """
            visited_file = open(self.visited_file, 'r')
            if visited_file.readline() != visited_file_header:
                raise Exception('visited_file has header missing, possibly corrupted.')
            
            line = visited_file.readline()
            
            if line:
                self.break_line_up(line) # fills self.profile, self.accessible, self.scraped
                
                terminate = False
                if self.scraped == True:
                    self.queue.insert(0, self.profile)
                    while len(self.queue) > 0 and not terminate:
                        level_size = len(self.queue)
                        while level_size > 0 and not terminate:
                            level_size -= 1
                            top = self.queue.pop(0)

                            if top != self.profile:
                                raise Exception('top not matching self.profile, visited_file possibly corrupted.')
                            
                            if self.accessible and os.path.exists(self.get_following_file(top)):
                                with open(self.get_following_file(top), 'r') as fin:
                                    for line in fin:
                                        if self.depth < self.MAX_DEPTH:
                                            child = self.get_username(line.replace('\n', ''))
                                            if child not in self.visited:
                                                self.queue.append(child)

                            self.visited.add(top)

                            line = visited_file.readline()
                            if not line:
                                terminate = True
                            else:
                                self.break_line_up(line) # fills self.profile, self.accessible, self.scraped
                                if self.scraped == False:
                                    terminate = True

                        if not terminate:
                            self.depth += 1

                    if len(self.queue) == 0:
                        if terminate:
                            self.process_incomplete = False # ie, the recusrive script has been completed.
                        else:
                            raise Exception('queue empty without visited_file read completely, visited_file possibly corrupted.')

            visited_file.close()
    
    def start(self):
        if not self.process_incomplete:
            print('Process was already completed.')
            exit(1)
        
        self.perform_login(self.username, self.password)
        
        if not self.scraped:
            self.queue.insert(0, self.profile)
        else:
            self.accessible = None
        while len(self.queue) > 0:
            level_size = len(self.queue)
            while level_size > 0:
                level_size -= 1
                self.profile = self.queue.pop(0)

                self.ii.go_to_account(self.profile)
                profile_header = self.ii.get_header_info()
                
                if self.accessible is None:
                    self.log(f'{self.profile}, {profile_header["posts"]}, {profile_header["followers"]}, {profile_header["following"]}')
                    self.accessible = self.ii.is_following_list_accessible()
                    self.log(f', {self.accessible}')
                
                if self.accessible:
                    if not os.path.exists(self.get_following_file(self.profile)):
                        if profile_header['following'] > 0:
                            following_list = self.ii.get_following()
                        with open(self.get_following_file(self.profile), 'w+') as fout:
                            for following in following_list:
                                fout.write(f'{following}\n')

                    if profile_header['following'] > 0:
                        with open(self.get_following_file(self.profile), 'r') as fin:
                            for line in fin:
                                if self.depth < self.MAX_DEPTH:
                                    child = self.get_username(line.replace('\n', ''))
                                    if child not in self.visited:
                                        self.queue.append(child)
                        
                    self.scraped = True
                    self.log(f', {self.scraped}')
                
                self.log('\n')
                self.visited.add(self.profile)
                self.accessible = None
                self.scraped = None
                
            self.depth += 1

    def log(self, message):
        with open(self.visited_file, 'a') as fout:
            fout.write(message)

    @staticmethod
    def mkdir(folderpath):
        if not os.path.exists(folderpath):
            os.system(f'mkdir {folderpath}')
            return True
        return False
    
    @staticmethod
    def mv(from_p, to_p):
        os.system(f'mv {from_p} {to_p}')

    @staticmethod
    def get_profile_url(username):
        return f'https://www.instagram.com/{username}/'
    
    @staticmethod
    def get_username(profile_url):
        return profile_url[len('https://www.instagram.com/'):-1]
    
    def get_following_file(self, profile):
        return os.path.join(self.following_folder, f'{profile}_following.csv')
    
    def break_line_up(self, line):
        """
        fills self.profile, self.accessible, self.scraped
        """
        splits = line.replace('\n', '').split(', ')
        self.profile = splits[0]
        if len(splits) == 6:
            self.accessible = True
            self.scraped = splits[5] == 'True'
        elif len(splits) == 5:
            self.accessible = splits[4] == 'True'
            self.scraped = None
        else:
            raise Exception('line incomplete, visited_file possibly corrupted.')
