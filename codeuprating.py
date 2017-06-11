import requests
from bs4 import BeautifulSoup

import sys, time, datetime, pymysql
from time import localtime, strftime

conn = pymysql.connect(host="172.19.8.100", port=7000, user="s15068", passwd="1111", db="s15068", autocommit=True, charset="utf8")
cur = conn.cursor(pymysql.cursors.DictCursor)

def ID_score(id, ID, ratio, AC):
    base_url = 'http://codeup.kr/JudgeOnline/problemstatus.php?id=' + str(ID) + '&page='
    i = 0
    while i < 10000:
        url = base_url + str(i)
        i = i + 1
        source_code = requests.get(url)
        plain_text = source_code.text
        soup = BeautifulSoup(plain_text, 'lxml')

        s = str(soup).find('userinfo.php?user=' + id)
        if s == -1:
            continue
        while str(soup)[s:s+5] != '0.8em':
            s = s - 1
        rankinfo = str(soup)[s+3:s+20]
        while rankinfo[0] < '0' or rankinfo[0] > '9':
            rankinfo = rankinfo[1:]
        rank = 0
        while rankinfo[0] >= '0' and rankinfo[0] <= '9':
            rank = rank * 10 + int(rankinfo[0])
            rankinfo = rankinfo[1:]
        low = min(4.5, 1 / ratio - 0.5)
        high = min(5, 1 / ratio)
        res = (low * (rank - 1) / AC) + (high * (AC - rank + 1) / AC)
        return res
    return 0

def spider(id):
    url = 'http://codeup.kr/JudgeOnline/userinfo.php?user=' + id
    source_code = requests.get(url)
    plain_text = source_code.text
    soup = BeautifulSoup(plain_text, 'lxml')

    if len(str(soup)) <= 5000:
        print("존재하지 않는 아이디입니다.")
        return

    s = str(soup).find(id + '(')
    s = s + len(id) + 1
    name = str(soup)[s:s+50]
    name = name[:name.find(')')]
    print('이름 : ', name)

    tStr = soup.find_all('script', attrs = {'language':'javascript'})
    tStr = str(tStr).replace(';','')
    tStr = tStr[110:-10]

    tStr = tStr.replace('p(', '')
    tStr = tStr.replace(')', ' ')
    print(tStr)
    print('총 해결 문제 수 : ', int(len(tStr) / 5))

    cnt = int(len(tStr) / 5)
    if cnt < 20:
        print("당신을 평가하기에는 문제를 너무 적게 풀었군요.")
        return
    prob = []
    print('평가 준비중...')
    for i in range(cnt):
        ID = int(tStr[i*5]) * 1000 + int(tStr[i*5+1]) * 100 + int(tStr[i*5+2]) * 10 + int(tStr[i*5+3])
        query = "select submit, AC from problems where ID=" + str(ID)
        cur.execute(query)
        result = cur.fetchone()
        
        AC = float(result['AC'])
        submit = float(result['submit'])
        prob.append((float(AC) / float(submit), ID))
    prob.sort()

    score = 0
    iterator = 0
    print('레이팅 산정중...')
    for x,y in prob:
        query = "select submit, AC from problems where ID=" + str(y)
        cur.execute(query)
        result = cur.fetchone()
        AC = float(result['AC'])
        score += ID_score(id, y, x, AC)
        iterator = iterator + 1
        if iterator >= 20:
            break
    print("당신의 레이팅은 " + str(int(score * 100)))


print('아이디를 입력해 주세요 : ')
ID = input()

spider(ID)

