import random
random.seed(42)

class SKU:
    def __init__(self, name, stock, safety_stock, order_qty, avg_daily_demand):
        self.name = name                            # SKU 이름
        self.stock = stock                          # 현재 재고
        self.safety_stock = safety_stock            # 안전 재고
        self.order_qty = order_qty                  # 발주량
        self.backorder = 0                          # 누적 미출고 수량
        self.avg_daily_demand = avg_daily_demand    # 일평균 수요

        self.stock_history = []             # 일자별 재고 기록
        self.order_history = []             # 주문/출고 기록
        self.purchase_history = []          # 발주 기록
        self.pipeline = []                  # 입고 예정 리스트

    def add_order_record(self, day, demand, shipped, unfilled):     # 주문 기록 메서드
        self.order_history.append({
            "day": day,             # 주문 날짜
            "demand": demand,       # 주문 수량
            "shipped": shipped,     # 출고 수량
            "unfilled": unfilled    # 미출고/품절 수량
        })

    def add_purchase_record(self, day, qty, lead_time):    # 발주 기록 메서드
        self.purchase_history.append({
            "day": day,                         # 발주일
            "qty": qty,                         # 발주 수량
            "stock_at_order": self.stock,       # 발주 당시 재고
            "arrival_day": day + lead_time      # 입고 예정일
        })

    def add_pipeline(self, arrival_day, qty):   # 입고 예정 기록 메서드
        self.pipeline.append({
            "arrival_day": arrival_day,     # 입고 예정일
            "qty": qty                      # 입고 수량
        })

    def receive(self, day):     # 입고 메서드
        arrivals = [p for p in self.pipeline if p["arrival_day"] == day]
        for p in arrivals:
            qty = p["qty"]

            # 1. backorder 먼저 처리
            if self.backorder > 0:
                filled = min(qty, self.backorder)
                self.backorder -= filled
                qty -= filled

            # 2. 남은건 재고로
            self.stock += qty

        # 입고된 항목 삭제
        self.pipeline = [p for p in self.pipeline if p["arrival_day"] != day]

    def ship(self, day, demand):    # 출고 메서드
        # 출고 처리
        shipped = min(self.stock, demand)   # 출고량
        unfilled = demand - shipped

        # 재고 차감
        self.stock -= shipped

        # backorder 누적
        self.backorder += unfilled

        # 주문 기록
        self.add_order_record(day, demand, shipped, unfilled)

    def place_order(self, day, lead_time):     # 발주 메서드
        self.add_purchase_record(day, self.order_qty, lead_time)              # 발주 이력 기록
        self.add_pipeline(day + lead_time, self.order_qty)    # 입고 예정 기록

    def has_open_order(self):   # 아직 도착하지 않은 발주 체크
        return bool(self.pipeline)  # 입고 예정이 하나라도 있으면 True

    # 발주 정책
    def policy_sQ(self, today):
        # 리드타임
        lead_time = random.randint(2,8)

        # 재주문점 계산
        ROP = self.avg_daily_demand * lead_time + self.safety_stock

        # 재주문점 이하 & 중복 발주 방지
        if self.stock <= ROP and not self.has_open_order():
            self.place_order(today, lead_time)

    # KPI 계산
    def calculate_kpi(self):
        total_demand = sum(o["demand"] for o in self.order_history)
        total_shipped = sum(o["shipped"] for o in self.order_history)
        total_backorder = sum(o["unfilled"] for o in self.order_history)

        stockout_days = sum(1 for o in self.order_history if o["unfilled"] > 0)
        order_count = len(self.purchase_history)

        avg_stock = sum(self.stock_history) / len(self.stock_history)

        fill_rate = total_shipped / total_demand

        inventory_turnover = total_shipped / avg_stock if avg_stock > 0 else 0

        stock_safety_ratio = avg_stock / self.safety_stock if self.safety_stock > 0 else 0

        return {
            "SKU": self.name,
            "Total Demand": total_demand,
            "Total Shipped": total_shipped,
            "Total Backorder": total_backorder,
            "Stockout Days": stockout_days,
            "Fill Rate": round(fill_rate,2),
            "Order Count": order_count,
            "Average Stock": round(avg_stock, 2),
            "Inventory Turnover": round(inventory_turnover, 2),
            "AvgStock / SafetyStock": round(stock_safety_ratio, 2)
        }
