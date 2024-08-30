import pandas as pd
import tkinter as tk
from tkinter import filedialog

# tkinter 창 숨기기
root = tk.Tk()
root.withdraw()

# 파일 탐색기를 열고 Excel 파일 선택
excel_file_path = filedialog.askopenfilename(
    title="Select an Excel file",
    filetypes=[("Excel files", "*.*")]
)

if excel_file_path:
    # Excel 파일을 DataFrame으로 읽어오기
    df = pd.read_excel(excel_file_path)

    # DataFrame을 JSON 형식으로 변환하기
    json_data = df.to_json(orient='records', force_ascii=False)

    # JSON 데이터를 파일로 저장하기
    json_file_path = filedialog.asksaveasfilename(
        title="Save JSON file",
        defaultextension=".json",
        filetypes=[("JSON files", "*.json")]
    )

    if json_file_path:
        with open(json_file_path, 'w', encoding='utf-8') as json_file:
            json_file.write(json_data)

        print(f"JSON 파일이 {json_file_path}에 저장되었습니다.")
    else:
        print("JSON 파일 저장이 취소되었습니다.")
else:
    print("Excel 파일 선택이 취소되었습니다.")