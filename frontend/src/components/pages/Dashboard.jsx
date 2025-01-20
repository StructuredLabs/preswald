import { Alert, AlertDescription } from "@/components/ui/alert";

import DynamicComponents from "../DynamicComponents";

const Dashboard = ({ components, error, handleComponentUpdate }) => {
  console.log("{ components, error, handleComponentUpdate }", { components, error, handleComponentUpdate });
  
  return (
    <div className="min-h-screen">
      {error && (
        <Alert variant="destructive" className="mb-4">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}
      {!Array.isArray(components) || components.length === 0 ? (
        <div className="flex items-center justify-center h-64">
          <div className="text-center space-y-4">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
            <p className="text-sm text-muted-foreground">
              {!Array.isArray(components) 
                ? "Invalid components data" 
                : "Loading components..."}
            </p>
          </div>
        </div>
      ) : (
        <DynamicComponents 
          components={components} 
          onComponentUpdate={handleComponentUpdate} 
        />
      )}
    </div>
  );
};

export default Dashboard;
