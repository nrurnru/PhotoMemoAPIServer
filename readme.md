# API 명세

## 공통
- 날짜 포맷으로 ISO8601을 사용합니다.
- 메모 id는 SHA-256으로 해싱합니다.
- 이미지는 이미지 서버를 통해 url을 얻어옵니다.

## 회원가입

|METHOD|URL|DESC|
|---|---|---|
|POST|http://nrurnru.pythonanywhere.com/memo/login|입력된 정보로 회원가입을 시도합니다.|

### Header
|KEY|VALUE|
|---|---|
|Userid|(가입할 아이디)|
|Userpassword|(가입할 패스워드)|

### Request

```json
{
}
```

### Response

```json
"success" //HTTP Code로 성공 여부 구별
```

## 로그인

|METHOD|URL|DESC|
|---|---|---|
|GET|http://nrurnru.pythonanywhere.com/memo/login|입력된 정보로 서버에 로그인합니다.|

### Header
|KEY|VALUE|
|---|---|---|
|Userid|(가입할 아이디)|
|Userpassword|(가입할 패스워드)|

### Request

```json
{   
}
```

### Response

```json
{
    "token" : "(유저별 jwt 토큰값)"
}
```

## 메모 동기화(업로드)

|METHOD|URL|DESC|
|---|---|---|
|POST|http://nrurnru.pythonanywhere.com/memo/sync|메모 데이터를 json형식으로 전송해 서버로 업로드합니다.|

### Header
|KEY|VALUE|
|---|---|---|
|jwt|(발급받은 토큰)|


### Request
```json
{
  "updated_memos": [
    {
      "created_at": "2021-02-21T13:09:50Z",
      "id": "41e07aff3f80884401d2857c44fb4a40502cef95f1132df77decf0725f72178f",
      "updated_at": "2021-02-21T13:09:50Z",
      "image_url": "https://i.imgur.com/Uh5oCMD.png",
      "text": "메모 내용"
    }
  ],
  "last_synced": "2021-02-21T13:09:34Z",
  "deleted_memo_ids": [
      "a40502cef95f1132df77decf0725f72178f41e07aff3f80884401d2857c44fb4",
      "0725f72178f41e07aff3f80884401d2857c44fb4a40502cef95f1132df77decf"
  ]
}
```

## 메모 동기화(다운로드)

|METHOD|URL|DESC|
|---|---|---|
|GET|http://nrurnru.pythonanywhere.com/memo/sync|메모 데이터를 json형식으로 전송해 서버로 다운로드합니다.|

### Header
|KEY|VALUE|
|---|---|---|
|jwt|(발급받은 토큰)|

### Query string
|KEY|VALUE|
|---|---|---|
|last_synced|(마지막 동기화 날짜)|

### Request
```json
{
}
```

### Response
```json
{
  "updated_memos": [
    {
      "created_at": "2021-02-21T13:25:16Z",
      "id": "79e7db113bc4329186440c9c6a596e66d300192a30809c5ce83f1de23f97819c",
      "updated_at": "2021-02-21T13:25:16Z",
      "image_url": "https://i.imgur.com/IrDZIBx.png",
      "text": "메모 내용"
    }
  ],
  "deleted_memo_ids": [
      "3f1de23f97819c79e7db113bc4329186440c9c6a596e66d300192a30809c5ce8"
  ]
}
```