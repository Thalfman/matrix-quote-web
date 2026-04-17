import {
  CartesianGrid, ResponsiveContainer, Scatter, ScatterChart, Tooltip, XAxis, YAxis, ZAxis,
} from "recharts";
import { CalibrationPoint } from "@/api/types";

export function CalibrationScatter({ points }: { points: CalibrationPoint[] }) {
  if (points.length === 0) {
    return (
      <div className="card p-6 text-sm text-muted">
        Calibration data isn't available yet. Persist predicted vs actual points during training to populate this chart.
      </div>
    );
  }
  const inside = points.filter((p) => p.inside_band).map((p) => ({
    mid: (p.predicted_low + p.predicted_high) / 2,
    actual: p.actual,
  }));
  const outside = points.filter((p) => !p.inside_band).map((p) => ({
    mid: (p.predicted_low + p.predicted_high) / 2,
    actual: p.actual,
  }));

  return (
    <div className="card p-4 h-80">
      <div className="text-xs tracking-widest text-muted uppercase mb-2">Confidence calibration</div>
      <ResponsiveContainer width="100%" height="100%">
        <ScatterChart>
          <CartesianGrid />
          <XAxis type="number" dataKey="mid" name="Predicted (mid)" tick={{ fontSize: 11 }} />
          <YAxis type="number" dataKey="actual" name="Actual"       tick={{ fontSize: 11 }} />
          <ZAxis range={[50, 50]} />
          <Tooltip cursor={{ strokeDasharray: "3 3" }} />
          <Scatter name="Inside 90% band"   data={inside}  fill="#0F766E" />
          <Scatter name="Outside 90% band"  data={outside} fill="#B45309" />
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
}
