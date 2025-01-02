import React from "react";

const TextInputWidget = ({ label, placeholder, value = "", id = "text-input", onChange }) => {
  const handleChange = (e) => {
    const newValue = e.target.value;
    console.log("[TextInputWidget] Change event:", {
      id,
      oldValue: value,
      newValue: newValue,
      timestamp: new Date().toISOString()
    });

    try {
      onChange?.(newValue);
      console.log("[TextInputWidget] State updated successfully:", {
        id,
        value: newValue
      });
    } catch (error) {
      console.error("[TextInputWidget] Error updating state:", {
        id,
        error: error.message
      });
    }
  };

  return (
    <div>
      <label
        htmlFor={id}
        className="block text-sm font-medium text-gray-900"
      >
        {label}
      </label>
      <div className="mt-2">
        <input
          type="text"
          id={id}
          name={id}
          value={value}
          onChange={handleChange}
          placeholder={placeholder}
          className="block w-full rounded-md bg-white px-3 py-1.5 text-base text-gray-900 outline outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline focus:outline-2 focus:-outline-offset-2 focus:outline-blue-600 sm:text-sm"
        />
      </div>
    </div>
  );
};

export default TextInputWidget;
