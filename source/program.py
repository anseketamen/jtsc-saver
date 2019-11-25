import datetime
import os
from pathlib import Path
import pickle
import time
import tweepy
import urllib.error
import urllib.request

import uploader
import usersettings
import settings


def get_tweets(api):
    since_id = None
    try:
        with open(settings.tweet_history_file_path, 'r') as f:
            for line in f.readlines():
                since_id = int(line.split(',')[-1])
    # ファイルがない場合
    except FileNotFoundError:
        pass
    # intに変換できなかった場合（しらん）
    except ValueError:
        pass

    results = []
    max_id = None

    # 最大3200件までぶわーっと取得する
    while True:
        # countは最大200で、最新から3200件まで取得できる
        # レートリミット 900 / 15min
        # since_idより新しくて、max_idと同じかそれより古いツイートを取得
        if since_id is None:
            if max_id is None:
                response = api.user_timeline(id=api.me().screen_name, count=200)
            else:
                response = api.user_timeline(id=api.me().screen_name, max_id=max_id, count=200)
        else:
            if max_id is None:
                response = api.user_timeline(id=api.me().screen_name, since_id=since_id, count=200)
            else:
                response = api.user_timeline(id=api.me().screen_name, max_id=max_id, since_id=since_id, count=200)

        # 前回取得したときより新しいツイートがない場合
        if max_id is None and len(response) == 0:
            return results

        # 取得できる分を取得しきった場合
        if len(response) == 0:
            break

        # 今のループで取得したツイートでギリギリ取得できなかったツイートのIDがmax_idになる
        if len(response) > 0:
            max_id = response.max_id

        for elem in response:
            results.append(elem)

        newest_time = response[0].created_at + datetime.timedelta(hours=9)
        oldest_time = response[-1].created_at + datetime.timedelta(hours=9)
        print(f'Tweets downloaded. ({oldest_time} ~ {newest_time}, {len(response)} tweets)')

    # 今回取得したツイートIDを記録しておく
    # resultがなにも無ければ（early returnしていれば）前回取得時より新しいツイートがないので、IndexErrorにはならないはず
    latest_id = results[0].id_str
    # 9時間足してJSTにする
    latest_date = (results[0].created_at + datetime.timedelta(hours=9)).strftime('%Y%m%d_%H%M%S')
    try:
        if not os.path.exists(os.path.dirname(settings.tweet_history_file_path)):
            os.mkdir(os.path.dirname(settings.tweet_history_file_path))
        with open(settings.tweet_history_file_path, 'a') as f:
            f.write(f'{latest_date},{latest_id}\n')
    except:
        # 記録できなければとりあえずコンソールに表示しておく
        print(f'latest id: {latest_id}')
        print(f'latest date: {latest_date}')

    # ツイートを保存(デバッグ用)
    # try:
    #     Path(f'{settings.appdata_dir_name}/api_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.pkl') \
    #         .write_bytes(pickle.dumps(results))
    # except Exception as e:
    #     print(f'error occured: {e}')

    return results


def save_pics(pics):
    # uploader.save_to_local(pics)
    uploader.upload_to_google_photos(pics)


def generate_api():
    auth = tweepy.OAuthHandler(usersettings.twitter_consumer_key, usersettings.twitter_consumer_secret)
    auth.set_access_token(usersettings.twitter_access_token_key, usersettings.twitter_access_token_secret)
    api = tweepy.API(auth)

    return api


def main():
    api = generate_api()
    tweets = get_tweets(api)
    print(f'downloading pics...')
    pic_list = []

    for tweet in tweets:
        # ふぁぼ＆リツイートじゃなければ飛ばす
        if not (tweet.favorited and tweet.retweeted):
            continue

        # 画像がついているか、ついているなら何枚あるかを調べる
        try:
            contains_multiple_media = True if len(tweet.extended_entities["media"]) > 1 else False
        except KeyError:
            # 画像がついていないと'media'キーさえなくなるのでKeyError（ここ）
            # その場合は次のツイートへ
            continue

        for i_media, media in enumerate(tweet.extended_entities["media"]):
            url = media["media_url"]
            ulr_orig = url + ":orig"
            # エラーが出ても settings.try_max_pic_download の回数だけリトライする
            for i_try in range(settings.try_max_pic_download):
                try:
                    time.sleep(settings.wait_sec_for_download_pic)
                    with urllib.request.urlopen(ulr_orig) as web_file:
                        pict_bin = web_file.read()
                    # ファイル名はユーザーID_ツイート時刻(複数枚なら_1,_2,...).拡張子
                    user_id = tweet.retweeted_status.user.screen_name
                    created_at_jst = (tweet.retweeted_status.created_at
                                      + datetime.timedelta(hours=9)).strftime('%Y%m%d_%H%M%S')  # 9時間足してJSTにする
                    file_name = f'{user_id}@{created_at_jst}'
                    # メディアが複数ある場合はファイル名の重複を防ぐために連番をつける
                    if contains_multiple_media:
                        file_name += f"_{i_media + 1}"
                    extention = '.' + url.split('.')[-1]
                    file_name += extention
                    # 説明はツイート本文
                    description = tweet.retweeted_status.text
                    pic_list.append([pict_bin, file_name, description])
                    break
                except urllib.error.URLError as e:
                    print(f'Pic download failed: {e}')
                    if i_try < settings.try_max_pic_download - 1:
                        print('retrying...')
    print(f'downloading pics complete.')
    print(f'number of jtsc media: {len(pic_list)}')
    save_pics(pic_list)


def main_loop():
    while True:
        try:
            main()
        except Exception as e:
            print(f'exception occured \n{e}')

        one_day_sec = 60 * 60 * 24
        time.sleep(one_day_sec)


if __name__ == '__main__':
    main()
