# 설치
## Install Meilisearch
```
curl -L https://install.meilisearch.com | sh
```

## Launch Meilisearch
```
./meilisearch --master-key {마스터키} --db-path ./data.ms --http-addr 'localhost:7700'
```

# python 환경 설정
## 가상환경
```
python -m venv .venv
source .venv/bin/activate
```

## 의존성 설치
```
pip install -r requirements.txt
pip freeze > requirements.txt
```

# movie
## 데이터 다운로드
```
curl -O https://www.meilisearch.com/movies.json
```

## 데이터 색인
```
curl \
  -X POST 'http://localhost:7700/indexes/movies/documents?primaryKey=id' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer {마스터키}' \
  --data-binary @movies.json
```

# girlgroup
## 데이터 다운로드
https://huggingface.co/datasets/heegyu/namuwiki

## 필터링 및 색인
```
meilisearch.ipynb
```

# RAG
```
streamlit run rag-gemini.py
```

# 세팅
## 검색결과
```
curl \
-X PATCH 'http://localhost:7700/indexes/{인덱스명}/settings/pagination' \
-H 'Content-Type: application/json' \
-H 'Authorization: Bearer {마스터키}' \
--data-binary '{"maxTotalHits": {원하는 검색 수}}'
```

## 필터링
```
curl \
  -X PUT 'http://localhost:7700/indexes/{인덱스명}/settings/filterable-attributes' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer {마스터 키}' \
  --data-binary '[
    "f_subject_id",
    "f_area_cd",
    "f_eduprocess_cd"
  ]'
```