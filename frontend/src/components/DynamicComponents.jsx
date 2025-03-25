import React, { memo, useEffect } from 'react';

// UI components
import { Alert, AlertDescription } from '@/components/ui/alert';

import { cn } from '@/lib/utils';
import { comm } from '@/utils/websocket';

// Utilities
import { createExtractKeyProps } from '../utils/extractKeyProps';
// Widgets
import AlertWidget from './widgets/AlertWidget';
import ButtonWidget from './widgets/ButtonWidget';
import ChatWidget from './widgets/ChatWidget';
import CheckboxWidget from './widgets/CheckboxWidget';
import ConnectionInterfaceWidget from './widgets/ConnectionInterfaceWidget';
import DAGVisualizationWidget from './widgets/DAGVisualizationWidget';
import DataVisualizationWidget from './widgets/DataVisualizationWidget';
import FastplotlibWidget from './widgets/FastplotlibWidget';
import ImageWidget from './widgets/ImageWidget';
import MarkdownRendererWidget from './widgets/MarkdownRendererWidget';
import MatplotlibWidget from './widgets/MatplotlibWidget';
import PlaygroundWidget from './widgets/PlaygroundWidget';
import ProgressWidget from './widgets/ProgressWidget';
import SelectboxWidget from './widgets/SelectboxWidget';
import SidebarWidget from './widgets/SidebarWidget';
import SliderWidget from './widgets/SliderWidget';
import SpinnerWidget from './widgets/SpinnerWidget';
import TableViewerWidget from './widgets/TableViewerWidget';
import TextInputWidget from './widgets/TextInputWidget';
import TopbarWidget from './widgets/TopbarWidget';
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
  ({
    component,
    index,
    handleUpdate,
    extractKeyProps,
    sidebarOpen,
    setSidebarOpen,
    isCollapsed,
    setIsCollapsed,
  }) => {
    const [componentId, componentKey, props] = extractKeyProps(component, index);

    switch (component.type) {
      case 'sidebar':
        return <SidebarWidget defaultOpen={component.defaultopen} />;

      case 'button':
        return (
          <ButtonWidget
            key={componentKey}
            {...props}
            label={component.label || 'Button'}
            variant={component.variant || 'outline'}
            size={component.size || 'default'}
            disabled={component.disabled || false}
            loading={component.loading || false}
            onClick={() => handleUpdate(componentId, true)}
          />
        );

      case 'matplotlib':
        return <MatplotlibWidget key={componentKey} {...props} image={component.image} />;

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
          />
        );

      case 'topbar':
        return <TopbarWidget key={componentKey} {...props} />;

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
          />
        );

      case 'selectbox':
        return (
          <SelectboxWidget
            key={componentKey}
            {...props}
            label={component.label}
            options={component.options || []}
            value={component.value || (component.options && component.options[0]) || ''}
            onChange={(value) => handleUpdate(componentId, value)}
            placeholder={component.placeholder}
            disabled={component.disabled}
            error={component.error}
            required={component.required}
            size={component.size || 'default'}
          />
        );

      case 'progress':
        return (
          <ProgressWidget
            key={componentKey}
            {...props}
            label={component.label || 'Progress'}
            value={component.value !== undefined ? component.value : 0}
            steps={component.steps}
            showValue={component.showValue !== undefined ? component.showValue : true}
            size={component.size || 'default'}
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
          />
        );

      case 'alert':
        return (
          <AlertWidget
            key={componentKey}
            {...props}
            level={component.level || 'info'}
            message={component.message || component.content || ''}
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
          />
        );

      case 'table':
        return (
          <TableViewerWidget
            key={componentKey}
            {...props}
            rowData={component.data || []}
            title={component.title || 'Table Viewer'}
            variant={component.variant || 'default'}
            showTitle={component.showTitle ?? true}
            striped={component.striped ?? true}
            dense={component.dense ?? false}
            hoverable={component.hoverable ?? true}
            className={component.className}
          />
        );

      case 'connection':
        return (
          <ConnectionInterfaceWidget
            key={componentKey}
            {...props}
            disabled={component.disabled}
            onConnect={(connectionData) => handleUpdate(componentId, connectionData)}
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
          />
        );

      case 'dag':
        return <DAGVisualizationWidget key={componentKey} {...props} data={component.data || {}} />;

      case 'fastplotlib_component':
        const { className, data, config, label, src } = component;
        return (
          <FastplotlibWidget
            key={componentKey}
            {...props}
            data={component.data}
            config={component.config}
            src={src}
            label={label}
            className={className}
            clientId={comm.clientId}
          />
        );

      case 'playground':
        return (
          <PlaygroundWidget
            {...commonProps}
            label={component.label || 'Query Playground'}
            data={component.data || []}
            source={component.source}
            value={component.value}
            onChange={(value) => handleUpdate(componentId, value)}
            error={component.error}
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
          />
        );
    }
  },
  (prevProps, nextProps) => {
    // Custom comparison function for memoization
    return (
      prevProps.component.id === nextProps.component.id &&
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

          return (
            <React.Fragment key={componentKey}>
              <div
                className={cn(
                  'dynamiccomponent-component',
                  component.type === 'separator' && 'dynamiccomponent-hidden'
                )}
                style={{ flex: component.flex || 1 }}
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
              {index < row.length - 1 && <div className="dynamiccomponent-separator" />}
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
