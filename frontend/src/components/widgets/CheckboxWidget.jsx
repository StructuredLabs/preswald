import React from "react";

const CheckboxWidget = ({ label, checked, description, id, onChange }) => {
  const handleChange = (e) => {
    const newValue = e.target.checked;
    console.log("[CheckboxWidget] Change event:", {
      id,
      oldValue: checked,
      newValue: newValue,
      timestamp: new Date().toISOString()
    });
    
    try {
      onChange?.(newValue);
      console.log("[CheckboxWidget] State updated successfully:", {
        id,
        value: newValue
      });
    } catch (error) {
      console.error("[CheckboxWidget] Error updating state:", {
        id,
        error: error.message
      });
    }
  };

  return (
    <fieldset>
      <legend className="sr-only">{label}</legend>
      <div className="space-y-5">
        <div className="flex gap-3">
          <div className="flex h-6 shrink-0 items-center">
            <div className="group grid size-4 grid-cols-1">
              <input
                id={id}
                name={id}
                type="checkbox"
                checked={checked}
                onChange={handleChange}
                aria-describedby={`${id}-description`}
                className="col-start-1 row-start-1 appearance-none rounded border border-gray-300 bg-white checked:border-blue-600 checked:bg-blue-600 indeterminate:border-blue-600 indeterminate:bg-blue-600 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600 disabled:border-gray-300 disabled:bg-gray-100 disabled:checked:bg-gray-100 forced-colors:appearance-auto"
              />
              <svg
                fill="none"
                viewBox="0 0 14 14"
                className="pointer-events-none col-start-1 row-start-1 size-3.5 self-center justify-self-center stroke-white group-has-[:disabled]:stroke-gray-950/25"
              >
                <path
                  d="M3 8L6 11L11 3.5"
                  strokeWidth={2}
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  className={`opacity-0 ${checked ? "opacity-100" : ""}`}
                />
              </svg>
            </div>
          </div>
          <div className="text-sm/6">
            <label htmlFor={id} className="font-medium text-gray-900">
              {label}
            </label>{" "}
            <span id={`${id}-description`} className="text-gray-500">
              <span className="sr-only">{label} </span>
              {description}
            </span>
          </div>
        </div>
      </div>
    </fieldset>
  );
};

export default CheckboxWidget;
