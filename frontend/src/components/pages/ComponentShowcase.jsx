import Dashboard from './Dashboard';
import DynamicComponents from '../DynamicComponents';
import React from 'react';

const ComponentShowcase = () => {
  // Sample data for all possible components based on components.py
  const sampleComponents = [
    // Text Input
    {
      type: "text_input",
      id: "text-input-sample",
      label: "Sample Text Input",
      placeholder: "Enter some text...",
      value: "",
    },

    // Checkbox
    {
      type: "checkbox",
      id: "checkbox-sample",
      label: "Sample Checkbox",
      value: false,
    },

    // Slider
    {
      type: "slider",
      id: "slider-sample",
      label: "Sample Slider",
      min: 0,
      max: 100,
      step: 1,
      value: 50,
    },

    // Button
    {
      type: "button",
      id: "button-sample",
      label: "Sample Button",
    },

    // Selectbox
    {
      type: "selectbox",
      id: "selectbox-sample",
      label: "Sample Selectbox",
      options: ["Option 1", "Option 2", "Option 3"],
      value: "Option 1",
    },

    // Progress
    {
      type: "progress",
      id: "progress-sample",
      label: "Sample Progress",
      value: 75,
    },

    // Spinner
    {
      type: "spinner",
      id: "spinner-sample",
      label: "Sample Spinner",
    },

    // Alert (Info)
    {
      type: "alert",
      id: "alert-info-sample",
      message: "This is an info alert message",
      level: "info",
    },

    // Alert (Error)
    {
      type: "alert",
      id: "alert-error-sample",
      message: "This is an error alert message",
      level: "error",
    },

    // Image
    {
      type: "image",
      id: "image-sample",
      src: "https://raw.githubusercontent.com/jayanth-kumar-morem/preswald/main/preswald_logo.png",
      alt: "Sample Image",
    },

    // Text/Markdown
    {
      type: "text",
      id: "text-sample",
      markdown: "# Sample Markdown\nThis is a sample markdown text with:\n- Bullet points\n- **Bold text**\n- *Italic text*\n\n```python\nprint('Code blocks')\n```",
      value: "Sample Markdown Text",
    },

    // Plot
    {
      type: "plot",
      id: "plot-sample",
      data: {
        data: [
          {
            x: [1, 2, 3, 4, 5],
            y: [2, 4, 6, 8, 10],
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Sample Data'
          }
        ],
        layout: {
          title: 'Sample Plot',
          xaxis: { title: 'X Axis' },
          yaxis: { title: 'Y Axis' }
        },
        config: {
          responsive: true,
          displayModeBar: true,
          displaylogo: false,
          scrollZoom: true,
        }
      }
    },

    // Table
    {
      type: "table",
      id: "table-sample",
      data: [
        { id: 1, name: "John Doe", age: 30, city: "New York" },
        { id: 2, name: "Jane Smith", age: 25, city: "Los Angeles" },
        { id: 3, name: "Bob Johnson", age: 35, city: "Chicago" }
      ],
      title: "Sample Table"
    },

    // DAG Visualization
    {
      type: "dag",
      id: "dag-sample",
      data: {
        data: [{
          type: "scatter",
          customdata: [
            {
              name: "Task 1",
              status: "completed",
              execution_time: "2s",
              attempts: 1,
              error: null,
              dependencies: [],
              force_recompute: false
            },
            {
              name: "Task 2",
              status: "running",
              execution_time: "5s",
              attempts: 2,
              error: null,
              dependencies: ["Task 1"],
              force_recompute: false
            },
            {
              name: "Task 3",
              status: "pending",
              execution_time: null,
              attempts: 0,
              error: null,
              dependencies: ["Task 1", "Task 2"],
              force_recompute: true
            }
          ],
          node: {
            positions: []
          }
        }],
        layout: {
          title: { text: "Sample Workflow DAG" },
          showlegend: true
        }
      }
    }
  ];

  const handleComponentUpdate = (componentId, value) => {
    console.log('Component updated:', { componentId, value });
  };

  return (
    <div className="p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Component Showcase</h1>
        <p className="text-muted-foreground mb-8">
          This page showcases all possible components that can be rendered by the Preswald frontend.
          Each component demonstrates different features and states.
        </p>
        <Dashboard
          components={sampleComponents}
          error={null}
          handleComponentUpdate={handleComponentUpdate}
        />
      </div>
    </div>
  );
};

export default ComponentShowcase; 