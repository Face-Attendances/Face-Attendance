import pandas as pd

def load_and_clean(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    # ví dụ: loại bỏ null, chuẩn hoá tên cột
    df = df.dropna()
    df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]
    return df

def split_train_test(df: pd.DataFrame, test_ratio: float = 0.2):
    from sklearn.model_selection import train_test_split
    train, test = train_test_split(df, test_size=test_ratio, random_state=42)
    return train, test
