#!/usr/bin/env python3
"""
从 HAN.md, HPH.md, SGN.md, all.md 提取城市对的结构化信息
生成 Excel 文件，包含完整的航班信息
"""

import json
from pathlib import Path
from collections import defaultdict
import pandas as pd
import re

def load_json(file_path):
    """加载单个 JSON 数据"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_multiple_jsons(file_path):
    """加载包含多个 JSON 对象的文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 分割 JSON 对象
    objects = []
    decoder = json.JSONDecoder()
    pos = 0
    while pos < len(content):
        # 跳过空白
        while pos < len(content) and content[pos].isspace():
            pos += 1
        if pos >= len(content):
            break

        try:
            obj, end = decoder.raw_decode(content, pos)
            objects.append(obj)
            pos = end
        except json.JSONDecodeError:
            break

    return objects

def normalize_aircraft(code):
    """标准化机型代码"""
    mapping = {
        'A21N': 'A321neo',
        'A321': 'A321ceo',
        'A320': 'A320ceo',
        'A321neo': 'A321neo',
        'A320neo': 'A320neo',
        'A330': 'A330',
        'A333': 'A330-300',
        '332': 'A330-200',
        '333': 'A330-300',
        '321': 'A321ceo',
        '320': 'A320ceo',
        'AJ27': 'ATR72-500',
        'C09': 'Cessna 208B',
        'GLEX': 'Gulfstream G650'
    }
    return mapping.get(code, code)

def process_json_data(data, hub_code, hub_city, hub_lat, hub_lon, hub_icao):
    """处理单个 JSON 数据，返回所有航线数据"""
    routes = []

    # 处理到达航班 - 这里的到达是指飞向枢纽
    arrivals = data.get('arrivals', {})
    for country, country_data in arrivals.items():
        airports = country_data.get('airports', {})
        for airport_code, airport_data in airports.items():
            # 收集所有航班号和机型
            flight_info = []
            aircraft_types = set()
            flights = airport_data.get('flights', {})
            for flight_num, flight_data in flights.items():
                for date, detail in flight_data.get('utc', {}).items():
                    ac = detail.get('aircraft', '')
                    if ac:
                        aircraft_types.add(normalize_aircraft(ac))
                # 获取该航班的任何一天的时间作为示例
                sample_date = list(flight_data.get('utc', {}).values())[0] if flight_data.get('utc') else {}
                flight_info.append({
                    'flight_number': flight_num,
                    'sample_time': sample_date.get('time', ''),
                    'sample_aircraft': normalize_aircraft(sample_date.get('aircraft', ''))
                })

            routes.append({
                '出发城市': airport_data.get('city', ''),
                '出发城市代码': airport_code,
                '出发城市国家': country,
                '出发城市ICAO': airport_data.get('icao', ''),
                '出发纬度': airport_data.get('position', {}).get('lat', ''),
                '出发经度': airport_data.get('position', {}).get('lon', ''),
                '到达城市': hub_city,
                '到达城市代码': hub_code,
                '到达城市国家': 'Vietnam',
                '到达城市ICAO': hub_icao,
                '到达纬度': hub_lat,
                '到达经度': hub_lon,
                '距离_km': round(airport_data.get('distance', 0) / 1000, 1),
                '机型列表': ', '.join(sorted(list(aircraft_types))),
                '航班数': len(flights),
                '航班号列表': ', '.join([f['flight_number'] for f in flight_info]),
                '航线方向': '到达枢纽'
            })

    # 处理出发航班 - 这里的出发是指从枢纽飞出
    departures = data.get('departures', {})
    for country, country_data in departures.items():
        airports = country_data.get('airports', {})
        for airport_code, airport_data in airports.items():
            # 收集所有航班号和机型
            flight_info = []
            aircraft_types = set()
            flights = airport_data.get('flights', {})
            for flight_num, flight_data in flights.items():
                for date, detail in flight_data.get('utc', {}).items():
                    ac = detail.get('aircraft', '')
                    if ac:
                        aircraft_types.add(normalize_aircraft(ac))
                sample_date = list(flight_data.get('utc', {}).values())[0] if flight_data.get('utc') else {}
                flight_info.append({
                    'flight_number': flight_num,
                    'sample_time': sample_date.get('time', ''),
                    'sample_aircraft': normalize_aircraft(sample_date.get('aircraft', ''))
                })

            routes.append({
                '出发城市': hub_city,
                '出发城市代码': hub_code,
                '出发城市国家': 'Vietnam',
                '出发城市ICAO': hub_icao,
                '出发纬度': hub_lat,
                '出发经度': hub_lon,
                '到达城市': airport_data.get('city', ''),
                '到达城市代码': airport_code,
                '到达城市国家': country,
                '到达城市ICAO': airport_data.get('icao', ''),
                '到达纬度': airport_data.get('position', {}).get('lat', ''),
                '到达经度': airport_data.get('position', {}).get('lon', ''),
                '距离_km': round(airport_data.get('distance', 0) / 1000, 1),
                '机型列表': ', '.join(sorted(list(aircraft_types))),
                '航班数': len(flights),
                '航班号列表': ', '.join([f['flight_number'] for f in flight_info]),
                '航线方向': '离开枢纽'
            })

    return routes

