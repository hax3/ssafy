import json
import urllib.request

def trans(q):
    encText = urllib.parse.quote(q)
    client_id = "xw10jt_pmZljTuyq3ZOy"
    client_secret = "FQEEIGd8Yp"
    #언어감지
    data = "query=" + encText
    url = "https://openapi.naver.com/v1/papago/detectLangs"
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", client_id)
    request.add_header("X-Naver-Client-Secret", client_secret)
    response = urllib.request.urlopen(request, data=data.encode("utf-8"))
    rescode = response.getcode()
    from_type = 'ko'
    to_type = 'en'
    if (rescode == 200):
        response_body = response.read()
        res = json.loads(response_body.decode('utf-8'))
        from_type = res['langCode']
        if from_type == 'en':
            to_type = 'ko'
        elif from_type != 'ko':
            print("번역 불가 타입")
            return "번역이 안되는 언어입니다! 죄송해요!"
    else:
        print("Error Code:" + rescode)
    #번역
    data = "source={}&target={}&text={}".format(from_type, to_type, encText)
    url = "https://openapi.naver.com/v1/papago/n2mt"
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id",client_id)
    request.add_header("X-Naver-Client-Secret",client_secret)
    response = urllib.request.urlopen(request, data=data.encode("utf-8"))
    rescode = response.getcode()

    #번역 결과
    if(rescode==200):
        response_body = response.read()
        res = json.loads(response_body.decode('utf-8'))
        from_type = res['message']['result']['srcLangType']
        to_type = res['message']['result']['tarLangType']
        translated = res['message']['result']['translatedText']
        return """
        == {} -> {} ==
        {}
        """.format(from_type, to_type, translated)
    else:
        print("Error Code:" + rescode)
        return rescode

# print(trans("안녕, 내이름은 수잔이야."))
# print(trans("Hi, my name is Susan."))