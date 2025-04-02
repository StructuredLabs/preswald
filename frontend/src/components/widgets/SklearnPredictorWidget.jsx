import React from 'react';
import { Card, CardContent } from '@/components/ui/card';

const SklearnPredictorWidget = ({ label, result }) => {
  if (!result) {
    return <div>Waiting for prediction...</div>;
  }

  const { prediction, confidence, probabilities } = result;

  return (
    <Card className="sklearn-predictor-widget mb-4 p-4">
      <CardContent>
        <h3 className="text-lg font-semibold mb-2">{label || 'Prediction'}</h3>
        <p className="text-xl font-bold mb-2">Prediction: {prediction}</p>
        {confidence && <p className="text-sm text-muted-foreground">Confidence: {(confidence * 100).toFixed(2)}%</p>}

        {/* Optional: Table like in your screenshot */}
        {probabilities && (
          <div className="mt-4">
            {probabilities.map((p) => (
              <div key={p.label} className="flex justify-between">
                <span>{p.label}</span>
                <span>{(p.prob * 100).toFixed(2)}%</span>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default SklearnPredictorWidget; 


