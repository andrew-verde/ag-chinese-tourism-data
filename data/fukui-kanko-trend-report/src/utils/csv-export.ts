import type { ChartDataItem, TimeUnit } from "@/types/types";
import type { Dayjs } from "dayjs";

export const HEADER_MAP = {
  date: "日付",
  map_views: "地図検索",
  search_views: "Web検索",
  directions: "ルート検索",
  call_clicks: "通話",
  website_clicks: "ウェブサイトクリック",
  review_count_change: "レビュー投稿数",
  review_count_by_rating_5: "星5_レビュー数",
  review_count_by_rating_4: "星4_レビュー数",
  review_count_by_rating_3: "星3_レビュー数",
  review_count_by_rating_2: "星2_レビュー数",
  review_count_by_rating_1: "星1_レビュー数",
  average_rating: "平均評点",
} as const;

export const DATE_FORMATS = {
  month: "YYYYMM",
  week: "YYYYMMDD[週]",
  day: "YYYYMMDD",
} as const;

export function generateCSVContent(data: ChartDataItem[]): string {
  const headers = Object.values(HEADER_MAP).join(",");
  const keys = Object.keys(HEADER_MAP) as (keyof typeof HEADER_MAP)[];

  const rows = data.map((item) =>
    keys.map((key) => `"${item[key] ?? ""}"`).join(","),
  );

  return [headers, ...rows].join("\n");
}

export function generateCSVFileName({
  areaFilenames,
  selectedAreaId,
  timeUnit,
  start,
  end,
}: {
  areaFilenames: Record<number, string>;
  selectedAreaId: string;
  timeUnit: TimeUnit;
  start: Dayjs;
  end: Dayjs;
}): string {
  const name =
    selectedAreaId === "total"
      ? "全域"
      : Object.values(areaFilenames)[0]?.split("_")[1] || "不明";

  const formatStr = DATE_FORMATS[timeUnit];
  const dateRangeStr = `${start.format(formatStr)}-${end.format(formatStr)}`;

  return `トレンドレポート_${name}_${dateRangeStr}.csv`;
}
