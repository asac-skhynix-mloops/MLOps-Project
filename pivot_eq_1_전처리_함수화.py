# -*- coding: utf-8 -*-
"""pivot_EQ_1_전처리_함수화

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1vh-eHXLDW2-w2QhcwYjm36kouH_8uWra
"""

from google.colab import drive
drive.mount('/content/drive')

import pandas as pd
from datetime import datetime

def load_and_process_data(file_path):
   # CSV 파일 불러오기
    df1 = pd.read_csv(file_path, encoding='cp949')

    # 날짜와 시간 데이터를 24시간제로 변환하는 함수
    def convert_to_24hr(date_str):
        # 오전/오후 문자를 AM/PM으로 변환
        date_str = date_str.replace("오전", "AM").replace("오후", "PM")
        # 24시간제 형식으로 변환
        date_obj = datetime.strptime(date_str, "%Y-%m-%d %p %I:%M:%S")
        # 변환된 객체를 문자열 형식으로 반환
        return date_obj.strftime("%Y-%m-%d %H:%M:%S")

    # 날짜 시간 열을 24시간제로 변환
    df1['start_dt_tm'] = df1['start_dt_tm'].apply(convert_to_24hr)
    df1['end_dt_tm'] = df1['end_dt_tm'].apply(convert_to_24hr)

    # 'start_dt_tm' 열을 datetime64[ns]로 변환
    df1['start_dt_tm'] = pd.to_datetime(df1['start_dt_tm'])
    df1['end_dt_tm'] = pd.to_datetime(df1['end_dt_tm'])

    return df1

# 파일 경로 설정
file_path = '/content/drive/MyDrive/ASAC_4기_기업프로젝트_SK하이닉스/00.Data_set/ASAC_4기_Dataset_FDC_Summary_Fullset_22년PoC.csv'
# 데이터 처리 및 출력
df1_1 = load_and_process_data(file_path)
print(df1_1.head())

from datetime import datetime
import pandas as pd
import numpy as np

def load_and_convert_dates(file_path, date_columns):
    # CSV 파일 불러오기
    df2 = pd.read_csv(file_path, encoding='utf-16', sep='\t')

    # 날짜와 시간 데이터를 24시간제로 변환하는 내부 함수
    def convert_to_24hr(date_str):
        if pd.isna(date_str):
            # 입력 값이 NaN이라면, 그대로 반환
            return date_str
        # 오전/오후 문자를 AM/PM으로 변환
        date_str = date_str.replace("오전", "AM").replace("오후", "PM")
        # 24시간제 형식으로 변환
        date_obj = datetime.strptime(date_str, "%Y-%m-%d %p %I:%M:%S")
        # 변환된 객체를 문자열 형식으로 반환
        return date_obj.strftime("%Y-%m-%d %H:%M:%S")

    # 지정된 모든 날짜-시간 열을 변환
    for col in date_columns:
        df2[col] = df2[col].apply(convert_to_24hr)
        df2[col] = pd.to_datetime(df2[col])

    return df2

# 사용 예시
file_path = '/content/drive/MyDrive/ASAC_4기_기업프로젝트_SK하이닉스/00.Data_set/ASAC_4기_Dataset_Alarm_22년PoC.csv'
date_columns = ['Time', 'PUMP UP TIME']
df2_1 = load_and_convert_dates(file_path, date_columns)
print(df2_1.head())

def eq_sort(df1_1,eq_id):
  # EQ_ID가 주어진 값과 일치하는 행을 필터링
  filter_df1_1  = df1_1 [df1_1 ['EQ_ID'] == eq_id]
  # 'start_dt_tm'을 기준으로 데이터 정렬
  sort_df1_1  = filter_df1_1.sort_values('start_dt_tm')
  return sort_df1_1

# EQ=1만 불러오기
sort_df1_1  = eq_sort(df1_1 ,1)
sort_df1_1

def sort_alarm(df2_1,eq_id):
  # 특정 EQ_ID 값으로 필터링
  filter_df2_1 = df2_1[df2_1['EQ_ID']== eq_id]
  # Time 열을 기준으로 정렬
  filter_df2_1 = filter_df2_1.sort_values('Time')
  # Time 열에서 결측값이 있는 행을 제거
  filter_df2_1_cleaned = filter_df2_1.dropna(subset=['Time'])
  # 결과로 반환할 열만 선택 (Time=Tool Alarm시간만 불러오기)
  filter_df2_1_cleaned = filter_df2_1_cleaned[['Time']]
  return filter_df2_1_cleaned

