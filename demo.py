import requests

# 準備要發送的資料
new_post = {
    'title': '我的第一篇文章',
    'body': '這是文章內容',
    'userId': 1
}

# 發送 POST 請求
response = requests.post(
    'https://jsonplaceholder.typicode.com/posts',
    json=new_post  # 自動轉為 JSON 並設定 Content-Type
)

if response.status_code == 201:  # 201 Created
    created_post = response.json()
    print(f"文章已建立！ID: {created_post['id']}")
    print(f"標題：{created_post['title']}")
else:
    print("建立失敗")



