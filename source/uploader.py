import os.path
from pathlib import Path

import googlephotos_helper
import settings


def upload_to_google_photos(pics):
    print(f'Uploading to google photos...')
    if len(pics) > 0:
        session = googlephotos_helper.get_session()
        # 古い画像からアップロードしたほうが並び順的にいい感じだと思うのでreversedにしておく
        googlephotos_helper.upload_pics(session, reversed(pics))
        print(f'Uploading to google photos completed.')
    else:
        print(f'No photos.')


def save_to_local(pics):
    print(f'Saving to local files...')
    for data, file_name in pics:
        dir_name = settings.local_pict_dir_name
        if not os.path.exists(dir_name):
            os.mkdir(dir_name)
        path = Path(dir_name + '/' + file_name)
        path.write_bytes(data)
    print(f'Saving completed.')
