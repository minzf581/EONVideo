interface MetricCardProps {
  label: string;
  value: string | number;
  tone?: "default" | "green" | "blue" | "amber";
}

const toneClass = {
  default: "border-gray-200 bg-white",
  green: "border-teal-100 bg-teal-50",
  blue: "border-blue-100 bg-blue-50",
  amber: "border-amber-100 bg-amber-50",
};

export function MetricCard({ label, value, tone = "default" }: MetricCardProps) {
  return (
    <div className={`rounded-md border p-4 ${toneClass[tone]}`}>
      <div className="text-xs text-gray-500">{label}</div>
      <div className="mt-2 text-2xl font-semibold text-gray-950">{value}</div>
    </div>
  );
}

