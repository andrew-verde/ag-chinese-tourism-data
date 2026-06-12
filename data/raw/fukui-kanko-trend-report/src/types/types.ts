export type DataPoint = {
  date: string;
  map_views: number;
  search_views: number;
  directions: number;
  call_clicks: number;
  website_clicks: number;
  total_reviews: number;
  average_rating: number | null;
  review_count_change: number;
  review_count_by_rating_1: number;
  review_count_by_rating_2: number;
  review_count_by_rating_3: number;
  review_count_by_rating_4: number;
  review_count_by_rating_5: number;
};

export type ChartDataItem = {
  date: string;
  map_views: number;
  search_views: number;
  directions: number;
  call_clicks: number;
  website_clicks: number;
  average_rating: number | null;
  review_count_change: number;
  review_count_by_rating_1: number;
  review_count_by_rating_2: number;
  review_count_by_rating_3: number;
  review_count_by_rating_4: number;
  review_count_by_rating_5: number;
};

export type ChartMetric = {
  id: string;
  name: string;
  color: string;
  type?: "line" | "bar";
  stackId?: string;
};

export type TimeUnit = "day" | "week" | "month";

export type DateRangeVariant = "primary" | "comparison";
