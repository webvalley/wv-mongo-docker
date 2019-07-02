# Copyright (c) 2019 Marco Marinello <marco.marinello@school.rainerum.it>

from .utils import PLICImporter
from .monplic import push_df
import json


separation = [
    [['excel_to_pandas_df', "Parse uploaded file"]],
    [
        ['drop_empty_cols', "Drop empty columns"],
        ['identify_vars_category', "Map columns with their own cateogry"],
        ['drop_date_cols', "Drop columns with dates"],
        ['visit_cols_to_rows', "Move different visits to one row each"],
        ['convert_string_values', "Convert string to numbers"],
        ['export_mapped_columns', "Export encoded columns"],
        ['drop_useless_columns', "Remove useless columns for the AI"],
        ['fix_useful_string_columns', "Fix known problems with some columns"],
        ['translate_cols', "Translate column labels into English"]
    ],
    [
        ["push_to_mongo", "Pushing data into DataBase"]
    ]
]


def frontend_msg(value):
    return "\n%s" % (json.dumps(value))


def trigger(filename, study):
    imp = PLICImporter(filename)
    functions = [
        imp.excel_to_pandas_df,
        imp.drop_empty_cols,
        imp.identify_vars_category,
        imp.drop_date_cols,
        imp.visit_cols_to_rows,
        imp.convert_string_values,
        imp.export_mapped_columns,
        imp.drop_useless_columns,
        imp.fix_useful_string_columns,
        imp.translate_cols,
    ]

    yield frontend_msg({
        "next_stage": functions[0].__name__
    })

    for i in enumerate(functions):
        status = {
            "current_stage": i[1].__name__,
            "next_stage": len(functions) > i[0]+1 and functions[i[0]+1].__name__ or None,
        }
        try:
            out = i[1]()
            with open(i[1].__name__+".log.txt", "w") as fh:
                fh.write(str(list(imp.df.columns.values)))
            if i[1].__name__ == "export_mapped_columns":
                status["artifacts"] = {
                    "Encoded columns association": out
                }
        except Exception as e:
            print(e)
            yield "\n" + json.dumps({
                "current_stage": i[1].__name__,
                "status": "error",
                "error": "An error (%s) occurred while running %s" % (e, i[1].__name__)
            })
            raise StopIteration
        yield frontend_msg(status)

    imp.df.to_csv("/tmp/plic_milano_clean.csv")
    yield frontend_msg({
        "next_stage":"push_to_mongo"
    })
    push_df(imp.df, study)
    yield frontend_msg({
        "current_stage":"push_to_mongo"
    })

    yield "\n" + json.dumps({
        "status": "complete"
    })
