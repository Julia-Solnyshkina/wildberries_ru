import pandas as pd


class WildberriesRuPipeline:
    def process_item(self, item, spider):
        return item


class DualExcelPipeline:

    def open_spider(self, spider):
        self.items = []

    def process_item(self, item, spider):
        self.items.append(dict(item))

        # каждые 100 товаров сохраняем
        if len(self.items) % 100 == 0:
            self.save_files()

        return item

    def close_spider(self, spider):
        self.save_files()

    def save_files(self):
        if not self.items:
            return

        df = pd.DataFrame(self.items)
        df = df.fillna("")

        df["price"] = pd.to_numeric(df.get("price"), errors="coerce")
        df["rating"] = pd.to_numeric(df.get("rating"), errors="coerce")

        if "country" in df.columns:
            df["country"] = df["country"].astype(str).str.strip()
        else:
            df["country"] = ""

        # полный файл
        df.to_excel("all_items.xlsx", index=False)

        # фильтр
        filtered = df[
            (df["rating"] >= 4.5) &
            (df["price"] <= 10000) &
            (df["country"] == "Россия")
        ]

        filtered.to_excel("filtered_items.xlsx", index=False)