# 출력예시
df2_1_cleaned = sort_alarm(df2_1,1)
print(df2_1_cleaned)

def sort_replacement(df2_1,eq_id, time_column='PUMP UP TIME'):
  # 특정 EQ_ID 값으로 필터링
  filter_df2_2 = df2_1[df2_1['EQ_ID']== eq_id]
  # 'PUMP UP TIME'열을 기준으로 정렬
  filter_df2_2 = filter_df2_2.sort_values(time_column)
  # 'PUMP UP TIME'열에서 결측값이 있는 행을 제거
  filter_df2_2_cleaned = filter_df2_2.dropna(subset=[time_column])
  # 결과로 반환할 열만 선택 (Alarm_dataset에서 EQ=1의 PUMP UP TIME (replacement 후 재가동 시간 불러오기))
  filter_df2_2_cleaned = filter_df2_2_cleaned[[time_column]]
  return filter_df2_2_cleaned

# 출력예시
df2_2_cleaned = sort_replacement(df2_1,1,'PUMP UP TIME')
print(df2_2_cleaned)

def merge_close_alarms(main_df, alarms_df, main_time_col='start_dt_tm', alarm_time_col='Time'):
  # 'forward' 방향으로 가장 가까운 알람 시간 합병 (start_dt_tm보다 늦게 일어난 Tool Alarm)
  merged_forward = pd.merge_asof(main_df, alarms_df, left_on=main_time_col, right_on=alarm_time_col, direction='forward', suffixes=('','TA_tm_after'))
  # 'backward' 방향으로 가장 가까운 알람 시간 합병 (start_dt_tm보다 먼저 일어난 Tool Alarm)
  merged_result = pd.merge_asof(merged_forward, alarms_df, left_on=main_time_col, right_on=alarm_time_col, direction='backward', suffixes=('TA_tm_after','TA_tm_before'))
  # 병합 결과에서 컬럼 이름 변경
  merged_result.rename(columns={'TimeTA_tm_after': 'TA_tm_after','TimeTA_tm_before':'TA_tm_before'}, inplace=True)
  return merged_result

# 출력예시
merged1_2 = merge_close_alarms(sort_df1_1 , df2_1_cleaned)
print(merged1_2)

def merge_with_closest_time(merged_result, pump_up_df):
  # 'PUMP UP TIME' 열을 날짜/시간 타입으로 변환
  pump_up_df['PUMP UP TIME'] = pd.to_datetime(pump_up_df['PUMP UP TIME'])
  # pd.merge_asof를 사용하여 start_dt_tm 기준으로 이전 시간의 PUMP UP TIME을 찾아 병합
  result_df = pd.merge_asof(merged_result, pump_up_df, left_on='start_dt_tm', right_on='PUMP UP TIME', direction='backward')
  # 병합 결과에서 컬럼 이름 변경
  result_df.rename(columns={'PUMP UP TIME':'P_Time'}, inplace=True)
  return result_df

merged1_3 = merge_with_closest_time(merged1_2, df2_2_cleaned)
print(merged1_3)

# 원하는 컬럼의 결측치 포함 행 제거
def drop_na_rows(result_df, column_name):
  cleaned_df = result_df.dropna(subset=[column_name])
  return cleaned_df

# merged1_3 데이터프레임에서 'TA_tm_before' 열에 있는 NA/NaN 값을 포함하는 행을 제거
merged1_4 = drop_na_rows(merged1_3, 'TA_tm_before')
print(merged1_4)

def select_and_sort_columns(cleaned_df, columns):
  # 원하는 컬럼 선택
  selected_df = cleaned_df[columns]
  sorted_df = selected_df.sort_values('start_dt_tm')
  sorted_df.reset_index(drop=True, inplace=True)
  return sorted_df

