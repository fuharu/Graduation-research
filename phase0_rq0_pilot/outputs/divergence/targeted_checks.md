# 特定観点の機械照会（該当サンプル番号のみ）

判断・解釈は行わない。各項目について該当サンプル番号を列挙するのみ。

## task01

- 1. pd.read_csv に header= または names= を渡している: 該当 0/30 []
- 2. pd.to_datetime に format= または errors= を渡している: 該当 0/30 []
- 3. dropna/fillna/isna/notna/astype(float)/pd.to_numeric のいずれかを使っている: 該当 0/30 []

## task02

- 4. requests.get に timeout= を渡している: 該当 0/30 []
- 5. 'daily'/'time' キーの存在を事前確認している（in / .get() / except KeyError）: 該当 1/30 [15]

## task03

- 6. mkdir/shutil.move の前に対象パスがファイルとして存在しないか確認している（is_file / os.path.isfile）: 該当 21/30 [2,4,5,6,8,9,10,11,13,14,15,16,17,18,20,21,24,25,27,28,30]
- 7. iterdir/glob の結果を is_file() で絞り込んでいる: 該当 22/30 [2,3,4,5,6,8,9,10,11,13,14,15,16,17,18,20,21,24,25,27,28,30]
