import pandas as pd

def read_the_spreadsheet(path):
    return pd.read_excel(path, dtype=str).fillna('')


        
def write_spreadsheet(df_result, output, file_name):
    df_result.to_excel (f'{output}/{file_name}.xlsx', index=False)


def search_for_data(table: pd.DataFrame, data_sought: str):
    for column in table.columns:
        if data_sought.strip() in column.strip().lower():
            return column
    return None
        

def concatenate_database_results(df_result, df_db):
    #Concatenar resultados
    if df_result.empty == False:
        frames = [df_result, df_db]
        df_result = pd.concat(frames, ignore_index=True)
        return df_result
    else:
        df_result = df_db
        return df_result
    


