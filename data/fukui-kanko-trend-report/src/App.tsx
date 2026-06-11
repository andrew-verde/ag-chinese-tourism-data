import { DateRangePicker } from "@/components/parts/date-range-picker";
import { Graph } from "@/components/parts/graph";
import { Header } from "@/components/parts/header";
import { AreaSelector } from "@/components/parts/selector/area-selector";
import { TimeUnitSelector } from "@/components/parts/selector/time-unit-selector";
import { Checkbox } from "@/components/ui/checkbox";
import { useChartSettings } from "@/context/ChartSettingsContext";
import { DownloadCSVButton } from "./components/parts/download-csv-button";

function App() {
  const { isComparison, setIsComparison } = useChartSettings();

  return (
    <div className="flex flex-col min-h-screen items-center w-full p-4">
      <Header />

      <div className="flex flex-col gap-2 w-full">
        <div className="flex flex-col sm:flex-row items-center w-full mt-3">
          <div className="flex-1" />
          <div className="flex flex-row items-center gap-[68px] pl-4">
            <AreaSelector />
            <TimeUnitSelector />
          </div>
          <div className="flex-1 flex flex-row items-center gap-2 pl-4">
            <Checkbox
              id="comparison"
              checked={isComparison}
              onCheckedChange={(checked) => setIsComparison(!!checked)}
              className="
            bg-white 
            border-[#6eba2c] 
            hover:bg-gray-100 
            data-[state=checked]:bg-[#6eba2c]
            data-[state=checked]:border-[#6eba2c]
            data-[state=checked]:text-white"
            />
            <label htmlFor="comparison">2期間比較</label>
          </div>
        </div>
        <div className="flex flex-col md:flex-row w-full gap-4 justify-center">
          <div className="w-full min-w-0 flex flex-col items-center">
            <div className="flex flex-row items-end w-full">
              <div className="flex-1" />
              <div className="flex flex-row items-end pl-4">
                <DateRangePicker variant="primary" />
              </div>
              <div className="flex-1 flex flex-row items-end gap-2 pl-4">
                <DownloadCSVButton variant="primary" />
              </div>
            </div>
            <div className="flex flex-row gap-4 w-full">
              <Graph variant="primary" />
            </div>
          </div>
          {isComparison && (
            <div className="w-full min-w-0 flex flex-col items-center">
              <div className="flex flex-row items-end w-full">
                <div className="flex-1" />
                <div className="flex flex-row items-end pl-4">
                  <DateRangePicker variant="comparison" />
                </div>
                <div className="flex-1 flex flex-row items-end gap-2 pl-4">
                  <DownloadCSVButton variant="comparison" />
                </div>
              </div>
              <div className="flex flex-row gap-4 w-full">
                <Graph variant="comparison" />
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
