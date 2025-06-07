import React from "react";
import { PieChart, Pie, Cell, Tooltip, Legend } from "recharts";

const COLORS = ["#8884d8", "#82ca9d", "#ffc658", "#ff8042", "#a4de6c"];

export default function ResultsChart({ data }) {
  if (!data || !Array.isArray(data) || data.length === 0) {
    return <p>No chart data to display.</p>;
  }

  // Group by condition
  const conditionCounts = data.reduce((acc, patient) => {
    const cond = patient.condition;
    acc[cond] = (acc[cond] || 0) + 1;
    return acc;
  }, {});

  const chartData = Object.entries(conditionCounts).map(([key, value]) => ({
    name: key,
    value,
  }));

  return (
    <div className="mt-6">
      <h2>Conditions Chart</h2>
      <PieChart width={400} height={300}>
        <Pie data={chartData} dataKey="value" nameKey="name" outerRadius={100}>
          {chartData.map((entry, idx) => (
            <Cell key={`cell-${idx}`} fill={COLORS[idx % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip />
        <Legend />
      </PieChart>
    </div>
  );
}
