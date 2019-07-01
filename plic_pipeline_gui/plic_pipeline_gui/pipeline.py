# Copyright (c) 2019 Marco Marinello <marco.marinello@school.rainerum.it>

from .utils import Plic_importer
import json


separation = [
    [['excel_to_pandas_df', "Parse uploaded file"]],
    [
        ['drop_empty_cols', "Drop empty columns"],
        ['visit_cols_to_rows', "Move different visits to one row each"],
        ['convert_string_values', "Convert string to numbers"],
        ['export_mapped_columns', "Export encoded columns"],
        ['drop_useless_columns', "Remove unuseful columns for the AI"],
        ['fix_useful_string_columns', "Fix known problems with some columns"],
        ['translate_cols', "Translate column labels into English"]
    ]
]


def frontend_msg(value):
    return "\n%s" % (json.dumps(value))


def trigger(filename, study):
    imp = Plic_importer(filename)
    functions = [
        imp.excel_to_pandas_df,
        imp.drop_empty_cols,
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
            i[1]()
            if i[1].__name__ == "export_mapped_columns":
                status["artifacts"] = {
                    "Encoded columns association": imp.cols_export
                }
        except Exception as e:
            print(e)
            yield "\n" + json.dumps({
                "current_stage": i[1].__name__,
                "status": "error",
                "error": "An error (%s) occurred while running %s" % (e, i[1].__name__)
            })
            raise StopIteration
        yield "\n" + json.dumps(status)

    yield "\n" + json.dumps({
        "status": "complete"
    })
