import { useEffect, useState } from "react";
import { PieChart } from "@mui/x-charts/PieChart";

export default function Piechart({ Data, Height, t }) {
  const [dimensions, setDimensions] = useState({
    width: window.innerWidth > 768 ? t || 1000 : window.innerWidth - 20,
    height: Height || (window.innerWidth > 768 ? 300 : 250),
  });

  useEffect(() => {
    const handleResize = () => {
      setDimensions({
        width: window.innerWidth > 768 ? t || 1000 : window.innerWidth - 20,
        height: Height || (window.innerWidth > 768 ? 300 : 250),
      });
    };

    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, [Height, t]);

  const data = [
    { id: 0, value: Data["manufacturing_cost"], label: "Manufacturing Cost" },
    { id: 1, value: Data["marketing_expenses"], label: "Marketing Expenses" },
    { id: 2, value: Data["salary_expenses"], label: "Salary Expenses" },
    { id: 3, value: Data["other_expenses"], label: "Other Expenses" },
    { id: 4, value: Data["tax"], label: "Tax" },
    { id: 5, value: Data["net_profit"], label: "Net Profit" },
  ];

  // Calculate the total value
  const totalValue = data.reduce((sum, item) => {
    const value = parseInt(item.value);
    // Only add valid numbers (if parseInt returns NaN, it won't add it)
    return !isNaN(value) ? sum + value : sum;
  }, 0);

  // Convert values to percentages and update labels
  const percentageData = data.map((item) => ({
    ...item,
    label: `${item.label} (${((parseInt(item.value) / totalValue) * 100).toFixed(2)}%)`, // Include percentage in the label
    value: parseInt(item.value), // Keep original value for proper chart display
  }));

  const valueFormatter = (item) => `${item.value}`;

  return (
    <PieChart
      series={[
        {
          data: percentageData,
          highlightScope: { fade: "global", highlight: "item" },
          faded: { innerRadius: 30, additionalRadius: -30, color: "gray" },
          valueFormatter,
        },
      ]}
      height={dimensions.height}
    />
  );
}