columns_to_include =  ['WAFER_ID', 'PROD_CD', 'EQ_ID', 'OPER_ID', 'RCP_ID', 'STEP_NM', 'PRMT_NM', 'TA_tm_before', 'start_dt_tm', 'end_dt_tm', 'TA_tm_after', 'P_Time', 'max_val', 'min_val', 'mean_val', 'stddev_val', 'range_val', 'median_val', 'p05_val', 'p10_val', 'p90_val', 'p95_val']
merged1_5 = select_and_sort_columns(merged1_4, columns_to_include)
merged1_5

# 결측치 처리
def fill_missing_values(sorted_df):
  sorted_df['max_val'].fillna(sorted_df['p95_val'],inplace=True)
  sorted_df['min_val'].fillna(sorted_df['p05_val'],inplace=True)
  sorted_df['range_val'].fillna(sorted_df['p95_val'] - sorted_df['p05_val'],inplace=True)

fill_missing_values(merged1_5)
print(merged1_5)

def replace_stddev_if_max_equals_min(sorted_df):
  for index, row in sorted_df.iterrows():
    if row['max_val']==row['min_val']:
      sorted_df.at[index, 'stddev_val'] = 0

replace_stddev_if_max_equals_min (merged1_5)

merged1_5['stddev_val'].isnull().sum()

def analyze_and_clean_data(df):
    # 각 컬럼별 결측치 개수 출력
    for col in ['max_val', 'min_val', 'range_val', 'mean_val', 'median_val', 'stddev_val', 'p05_val', 'p10_val', 'p90_val', 'p95_val']:
        print(f'{col} 결측치 개수는', df[col].isnull().sum())

    # 'mean_val'과 'stddev_val'이 둘 다 NaN인 행의 개수 계산 및 출력
    na_both = df[df['mean_val'].isna() & df['stddev_val'].isna()]
    print('mean_val과 stddev_val이 둘 다 NaN인 행의 개수:', len(na_both))

    # 'mean_val' 열에서 결측치를 포함하는 행을 제거
    cleaned_df_1 = df.dropna(subset=['mean_val'])

    return cleaned_df_1

# 함수 사용
merged1_6 = analyze_and_clean_data(merged1_5)

# 결과 출력
print(merged1_6.head())
print('제거 후 행의 개수:', len(merged1_6))

def create_pivot_table(df):
    # 피벗 테이블 생성
    pivot_df = df.pivot_table(
        index=[
            'WAFER_ID', 'PROD_CD', 'EQ_ID', 'OPER_ID', 'RCP_ID', 'STEP_NM',
            'TA_tm_before', 'start_dt_tm', 'end_dt_tm', 'TA_tm_after', 'P_Time'
        ],
        columns='PRMT_NM',
        values=['max_val', 'min_val', 'stddev_val', 'mean_val', 'range_val', 'median_val'],
        aggfunc='first'
    ).reset_index()

    # 컬럼 이름 변경
    pivot_df.columns = [f'{val}_{prmt}' if prmt != '' else val for val, prmt in pivot_df.columns]

    return pivot_df

# 함수 사용
pivot_df_1 = create_pivot_table(merged1_6)

# 결과 출력
print(pivot_df_1)

"""# **PRMT 1~4 PCA분석**"""

# drop안한 버전
import pandas as pd
from sklearn.decomposition import PCA
import re

def apply_pca_to_val_columns(df, val_type):
    # PCA 인스턴스 생성
    pca = PCA(n_components=1)  # 1개의 주성분으로 축소, 필요에 따라 조정 가능

    # 정규식 패턴으로 정확한 컬럼만 선택
    regex_pattern = rf"{val_type}_[1-4]$"
    val_columns = [col for col in df.columns if re.search(regex_pattern, col)]

    # 결과를 저장할 DataFrame 생성
    pca_results = pd.DataFrame()

    # 선택된 컬럼이 비어있지 않은 경우에 PCA 적용
    if val_columns:
        # 해당 컬럼 데이터 선택
        data_subset = df[val_columns]

        # PCA 적용
        pca_result = pca.fit_transform(data_subset)

        # PCA 결과를 DataFrame에 저장
        pca_results[f"{val_type}_pca"] = pca_result[:, 0]

        # 원본 데이터프레임에서 선택된 컬럼 삭제
        df = df.drop(columns=val_columns)

    return pca_results, df

