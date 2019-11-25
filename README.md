# JTSC saver


## 1. これはなに？

よさみイラスト（JTSC: Japanese Tottemo Subarashii Culture）を自動でGoogleフォトに上げるPythonスクリプトです。

もうちょっと具体的に言うと、前回取得以降のツイートもしくは最新3200件のツイートを分析して、いいねとリツイートの両方をしたツイート（どちらか片方ではNG）に含まれる画像すべてをGoogleフォトにアップロードするPythonスクリプトです。


## 2. 動作環境

- Windows 10
  - 他のOSでも動くかもしれませんが、検証はしていません。
- Python (v3.6以降)
  - 動作確認は3.7で行っています。古いとSyntaxErrorが出ると思います。
- Pythonライブラリ　`pip install` してください。
  - google-auth-oauthlib
  - more-itertools
  - それらに付随するライブラリ


## 3. 使う前の準備

GoogleとTwitterの認証が必要です。


### 3.1 Googleの認証

https://developers.google.com/photos/library/guides/get-started

上のURLへ移動して「Enable Photos Library API」ボタンを押して、プロジェクトの作成とAPIの利用登録をしてください。「Where are you calling from?」に対してはOtherと答えればOKです。
CREATEしたら`credentials.json`をダウンロードして、JTSC saverのappdataディレクトリにある同名ファイルを上書きしてください。

最後に、`$ python googlephotos_helper.py` でトークンを取得・保存します。


### 3.2 Twitterの認証

https://developer.twitter.com/en/apps

上のURLから新規アプリを作ります。

作ったらConsumer API keys、Access token & access token secretをJTSC saverの`usersettings.py`の対応箇所にそれぞれコピペしてください。


### 3.3 その他の設定

JTSC saverの`usersettings.py`のtwitter_idをあなたのTwitter IDに書き換えてください。


## 4. 使い方

1. よさみイラストをいいねしてリツイートする
2. `$ python program.py`
3. イラストがGoogleフォトに保存される
4. しあわせな気分になる


## 5. 使用ライブラリ

- google-auth-oauthlib
    - Apache 2.0
- more-itertools
    - MIT License
