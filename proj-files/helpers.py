from flask import render_template
from decimal import *

def error(message="Bad request", code=400):
    return render_template("error.html", code=code, message=message), code

def chance(p1, p2, dom_s, rec_s):
    # format symbols
    n1 = dom_s + dom_s
    n2 = dom_s + rec_s
    n3 = rec_s + rec_s
    
    # decide base case
    
    # if either is hd
    if p1 == 'hd' or p2 == 'hd':
        # if only 1 is hd
        if (p1 == 'hd' and p2 != 'hd') or (p1 != 'hd' and p2 == 'hd'):
            # if other is he
            if (p1 == 'hd' and p2 == 'he') or (p1 == 'he' and p2 == 'hd'):
                # he + hd 
                return {
                    'hd':[0.5, n1], 
                    'he':[0.5, n2]
                    }
            else:
                # hd + hr
                return {
                    'he':[1, n2]
                    }
        else:
            # hd + hd
            return {
                'hd': [1, n1]
                }
    # if one is he
    elif p1 == 'he' or p2 == 'he':
        # if other is he
        if (p1 == 'he' and p2 == 'he'):
            # he + he
            return {'he': [0.5, n2],
            'hr': [0.25, n3],
            'hd': [0.25, n1]}
        else:
            # he + hr
            return {'he': [0.5, n2],
            'hr': [0.5, n3]}
    else:
        # hr + hr
        return {'hr': [1, n3]}

def mult(data):
    chances = []
    rowN = 0
    rownum = 0
    for row in data:
        for key, value in row.items():
            for thisrow in data:
                if rowN != len(data) and rowN != rownum:
                    thisgene = []
                    for k, v in thisrow.items():
                        c = (value[0] * v[0]).as_integer_ratio()
                        r = rowN
                        h = value[1] + v[1]
                        thisgene.append({'chance' : c, 'gene' : r, 'h' : h})
                    chances.append(thisgene)
                rowN += 1
        rownum += 1
    return chances