import type { TimeUnit } from "@/types/types";
import dayjs from "dayjs";
import {
  createContext,
  useContext,
  useState,
  type Dispatch,
  type ReactNode,
  type SetStateAction,
} from "react";
import type { DateRange } from "react-day-picker";

interface ChartSettingsContextType {
  selectedAreaId: string;
  setSelectedAreaId: (id: string) => void;
  areaFilenames: Record<number, string>;
  setAreaFilenames: (filenames: Record<number, string>) => void;
  timeUnit: TimeUnit;
  setTimeUnit: (timeUnit: TimeUnit) => void;
  isComparison: boolean;
  setIsComparison: (isComparison: boolean) => void;
  dateRange: DateRange | undefined;
  setDateRange: Dispatch<SetStateAction<DateRange | undefined>>;
  comparisonRange: DateRange | undefined;
  setComparisonRange: Dispatch<SetStateAction<DateRange | undefined>>;
  availableRange: { min: Date | null; max: Date | null };
  setAvailableRange: Dispatch<
    SetStateAction<{ min: Date | null; max: Date | null }>
  >;
}

const ChartSettingsContext = createContext<
  ChartSettingsContextType | undefined
>(undefined);

export const ChartSettingsProvider = ({
  children,
}: {
  children: ReactNode;
}) => {
  const [selectedAreaId, setSelectedAreaId] = useState<string>("total");
  const [areaFilenames, setAreaFilenames] = useState<Record<number, string>>(
    {},
  );
  const [timeUnit, setTimeUnit] = useState<TimeUnit>("day");
  const [isComparison, setIsComparison] = useState(false);
  const [dateRange, setDateRange] = useState<DateRange | undefined>({
    from: dayjs().subtract(5, "day").subtract(3, "month").toDate(),
    to: dayjs().subtract(5, "day").toDate(),
  });
  const [comparisonRange, setComparisonRange] = useState<DateRange | undefined>(
    {
      from: dayjs().subtract(5, "day").subtract(3, "month").toDate(),
      to: dayjs().subtract(5, "day").toDate(),
    },
  );
  const [availableRange, setAvailableRange] = useState<{
    min: Date | null;
    max: Date | null;
  }>({
    min: dayjs("2024-01-01").toDate(),
    max: dayjs().subtract(5, "day").toDate(),
  });

  return (
    <ChartSettingsContext.Provider
      value={{
        selectedAreaId,
        setSelectedAreaId,
        areaFilenames,
        setAreaFilenames,
        timeUnit,
        setTimeUnit,
        isComparison,
        setIsComparison,
        dateRange,
        setDateRange,
        comparisonRange,
        setComparisonRange,
        availableRange,
        setAvailableRange,
      }}
    >
      {children}
    </ChartSettingsContext.Provider>
  );
};

export const useChartSettings = () => {
  const context = useContext(ChartSettingsContext);

  if (context === undefined) {
    throw new Error(
      "useChartSettings は ChartSettingsProvider の中で使用してください",
    );
  }

  return context;
};
