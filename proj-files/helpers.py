from flask import render_template, session
from functools import wraps
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
    rownum = 0
    for row in data:
        # checks if this is the first iteration (runs code only once below but gets the data from the first row)
        if rownum == 0:
            # iterates over the key value pairs in the first row of data
            for key, value in row.items():
                # sets a counter
                rowN = 0
                # itterates through the rows of data again skipping the first to avoid multiplying a gene by itself
                for thisrow in data:
                    if rowN > 0 and not rowN > 1:
                        # sets a blank list
                        thisgene = []
                        # iterates over key value pairs for other rows
                        for k, v in thisrow.items():
                            # calculates chance as a fraction
                            c = (value[0] * v[0]).as_integer_ratio()
                            # adds symbols together to form the full symbol (i.e: AaSs)
                            h = value[1] + v[1]
                            # appends these to a dictionary
                            thisgene.append({'chance' : c, 'h' : h})
                        # appends dictionary to list
                        chances.append(thisgene)
                    rowN += 1
        rownum += 1
        # recursion?
        if len(data) > 2:
            mult(chances)
        # returns value on second itteration of first loop for efficency
        if rownum > 0:
            return chances

def prob(genes):
    return genes

def count_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("count") is None:
            return error("Bad request: Start at the beginning.", 400)
        return f(*args, **kwargs)
    return decorated_function