def test_openpyxl():
    import os
    import pathlib
    from openpyxl import load_workbook
    import shutil

    folder = pathlib.Path(__file__).parent.resolve()
    path = folder / "openpyxl_test.xlsx"

    tmp_folder = pathlib.Path(__file__).parent.resolve() / "output_folder"
    os.makedirs(tmp_folder)
    tmp_path = tmp_folder / "output.xlsx"
    shutil.copy(path, tmp_path)

    excel_file = load_workbook(tmp_path)
    excel_file.close()
    if tmp_folder.exists():
        shutil.rmtree(tmp_folder)
