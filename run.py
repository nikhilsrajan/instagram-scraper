import config
from script_collect_post_links import ScriptCollectPostlinks
from script_collect_post_info import ScriptCollectPostInfo

ScriptCollectPostlinks(target_username=config.target_username,
                       post_links_file=config.post_links_file,
                       account_info_file=config.account_info_file,
                       username=config.username,
                       password=config.password).run()

ScriptCollectPostInfo(target_username=config.target_username,
                       post_info_file=config.post_info_file,
                       post_links_file=config.post_links_file,
                       must_perform_login= config.login_for_post_info_collection,
                       username=config.username,
                       password=config.password).run()