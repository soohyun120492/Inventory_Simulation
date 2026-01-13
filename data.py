import random
random.seed(42)

# 수요 생성 메서드
def generate_demand(sku_names):
    demand_data = {name: [] for name in sku_names}     # SKU별 demand list

    # SKU별 초기값 세팅
    sku_configs = {
        "A001": {"baseline": 50, "trend": 0.10, "event_days": {120:1.8, 250: 1.5}},
        "A002": {"baseline": 80, "trend": -0.05, "event_days": {90: 2.0, 300: 1.6}},
        "A003": {"baseline": 60, "trend": 0.20, "event_days": {50: 1.8, 200: 2.0}}
    }

    # 월화수목금토일 패턴
    weekday_factor = [0.8,0.9,1.0,1.15,1.25,1.4,1.6]

    for day in range(365):
        weekday = day % 7

        for name in sku_names:
            cfg = sku_configs[name]

            # 구성 요소별 계산
            baseline = cfg["baseline"]
            trend = cfg["trend"] * day
            seasonality = weekday_factor[weekday]

            event_factor = cfg["event_days"].get(day, 1)

            noise = random.gauss(0, baseline * 0.1) # 변동성 10%

            demand = (baseline + trend) * seasonality * event_factor + noise

            # 음수 방지 + 정수화
            demand = max(0, int(demand))

            # 저장
            demand_data[name].append({
                "day": day + 1,
                "demand": demand
            })

    return demand_data

