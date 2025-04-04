import * as React from 'react';

const Progress = React.forwardRef((props, ref) => {
  const { value = 0, ...other } = props;

  return (
    <div
      ref={ref}
      className="relative h-2 w-full overflow-hidden rounded-full bg-gray-200"
      {...other}
    >
      <div className="h-full bg-black transition-all" style={{ width: `${value}%` }} />
    </div>
  );
});

Progress.displayName = 'Progress';

export { Progress };
