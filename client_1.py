import requests
# route A
subs = '615ad7f4a2f37a0014bb9ef3'
creat = '61827db682ef2c529e2bf44e'
vend = '61793ee4c55ef2001b82e877'
acc = '617c166b82ef2c529e94f7ea'
payer = '615483948d889d0013ea3918'
cat_x = '1'
item_x = '1'

# ## route G2
# subs = '600fd4085f99d20014946b77'
# creat = '6154629c8f1006dc45f07cc4'
# vend = 'xxxx'
# acc = '6132d41e02d4c192daff4524'
# payer = '600fd4085f99d20014946b56'
# cat_x = 5
# item_x = 5

url = 'http://ec2-3-120-126-159.eu-central-1.compute.amazonaws.com:5000/recommend?' #####
# url = 'http://127.0.0.1:5000/recommend?' ####### this is localhost for demo


# url_full = "http://{}/recommend?subs={}&creat={}&vend={}&acc={}&payer={}&cat_x={}&item_x={}".\
#     format(url, subs, creat, vend, acc, payer, cat_x, item_x)
# response = requests.get(url_full)


params = {
    'subs': subs,
    'creat': creat,
    'vend': vend,
    'acc': acc,
    'payer': payer,
    'cat_x': cat_x,
    'item_x': item_x
}

response = requests.get(url, params=params)
result = response.json()
print(result)