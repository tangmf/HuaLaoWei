import httpx
import os
import asyncio

class OneMapAPISocioeconomicModule:
    def __init__(self):
        self.auth_token = os.getenv("ONEMAP_TOKEN")  # assume you have stored the token

    async def get_socioeconomic_features(self, planning_area: str):
        age_url = f"https://www.onemap.gov.sg/api/public/popapi/getPopulationAgeGroup?planningArea={planning_area}&year=2020&gender=female"
        income_url = f"https://www.onemap.gov.sg/api/public/popapi/getHouseholdMonthlyIncomeWork?planningArea={planning_area}&year=2020"

        headers = {"Authorization": self.auth_token}

        async with httpx.AsyncClient() as client:
            age_task = client.get(age_url, headers=headers)
            income_task = client.get(income_url, headers=headers)
            age_resp, income_resp = await asyncio.gather(age_task, income_task)

        age_data = (await age_resp.json())[0] if age_resp.status == 200 else None
        income_data = (await income_resp.json())[0] if income_resp.status == 200 else None

        if not age_data or not income_data:
            raise ValueError("Failed to fetch socioeconomic data")

        avg_age, total_pop = self._calculate_average_age(age_data)
        avg_income, total_households = self._calculate_average_income(income_data)

        return {
            "averageAge": avg_age,
            "totalPopulation": total_pop,
            "averageIncome": avg_income,
            "totalHouseholds": total_households
        }

    def _calculate_average_age(self, data):
        weighted_sum = total = 0
        for key, count in data.items():
            if key.startswith("age_"):
                range_ = key.replace("age_", "")
                if "_" in range_:
                    min_age, max_age = map(int, range_.split("_"))
                    mid_age = (min_age + max_age) / 2
                else:
                    mid_age = int(range_)
                weighted_sum += mid_age * (count or 0)
                total += (count or 0)
        return (weighted_sum / total if total else None, total)

    def _calculate_average_income(self, data):
        income_bands = [
            ("below_sgd_1000", 0, 999),
            ("sgd_1000_to_1999", 1000, 1999),
            ("sgd_2000_to_2999", 2000, 2999),
            ("sgd_3000_to_3999", 3000, 3999),
            ("sgd_4000_to_4999", 4000, 4999),
            ("sgd_5000_to_5999", 5000, 5999),
            ("sgd_6000_to_6999", 6000, 6999),
            ("sgd_7000_to_7999", 7000, 7999),
            ("sgd_8000_to_8999", 8000, 8999),
            ("sgd_9000_to_9999", 9000, 9999),
            ("sgd_10000_to_10999", 10000, 10999),
            ("sgd_11000_to_11999", 11000, 11999),
            ("sgd_12000_to_12999", 12000, 12999),
            ("sgd_13000_to_13999", 13000, 13999),
            ("sgd_14000_to_14999", 14000, 14999),
            ("sgd_15000_to_17499", 15000, 17499),
            ("sgd_17500_to_19999", 17500, 19999),
            ("sgd_20000_over", 20000, 20000)
        ]
        weighted_sum = total = 0
        for key, min_val, max_val in income_bands:
            count = data.get(key) or 0
            mid = (min_val + max_val) / 2
            weighted_sum += count * mid
            total += count
        return (weighted_sum / total if total else None, total)