def detect_hub_from_data(data):
    """根据数据内容推断枢纽机场"""
    departures = data.get('departures', {})
    arrivals = data.get('arrivals', {})

    # 检查 departures 中是否有国际航班
    intl_countries = [k for k in departures.keys() if k != 'Vietnam']

    if not intl_countries:
        # 只有越南国内航班，检查 arrivals
        arrival_countries = list(arrivals.keys())
        if 'Thailand' in arrival_countries or 'Singapore' in arrival_countries:
            return 'SGN', 'Ho Chi Minh City', '10.818790', '106.651802', 'VVTS'

        # 检查到 SGN 的距离来判断
        if 'Vietnam' in arrivals:
            sgn_data = arrivals['Vietnam'].get('airports', {}).get('SGN', {})
            distance = sgn_data.get('distance', 0) / 1000
            if 990 < distance < 1050:
                return 'DAD', 'Da Nang', '16.043909', '108.199303', 'VVDN'
            elif 1100 < distance < 1200:
                return 'HAN', 'Hanoi', '21.221200', '105.807200', 'VVCT'
            elif 600 < distance < 650:
                return 'HUI', 'Hue', '16.401489', '107.702599', 'VVPC'

    else:
        # 有国际航班
        if 'South Korea' in intl_countries:
            return 'HAN', 'Hanoi', '21.221200', '105.807200', 'VVCT'
        if 'Australia' in intl_countries:
            return 'SGN', 'Ho Chi Minh City', '10.818790', '106.651802', 'VVTS'

    return 'UNKNOWN', 'Unknown', '', '', ''

