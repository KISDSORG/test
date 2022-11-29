from flask import Flask, render_template, request, jsonify
import stock_news
import stock_info
from kakaoChatbot import render_json

app = Flask(__name__,static_url_path='/static')
app.config['JSON_AS_ASCII'] = False

@app.route('/')
def basic():
    return render_template("test2.html")

@app.route('/stock_info/<param>') #get echo api
def get_stock_info(param):
    try:
        return stock_info.stock_info_ret(param)
    except:
        return jsonify({"param": param,"error":"Not Symbol"})

@app.route('/stock_info', methods=['POST']) # 기본 동작
def post_stock_info():
    request_data = request.get_json()
    try:
        if (request_data["intent"]["name"] == "폴백 블록"):
            # param = request_data['action']['params']['stock']
            param = request_data['userRequest']['utterance'].replace('\n','').lower()
            param = param.replace(' ','')
            if ("," in param):
                return jsonify(render_json.multi_item_carousel(param))
            # print(request_data)
            ret = stock_info.stock_info_ret(param)
            return jsonify(ret)
        else:
            return render_json.simple_text("error")
    except:
        return render_json.simple_text("도움말 : 주식의 Symbol을 입력해주세요. (ex. AAPL, MSFT, GOOGL")

@app.route('/multi_stock',methods=['POST'])
def multi_stock_info():
    request_data =request.get_json()
    print(request_data)
    try:
        stocks = request_data['userRequest']['utterance'].replace('\n','').lower()
        return jsonify(render_json.multi_item_carousel(stocks))
    except:
        return render_json.simple_text("도움말 : 주식의 Symbol을 입력해주세요. (ex. AAPL, MSFT, GOOGL")

@app.route('/stock_info_deep', methods=['POST']) #회사 상세
def post_stock_info_deep():
    request_data = request.get_json()
    try:
        if (request_data["intent"]["name"] == "Fundamental"):
            # param = request_data['action']['params']['stock']
            param = request_data['action']['clientExtra']['stock'].replace('\n','').lower()
            param = param.replace(' ','')
            # print(request_data)
            ret = stock_info.stock_info_ret_deep(param)
            return jsonify(ret)
        else:
            return render_json.simple_text("error")
    except:
        return render_json.simple_text("error symbol")

@app.route('/stock_news', methods=['POST']) #회사 뉴스
def post_stock_news():
    request_data = request.get_json()
    try:
        if (request_data["intent"]["name"] == "news"):
            param_stock = str(request_data['action']['clientExtra']['stock']).replace('\n','').lower()
            param_start = str(request_data['action']['clientExtra']['start']).replace('\n', '')
            param_end = str(request_data['action']['clientExtra']['end']).replace('\n', '')
            param_stock = param_stock.replace(' ','')
            param_start = param_start.replace(' ', '')
            param_end = param_end.replace(' ', '')
            ret = stock_news.news_info(param_stock,int(param_start),int(param_end))
            return jsonify(ret)
        else:
            return render_json.simple_text("error")
    except:
        return render_json.simple_text("error symbol")

@app.route('/stock_outer', methods=['POST']) #리서치 전망
def post_stock_outer():
    request_data = request.get_json()
    try:
        if (request_data["intent"]["name"] == "outer"):
            param_stock = str(request_data['action']['clientExtra']['stock']).replace('\n','').lower()
            param_stock = param_stock.replace(' ','')
            ret = stock_info.stock_rating(param_stock)
            return jsonify(ret)
        else:
            return render_json.simple_text("error")
    except:
        return render_json.simple_text("error symbol")

@app.route('/stock_fund/<param>') #get echo api
def get_stock_fund(param):
    try:
        return jsonify(stock_info.stock_funddament(param))
    except:
        return jsonify({"param": param,"error":"Not Symbol"})

@app.route('/stock_rating/<param>') #get echo api
def get_stock_rating(param):
    try:
        return jsonify(stock_info.stock_rating(param))
    except:
        return jsonify({"param": param,"error":"Not Symbol"})

@app.route('/echo_call', methods=['POST']) #post echo api
def post_echo_call():
    param = request.get_json()
    ret = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": "hello, world"
                    }
                }
            ]
        }
    }
    return jsonify(ret)

@app.route('/stock_news/<param>')#list_card
def get_news_info(param):
    try:
        return jsonify(stock_news.news_info(param))
    except:
        return jsonify({"param": param,"error":"Not Symbol"})

def get_news_trans(param):
    pass


@app.route("/news_trans",methods=['POST'])
def animal():
    req = request.get_json()
    animal_type = req["action"]["detailParams"]["Animal_type"]["value"]  # json파일 읽기
    answer = animal_type

    # 답변 텍스트 설정
    res = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": answer
                    }
                }
            ]
        }
    }

    # 답변 전송
    return jsonify(res)
if __name__ == '__main__':
    app.run(debug=True)
