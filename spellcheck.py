# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup

def spellCorrection(q):
    datas = {'text1':q}
    post_result = requests.post("http://speller.cs.pusan.ac.kr/PnuWebSpeller/lib/check.asp", data=datas)
    print(post_result.status_code)
    if post_result.status_code != 200 :
        return """지금 API에 문제가 있어서 검사가 안될것같아요ㅠ
        조금 있다가 다시 시도해주세요!"""
    res = post_result.text
    soup = BeautifulSoup(res, "html.parser")

    tables = soup.find_all("table", class_="tableErrCorrect")
    replaced_list=[]
    for table in tables:
        err = table.find("td", class_="tdErrWord").get_text()
        cor = table.find("td", class_="tdReplace").get_text()
        replaced_list.append([err, cor])
    after = q;
    print(replaced_list)
    for replace_word in replaced_list:
        after = after.replace(replace_word[0], replace_word[1])
        print(after)
    return after

print(spellCorrection("안녕디지몬, 네꿈을 꾸 면서 잠을들래."))