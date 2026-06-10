import numpy as np
import pandas as pd
import unicodedata


#
def is_valid_value(value) -> bool:
    if value == "-":
        return True
    try:
        float(value)
        return True
    except ValueError:
        return False

#
def dataframe_has_pending(df: pd.DataFrame) -> bool:
    return (df == "-").any().any()

#
def compare_headers(existing, incoming):
    return {
        "missing": list(set(existing) - set(incoming)),
        "extra": list(set(incoming) - set(existing))
    }

# distinguish between a form file data and matrix data:
def detect_file_type(df, file_ext):
    '''
        Distinguish between a form file data and matrix data
    '''
    if file_ext == ".csv":
        df_temp = df.copy()
    else:
        return None

    # check is the sheet has an index name column:
    has_index_col = "Unnamed: 0" in df_temp.columns

    # update index name column:
    if has_index_col:
        df_temp.set_index(df_temp.columns[0], inplace=True)

    # checks if the table is squared:
    is_square = df_temp.shape[0] == df_temp.shape[1]

    # checks if index and columns has same labels:
    has_same_labels = list(df_temp.index) == list(df_temp.columns)

    # checks if file data has some metadata cols:
    has_metadata = has_metadata_cols(df_temp)

    if has_metadata:
        return "forms"

    elif is_square and has_same_labels:
        return "matrix"

    else:
        return "ambiguous"

# checks for metadata columns:
def has_metadata_cols(df):
    '''
        Checks for metadata columns
    '''
    for col in df.columns:
        series = df[col]

        # Verifica de forma segura se a coluna é object (versões antigas) ou string/str (versões novas):
        if pd.api.types.is_object_dtype(series) or pd.api.types.is_string_dtype(series):
            # if series.nunique() > 1:
            return True

    return False

# converts a triangular matrix to symmetric matrix:
def triangular_to_symmetric(df):
    '''
        Converts a triangular matrix to symmetric matrix
    '''

    new_df = df.fillna(df.T)

    np.fill_diagonal(new_df.values, 0)
    # # convert to np.array:
    # arr = df.to_numpy()
    # # create symmetric matrix:
    # arr_t = arr.T

    # sym = np.where(np.isnan(arr), arr_t, arr)
    # np.fill_diagonal(sym, 0)

    # # re-convert to a DataFrame:
    # new_df = pd.DataFrame(sym, index=df.index, columns=df.columns)

    # replacing
    return new_df

def unicode_text(text):
    normalized_text = unicodedata.normalize('NFD', text)
    new_text = "".join(c for c in normalized_text if unicodedata.category(c) != 'Mn')
    return new_text
