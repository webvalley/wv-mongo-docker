# Copyright (c) 2019 Gianmarco Gamo
# Copyright (c) 2019 Leonardo Dusini
# Adapted to the django project by
# Copyright (c) 2019 Marco Marinello <marco.marinello@school.rainerum.it>

import pandas as pd
import os
import math
from . import monplic

def step1(age,sex,chd=True):
    #CHD
    if (chd):            #constants for chd
        if (sex):              # 0 for men and 1 for women
            a=-29.8
            p = 6.36
        else:
            a=-22.1
            p = 4.71

    else:                #constants for non chd
        if (sex):
            a = -31.0
            p = 6.62
        else:

            a = -26.7
            p = 5.64

    #print("a =", a, "; p =",p)
    if age>20:
        s = math.exp(-(math.exp(a))*(age-20)**p)
    else:
        s =0
    return s

def step2(chol, SBP, smoker, chd=True):
    if chd:
        c_smoker = 0.71
        c_chol = 0.24
        c_SBP = 0.018
    else:
        c_smoker = 0.63
        c_chol = 0.02
        c_SBP = 0.022

    w = (c_chol*(chol-6))+(c_SBP*(SBP-120))+(c_smoker*smoker)
    return w

def score_algorithm(age, chol, SBP, sex, smoker):
    #CHD
    s = step1(age,sex)
    s10 = step1(age+10,sex)

    w = step2(chol, SBP, smoker)

    s=s**(math.exp(w))
    s10=s10**(math.exp(w))
    try:
        stot=s10/s
    except:
        stot=1
    riskc = 1 -stot


    #NON CHD
    s = step1(age,sex,chd=False)
    s10 = step1(age+10,sex, chd=False)

    w = step2(chol, SBP, smoker, chd=False)

    s=s**(math.exp(w))
    s10=s10**(math.exp(w))
    try:
        stot=s10/s
    except:
        stot=1
    risknon = 1 -stot


    #print ("risk CHD: ", riskc *100)
    #print ("risk nonCHD: " ,risknon * 100)
    risktot = 1 - (1-riskc) * (1-risknon)


    #print('total RISK:',risktot)
    return risktot


def score_to_collection(coll_name):
    client = monplic.get_client()
    coll = client.plic[coll_name].find()
    for i in coll:
        age = i["ana:age"]
        gender = i["ana:gender"]
        tot_chol = i["lab:total_cholesterol"]*0.02586
        sbp = i["esa_obi:sbp"]
        smoking = i["ana_fis:smoking"] == "no" and 0 or 1
        if smoking == 2:
            smoking = 1
        score = score_algorithm(age, tot_chol, sbp, gender, smoking)*100
        client.plic[coll_name].update_one({"_id": i["_id"]}, {"$set": {"score": score}})
        print(i["patient_id"], score)
