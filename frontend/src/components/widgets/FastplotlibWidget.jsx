import PropTypes from 'prop-types';

import { Card } from '@/components/ui/card';

import { cn } from '@/lib/utils';

const FastplotlibWidget = ({ label, src, className }) => {
  return (
    <Card className={cn('w-full p-4 flex justify-center', className)}>
      <img src={src} alt={label} className="max-w-full h-auto" />
    </Card>
  );
};

FastplotlibWidget.propTypes = {
  label: PropTypes.string.isRequired,
  src: PropTypes.string.isRequired,
  className: PropTypes.string,
};

export default FastplotlibWidget;