def integrate_pca_results(df, val_types):
    # 각 val 종류별로 PCA 적용 후 결과 병합
    for val_type in val_types:
        # PCA 결과 계산 및 원래 컬럼 삭제
        pca_result_df, df = apply_pca_to_val_columns(df, val_type)

        # PCA 결과를 원래의 데이터프레임에 병합
        df = pd.concat([df, pca_result_df], axis=1)

    return df

# PCA 적용 함수 호출 및 결과 확인
val_types = ['max_val', 'min_val', 'stddev_val', 'mean_val', 'range_val', 'median_val']
pivot_df_2= integrate_pca_results(pivot_df_1, val_types)
print(pivot_df_2)

pivot_df_2.isnull().sum()

# 확인용
pivot_df_2.columns.tolist()

"""# **DROP할 컬럼들**"""

def filter_low_frequency_rows(df, column_name, threshold_ratio):
    # 각 값에 대한 빈도 계산 후 최빈값 빈도로 나누어 각 값의 비율 계산
    value_counts_ratio = df[column_name].value_counts() / df[column_name].value_counts().max()

    # 비율이 threshold_ratio 이하인 값 필터링
    low_frequency_values = value_counts_ratio[value_counts_ratio <= threshold_ratio].index

    # 낮은 비율 값을 출력
    print(f"Low frequency values in {column_name} below {threshold_ratio} threshold: {low_frequency_values.tolist()}")

    # 이러한 값들을 가진 행들을 제거
    filtered_df = df[~df[column_name].isin(low_frequency_values)]

    return filtered_df

# 함수 호출 및 결과 확인
pivot_df_3 = filter_low_frequency_rows(pivot_df_2, 'STEP_NM', 0.1)
print(pivot_df_3.shape)

pivot_df_3.isnull().sum()

"""# **파생변수 생성**

**1) diff값 (start_dt_tm ~ TA_time_after)**
"""

def calculate_time_difference(df, start_column, end_column):

    # 시간 차이를 계산 후 시간 단위로 변환
    df['diff_hours'] = (df[end_column] - df[start_column]).dt.total_seconds() / 3600

    # start_column 기준으로 데이터프레임 정렬
    sorted_df = df.sort_values(start_column)

    return sorted_df

# 함수 호출 및 결과 확인
pivot_df_4 = calculate_time_difference(pivot_df_3, 'start_dt_tm', 'TA_tm_after')
print(pivot_df_4)

"""**2) 공정별 소요시간 (STEP) (start_dt_tm ~ end_dt_tm)**"""

def calculate_process_time(df, start_column, end_column):

    # 공정 소요 시간 계산 후 시간 단위로 변환
    df['step_hours'] = (df[end_column] - df[start_column]).dt.total_seconds() / 3600

    # start_column 기준으로 데이터프레임 정렬
    sorted_df = df.sort_values(start_column)

    return sorted_df

# 함수 호출 및 결과 확인
pivot_df_5 = calculate_process_time(pivot_df_4, 'start_dt_tm', 'end_dt_tm')
print(pivot_df_5)

"""**3) last_hours (TA_before로부터 start_dt_tm까지의 시간)**"""

def calculate_time_from_last_event(df, last_event_column, start_column):

    # last_event_column에서 start_column까지의 시간 차이 계산 후 시간 단위로 변환
    df['last_hours'] = (df[start_column] - df[last_event_column]).dt.total_seconds() / 3600

    # start_column 기준으로 데이터프레임 정렬
    sorted_df = df.sort_values(start_column)

    return sorted_df

# 함수 호출 및 결과 확인
pivot_df_6 = calculate_time_from_last_event(pivot_df_5, 'TA_tm_before', 'start_dt_tm')
print(pivot_df_6)

"""**4) rep_hours(PUMP_UP_Time ~ start_dt_tm 시간(누적가동시간))**

(replacement 가까워질수록 Tool Alarm의 빈도가 높아진다는 가정)
"""

def calculate_time_from_replacement(df, replacement_time_column, start_column):

    # replacement_time_column에서 start_column까지의 시간 차이 계산 후 시간 단위로 변환
    df['rep_hours'] = (df[start_column] - df[replacement_time_column]).dt.total_seconds() / 3600

    # replacement_time_column 기준으로 데이터프레임 정렬
    sorted_df = df.sort_values(replacement_time_column)

    return sorted_df

