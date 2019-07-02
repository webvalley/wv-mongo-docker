# Copyright (c) 2019 Marco Marinello <marco.marinello@school.rainerum.it>

from .utils import PLICImporter
from .monplic import push_df
import json


separation = [
    [['excel_to_pandas_df', "Parse uploaded file"]],
    [
        ['identify_vars_category', "Map columns with their own cateogry"],
        ['drop_empty_cols', "Drop empty columns"],
        ['drop_date_cols', "Drop columns with dates"],
        ['visit_cols_to_rows', "Move different visits to one row each"],
        ['convert_string_values', "Convert string to numbers"],
        ['export_mapped_columns', "Export encoded columns"],
        ['drop_useless_columns', "Remove useless columns for the AI"],
        ['fix_useful_string_columns', "Fix known problems with some columns"],
        ['translate_cols', "Translate column labels into English"],
        ['yn_to_int', "Codify booleans as integers"],
        ['export_artifacts', "Export the cleaned dataframe"],
    ],
    [
        ["push_to_mongo", "Pushing data into DataBase"]
    ]
]


def frontend_msg(value):
    return "\n%s" % (json.dumps(value))


def trigger(filename, study):
    imp = PLICImporter(filename)
    imp.study = study

    functions = [
        imp.excel_to_pandas_df,
        imp.identify_vars_category,
        imp.drop_empty_cols,
        imp.drop_date_cols,
        imp.visit_cols_to_rows,
        imp.convert_string_values,
        imp.export_mapped_columns,
        imp.drop_useless_columns,
        imp.fix_useful_string_columns,
        imp.translate_cols,
        imp.yn_to_int,
        imp.export_artifacts,
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
            if out:
                status["artifacts"] = out
        except Exception as e:
            print(e)
            yield frontend_msg({
                "current_stage": i[1].__name__,
                "status": "error",
                "error": "An error (%s) occurred while running %s" % (e, i[1].__name__)
            })
            raise StopIteration
        yield frontend_msg(status)

    yield frontend_msg({
        "next_stage":"push_to_mongo"
    })

    push_df(imp.df, study)

    yield frontend_msg({
        "current_stage":"push_to_mongo",
        "status": "complete"
    })
