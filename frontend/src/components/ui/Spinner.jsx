/* eslint-disable react/prop-types */
export default function Spinner({ size = "md", className = "", ...props }) {
  const sizeStyles = {
    sm: "w-4 h-4 border-2",
    md: "w-6 h-6 border-2",
    lg: "w-8 h-8 border-3",
  };

  return (
    <div
      className={`inline-block border-current border-t-transparent rounded-full animate-spin ${
        sizeStyles[size] || sizeStyles.md
      } ${className}`}
      role="status"
      aria-label="Loading"
      {...props}
    />
  );
}
