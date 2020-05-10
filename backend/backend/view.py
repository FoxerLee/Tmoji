from django.shortcuts import render
# from pyspark.sql import SparkSession
import emoji
import json
from pymongo import MongoClient
import numpy as np


def _connect_mongo(host, port, username, password, db):
    """ A util for making a connection to mongo """

    if username and password:
        # mongo_uri = 'mongodb://%s:%s@%s:%s/%s' % (username, password, host, port, db)
        mongo_uri = 'mongodb://%s/%s' % (host, db)
        conn = MongoClient(mongo_uri)
    else:
        conn = MongoClient(host, port)

    return conn[db]


def q(request):
    context = {}

    # collect to mongodb
    db = _connect_mongo(host='127.0.0.1', port=27017, username='admin', password='123456', db='bigdata')


    # q1
    q1 = []
    cursor = db['t1'].find()
    cursor = list(cursor)
    emojis = [row['emoji'] for row in cursor]
    fres = [row['fre'] for row in cursor]

    for i in range(len(emojis)):
        tmp = {
            'text': emoji.emojize(emojis[i]),
            'value': str(float(fres[i])*10000)
        }
        # tmp[emoji.emojize(emojis[i])] = str(float(fres[i])*10000)
        q1.append(tmp)
    context['q1'] = q1

    # q2
    cursor = db['t2'].find()
    cursor = list(cursor)
    emojis_ = [row['emoji'] for row in cursor]
    cols = [row['col'] for row in cursor]

    emojis = [':face_with_tears_of_joy:', ':red_heart:', ':loudly_crying_face:', ':fire:',
             ':smiling_face_with_heart-eyes:', ':female_sign:', ':clapping_hands:',
             ':folded_hands:', ':male_sign:', ':backhand_index_pointing_right:', 'others']
    matrix = [[0]*11]*11
    indexByName = []
    nameByIndex = []

    for emo, col in zip(emojis_, cols):
        idx = emojis.index(emo)
        for val_dict in col.values():
            emo1 = val_dict['_1']
            val1 = val_dict['_2']
            matrix[idx][emojis.index(emo1)] = val1

    for i in range(len(emojis)):
        indexByName.append([emoji.emojize(emojis[i]), i])
        nameByIndex.append([i, emoji.emojize(emojis[i])])
    # print(context)
    # context['hello'] = 'hello'
    # return render(request, 'index.html', context)
    q2 = {'matrix': matrix, 'indexByName': indexByName, 'nameByIndex': nameByIndex}
    context['q2'] = q2


    # q4
    q4 = {}
    collection = db.top10Word
    collection = list(collection.find())
    q4['name'] = 'flare'
    result_children = []
    for row in collection:
        temp_dict = {}
        temp_dict['name'] = emoji.emojize(row['_1'])
        children = []
        words = row['_2']
        for i in range(len(words)):
            each_word = {}
            each_word['name'] = words[i]
            each_word['value'] = 10000
            children.append(each_word)
        temp_dict['children'] = children
        result_children.append(temp_dict)
    q4['children'] = result_children
    context['q4'] = q4

    # q5 = {}
    # collection = db.alphabet
    # collection = list()

    q6 = {}
    collection = db.pairWise
    collection = list(collection.find())
    q6['nodes'] = []
    q6['links'] = []
    i = 0
    for row in collection:
        if i > 19:
            break
        node1 = {}
        node2 = {}
        link = {}
        node1['name'] = emoji.emojize(row['_1'])
        node2['name'] = row['_2'][0]['_1']['_1']
        q6['nodes'].append(node1)
        q6['nodes'].append(node2)
        link['source'] = i
        link['target'] = i + 1
        link['value'] = row['_2'][0]['_2']
        q6['links'].append(link)
        i = i + 2
    context['q6'] = q6

    # q3
    cursor = db['t3'].find()
    emojis_ = []
    uppers = []
    lowers = []
    for row in cursor:
        emojis_.append(row['emoji'])
        uppers.append(row['upper'])
        lowers.append(row['lower'])

    q3 = []
    for emo, up, lo in zip(emojis_, uppers, lowers):
        tmp = {
            'name': emoji.emojize(emo),
            'x': up/(up+lo),
            'y': lo/(lo+up)
        }
        q3.append(tmp)
    context['q3'] = q3

    # q7
    q7 = []
    cursor = db['t7'].find()
    nums = []
    counts = []
    for row in cursor:
        nums.append(row['num'])
        counts.append(row['counts'])

    for n, c in zip(nums, counts):
        tmp = {
            'name': n,
            'value': c
        }
        q7.append(tmp)
    context['q7'] = q7


    # q8
    cursor = db['t8'].find()
    emojis_ = []
    pos = []
    for row in cursor:
        emojis_.append(row['emoji'])
        pos.append(row['pos'])

    head = []
    middle = []
    tail = []
    for e, p in zip(emojis_, pos):
        tmp = {}
        tmp['name'] = emoji.emojize(e)
        tmp['value'] = 5
        if p == 0:
            head.append(tmp)
        elif p == 1:
            middle.append(tmp)
        else:
            tail.append(tmp)
    head_dict = {}
    head_dict['name'] = 'Head'
    head_dict['children'] = head
    head_dict['value'] = len(head)

    middle_dict = {}
    middle_dict['name'] = 'Middle'
    middle_dict['children'] = middle
    middle_dict['value'] = len(middle)

    tail_dict = {}
    tail_dict['name'] = 'Tail'
    tail_dict['children'] = tail
    tail_dict['value'] = len(tail)

    context['q8'] = {'children': [head_dict, middle_dict, tail_dict], 'value': 5}

    # q9
    cursor = db['t9'].find()
    x = []
    y = []
    num = []
    for row in cursor:
        x.append(row['sent_len'])
        y.append(row['emoji_len'])
        num.append(row['count'])

    q9 = []
    for x_, y_, num_ in zip(x, y, num):
        tmp = {}
        tmp['x'] = x_
        tmp['y'] = y_
        tmp['num'] = num_
        q9.append(tmp)
    context['q9'] = q9

    # q10
    cursor = db['t10'].find()
    emojis_ = []
    counts = []
    for row in cursor:
        emojis_.append(row['emoji'])
        counts.append(row['count'])

    q10 = []
    for e, c in zip(emojis_, counts):
        tmp = {}
        tmp['name'] = emoji.emojize(e)
        tmp['value'] = c
        q10.append(tmp)
    context['q10'] = q10

    # q11
    cursor = db['t11'].find()
    emojis_ = []
    ave_lens = []
    for row in cursor:
        emojis_.append(row['emoji'])
        ave_lens.append((row['ave_len']))

    q11 = []
    for n, c in zip(emojis_, ave_lens):
        tmp = {}
        tmp['emoji'] = emoji.emojize(n)
        tmp['ave_len'] = c
        q11.append(tmp)
    print(q11)

    context['q11'] = q11

    return render(request, 'index.html', {'context': json.dumps(context)})


