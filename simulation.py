from data import generate_demand
from sku import SKU
import matplotlib.pyplot as plt

# SKU 생성
items = [SKU("A001", stock=411, safety_stock=71, order_qty=595, avg_daily_demand=85),
        SKU("A002", stock=498, safety_stock=138, order_qty=450, avg_daily_demand=90),
        SKU("A003", stock=621, safety_stock=141, order_qty=600, avg_daily_demand=120)
]

SKU_NAMES = ["A001", "A002", "A003"]

demand_data = generate_demand(SKU_NAMES)

for day in range(1, 366):
    for sku in items:
        # 입고
        sku.receive(day)

        # 주문
        today_demand = demand_data[sku.name][day - 1]["demand"]
        sku.ship(day, today_demand)

        # 발주 정책
        sku.policy_sQ(day)

        # 재고 기록
        sku.stock_history.append(sku.stock)

# KPI 저장
results = {sku.name: sku.calculate_kpi() for sku in items}

def monthly_summary(sku):
    monthly = {m: {"demand": 0, "shipped": 0, "stock": []} for m in range(1, 13)}

    for o in sku.order_history:
        month = min((o["day"] - 1) // 30 + 1, 12)  # 한 달을 30일로 가정
        monthly[month]["demand"] += o["demand"]
        monthly[month]["shipped"] += o["shipped"]

    for day, stock in enumerate(sku.stock_history, start=1):
        month = min((day - 1) // 30 + 1, 12)
        monthly[month]["stock"].append(stock)

    return monthly

# KPI 요약
for sku_name, kpi in results.items():
    print(f"[SKU: {sku_name}]")
    for key, value in kpi.items():
        print(f"{key:25}: {value}")
    print("-" * 40)

for sku in items:
    kpi = results[sku.name]

    # 총수요, 총출고 그래프
    plt.figure(figsize=(6, 4))
    plt.bar(["Demand", "Shipped"],[kpi["Total Demand"], kpi["Total Shipped"]])
    plt.title(f"Total Volume - {sku.name}")
    plt.ylabel("Quantity")
    plt.show()

    # 월별 주문・출고・평균재고 그래프
    monthly = monthly_summary(sku)

    months = list(monthly.keys())
    monthly_demand = [monthly[m]["demand"] for m in months]
    monthly_shipped = [monthly[m]["shipped"] for m in months]
    monthly_stock = [sum(monthly[m]["stock"]) / len(monthly[m]["stock"]) for m in months]

    plt.figure(figsize=(8, 4))
    plt.plot(months, monthly_demand, label="Order (Demand)")
    plt.plot(months, monthly_shipped, label="Shipped")
    plt.plot(months, monthly_stock, label="Avg Stock")

    plt.title(f"Monthly Trend - {sku.name}")
    plt.xlabel("Month")
    plt.ylabel("Quantity")
    plt.legend()
    plt.show()