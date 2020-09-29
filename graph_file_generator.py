import os, os.path
import json

"""
JSON Format
-----------
{
    "nodes": [
        {
            "id": 0,
            "name": "A",
            "group": 1
        },
        {
            "id": 1,
            "name": "B",
            "group": 1
        },
        {
            "id": 2,
            "name": "C",
            "group": 1
        },
        {
            "id": 3,
            "name": "D",
            "group": 2
        }
    ],
    "links": [
        {
            "id": 0,
            "source": 0,
            "target": 1,
            "value": 0.3,
            "bi_directional": true
        },
        {
            "id": 1,
            "source": 1,
            "target": 2,
            "value": 0.3,
            "bi_directional": false
        },
        {
            "id": 2,
            "source": 2,
            "target": 0,
            "value": 0.3,
            "bi_directional": false
        }
    ]
}

DOT Format
----------
digraph G {
    A -> { B };
    B -> { A C };
    C -> { A };
    D -> {};
}

==============================================================

usage:
-----
start_list = [
    'target_username_1',
    'target_username_2',
]

fc = FileCollector('path/to/(*.)_following.csv files')
for start in start_list:
    fc.gather_files(start_username=start,   # gather_files performs BFS starting from start_username
                    max_depth=1)            # max_depth works same as MAX_DEPTH in ScriptRecursiveFollowing

gfg = GraphFileGenerator()
gfg.compile_by_files(fc.filepaths)          # compile_by_files creates a node - connections map using the following_files

gfg.prune(remove_if_occurance_le=10,        # remove the user, connection if occurs less than 10 times
          min_connections_per_user=10,      # remove the user if it has less than 10 connections
          prune_users=False,                # should prune users by remove_if_occurance_le
          prune_connections=True)           # should prune connections by remove_if_occurance_le

gfg.export_as_json(relations_path='./visualise/relations.json', 
                   use_pruned=True, 
                   isolate=start_list)

"""
class GraphFileGenerator(object):
    """
    given a file or a folder, it would read the (.*)_following.csv files
    and export a full-graph or pruned-graph to json or DOT.
    """
    def __init__(self):
        self.graph = dict()
        self.pruned_graph = None
        self.name_ID_map = dict()
        self.current_ID = 1
        self.name_count_map = dict()

        self.valid_file_suffix = '_following.csv'  # {username}_following.csv
        self.valid_connection_prefix = 'https://www.instagram.com/' # https://www.instagram.com/{username}/
    
    def compile_by_folder(self, folderpath):
        folderpath = os.path.normpath(folderpath)
        for filename in os.listdir(folderpath):
            filepath = os.path.join(folderpath, filename)
            self.compile_by_file(filepath)
        
    def compile_by_files(self, filepaths):
        for filepath in filepaths:
            self.compile_by_file(filepath)
    
    def compile_by_file(self, filepath):
        filename = filepath.replace('\\', '/').split('/')[-1]
        if filename[-len(self.valid_file_suffix):] != self.valid_file_suffix:
            print(f'{filename} has invalid suffix {filename[-len(self.valid_file_suffix):]}, ignoring...')
            return
        username = filename[:-len(self.valid_file_suffix)]
        connections = self.__get_connections(filepath)
        self.graph[username] = connections

    def prune(self, remove_if_occurance_le=2, min_connections_per_user = 1,
              prune_users=True, prune_connections=True, ignore_users=set()):
        """
        to be used after compile
        """
        self.pruned_graph = dict()
        usernames_with_count_le = set()

        # count the occurances of each name
        for username, connections in self.graph.items():
            self.__count_name(username)
            for connection in connections:
                self.__count_name(connection)

        # collect names with single occurance
        for username, count in self.name_count_map.items():
            if count <= remove_if_occurance_le:
                usernames_with_count_le.add(username)
        
        # create a new graph with single occurance names removed
        usernames_omitted = 0
        connections_omitted = 0
        for username, connections in self.graph.items():
            if username in ignore_users:
                continue
            if username not in usernames_with_count_le or not prune_users:
                p_connections = set()
                for connection in connections:
                    if connection in ignore_users:
                        continue
                    if connection not in usernames_with_count_le or not prune_connections:
                        p_connections.add(connection)
                    else:
                        connections_omitted += 1
                if len(p_connections) >= min_connections_per_user:
                    self.pruned_graph[username] = p_connections
                else:
                    usernames_omitted += 1
            else:
                usernames_omitted += 1
        
        print(f'usernames omitted: {usernames_omitted}')
        print(f'connections omitted: {connections_omitted}')

    def __count_name(self, name):
        if name in self.name_count_map.keys():
            self.name_count_map[name] += 1
        else:
            self.name_count_map[name] = 1

    def __get_connections(self, filepath):
        connections = set()
        with open(filepath, 'r') as fin:
            line_number = 1
            for line in fin:
                line = line.replace('\n', '')
                if line[:-(len(line) - len(self.valid_connection_prefix))] != self.valid_connection_prefix:
                    print(f'Invalid connection, {line}, at line number {line_number}')
                    raise Exception('Invalid connection format')
                connections.add(line[len(self.valid_connection_prefix):-1]) 
                line_number += 1
        return connections

    def __get_ID(self, name):
        if name in self.name_ID_map.keys():
            ID = self.name_ID_map[name]
        else:
            ID = self.current_ID
            self.current_ID += 1
            self.name_ID_map[name] = ID
        return ID

    def export_as_dot(self, export_path='export.DOT', use_pruned=True):
        if not use_pruned:
            graph = self.graph
        else:
            graph = self.pruned_graph
        with open(export_path, 'w+') as fout:
            fout.write('digraph G {\n')
            for username, connections in graph.items():
                fout.write(f'\t{self.__get_ID(username)} -> {{')
                for connection in connections:
                    fout.write(f' {self.__get_ID(connection)}')
                fout.write(' };\n')
            fout.write('}')
    
    def export_as_json(self, relations_path='relations.json', use_pruned=True, isolate=[]):
        """
        as per https://github.com/MaximPiessen/instagram_network_analysis
        """
        if use_pruned:
            graph = self.pruned_graph
        else:
            graph = self.graph
        relations_path = os.path.normpath(relations_path)
        nodes = set()
        relations = dict()
        edges = set()
        name_to_id = dict()
        for username, connections in graph.items():
            nodes.add(username)
            for connection in connections:
                nodes.add(connection)
                edges.add((username, connection))
        
        relations['nodes'] = []
        id_n = 0
        for node in nodes:
            group = 1
            if node in isolate:
                group = 2
            
            relations['nodes'].append({'id':id_n, 'name':node, 'group':group})

            name_to_id[node] = id_n
            id_n += 1
        
        relations['links'] = []
        bi_links = set()
        id_l = 0
        for accounts in edges:
            id_1 = name_to_id[accounts[0]]
            id_2 = name_to_id[accounts[1]]
            if (accounts[1], accounts[0]) in edges:
                bi_links.add((id_1, id_2))
                if (id_1, id_2) not in bi_links:
                    relations['links'].append({'id':id_l, 'source':id_1, 'target':id_2, 'value': 0.3, 'bi_directional':True})
                    id_l += 1
            else:
                relations['links'].append({'id':id_l, 'source':id_1, 'target':id_2, 'value': 0.3, 'bi_directional':False})
                id_l += 1

        with open(relations_path, 'w') as fout:
            json.dump(relations, fout)


