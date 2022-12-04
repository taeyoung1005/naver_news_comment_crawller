# naver_news_comment_crawller

### 설치 라이브러리
- pip3 install selenium chromedriver_autoinstaller numpy openpyxl

<br>

naver_news_crawler.py 뉴스기사링크 크롤러

naver_news_comment_crawler.py 뉴스기사댓글 크롤러

naver_news_crawler.py 링크 + 댓글 합친 크롤러

search에 검색어 입력

start_date에 시작날짜 입력

end_date에 종료날짜 입력

CPU에 과한 학대를 하지않기 위해 최대 코어수에서 0.8 곱했음

순서 : 검색어 대한 뉴스링크 크롤링 -> 뉴스링크의 댓글 크롤링

### 저장파일

1. 검색어_시작날짜_종료날짜_link.txt
2. 검색어_시작날짜_종료날짜_comment.csv
3. 검색어_시작날짜_종료날짜_comment.xlsx

#### 검색어_시작날짜_종료날짜_comment 형식
- 기사제목/댓글작성날짜/댓글
