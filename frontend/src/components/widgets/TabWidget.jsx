import React from 'react';

import { Card } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

import DynamicComponents from '../DynamicComponents';

const TabWidget = ({ label, tabs = [], onComponentUpdate }) => {
  const [activeTab, setActiveTab] = React.useState(tabs?.[0]?.title || '');

  const normalizeComponents = (components, tabTitle) => {
    if (!components) return [];

    return components.map((component, index) => {
      if (typeof component === 'string') {
        return {
          id: `tab-${tabTitle}-text-${hashString(component)}-${index}`,
          type: 'text',
          content: component,
          markdown: component,
          value: component,
        };
      }

      const baseId = component.id || `comp-${index}`;
      return {
        ...component,
        id: `tab-${tabTitle}-${baseId}`,
        type: component.type || 'text',
      };
    });
  };

  const hashString = (str) => {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      hash = (hash << 5) - hash + str.charCodeAt(i);
      hash |= 0;
    }
    return Math.abs(hash).toString(36);
  };

  return (
    <Card className="mb-4 p-4 rounded-2xl shadow-md">
      <h2 className="font-semibold text-lg mb-2">{label}</h2>
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="mb-2 flex space-x-2">
          {tabs.map((tab) => (
            <TabsTrigger key={tab.title} value={tab.title}>
              {tab.title}
            </TabsTrigger>
          ))}
        </TabsList>

        {tabs.map((tab) => {
          const normalizedComponents = normalizeComponents(tab.components || [], tab.title);
          return (
            <TabsContent key={tab.title} value={tab.title} className="isolate">
              <DynamicComponents
                components={{ rows: [normalizedComponents] }}
                onComponentUpdate={onComponentUpdate}
              />
            </TabsContent>
          );
        })}
      </Tabs>
    </Card>
  );
};

export default TabWidget;
