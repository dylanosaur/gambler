
import random

from flask import Flask, jsonify, redirect, render_template, request, session
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
app.config['SECRET_KEY'] = "BLAH"
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = True
app.config['TEMPLATES_AUTO_RELOAD'] = True

# we seek to present an interface that allows the user to buy mystery packs!
# this minimal interface will demo the functionality by mocking the objects

# there will be a referenced collection with some item_list_id
# fill with real items, linked to generic items,
# each real item can have a forsale price, tcglow value, fmv/credit values

user = {
            'credit': 10_000,
            'item_count': 12,
            'item_credit_total': 0.0,
            'item_list': [],
            'credit_bought': 10000
        }

def generate_box():

    item_list = {
        'database_id': 1000,
        'real_items': [
            {'id': 1, "item_hash": "LEA_Alpha Lotus_NM", 'forsale_price': 10000, 'tcglow': 9000, 'fmv':7000, 'credit': 8050}, 
            {'id': 2, "item_hash": "LEA_Alpha Lotus_LP", 'forsale_price': 7000, 'tcglow': 6500, 'fmv':5000, 'credit': 5750}, 
            {'id': 3, "item_hash": "LEA_Alpha Lotus_LP", 'forsale_price': 7000, 'tcglow': 6500, 'fmv':5000, 'credit': 5750}, 
            {'id': 4, "item_hash": "LEA_Alpha Lotus_POOR", 'forsale_price': 2000, 'tcglow': 1700, 'fmv':1500, 'credit': 1600}, 
            {'id': 5, "item_hash": "LEA_Alpha Lotus_DAMAGED", 'forsale_price': 1000, 'tcglow': 800, 'fmv':700, 'credit': 750}, 
            {'id': 6, "item_hash": "LEA_Alpha Lotus_DAMAGED", 'forsale_price': 1000, 'tcglow': 800, 'fmv':700, 'credit': 750}, 
            {'id': 7, "item_hash": "LEA_Alpha Lotus_DAMAGED", 'forsale_price': 1000, 'tcglow': 800, 'fmv':700, 'credit': 750}, 
            {'id': 8, "item_hash": "LEA_Alpha Lotus_DAMAGED", 'forsale_price': 1000, 'tcglow': 800, 'fmv':700, 'credit': 750}, 
        ],
    }
    for i in range(10):
        new_item = {'id': 9+i, "item_hash": "LEA_Alpha Lotus_DAMAGED", 'forsale_price': 1000, 'tcglow': 800, 'fmv':700, 'credit': 750}
        item_list['real_items'].append(new_item)
    return item_list

item_list = generate_box()

def total_value(item_list):
    return sum([x['tcglow'] for x in item_list['real_items']])

def count_items(item_list):
    return len(item_list['real_items'])



@app.route('/', methods=['GET', 'POST'])
def home():

    print(len(user['item_list']))
    print(user)
    item_list['total_tcglow'] = total_value(item_list)
    item_list['count'] = count_items(item_list)
    print('tcglow total', item_list['total_tcglow'])
    user['item_count'] = len(user['item_list'])
    user['item_credit_total'] = sum([x['credit'] for x in user['item_list']])
    pull_average = round(total_value(item_list) / count_items(item_list),0)
    pull_enabled = user['credit'] > pull_average
    pull_text = f"Draw from the box for {pull_average} gems" if pull_enabled else "Buy more gems or buylist cards!"
    
    return render_template('box.html', 
        data=item_list['real_items'],
        item_list=item_list,
        user=user,
        box_cost=pull_average,
        pull_text=pull_text,
        pull_enabled=pull_enabled,
        credit_bought=user['credit_bought']
    )


@app.route('/reset', methods=['GET', 'POST'])
def reset():
    new_user = {
            'credit': 10_000,
            'item_count': 12,
            'item_credit_total': 0.0,
            'item_list': [],
            'credit_bought': 10000
        }
    for field in new_user:
        user[field] = new_user[field]
    new_item_list = generate_box()
    for field in new_item_list:
        item_list[field] = new_item_list[field]
    return redirect('/')

@app.route('/pull', methods=['GET', 'POST'])
def pull_from_box():
    # user can only reach here with a POST (button press)
    # users's credit is deducted
    # user = user
    pull_average = round(total_value(item_list) / count_items(item_list),0)

    user['credit'] -= pull_average
    # an item is drawn from the list
    drawn_item = random.choice(item_list['real_items'])
    item_list['real_items'] = [x for x in item_list['real_items'] if x['id'] != drawn_item['id']]
    # item is xferred
    print(len(user['item_list']))
    user['item_list'] = user['item_list'] + [drawn_item]
    print(len(user['item_list']))

    # page refreshes
    print(user)
    user['item_count'] = len(user['item_list'])
    user['item_credit_total'] = sum([x['credit'] for x in user['item_list']])
    return redirect('/')

@app.route('/buylist', methods=['GET', 'POST'])
def buylist_card():

    # return card to PM and credit user
    item_id = int(request.args.get('id'))
    print(item_id)
    print(user['item_list'])
    item = [x for x in user['item_list'] if x['id'] == item_id][0]
    user['item_list'] = [x for x in user['item_list']  if x['id'] != item_id]
    user['credit'] += item['credit']
    return redirect('/')

@app.route('/buy_gems', methods=['GET', 'POST'])
def buy_more_gems():

    user['credit'] += 10000
    user['credit_bought'] += 10_000
    return redirect('/')

app.run(host='0.0.0.0', port=5555,)