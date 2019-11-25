from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import AuthorizedSession
from google.oauth2.credentials import Credentials
import json
from more_itertools import chunked
from pathlib import Path

import settings

SCOPE = 'https://www.googleapis.com/auth/photoslibrary.appendonly'


def get_session():
    auth_path = Path(settings.googlephoto_token_file_path)
    credentials = None

    # すでにトークンを取得していればそれを読み込む
    if auth_path.exists():
        try:
            credentials = Credentials.from_authorized_user_file(auth_path.absolute(), [SCOPE])
        except Exception as e:
            print(f'An erroe occured while loading a token.\n{e}')

    # まだトークンを取得していなければ取得する
    if credentials is None:
        flow = InstalledAppFlow.from_client_secrets_file(
            settings.googlephoto_client_secrets_file_path,
            scopes=SCOPE)
        credentials = flow.run_local_server(host='localhost',
                                            port=8080,
                                            authorization_prompt_message="",
                                            success_message='Authentication completed. Close this page.',
                                            open_browser=True)
        # アクセストークンを保存しておく
        cred_json = json.dumps({
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'id_token': credentials.id_token,
            'scopes': credentials.scopes,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret
        })
        try:
            auth_path.write_text(cred_json)
            print(f'Token file has been saved.')
        except OSError as e:
            print(f'An error occured while saving auth token file.\nToken: {cred_json}\nError: {e}')

    session = AuthorizedSession(credentials)
    return session


def upload_pics(session, pics):
    # Google Photosで一度にアップロードできるのは50枚までなので細切れにする
    # more_itertools.chunkedで、指定された数ごとに細切れにできる　便利！！
    group_by = 40
    pics_splitted = chunked(pics, group_by)

    for pics_elem in pics_splitted:
        successed_uploads = []
        # ファイルをアップロードしてトークンを得る
        # トークンの有効期限は1日らしいので、アップロードに1日単位の時間がかかる場合は処理を見直すかも
        for pict_bin, file_name, description in pics_elem:
            session.headers["Content-type"] = "application/octet-stream"
            session.headers["X-Goog-Upload-Protocol"] = "raw"
            session.headers["X-Goog-Upload-File-Name"] = file_name
            upload_token = session.post('https://photoslibrary.googleapis.com/v1/uploads', pict_bin)

            if upload_token.status_code == 200:
                successed_uploads.append([upload_token, description])
            else:
                print(f'An error occured while uploading file "{file_name}". Response: {upload_token}')

        # バッチ処理(mediaItems:batchCreate)用のリクエストを作る
        batch_request_body = {"newMediaItems": []}
        for upload_token, description in successed_uploads:
            batch_request_body['newMediaItems'].append(
                {"description": description,
                 "simpleMediaItem": {"uploadToken": upload_token.content.decode()}
                 }
            )

        batch_request_json = json.dumps(batch_request_body)

        result = session.post('https://photoslibrary.googleapis.com/v1/mediaItems:batchCreate', batch_request_json)
        if result.status_code != 200:
            print(f'An error occured while batch creating. \nStatus code:{result.status_code} Reason: {result.reason}')


if __name__ == '__main__':
    s = get_session()