class FileCollector(object):
    """
    collects a list of files to pass to the GraphFileGenerator
    """
    def __init__(self, followings_folder_path):
        self.followings_folder_path = os.path.normpath(followings_folder_path)
        self.filepaths = set()

    def gather_files(self, start_username, max_depth=2):
        start_file = self.__get_following_filepath(start_username)
        print(start_file)
        
        if not os.path.exists(start_file):
            print(f'{start_file} not found.')
            print('gather_files deliberately terminated.')
            return
        
        newly_added_files_count = 0
        queue = [start_file]
        visited = set([start_file])
        current_depth = 0
        while len(queue) > 0:
            level_size = len(queue)
            while level_size > 0:
                level_size -= 1
                top_file = queue.pop(0)
                with open(top_file, 'r') as fin:
                    print(f'reading: {top_file}')
                    for line in fin:
                        if current_depth < max_depth:
                            child_username = self.__get_username_from_url(line.replace('\n', ''))
                            child_file = self.__get_following_filepath(child_username)
                            if os.path.exists(child_file):
                                if child_file not in visited:
                                    queue.append(child_file)
                                    visited.add(child_file)
                                    print(f'added: {child_file}')
                                    newly_added_files_count += 1
                self.filepaths.add(top_file)
            current_depth += 1
        print(f'newly added {newly_added_files_count} files')
        print(f'total files added {len(self.filepaths)}')

    def __get_following_filepath(self, username):
        return os.path.join(self.followings_folder_path, f'{username}_following.csv')
    
    def __get_username_from_url(self, url):
        return url[len('https://www.instagram.com/'):-1]
