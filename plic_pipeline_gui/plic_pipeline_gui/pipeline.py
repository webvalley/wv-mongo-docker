# Copyright (c) 2019 Marco Marinello <marco.marinello@school.rainerum.it>

from .utils import Plic_importer
import json


def trigger(filename, study):
    imp = Plic_importer(filename)
    functions = [
        imp.excel_to_pandas_df,
        imp.drop_empty_cols,
        imp.visit_cols_to_rows,
        imp.convert_string_values,
        imp.drop_useless_columns,
        imp.fix_useful_string_columns,
        imp.translate_cols,
    ]

    import time
    for i in enumerate(functions):
        time.sleep(0.9)
        print(i)
        yield "\n" + json.dumps({"current_stage": i[0]+1, "stages": len(functions), "stage_name": i[1].__name__})
