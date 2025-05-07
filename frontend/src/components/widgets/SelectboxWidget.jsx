'use client';

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

const SelectboxWidget = ({
  id,
  options = [],
  value,
  onChange,
  placeholder = 'Select an option',
}) => (
  <Select value={value} onValueChange={onChange}>
    <SelectTrigger id={id} className="w-[200px] justify-between" aria-label={placeholder}>
      <SelectValue placeholder={placeholder} />
      <span></span>
    </SelectTrigger>
    <SelectContent className="w-[200px] min-w-[200px]">
      {options.map((option) => (
        <SelectItem key={option} value={option}>
          {option}
        </SelectItem>
      ))}
    </SelectContent>
  </Select>
);

export default SelectboxWidget;
