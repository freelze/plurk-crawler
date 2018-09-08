plurk-crawler
=========================================================
Download all the photos from plurk users. 下載指定的噗浪使用者的圖片

下載一個噗浪使用者所有發過的圖片 ( 包含在下方回覆的圖片 )

目前已知Bug:
---
1. (已解決) ~~在回覆裡的圖片可能會少下載一張~~
2. 圖片有時候無法成功下載
3. (已解決) ~~如果使用者block搜尋,會無法下載,還沒寫不透過API,而直接去爬該使用者id~~
4. (已解決) ~~Queue嚴重吃記憶體 -> Pool 沒有在迴圈裡 close~~

作業系統:
---
只測試過Windows

前置作業:
---

1.安裝python3.6+

   `pip install plurk-oauth `
 
   `pip install base36 `

2.有一個Plurk帳號

3.到http://www.plurk.com/PlurkApp/ 申請API服務

  ( 請參考dada的教學文: https://dada.tw/2011/10/28/426/ )

  取得

    App Key
    App Secret 
    Access Token  
    Access Token Secret
    
  後

4.更改plurk.py裡的資料:


  CONSUMER_KEY = 'App Key放這裡'

  CONSUMER_SECRET = 'App Secret放這裡'

  ACCESS_TOKEN = 'Access Token放這裡'

  ACCESS_TOKEN_SECRET = 'Access Token Secret放這裡'

5.更改你想抓取的使用者帳號

  315行:

  userName = '你想抓取的使用者帳號' # User You Want To Crawl

6.執行程式


抓取速度參考:
---

爬取 5273 個噗浪貼文

共花了 672.0514919757843 秒

平均一張貼文花了 0.12745144926 秒

P.S.每個貼文留言數、圖片數不一樣

所以參考就好