# 함수 호출 및 결과 확인
pivot_df_7 = calculate_time_from_replacement(pivot_df_6, 'P_Time', 'start_dt_tm')
pivot_df_7

"""**6) TA/RP 사이에 (RCP, STEP) 조합의 반복횟수 (TA,RP에 영향을 미칠 수 있는 조합이 있는지)**"""

def calculate_cumulative_counts(df, sort_column):
    # 지정된 열을 기준으로 데이터프레임 정렬
    df.sort_values(sort_column, inplace=True)

    # TA_tm_before, RCP_ID, STEP_NM 조합별로 누적 카운트 계산
    df['Cumulative_Count_TA'] = df.groupby(['TA_tm_before', 'RCP_ID', 'STEP_NM']).cumcount() + 1

    # P_Time, RCP_ID, STEP_NM 조합별로 누적 카운트 계산
    df['Cumulative_Count_P'] = df.groupby(['P_Time', 'RCP_ID', 'STEP_NM']).cumcount() + 1

    return df

# 함수 호출 및 결과 확인
pivot_df_8 = calculate_cumulative_counts(pivot_df_7, 'start_dt_tm')
print(pivot_df_8)

"""## **원핫인코딩**"""

def group_step_nm_values(df, mapping):
    # mapping 딕셔너리를 순회하여 값을 변경
    for original, new in mapping.items():
        df.loc[df['STEP_NM'] == original, 'STEP_NM'] = new
    return df

# 사용 예
step_nm_mapping = {5: 6, 10: 11, 18: 19}
pivot_df_9 = group_step_nm_values(pivot_df_8, step_nm_mapping)

import pandas as pd
from sklearn.preprocessing import OneHotEncoder

def one_hot_encode_and_concat(df, column_name):
    # 인덱스 재설정
    df.reset_index(drop=True, inplace=True)

    # OneHotEncoder 생성 및 적용
    ohe = OneHotEncoder(sparse=False)
    ohe_df = ohe.fit_transform(df[[column_name]])

    # 원-핫 인코딩된 DataFrame 생성
    ohe_columns = [f"{column_name}_{int(col)}" for col in ohe.categories_[0]]
    ohe_df = pd.DataFrame(ohe_df, columns=ohe_columns)

    # 원래 DataFrame과 원-핫 인코딩된 DataFrame 병합
    df = pd.concat([df, ohe_df], axis=1)

    # 각 컬럼의 인덱스와 이름 출력 (필요시)
    for index, column in enumerate(df.columns):
        print(f"Index {index}: {column}")

    return df

# 사용 예
pivot_df_10 = one_hot_encode_and_concat(pivot_df_9, 'STEP_NM')
pivot_df_10

# 이동평균 고려한 val값들 생성 (window size =7)
col=pivot_df_1.columns[11:131]
for i in pivot_df_1['STEP_NM'].unique():
    for x in col:
        for y in pivot_df_1['P_Time'].unique():
            pivot_df_1.loc[(pivot_df_1['STEP_NM'] == i) & (pivot_df_1['P_Time'] == y) ,f'{x}_MA']=pivot_df_1.loc[(pivot_df_1['STEP_NM'] == i) & (pivot_df_1['P_Time'] == y),x].rolling(window=7).mean()w

import pandas as pd

def apply_rolling_mean(df, window_size=6):
    """
    데이터프레임에 이동평균을 적용하는 함수.
    Parameters:
    df : DataFrame
        대상 데이터프레임
    window_size : int
        이동 평균의 윈도우 크기 (기본값 6)
    """
    # 이동 평균을 적용할 열 선택 (예: 11번째부터 130번째까지의 열)
    cols_to_process = df.columns[11:131]

    # 'STEP_NM'과 'P_Time' 그룹에 대해 이동 평균 계산
    for col in cols_to_process:
        ma_col_name = f"{col}_MA"  # 새로운 열 이름 정의
        # 이동 평균 계산하여 새로운 열에 저장
        df[ma_col_name] = df.groupby(['STEP_NM', 'P_Time'])[col].transform(lambda x: x.rolling(window=window_size, min_periods=1).mean())

    return df

