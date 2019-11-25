import usersettings

# 動作に関連するやつ（ウエイトとかリトライ回数とか）
wait_sec_for_download_pic = 0
try_max_pic_download = 2

# 内部データの保存ディレクトリ
appdata_dir_name = 'appdata'

# 写真のローカル保存ディレクトリ
local_pict_dir_name = 'output'

# Twitter関連のファイルパスの設定
tweet_history_file_name = 'tweet_history.log'
tweet_history_file_path = f'{appdata_dir_name}/{tweet_history_file_name}'

# Google Photos関連のファイルパスの設定
googlephoto_token_file_name = 'googlephotos_token.json'
googlephoto_token_file_path = f'{appdata_dir_name}/{googlephoto_token_file_name}'
googlephoto_client_secrets_file_name = 'credentials.json'
googlephoto_client_secrets_file_path = f'{appdata_dir_name}/{googlephoto_client_secrets_file_name}'
