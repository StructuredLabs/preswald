'use client';

import { CheckIcon } from '@heroicons/react/20/solid';
import { ChevronUpDownIcon } from '@heroicons/react/20/solid';
import { Listbox } from '@headlessui/react';
import React from 'react';

const SelectboxWidget = ({ label, options, value, id, onChange }) => {
  const handleChange = (newValue) => {
    console.log("[SelectboxWidget] Change event:", {
      id,
      oldValue: value,
      newValue: newValue,
      timestamp: new Date().toISOString()
    });

    try {
      onChange?.(newValue);
      console.log("[SelectboxWidget] State updated successfully:", {
        id,
        value: newValue
      });
    } catch (error) {
      console.error("[SelectboxWidget] Error updating state:", {
        id,
        error: error.message
      });
    }
  };

  return (
    <div>
      <Listbox value={value} onChange={handleChange}>
        <Listbox.Label className="block text-sm font-medium text-gray-900">
          {label}
        </Listbox.Label>
        <div className="relative mt-2">
          <Listbox.Button className="grid w-full cursor-default grid-cols-1 rounded-md bg-white py-1.5 pl-3 pr-10 text-left text-gray-900 outline outline-1 -outline-offset-1 outline-gray-300 focus:outline focus:outline-2 focus:-outline-offset-2 focus:outline-blue-600 sm:text-sm">
            <span className="col-start-1 row-start-1 truncate pr-6">{value}</span>
            <ChevronUpDownIcon
              aria-hidden="true"
              className="col-start-1 row-start-1 size-5 self-center justify-self-end text-gray-500 sm:size-4"
            />
          </Listbox.Button>
          <Listbox.Options className="absolute z-10 mt-1 max-h-60 w-full overflow-auto rounded-md bg-white py-1 text-base shadow-lg ring-1 ring-black/5 focus:outline-none sm:text-sm">
            {options.map((option, index) => (
              <Listbox.Option
                key={index}
                value={option}
                className={({ active }) =>
                  `relative cursor-default select-none py-2 pl-3 pr-9 ${
                    active ? 'bg-blue-600 text-white' : 'text-gray-900'
                  }`
                }
              >
                {({ selected, active }) => (
                  <>
                    <span
                      className={`block truncate font-normal ${
                        selected ? 'font-semibold' : ''
                      }`}
                    >
                      {option}
                    </span>
                    {selected ? (
                      <span
                        className={`absolute inset-y-0 right-0 flex items-center pr-4 ${
                          active ? 'text-white' : 'text-blue-600'
                        }`}
                      >
                        <CheckIcon aria-hidden="true" className="size-5" />
                      </span>
                    ) : null}
                  </>
                )}
              </Listbox.Option>
            ))}
          </Listbox.Options>
        </div>
      </Listbox>
    </div>
  );
};

export default SelectboxWidget;
