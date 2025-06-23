import React, { memo, useEffect } from 'react';

// UI components
import { Alert, AlertDescription } from '@/components/ui/alert';

import { cn } from '@/lib/utils';
// Utilities
import { createExtractKeyProps } from '@/utils/extractKeyProps';

// Widgets
import AlertWidget from './widgets/AlertWidget';
import BigNumberWidget from './widgets/BigNumberWidget';
import ButtonWidget from './widgets/ButtonWidget';
import ChatWidget from './widgets/ChatWidget';
import CheckboxWidget from './widgets/CheckboxWidget';
import DAGVisualizationWidget from './widgets/DAGVisualizationWidget';
import DataVisualizationWidget from './widgets/DataVisualizationWidget';
//import FastplotlibWidget from './widgets/FastplotlibWidget';
import ImageWidget from './widgets/ImageWidget';
import JSONViewerWidget from './widgets/JSONViewerWidget';
import MarkdownRendererWidget from './widgets/MarkdownRendererWidget';
import MatplotlibWidget from './widgets/MatplotlibWidget';
import PlaygroundWidget from './widgets/PlaygroundWidget';
import ProgressWidget from './widgets/ProgressWidget';
import SelectboxWidget from './widgets/SelectboxWidget';
import SeparatorWidget from './widgets/SeparatorWidget';
import SidebarWidget from './widgets/SidebarWidget';
import SliderWidget from './widgets/SliderWidget';
import SpinnerWidget from './widgets/SpinnerWidget';
import TableViewerWidget from './widgets/TableViewerWidget';
import TextInputWidget from './widgets/TextInputWidget';
import TopbarWidget from './widgets/TopbarWidget';
import GenericWidget from './widgets/GenericWidget';
import UnknownWidget from './widgets/UnknownWidget';

const extractKeyProps = createExtractKeyProps();

// Error boundary component
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('[DynamicComponents] Component Error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <Alert variant="destructive">
          <AlertDescription>
            {this.state.error?.message || 'Error rendering component'}
          </AlertDescription>
        </Alert>
      );
    }

    return this.props.children;
  }
}

