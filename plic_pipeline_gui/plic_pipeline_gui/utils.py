#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import sys
import os
import re
from sklearn import preprocessing
from datetime import datetime


# In[2]:


class Plic_import_error(Exception):
    pass


# In[3]:

class Plic_importer:
    nan_value = -1
    sep = ","
    index_col = 0

    def __init__(self, file_name):
        self.file_name = file_name
        self.df = None
        self.map_dict = {}

    def __call__(self):
        return self.df

    def excel_to_pandas_df(self):
        self.df = pd.read_excel(self.file_name, index_col=self.index_col).fillna(self.nan_value)

    def csv_to_pandas_df(self):
        return pd.read_csv(self.file_name, index_col=self.index_col, sep=self.sep).fillna(self.nan_value)

    def drop_empty_cols(self):
        cols_to_drop = []

        for i in self.df.columns.values:
            o = self.df[i].unique()
            if len(o) == 1 and o[0] == -1:
                cols_to_drop.append(i)

        self.df.drop(cols_to_drop, axis=1, inplace=True)

    def visit_cols_to_rows(self):
        suffixes = ["_%s" % a for a in range(0,10)] + \
           ["_%s_a" % a for a in range(0,10)] + \
           ["_%s_recod" % a for a in range(0,10)]

        mv_cols = [x for x in self.df.columns if x.endswith(tuple(suffixes))]
        perdurant_cols = [x for x in self.df.columns if x not in mv_cols]

        new_cols = set()

        for col in mv_cols:
            for s in suffixes:
                col = col.replace(s, "")
            col.replace("__", "_")
            if col.endswith("_"):
                col = col[:-1]
            new_cols.add(col)

        for col in perdurant_cols:
            new_cols.add(col)

        new_cols.add("cod_pz")

        fields_per_visit = set()

        for col in mv_cols:
            for s in suffixes:
                col = col.replace(s, re.sub("\d", "%s", s))
            fields_per_visit.add(col)

        single = dict()

        for col in mv_cols:
            _col = col
            for s in suffixes:
                col = col.replace(s, "")
            col.replace("__", "_")
            if col.endswith("_"):
                col = col[:-1]
            single[_col] = col

        new_data = []

        for paz in self.df.index.values:
                obj = self.df.loc[paz]
                for visit in range(1, 5):
                    this = {"cod_pz": paz}
                    for old_col in fields_per_visit:
                        try:
                            this[single[old_col % visit]] = obj[old_col % visit]
                        except KeyError:
                            pass
                    for pd_col in perdurant_cols:
                        this[pd_col] = obj[pd_col]
                    new_data.append(this)

        self.df = pd.DataFrame(new_data, columns=new_cols).fillna(self.nan_value)

    def convert_string_values(self):
        yes_no = {"No": 0,
                "Sì": 1,
                "Si": 1,
                "no": 0,
                "sì": 1,
                "si": 1,
                "F": 1,
                "M": 0,
                "mancante": -1,
                 -1: -1,
                 -1.0: -1}
        le = preprocessing.LabelEncoder()
        for col in self.df.columns.values:
            if self.df[col].dtypes == "object_":
                remove_list = ["-1", -1, -1.0]
                unique_list = [str(item) for item in self.df[col].unique() if item not in remove_list]

                if all([x in yes_no.keys() for x in unique_list]):
                    self.df[col] = self.df[col].map(yes_no)

                elif "data" not in col and len(unique_list) < 8:
                    enc_value_list = le.fit_transform(unique_list)
                    col_map_dict = dict(zip(unique_list, [x+2 for x in enc_value_list]))
                    self.df[col] = self.df[col].map(col_map_dict)
                    self.map_dict[col] = col_map_dict

        self.df = self.df.fillna(self.nan_value)

    def drop_useless_columns(self):
        bad_col_contains = ["note", "endotelio",
                        "indagini", "tiroide_patologie_text",
                        "neoplasia_tipo", "altre_patologie",
                        "nefropatie_tipo", "diagnosi_nuove_rivalutazioni",
                        "addome_tipo", "neoplasia1_tipo", "soffi_tipo",
                        "HT_indicazione1",  "epatopatie_tipo", "_ei", "alimentazione",
                        "ei1", "ei2", "id_esame", "dietetic"]
        bad_col_list = []

        for c in self.df.columns.values:
            if any([x in c for x in bad_col_contains]):
                bad_col_list.append(c)

        self.df.drop(bad_col_list, axis=1, inplace=True)

    def fix_useful_string_columns(self):
        f = [
            self.fix_EA,
            self.fix_fumo,
            self.fix_grasso_epicardico,
            self.fix_date_objects,
        ]
        for i in f:
            try:
                i()
            except Exception as e:
                print(i.__name__, "raised", e)

    def fix_EA(self):
        self.df["EA"].replace("FA", -1, inplace=True)
        self.df["EA"].replace("fa", -1, inplace=True)
        self.df["EA"] = self.df["EA"].astype("float64")

    def fix_fumo(self):
        new_values = []
        for value in self.df["fumo"]:
            if "no" in value:
                new_values.append(0)
            elif "ex" in value:
                new_values.append(2)
            else:
                new_values.append(1)

        self.df["fumo"] = new_values

    def fix_grasso_epicardico(self):
        self.df["grasso_epicardico"] = self.df["grasso_epicardico"].apply(lambda s: str(s).replace(",", "."))

    def fix_date_objects(self):
        cur_year = datetime.now().year
        for col in self.df.columns.values:
            if "data" in col:
                new_value_list = []
                for val in self.df[col]:
                    if type(val) not in [pd._libs.tslibs.timestamps.Timestamp, np.datetime64]:
                        q = str(val).replace("?", "").strip().split(".")[0]
                        if len(q) == 4:
                            if 1900 <= int(q) <= cur_year:
                                new_value_list.append(datetime(int(q), month=1, day=1, hour=0, minute=0))
                            else:
                                new_value_list.append(-1)
                        else:
                            new_value_list.append(-1)

                    else:
                        new_value_list.append(val)
                self.df[col] = new_value_list

    def translate_cols(self):
        transfile = pd.read_excel("cols_trans.xlsx", index_col=0)
        tr_dict = {}
        for idx, row in transfile.iterrows():
            tr_dict[row.IT] = row.EN
        self._t = tr_dict
        new_cols_names = []
        for col in self.df.columns.values:
            col = col.lower().replace("_ns", "")
            if col in tr_dict:
                new_cols_names.append(tr_dict[col])
            else:
                new_cols_names.append(col)
        self.df.columns = new_cols_names
