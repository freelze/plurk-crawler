plurk-crawler
=========================================================
Download all the images from plurk users ( including images in the replies below ).

下載一個噗浪使用者所有發過的圖片 ( 包含在下方回覆的圖片 )


作業系統:
---
只測試過Windows

前置作業:
---
### 安裝 Python 3.6+
### 下載程式碼
    git clone https://github.com/freelze/plurk-crawler.git

### 安裝 Python 相關套件    
    pip install -r requirements.txt

### 註冊 Plurk 帳號：https://www.plurk.com/signup 

### 申請 API 服務：http://www.plurk.com/PlurkApp/ 

  ( 請參考 dada 的教學文: https://dada.tw/2011/10/28/426/ )

  取得

+   App Key
+   App Secret 
+   Access Token  
+   Access Token Secret
    

### 修改 .env 檔案的金鑰:

+ CONSUMER_KEY=***App Key放這裡***
+ CONSUMER_SECRET=***App Secret放這裡***
+ ACCESS_TOKEN=***Access Token放這裡***
+ ACCESS_TOKEN_SECRET=***Access Token Secret放這裡***


### 執行程式
    python plurk.py username1 username2 username3

`username` 就是 http://www.plurk.com/使用者帳號 的 `使用者帳號`

抓取速度參考:
---

爬取 5273 個噗浪貼文，

總共花費 672.0514919757843 秒，

平均一張貼文花了 0.12745144926 秒，

每個貼文留言數、圖片數不一樣，

僅供參考。

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
