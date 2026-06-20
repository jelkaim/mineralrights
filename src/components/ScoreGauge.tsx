interface ScoreGaugeProps {
  score: number;
}

export default function ScoreGauge({ score }: ScoreGaugeProps) {
  // Calculate color based on score
  let color = 'text-green-500';
  let strokeColor = '#22c55e'; // green-500

  if (score < 70) {
    color = 'text-red-500';
    strokeColor = '#ef4444'; // red-500
  } else if (score < 90) {
    color = 'text-yellow-500';
    strokeColor = '#eab308'; // yellow-500
  }

  // Circle properties
  const radius = 60;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <div className="relative flex flex-col items-center justify-center">
      <svg className="w-40 h-40 transform -rotate-90">
        {/* Background Circle */}
        <circle
          className="text-slate-200"
          strokeWidth="12"
          stroke="currentColor"
          fill="transparent"
          r={radius}
          cx="80"
          cy="80"
        />
        {/* Progress Circle */}
        <circle
          className={color}
          strokeWidth="12"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          stroke={strokeColor}
          fill="transparent"
          r={radius}
          cx="80"
          cy="80"
          style={{ transition: 'stroke-dashoffset 1s ease-in-out' }}
        />
      </svg>
      <div className="absolute flex flex-col items-center justify-center">
        <span className="text-4xl font-bold text-slate-900">{score}</span>
        <span className="text-xs text-slate-500 uppercase tracking-wider font-semibold">Score</span>
      </div>
    </div>
  );
}
