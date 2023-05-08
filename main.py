
from flask import Flask
from flask import request
import user_class

app = Flask(__name__)


@app.route('/recommend')
def recommend():
    subs = request.args.get('subs')
    creat = request.args.get('creat')
    vend = request.args.get('vend')
    acc = request.args.get('acc')
    payer = request.args.get('payer')
    cat_x = int(request.args.get('cat_x'))
    item_x = int(request.args.get('item_x'))

    user = user_class.user_profile(subs, creat, vend, acc, payer, cat_x, item_x)
    rec = user.get_recommendation()

    print(rec)
    return rec


if __name__ == '__main__':
    # app.run(host='0.0.0.0')
    app.run(host='10.16.96.8', port=8800)
