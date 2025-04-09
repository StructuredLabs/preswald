import React from "react";
import {
  ArrowUpRight,
  ArrowDownRight,
  User,
} from "lucide-react";
import * as LucideIcons from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";

const formatNumber = (value) => {
  if (typeof value === "string" && /[KMBT]$/.test(value.trim())) {
    return value;
  }

  const num = typeof value === "string" ? parseFloat(value) : value;
  if (isNaN(num)) return value;
  if (num >= 1e12) return (num / 1e12).toFixed(1) + "T";
  if (num >= 1e9) return (num / 1e9).toFixed(1) + "B";
  if (num >= 1e6) return (num / 1e6).toFixed(1) + "M";
  if (num >= 1e3) return (num / 1e3).toFixed(1) + "K";
  return num.toString();
};

const BigNumberCard = ({
  value,
  label,
  delta,
  deltaColor = "green",
  icon = "User",
  description = "",
  className,
}) => {
  const formattedValue = formatNumber(value);
  const IconComponent = icon && LucideIcons[icon] ? LucideIcons[icon] : User;

  const deltaTextColor = deltaColor ? `text-${deltaColor}-600` : "text-green-600";
  const isPositiveDelta = parseFloat(delta) >= 0;

  return (
    <Card className={cn("bg-white w-80 rounded-3xl  max-w-sm border border-gray-100 transition-shadow duration-300 shadow-md hover:shadow-lg", className)}>
      <CardHeader>
        <div className="flex justify-between items-start">
          <div>
            <CardTitle className="text-base text-muted-foreground">{label}</CardTitle>
          </div>
          {delta && (
            <div className={cn("flex items-center gap-1 text-sm font-medium", deltaTextColor)}>
              {isPositiveDelta ? <ArrowUpRight size={18} /> : <ArrowDownRight size={18} />}
              <span>{delta.toString()}</span>
            </div>
          )}
        </div>
      </CardHeader>
      <CardContent className="flex justify-between items-center">
        <div className="text-4xl font-bold tracking-tight">{formattedValue}</div>
        <IconComponent className="text-muted-foreground " size={36} />
      </CardContent>
      {description && (
        <CardContent className="pt-0 text-sm text-muted-foreground">{description}</CardContent>
      )}
    </Card>
  );
};

export default BigNumberCard;