# 함수 적용
pivot_df_1 = apply_rolling_mean(pivot_df_1)

# 결과 확인
print(pivot_df_1.head())

# 이동평균 고려한 val값들 생성 (window size =6)
col=pivot_df_1.columns[11:106]
for i in pivot_df_1['STEP_NM'].unique():
    for x in col:
        pivot_df_1.loc[pivot_df_1['STEP_NM'] == i,f'{x}_MA']=pivot_df_1.loc[pivot_df_1['STEP_NM'] == i,x].rolling(window=6).mean()

pivot_df_1

pivot_df_1.isnull().sum().sum()

# pivot_df_1 데이터프레임에서 '_MA' 열에 있는 NA/NaN 값을 포함하는 행을 제거
pivot_df_1 = pivot_df_1.dropna()

# 원본 데이터 열 이름들을 문자열로 변환 후 추출 (예: 'max_val_1', 'max_val_2', ...)
original_columns = [col for col in pivot_df_1.columns if not str(col).endswith('_MA')]

# 이동평균과의 차이를 계산하여 새 열로 저장
for col in original_columns:
    ma_col = f"{col}_MA"  # 이동평균 열 이름
    diff_col = f"{col}_Diff"  # 차이 열 이름

    if ma_col in pivot_df_1.columns:  # 이동평균 열이 존재하는 경우에만 계산
        pivot_df_1[diff_col] = pivot_df_1[col] - pivot_df_1[ma_col]

# 결과 확인
print(pivot_df_1.head())

# 차이 열만 선택하여 데이터프레임 생성
diff_columns = [col for col in pivot_df_1.columns if not str(col).endswith('_Diff')]
diff_df = pivot_df_1[diff_columns]

# 전체 데이터프레임에서 몇 가지 열을 선택하여 상위 5행 확인
# 예시로 'max_val_1', 'max_val_1_MA', 'max_val_1_Diff' 열을 확인
selected_columns = ['max_val_1', 'max_val_1_MA', 'max_val_1_Diff']
print(pivot_df_1[selected_columns].head())

# '_MA'로 끝나지 않는 열만을 선택하여 새로운 데이터프레임 생성
filtered_columns = [col for col in pivot_df_1.columns if not str(col).endswith('_MA')]
pivot_df_1_filtered = pivot_df_1[filtered_columns]

# 결과 확인
print(pivot_df_1_filtered.head())

"""**7) TA(fail to fail)기준으로 공정순서 매기기**"""

# TA(fail to fail)기준으로 공정순서 매기기
for i, group in pivot_df_1_filtered.groupby('TA_tm_after'):
    sequence = 0
    for j, _ in group.iterrows():
        pivot_df_1_filtered.loc[j, 'sequence'] = sequence
        sequence += 1

# 각 컬럼의 인덱스와 이름 출력
for index, column in enumerate(pivot_df_1_filtered.columns):
    print(f"Index {index}: {column}")

# Gather all columns by creating lists for individual columns and ranges of columns
columns_order = (
    [pivot_df_1_filtered.columns[277]] +
    list(pivot_df_1_filtered.columns[6:11]) +
    [pivot_df_1_filtered.columns[134]] +
    [pivot_df_1_filtered.columns[136]] +
    list(pivot_df_1_filtered.columns[138:157]) +
    list(pivot_df_1_filtered.columns[11:131]) +
    list(pivot_df_1_filtered.columns[157:277]) +
    [pivot_df_1_filtered.columns[132]]
)

# Reorder columns in the DataFrame using the specified order
df_ordered = pivot_df_1_filtered[columns_order]

# Display the first few rows of the reordered DataFrame to verify changes
print(df_ordered.head())

# 재배열된 df를 'final_df_reorder.csv' 파일로 저장
df_ordered.to_csv('final_df_reorder.csv', index=False)

# 성공적으로 저장되었음을 알림
print("인코딩 결과가 업데이트된 데이터가 'final_df_reorder.csv' 파일로 저장되었습니다.")

# 파일불러오기
# import pandas as pd
# file_name = '/content/naive.csv' # 파일경로
# df = pd.read_csv(file_name)
# df

