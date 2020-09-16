import config
from script_collect_post_links import ScriptCollectPostlinks
from script_collect_datetimes import ScriptCollectDatetimes

ScriptCollectPostlinks(target_username=config.target_username,
                       post_links_file=config.post_links_file,
                       account_info_file=config.account_info_file,
                       username=config.username,
                       password=config.password).run()

ScriptCollectDatetimes(target_username=config.target_username,
                       datetimes_file=config.datetimes_file,
                       post_links_file=config.post_links_file,
                       must_perform_login= config.login_for_datetimes_collection,
                       username=config.username,
                       password=config.password).run()