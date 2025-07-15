import React from 'react';

interface DatePickerProps {
  selectedYear: number;
  selectedMonth: number;
  onDateChange: (year: number, month: number) => void;
  availableData: Array<{ year: number; month: number; url: string }>;
}

const DatePicker: React.FC<DatePickerProps> = ({
  selectedYear,
  selectedMonth,
  onDateChange,
  availableData
}) => {
  const months = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  const availableYears = Array.from(
    new Set(availableData.map(item => item.year))
  ).sort((a, b) => b - a);

  const availableMonths = availableData
    .filter(item => item.year === selectedYear)
    .map(item => item.month)
    .sort((a, b) => a - b);

  const handleYearChange = (year: number) => {
    // Find the first available month for the selected year
    const firstAvailableMonth = availableData
      .filter(item => item.year === year)
      .map(item => item.month)
      .sort((a, b) => a - b)[0];
    
    if (firstAvailableMonth) {
      onDateChange(year, firstAvailableMonth);
    }
  };

  const handleMonthChange = (month: number) => {
    onDateChange(selectedYear, month);
  };

  return (
    <div className="flex flex-col sm:flex-row gap-4 p-4 bg-white rounded-lg shadow-sm">
      <div className="flex flex-col">
        <label className="text-sm font-medium text-gray-700 mb-1">Year</label>
        <select
          value={selectedYear}
          onChange={(e) => handleYearChange(parseInt(e.target.value))}
          className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          {availableYears.map(year => (
            <option key={year} value={year}>
              {year}
            </option>
          ))}
        </select>
      </div>

      <div className="flex flex-col">
        <label className="text-sm font-medium text-gray-700 mb-1">Month</label>
        <select
          value={selectedMonth}
          onChange={(e) => handleMonthChange(parseInt(e.target.value))}
          className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          {availableMonths.map(month => (
            <option key={month} value={month}>
              {months[month - 1]}
            </option>
          ))}
        </select>
      </div>

      <div className="flex flex-col justify-end">
        <button
          onClick={() => onDateChange(selectedYear, selectedMonth)}
          className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          Update Data
        </button>
      </div>
    </div>
  );
};

export default DatePicker;
