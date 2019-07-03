# Copyright (c) 2019 Julian Modanese <01modjul@rgtfo-me.it>
# Copyright (c) 2019 Marco Marinello <marco.marinello@school.rainerum.it>
# This script has been developed thanks to the help recived
# from Marco Chierici, Valerio Maggio, Stefano Fioravanzo
# & the whole MPBA Team@FBK

import pandas as pd
import numpy as np
import sys
import os
import re
from sklearn import preprocessing
from datetime import datetime
from collections import defaultdict
from itertools import product


class PLICImporterError(Exception):
    pass


class PLICImporter:
    NAN_VALUE = -1
    SEP = ","
    INDEX_COL = 0
    TRANSFILE = "cols_trans.xlsx"
    COLS_METADATA_FILE = "cols_metadata.xlsx"


    def __init__(self, file_name):
        self.file_name = file_name
        self.df = None
        self.map_dict = {}

    def __call__(self):
        return self.df

    def excel_to_pandas_df(self):
        self.df = pd.read_excel(self.file_name, index_col=self.INDEX_COL).fillna(self.NAN_VALUE)

    def csv_to_pandas_df(self):
        self.df = pd.read_csv(self.file_name, index_col=self.INDEX_COL, sep=self.SEP).fillna(self.NAN_VALUE)

    def identify_vars_category(self):
        trans = {}
        tag_cols = [
            'ANAGRAFICA',
            'ANAMNESI_FISIOLOGICA',
            'ANAMNESI_PATOLOGICA',
            'ANAMNESI_FARMACOLOGICA',
            'ESAME_OBIETTIVO',
            'LABORATORIO',
            'ULTRASOUND_TSA',
            'ENDOTELIO',
            'LUNAR_BODY_SCAN',
            'ECODOPPLER_ARTI'
        ]
        categories_map = {
            cat: "_".join([x[:3] for x in cat.split("_")])
            for cat in tag_cols
        }
        TAG = "ANAGRAFICA"
        for col in self.df.columns.values:
            if col in tag_cols:
                TAG = col
            trans[col] = "%s:%s" % (categories_map[TAG], col)

        # Keep
        new_cols_labels = [
            trans[a] for a in self.df.columns.values
        ]
        self.df.columns = new_cols_labels

    def drop_empty_cols(self):
        cols_to_drop = []

        for i in self.df.columns.values:
            o = self.df[i].unique()
            if len(o) == 1 and o[0] == -1:
                cols_to_drop.append(i)

        self.df.drop(cols_to_drop, axis=1, inplace=True)

    def drop_date_cols(self):
        self.df.drop([x for x in self.df.columns.values if "data" in x], axis=1, inplace=True)

    def visit_cols_to_rows(self):
        if self.study == "chiesa":
            return
        self.df.reset_index(inplace=True)
        suffixes = ["_%s" % a for a in range(0,10)] + \
           ["_%s_a" % a for a in range(0,10)] + \
           ["_%s_recod" % a for a in range(0,10)]

        mv_cols = [x for x in self.df.columns if x.endswith(tuple(suffixes))]
        perdurant_cols = [x for x in self.df.columns if x not in mv_cols]

        single = defaultdict(list)
        new_cols = [] #["cod_pz", "visit"]
        print(len(self.df.columns.values))
        for col in self.df.columns.values:
            if col in perdurant_cols:
                if col not in new_cols:
                    new_cols.append(col)
            else:
                old_col = col
                for s in suffixes:
                    col = col.replace(s, "")
                col.replace("__", "_")
                if col.endswith("_"):
                    col = col[:-1]
                if col not in new_cols:
                    new_cols.append(col)
                single[col].append(old_col)

        cols_per_line = []
        max_len = len(max(single.values(), key=len))
        for i in range(max_len):
            cols_per_line.append(["dummyvisit%s" % i])

        for col in new_cols:
            if col not in single:
                # The col is perdurant and should be present
                # for each visit
                for i in range(max_len):
                    cols_per_line[i].append(col)
            else:
                fill = {a: False for a in range(max_len)}
                for field in single[col]:
                    field_no = field.replace("_recod", "").replace("_a", "")
                    cols_per_line[int(field_no[-1])-1].append(field)
                    fill[int(field_no[-1])-1] = True
                missing = filter(lambda a: not fill[a], fill)
                for key in missing:
                    cols_per_line[key].append("dummycol")


        self.df["dummycol"] = None
        for i in range(max_len):
            self.df["dummyvisit%s" % i] = i

        new_cols = ["visit"] + new_cols

        new_df = pd.DataFrame(columns=new_cols)
        for cols in cols_per_line:
            tmp_df = pd.DataFrame(self.df[cols].values, columns=new_cols)
            new_df = pd.concat(
                (new_df, tmp_df),
                ignore_index=False
            )

        self.df = new_df

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

        for col in self.df.columns.values:
            le = preprocessing.LabelEncoder()
            if self.df[col].dtypes == "object_":
                remove_list = ["-1", -1, -1.0]
                unique_list = [str(item) for item in self.df[col].unique() if item not in remove_list]

                if all([x in yes_no.keys() for x in unique_list]):
                    self.df[col] = self.df[col].map(yes_no)

                elif len(unique_list) < 8 and col != "visit" and \
                    "_atc" not in col.lower() and "atc_" not in col.lower():
                    enc_value_list = le.fit_transform(unique_list)
                    col_map_dict = dict(zip(unique_list, [x+2 for x in enc_value_list]))
                    self.df[col] = self.df[col].map(col_map_dict)
                    self.map_dict[col] = col_map_dict

        self.df = self.df.fillna(self.NAN_VALUE)


    def export_mapped_columns(self):
        vals_conv = []
        for i in self.map_dict:
            for x in self.map_dict[i]:
                vals_conv.append([i, x, self.map_dict[i][x]])
        return {"Encoded columns association": ["assoc_%s.csv" % self.study, pd.DataFrame(
                vals_conv, columns=["column", "value", "replacing"]
            ).to_csv()]}


    def drop_useless_columns(self):
        bad_col_contains = ["note", "endotelio",
                        "indagini", "tiroide_patologie_text",
                        "neoplasia_tipo", "altre_patologie",
                        "nefropatie_tipo", "diagnosi_nuove_rivalutazioni",
                        "addome_tipo", "neoplasia1_tipo", "soffi_tipo",
                        "HT_indicazione1",  "epatopatie_tipo", "_ei", "alimentazione",
                        "ei1", "ei2", "id_esame", "dietetic", "nascita"]
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
        transfile = pd.read_excel(self.TRANSFILE, index_col=0)
        tr_dict = {}
        for idx, row in transfile.iterrows():
            tr_dict[row.IT] = row.EN
        self._t = tr_dict
        new_cols_names = []
        for col in self.df.columns.values:
            ns_in_col = False
            col = col.lower()
            if "_ns" in col:
                col = col.replace("_ns", "")
                ns_in_col = True
            try:
                col, target = col.split(":")
            except:
                target = col
            if target in tr_dict:
                eng_col = tr_dict[target]
                if ns_in_col and not eng_col.endswith("_yn"):
                    eng_col = eng_col + "_yn"
                new_col_name = "%s:%s" % (col, eng_col)
                new_cols_names.append(new_col_name)
            else:
                new_cols_names.append("%s:%s" % (col, target))
        fixed_new_cols_names = new_cols_names
        if self.study == "chiesa":
            fixed_new_cols_names = self.mv_lab_to_ult_tsa(new_cols_names)
        self.df.columns = fixed_new_cols_names

    def mv_lab_to_ult_tsa(self, new_cols_names):
        fixed_new_cols_names = []
        do_replace = False
        for col in new_cols_names:
            if col.startswith("lab:imt") and not do_replace:
                do_replace = True
            if do_replace and ":" in col and col.startswith("lab:"):
                col = "ult_tsa:%s" % col.split(":")[1]
            fixed_new_cols_names.append(col)
        return fixed_new_cols_names

    def yn_to_int(self):
        for col in [x for x in self.df.columns.values if "_yn" in x]:
            self.df[col] = self.df[col].astype("int")

    def export_artifacts(self):
        return {
            "CSV cleaned dataset": ["%s_cleaned.csv" % self.study, self.df.to_csv()]
        }
