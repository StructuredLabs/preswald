import AlertWidget from "./widgets/AlertWidget";
import ButtonWidget from "./widgets/ButtonWidget";
import CheckboxWidget from "./widgets/CheckboxWidget";
import ConnectionInterfaceWidget from "./widgets/ConnectionInterfaceWidget";
import DataVisualizationWidget from "./widgets/DataVisualizationWidget";
import ImageWidget from "./widgets/ImageWidget";
import MarkdownRendererWidget from "./widgets/MarkdownRendererWidget";
import ProgressWidget from "./widgets/ProgressWidget";
import React from "react";
import SelectboxWidget from "./widgets/SelectboxWidget";
import SliderWidget from "./widgets/SliderWidget";
import SpinnerWidget from "./widgets/SpinnerWidget";
import TableViewerWidget from "./widgets/TableViewerWidget";
import TextInputWidget from "./widgets/TextInputWidget";
import UnknownWidget from "./widgets/UnknownWidget";

const DynamicComponents = ({ components, onComponentUpdate }) => {
  const handleUpdate = (componentId, value) => {
    console.log(`[DynamicComponents] Component update triggered:`, {
      componentId,
      value,
      timestamp: new Date().toISOString()
    });

    // Log that we're initiating a script rerun
    console.log(`[DynamicComponents] Initiating script rerun for component:`, {
      componentId,
      value,
      timestamp: new Date().toISOString()
    });

    onComponentUpdate(componentId, value);
  };

  const renderComponent = (component, index) => {
    const componentId = component.id || `component-${index}`;
    const commonProps = {
      key: componentId,
      id: componentId,
      ...component,
    };

    try {
      switch (component.type) {
        case "button":
          return (
            <ButtonWidget
              {...commonProps}
              onClick={() => handleUpdate(componentId, true)}
            />
          );

        case "slider":
          return (
            <SliderWidget
              {...commonProps}
              min={component.min || 0}
              max={component.max || 100}
              step={component.step || 1}
              value={component.value !== undefined ? component.value : 50}
              onChange={(value) => handleUpdate(componentId, value)}
            />
          );

        case "text_input":
          return (
            <TextInputWidget
              {...commonProps}
              value={component.value || ""}
              onChange={(value) => handleUpdate(componentId, value)}
            />
          );

        case "checkbox":
          return (
            <CheckboxWidget
              {...commonProps}
              checked={!!component.value}
              onChange={(value) => handleUpdate(componentId, value)}
            />
          );

        case "selectbox":
          return (
            <SelectboxWidget
              {...commonProps}
              options={component.options || []}
              value={component.value || (component.options && component.options[0]) || ""}
              onChange={(value) => handleUpdate(componentId, value)}
            />
          );

        case "progress":
          return (
            <ProgressWidget
              {...commonProps}
              value={component.value !== undefined ? component.value : 0}
              steps={component.steps}
            />
          );

        case "spinner":
          return <SpinnerWidget {...commonProps} />;

        case "alert":
          return (
            <AlertWidget
              {...commonProps}
              level={component.level || "info"}
            />
          );

        case "image":
          return (
            <ImageWidget
              {...commonProps}
              size={component.size || "medium"}
              rounded={component.rounded !== undefined ? component.rounded : true}
            />
          );

        case "text":
          return (
            <MarkdownRendererWidget
              {...commonProps}
              markdown={component.markdown || component.content || component.value || ""}
              error={component.error}
            />
          );

        case "table":
          return (
            <TableViewerWidget 
              {...commonProps}
              data={component.data || []}
            />
          );

        case "connection":
          return <ConnectionInterfaceWidget {...commonProps} />;

        case "plot":
          return (
            <DataVisualizationWidget 
              {...commonProps}
              data={component.data || {}}
              layout={component.layout || {}}
              config={component.config || {}}
            />
          );

        default:
          console.warn(`Unknown component type: ${component.type}`);
          return <UnknownWidget {...commonProps} />;
      }
    } catch (error) {
      console.error(`Error rendering component ${componentId}:`, error);
      return (
        <div className="text-red-600 p-4">
          Error rendering component: {error.message}
        </div>
      );
    }
  };

  return (
    <div className="flex flex-col gap-4 p-4">
      {components.map((component, index) => (
        <div
          key={component.id || `component-${index}`}
          className="w-full p-4 bg-white"
        >
          {renderComponent(component, index)}
        </div>
      ))}
    </div>
  );
};

export default DynamicComponents;