// Memoized component wrapper
const MemoizedComponent = memo(
  ({ component, index, handleUpdate, extractKeyProps }) => {
    const [componentId, componentKey, props] = extractKeyProps(component, index);

    switch (component.type) {
      case 'sidebar':
        return (
          <SidebarWidget
            id={componentId}
            defaultOpen={component.defaultopen}
            branding={component.branding}
          />
        );

      case 'button':
        return (
          <ButtonWidget
            key={componentKey}
            onClick={() => {
              if (component.onClick) {
                handleUpdate(componentId, true);
              }
            }}
            disabled={component.disabled}
            isLoading={component.loading}
            variant={component.variant}
            id={componentId}
          >
            {component.label}
          </ButtonWidget>
        );

      case 'big_number':
        return (
          <BigNumberWidget
            key={componentKey}
            {...props}
            value={component.value}
            label={component.label}
            delta={component.delta}
            delta_color={component.delta_color}
            icon={component.icon}
            description={component.description}
            size={component.size}
            className={component.className}
            id={componentId}
          />
        );

      case 'matplotlib':
        return (
          <MatplotlibWidget
            key={componentKey}
            {...props}
            image={component.image}
            id={componentId}
          />
        );

      case 'slider':
        return (
          <SliderWidget
            key={componentKey}
            {...props}
            label={component.label || 'Slider'}
            min={component.min || 0}
            max={component.max || 100}
            step={component.step || 1}
            value={component.value !== undefined ? component.value : 50}
            onChange={(value) => handleUpdate(componentId, value)}
            disabled={component.disabled}
            showValue={component.showValue !== undefined ? component.showValue : true}
            showMinMax={component.showMinMax !== undefined ? component.showMinMax : true}
            variant={component.variant || 'default'}
            id={componentId}
          />
        );

      case 'json_viewer':
        return (
          <JSONViewerWidget
            key={componentKey}
            data={component.data || component.value} // fallback if `data` isn't set
            title={component.title}
            expanded={component.expanded !== false}
            className={component.className}
            id={componentId}
          />
        );

      case 'text_input':
        return (
          <TextInputWidget
            key={componentKey}
            {...props}
            label={component.label}
            placeholder={component.placeholder}
            value={component.value || ''}
            onChange={(value) => handleUpdate(componentId, value)}
            error={component.error}
            disabled={component.disabled}
            required={component.required}
            type={component.type || 'text'}
            size={component.size || 'default'}
            variant={component.variant || 'default'}
            id={componentId}
          />
        );

      case 'checkbox':
        return (
          <CheckboxWidget
            key={componentKey}
            {...props}
            label={component.label || 'Checkbox'}
            checked={!!component.value}
            description={component.description}
            disabled={component.disabled}
            onChange={(value) => handleUpdate(componentId, value)}
            id={componentId}
          />
        );

      case 'selectbox':
        return (
          <SelectboxWidget
            key={componentKey}
            {...props}
            options={component.options || []}
            value={component.value || (component.options && component.options[0]) || ''}
            onChange={(value) => handleUpdate(componentId, value)}
            placeholder={component.placeholder}
            id={componentId}
          />
        );

      case 'progress':
        return (
          <ProgressWidget
            key={componentKey}
            {...props}
            label={component.label || 'Progress'}
            value={component.value}
            id={componentId}
          />
        );

      case 'spinner':
        return (
          <SpinnerWidget
            key={componentKey}
            {...props}
            label={component.label || 'Loading...'}
            size={component.size || 'default'}
            variant={component.variant || 'default'}
            showLabel={component.showLabel !== undefined ? component.showLabel : true}
            id={componentId}
          />
        );

      case 'alert':
        return (
          <AlertWidget
            key={componentKey}
            {...props}
            level={component.level || 'info'}
            message={component.message || component.content || ''}
            id={componentId}
          />
        );

      case 'image':
        return (
          <ImageWidget
            key={componentKey}
            {...props}
            src={component.src}
            alt={component.alt || ''}
            size={component.size || 'medium'}
            rounded={component.rounded !== undefined ? component.rounded : true}
            withCard={component.withCard}
            aspectRatio={component.aspectRatio || 1}
            objectFit={component.objectFit || 'cover'}
            id={componentId}
          />
        );

      case 'text':
        return (
          <MarkdownRendererWidget
            key={componentKey}
            {...props}
            markdown={component.markdown || component.content || component.value || ''}
            error={component.error}
            variant={component.variant || 'default'}
            id={componentId}
          />
        );

      case 'chat':
        return (
          <ChatWidget
            key={componentKey}
            {...props}
            sourceId={component.config?.source || null}
            sourceData={component.config?.data || null}
            value={component.value || component.state || { messages: [] }}
            onChange={(value) => {
              handleUpdate(componentId, value);
            }}
            id={componentId}
          />
        );

      case 'table':
        return (
          <TableViewerWidget
            key={componentKey}
            {...props}
            rowData={component.data || []}
            className={component.className}
            id={componentId}
          />
        );

      case 'plot':
        return (
          <DataVisualizationWidget
            key={componentKey}
            {...props}
            data={component.data || {}}
            layout={component.layout || {}}
            config={component.config || {}}
            id={componentId}
          />
        );

      case 'dag':
        return (
          <DAGVisualizationWidget
            key={componentKey}
            {...props}
            data={component.data || {}}
            id={componentId}
          />
        );

      // case 'fastplotlib_component':
      //   const { className, data, config, label, src } = component;
      //   return (
      //     <FastplotlibWidget
      //       key={componentKey}
      //       {...props}
      //       data={component.data}
      //       config={component.config}
      //       src={src}
      //       label={label}
      //       className={className}
      //       clientId={comm.clientId}
      //       id={componentId}
      //     />
      //   );

      case 'playground':
        return (
          <PlaygroundWidget
            key={componentKey}
            {...props}
            label={component.label || 'Query Playground'}
            source={component.source}
            value={component.value}
            onChange={(value) => handleUpdate(componentId, value)}
            error={component.error}
            data={component.data}
            id={componentId}
          />
        );

      case 'topbar':
        return <TopbarWidget key={componentKey} {...props} id={componentId} />;

      case 'separator':
        return <SeparatorWidget key={componentKey} id={componentId} />;

      case 'generic':
        return (
          <GenericWidget
            key={componentKey}
            {...props}
            value={component.value}
            mimetype={component.mimetype || 'text/plain'}
            id={componentId}
          />
        );

      default:
        console.warn(`[DynamicComponents] Unknown component type: ${component.type}`);
        return (
          <UnknownWidget
            key={componentKey}
            {...props}
            type={component.type || 'unknown'}
            variant={component.variant || 'default'}
            id={componentId}
          />
        );
    }
  },
  (prevProps, nextProps) => {
    // Custom comparison function for memoization
    return (
      !prevProps.component.shouldRender &&
      prevProps.component.value === nextProps.component.value &&
      prevProps.component.error === nextProps.component.error &&
      prevProps.index === nextProps.index
    );
  }
);

const DynamicComponents = ({ components, onComponentUpdate }) => {
  useEffect(() => {
    extractKeyProps.reset();
  }, []);

  console.log('[DynamicComponents] Rendering with components:', components);

  if (!components?.rows) {
    console.warn('[DynamicComponents] No components or invalid structure received');
    return null;
  }

  const handleUpdate = (componentId, value) => {
    console.log(`[DynamicComponents] Component update triggered:`, {
      componentId,
      value,
      timestamp: new Date().toISOString(),
    });
    onComponentUpdate(componentId, value);
  };

  const renderRow = (row, rowIndex) => {
    if (!Array.isArray(row)) {
      console.warn(`[DynamicComponents] Invalid row at index ${rowIndex}`);
      return null;
    }

    return (
      <div key={`row-${rowIndex}`} className="dynamiccomponent-row">
        {row.map((component, index) => {
          if (!component) return null;

          const componentKey = component.id || `component-${index}`;
          const isSeparator = component.type === 'separator';

          return (
            <React.Fragment key={componentKey}>
              <div
                className={cn(isSeparator ? 'w-full' : 'dynamiccomponent-component')}
                style={!isSeparator ? { flex: component.flex || 1 } : undefined}
              >
                <ErrorBoundary>
                  <MemoizedComponent
                    component={component}
                    index={index}
                    handleUpdate={handleUpdate}
                    extractKeyProps={extractKeyProps}
                  />
                </ErrorBoundary>
              </div>
              {index < row.length - 1 && !isSeparator && (
                <div className="dynamiccomponent-separator" />
              )}
            </React.Fragment>
          );
        })}
      </div>
    );
  };

  return (
    <div className="dynamiccomponent-container">
      {components.rows.map((row, index) => renderRow(row, index))}
    </div>
  );
};

export default memo(DynamicComponents);
