plurk-crawler
=========================================================
Download all the photos from plurk users.

下載一個噗浪使用者所有發過的圖片 ( 包含在下方回覆的圖片 )


作業系統:
---
只測試過Windows

前置作業:
---

### 1.安裝python3.6+

   `$ pip install plurk-oauth `
 
   `$ pip install base36 `

### 2.註冊一個Plurk帳號 ( https://www.plurk.com/signup )

### 3.申請API服務 http://www.plurk.com/PlurkApp/ 

  ( 請參考dada的教學文: https://dada.tw/2011/10/28/426/ )

  取得

+   App Key
+   App Secret 
+   Access Token  
+   Access Token Secret
    

### 4.更改plurk.py裡的資料:

     CONSUMER_KEY = 'App Key放這裡'

     CONSUMER_SECRET = 'App Secret放這裡'

     ACCESS_TOKEN = 'Access Token放這裡'

     ACCESS_TOKEN_SECRET = 'Access Token Secret放這裡'

### 5.執行程式

方法一:

    $ python plurk.py

    再輸入你想抓的使用者名稱 ( 以空白分隔 )

    username1 username2 username3

方法二:

    $ python plurk.py username1 username2 username3

`username` 就是 http://www.plurk.com/使用者帳號 的 `使用者帳號`

抓取速度參考:
---

爬取 5273 個噗浪貼文

共花了 672.0514919757843 秒

平均一張貼文花了 0.12745144926 秒

P.S.每個貼文留言數、圖片數不一樣

所以參考就好

目前已知Bug:
---
1. (已解決) ~~在回覆裡的圖片可能會少下載一張~~
2. 圖片有時候無法成功下載
3. (已解決) ~~如果使用者block搜尋,會無法下載,還沒寫不透過API,而直接去爬該使用者id~~
4. (已解決) ~~Queue嚴重吃記憶體 -> Pool 沒有在迴圈裡 close~~

想增加的功能:
---

1. Proxy pac

2. 寫成 WebExtension
