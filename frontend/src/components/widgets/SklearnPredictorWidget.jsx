import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';

const SklearnPredictor = ({ data }) => {
  const { prediction, probabilities, output_label } = data;
  //console.log("Prediction Output:", data.prediction);
  
  return (
    <Card className="w-full max-w-md border-gray-300 shadow-lg rounded-lg">
      <CardHeader>
        <CardTitle className="text-xl font-bold text-center">
          {output_label}
        </CardTitle>
      </CardHeader>
      
      <CardContent className="space-y-4">
        <div className="text-center">
          <h3 className="text-lg font-semibold">Prediction: {prediction}</h3>
          <p className="text-2xl font-bold mt-2">{prediction}</p>
        </div>

        {probabilities && (
          <div className="space-y-2">
            {Object.entries(data.probabilities).map(([cls, prob]) => (
              <div key={cls} className="space-y-1">
                <div className="flex justify-between">
                  <span className="font-medium">{cls}</span>
                  <span className="text-muted-foreground">
                    {(prob * 100).toFixed(2)}%
                  </span>
                </div>
                <Progress 
                  value={prob * 100} 
                  className="h-2 bg-gray-300"
                />
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default SklearnPredictor;