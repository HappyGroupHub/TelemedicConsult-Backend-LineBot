# 通訊診療與個案管理系統 - 後端API及LineBot

📖 [英文版README.md](#TelemedicConsult-Backend-LineBot) 📖

## 本專案提供Line Bot給使用者(病人)通訊看診及個案管理

<img width="450" src="./readme_imgs/line_register.png">

### 專案簡述

> [通訊診療與個案管理系統-後端API及LineBot](https://github.com/HappyGroupHub/TelemedicConsult-Web)
> 與[前端網頁](https://github.com/HappyGroupHub/TelemedicConsult-Backend-LineBot)為**同一專案**


因為疫情的緣故，線上診療的需求日漸增加，因此計畫設計一連串從線上掛號開始，進入會議室看診到最後的個案管理，有一個對所有人都很親民的流程。讓通訊診療不再令人措手不及，院方也可在看診後留下診間及病患的紀錄，家屬時間成本得以捨去。

病人可以透過此網站進行掛號，由LINE進行通訊診療跟個案管理。因為LINE在台灣為主流的通訊軟體，幾乎每人至少都有一個LINE帳號也都會使用LINE，解決了裝置限定的問題。

### 專案功能

#### 後端API串接前端網頁

利用Flask建立一個框架作為API串接媒介。網頁透過vue.js發送請求，後端接收到訊息之後與資料庫聯繫，再將需求回應給網頁前端。

#### [LINE] 一般使用者(病人)

初診填寫基本資料後，過LINE APP進行加好友的驗證跟帳號的綁定。

- 初次綁定
- 病人查詢預約
- 查詢看診進度
- 看診提醒
- 過號提醒
- 個案管理
- 更換綁定裝置

#### [LINE] 醫生

- 使用創建的Line會議室連結進行視訊看診

---

## 如何使用

### 系統需求

- CPU: 64位元之四核心以上處理器, 基頻2.2Ghz以上
- RAM: 需至少4GB以上
- 作業系統: Windows 8或macOS 10.14以上之版本

### 開發環境與IDE

- 後端與Line機器人: JetBrains PyCharm Community Edition 2022.1.3

### 部署相關軟體

- XAMPP v7.4.33 or above
- MySQL based MariaDB v10.4.25
- Apache v2.4.54
- phpMyAdmin v5.2.0
- ngrok v3.1.0

### 安裝程序

- 依照官網指示完成下載安裝[PyCharm Community Edition](https://www.jetbrains.com/pycharm/)
- 依照官網指示完成下載安裝[XAMPP](https://www.apachefriends.org/zh_tw/download.html)
    - 勾選Apache服務
    - 勾選MySQL服務
    - 勾選PHP語言
- 依照官網指示完成下載[ngrok](https://ngrok.com/)

### 操作程序

1. 資料庫SQL設置
    - 請至 [通訊診療與個案管理系統 - 前端網頁](https://github.com/HappyGroupHub/TelemedicConsult-Web#readme) 查看

2. 後端API開發及部署
    - 執行檔案 `web_backend.py`即可

3. Line機器人開發及部署
    1. 先進入LINE Developers創建一個Messaging API
    2. 使用PyCharm將程式原始碼clone至本地端
    3. 確認安裝所有packages, 可以參考 `requirements.txt`
    4. 打開ngrok.exe並輸入`ngrok.exe http 5000` (務必要先完成登入程序)
    5. 複製Forwarding後面的網址並貼在第三節、應用程式介面API提到的Webhook URL位置
    6. 在網址後面加上/callback，並打勾Use webhook的選項
    7. 在專案目錄新增檔案`config.yml`，並填入資料庫連接資訊及LINE API所需的密鑰

---

## 協助專案開發

### 如何貢獻

1. Fork 這個專案
2. 複製你剛剛 Fork 的專案至本地
3. 建立新的分支
4. 盡情發揮你的能力
5. Commit / Push 你的程式碼
6. 建立新的 Pull Request
7. 等待回覆

### 程式碼撰寫/提交規範

* 每行不超過100個字元
* 使用 `snake_case` 命名變數及函式
* 在檔案尾處加上一個空行
* 最佳化程式碼並移除不必要的import
* 提交請求時請使用以下格式，並全英文撰寫
    - Update - your commit messages here
    - Fix bug - your commit messages here
    - Optimize - your commit messages here
    - Standardize - your commit messages here

### 建議/問題回報

如果你有任何建議或是發現了任何問題，請在 [Issues](https://github.com/HappyGroupHub/TelemedicConsult-Web/issues)
提交你的意見，我會盡快回覆你!

### 開發工具/函式庫

- Flask - 用來架設Webhook伺服器
- LineBotSDK - 用來與Line API溝通
- PyYAML - 用來讀取config.yml檔案
- mysql-connector-python - 用來與資料庫進行資料交互

---

# TelemedicConsult-Backend-LineBot

📖 [繁體中文版README.md](#通訊診療與個案管理系統---後端API及LineBot) 📖

Not yet supported...