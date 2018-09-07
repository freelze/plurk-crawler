# plurk-crawler
Download all the photos from plurk users. 下載指定的噗浪使用者的圖片

目前已知Bug:
1. (已解決)在回覆裡的圖片可能會少下載一張
2. 圖片有時候無法成功下載
3. (已解決)如果使用者block搜尋,會無法下載,還沒寫不透過API,而直接去爬該使用者id
4. (已解決)Queue嚴重吃記憶體 -> Pool 沒有在迴圈裡 close