def main():
    # 定义枢纽机场信息
    hubs = {
        'HAN': {'city': 'Hanoi', 'lat': '21.221200', 'lon': '105.807200', 'icao': 'VVCT'},
        'HPH': {'city': 'Haiphong', 'lat': '20.812700', 'lon': '106.622406', 'icao': 'VVHH'},
        'SGN': {'city': 'Ho Chi Minh City', 'lat': '10.818790', 'lon': '106.651802', 'icao': 'VVTS'},
        'DAD': {'city': 'Da Nang', 'lat': '16.043909', 'lon': '108.199303', 'icao': 'VVDN'},
        'HUI': {'city': 'Hue', 'lat': '16.401489', 'lon': '107.702599', 'icao': 'VVPC'},
        'CXR': {'city': 'Nha Trang', 'lat': '11.989623', 'lon': '109.219353', 'icao': 'VVCR'}
    }

    all_routes = []

    # 处理 HAN, HPH, SGN 文件
    for hub_code in ['HAN', 'HPH', 'SGN']:
        file_path = Path(f'd:/Code/V_Fin_Sim/{hub_code}.md')
        if file_path.exists():
            hub_info = hubs[hub_code]
            data = load_json(file_path)
            routes = process_json_data(
                data,
                hub_code,
                hub_info['city'],
                hub_info['lat'],
                hub_info['lon'],
                hub_info['icao']
            )
            all_routes.extend(routes)

    # 处理 all.md (包含多个 JSON 对象)
    all_file = Path('d:/Code/V_Fin_Sim/all.md')
    if all_file.exists():
        data_list = load_multiple_jsons(all_file)
        print(f"all.md 包含 {len(data_list)} 个 JSON 对象")

        for idx, data in enumerate(data_list):
            hub_code, hub_city, hub_lat, hub_lon, hub_icao = detect_hub_from_data(data)

            if hub_code == 'UNKNOWN':
                # 使用默认的 DAD
                hub_code = 'DAD'
                hub_info = hubs.get(hub_code, hubs['DAD'])
                hub_city = hub_info['city']
                hub_lat = hub_info['lat']
                hub_lon = hub_info['lon']
                hub_icao = hub_info['icao']
            else:
                hub_info = hubs.get(hub_code, {})
                if hub_info:
                    hub_lat = hub_info.get('lat', hub_lat)
                    hub_lon = hub_info.get('lon', hub_lon)
                    hub_icao = hub_info.get('icao', hub_icao)

            routes = process_json_data(
                data,
                hub_code,
                hub_city,
                hub_lat,
                hub_lon,
                hub_icao
            )
            all_routes.extend(routes)
            print(f"  - 处理对象 {idx+1}: {hub_code} ({hub_city}), {len(routes)} 条航线")

    # 创建 DataFrame
    df = pd.DataFrame(all_routes)

    # 去重（按出发-到达城市代码和航班号）
    df = df.drop_duplicates()

    # 按出发城市、到达城市排序
    df = df.sort_values(['出发城市代码', '到达城市代码']).reset_index(drop=True)

    # 输出到 Excel
    output_file = Path('d:/Code/V_Fin_Sim/city_pairs_all.xlsx')

    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # 主要航线表
        df.to_excel(writer, sheet_name='所有航线', index=False)

        # 城市对汇总表（双向合并）
        city_pairs = []
        seen_pairs = set()

        for _, row in df.iterrows():
            # 创建城市对键（不论方向）
            dep = row['出发城市代码']
            arr = row['到达城市代码']
            pair_key = tuple(sorted([dep, arr]))

            if pair_key not in seen_pairs:
                seen_pairs.add(pair_key)

                # 查找反向航线获取机型信息
                reverse_route = df[
                    (df['出发城市代码'] == arr) &
                    (df['到达城市代码'] == dep)
                ]

                # 合并机型
                aircraft_set = set()
                if row['机型列表']:
                    aircraft_set.update(row['机型列表'].split(', '))
                if not reverse_route.empty and reverse_route.iloc[0]['机型列表']:
                    aircraft_set.update(reverse_route.iloc[0]['机型列表'].split(', '))

                # 合并航班号
                flights_set = set()
                if row['航班号列表']:
                    flights_set.update(row['航班号列表'].split(', '))
                if not reverse_route.empty and reverse_route.iloc[0]['航班号列表']:
                    flights_set.update(reverse_route.iloc[0]['航班号列表'].split(', '))

                city_pairs.append({
                    '城市对': f"{dep}-{arr}",
                    '出发城市': row['出发城市'],
                    '到达城市': row['到达城市'],
                    '出发城市代码': row['出发城市代码'],
                    '到达城市代码': row['到达城市代码'],
                    '出发城市国家': row['出发城市国家'],
                    '到达城市国家': row['到达城市国家'],
                    '出发ICAO': row['出发城市ICAO'],
                    '到达ICAO': row['到达城市ICAO'],
                    '出发纬度': row['出发纬度'],
                    '出发经度': row['出发经度'],
                    '到达纬度': row['到达纬度'],
                    '到达经度': row['到达经度'],
                    '距离_km': row['距离_km'],
                    '机型列表': ', '.join(sorted(aircraft_set)),
                    '航班号列表': ', '.join(sorted(flights_set)),
                    '航线类型': '国际' if row['出发城市国家'] != row['到达城市国家'] else '国内',
                    '是否双向': '是' if not reverse_route.empty else '否'
                })

        df_pairs = pd.DataFrame(city_pairs)
        df_pairs = df_pairs.sort_values(['城市对']).reset_index(drop=True)
        df_pairs.to_excel(writer, sheet_name='城市对汇总', index=False)

        # 按枢纽统计
        hub_stats = []
        processed_hubs = set()

        for hub_code in df['出发城市代码'].unique():
            if hub_code in processed_hubs:
                continue

            hub_routes = df[
                (df['出发城市代码'] == hub_code) |
                (df['到达城市代码'] == hub_code)
            ]

            # 获取枢纽信息
            hub_row = df[df['出发城市代码'] == hub_code].iloc[0] if len(df[df['出发城市代码'] == hub_code]) > 0 else df[df['到达城市代码'] == hub_code].iloc[0]
            hub_name = hub_row['出发城市'] if len(df[df['出发城市代码'] == hub_code]) > 0 else hub_row['到达城市']

            # 统计国家
            countries = set()
            countries.update(df[df['出发城市代码'] == hub_code]['到达城市国家'])
            countries.update(df[df['到达城市代码'] == hub_code]['出发城市国家'])

            # 统计机型
            aircraft = set()
            for _, row in hub_routes.iterrows():
                if row['机型列表']:
                    aircraft.update(row['机型列表'].split(', '))

            hub_stats.append({
                '枢纽代码': hub_code,
                '枢纽城市': hub_name,
                '航线数': len(hub_routes),
                '通达国家数': len(countries),
                '使用机型数': len(aircraft),
                '机型列表': ', '.join(sorted(aircraft))
            })
            processed_hubs.add(hub_code)

        df_stats = pd.DataFrame(hub_stats)
        df_stats = df_stats.sort_values(['枢纽代码']).reset_index(drop=True)
        df_stats.to_excel(writer, sheet_name='枢纽统计', index=False)

        # 双向合并明细表
        bidirectional = []
        for pair_key in seen_pairs:
            dep_code, arr_code = pair_key

            # 获取正向航线
            forward = df[(df['出发城市代码'] == dep_code) & (df['到达城市代码'] == arr_code)]
            # 获取反向航线
            reverse = df[(df['出发城市代码'] == arr_code) & (df['到达城市代码'] == dep_code)]

            if not forward.empty and not reverse.empty:
                # 双向航线
                forward_row = forward.iloc[0]
                reverse_row = reverse.iloc[0]

                # 合并航班号（去重）
                forward_flights = set()
                reverse_flights = set()
                for _, r in forward.iterrows():
                    if r['航班号列表']:
                        forward_flights.update(r['航班号列表'].split(', '))
                for _, r in reverse.iterrows():
                    if r['航班号列表']:
                        reverse_flights.update(r['航班号列表'].split(', '))

                # 合并机型
                forward_aircraft = set()
                reverse_aircraft = set()
                for _, r in forward.iterrows():
                    if r['机型列表']:
                        forward_aircraft.update(r['机型列表'].split(', '))
                for _, r in reverse.iterrows():
                    if r['机型列表']:
                        reverse_aircraft.update(r['机型列表'].split(', '))

                bidirectional.append({
                    '城市对': f"{dep_code}-{arr_code}",
                    '出发城市': forward_row['出发城市'],
                    '到达城市': forward_row['到达城市'],
                    '出发代码': dep_code,
                    '到达代码': arr_code,
                    '出发国家': forward_row['出发城市国家'],
                    '到达国家': forward_row['到达城市国家'],
                    '出发ICAO': forward_row['出发城市ICAO'],
                    '到达ICAO': forward_row['到达城市ICAO'],
                    '出发纬度': forward_row['出发纬度'],
                    '出发经度': forward_row['出发经度'],
                    '到达纬度': forward_row['到达纬度'],
                    '到达经度': forward_row['到达经度'],
                    '距离_km': forward_row['距离_km'],
                    '去程航班号': ', '.join(sorted(forward_flights)),
                    '回程航班号': ', '.join(sorted(reverse_flights)),
                    '去程机型': ', '.join(sorted(forward_aircraft)),
                    '回程机型': ', '.join(sorted(reverse_aircraft)),
                    '航线类型': '国际' if forward_row['出发城市国家'] != forward_row['到达城市国家'] else '国内'
                })

        df_bidirectional = pd.DataFrame(bidirectional)
        df_bidirectional = df_bidirectional.sort_values(['城市对']).reset_index(drop=True)
        df_bidirectional.to_excel(writer, sheet_name='双向航线明细', index=False)

    print(f"\nExcel 文件已生成: {output_file}")
    print(f"  - 所有航线: {len(df)} 条")
    print(f"  - 城市对汇总: {len(df_pairs)} 个")
    print(f"\n航线按枢纽分布:")
    print(df_stats.to_string(index=False))

if __name__ == '__main__':
    main()
