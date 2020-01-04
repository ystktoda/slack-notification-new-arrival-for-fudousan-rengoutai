# 不動産連合隊の新着物件情報slack通知

不動産連合隊にて任意の検索条件で新着物件情報があれば、slack通知します。

## 使用方法

### 設定ファイルに追記

`.env.sample` を参考にして、 `.env` ファイルを作成します。
以下の情報を追記します。

- TARGET_URL
  - 不動産連合隊にて、参照したい検索条件で検索した後、URLをコピーして貼り付けます。
- SLACK_URL
  - 通知したいIncoming Webhook URL を貼り付けます。

### 実行

crontabなどで、`getNewArrivalForFudousanRengoutaiOnce.py` を定期的に実行します。

5分おきなど、迷惑かけない範囲で定義してください。

新着があればslackに通知されます。
