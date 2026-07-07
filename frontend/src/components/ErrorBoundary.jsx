/* eslint-disable react/prop-types */
import { Component } from "react";
import Button from "./ui/Button";
import Card from "./ui/Card";

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error(
      "Uncaught runtime error caught by ErrorBoundary:",
      error,
      errorInfo,
    );
  }

  handleReload = () => {
    window.location.reload();
  };

  handleGoHome = () => {
    window.location.href = "/";
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-slate-950 text-slate-100 flex items-center justify-center p-6 relative overflow-hidden">
          <div className="absolute top-0 right-1/3 w-96 h-96 bg-rose-600/15 rounded-full blur-3xl pointer-events-none animate-pulse" />
          <Card className="max-w-md w-full text-center p-8 space-y-6 border-rose-500/30">
            <div className="w-16 h-16 rounded-3xl bg-rose-500/10 border border-rose-500/20 text-rose-400 flex items-center justify-center text-3xl mx-auto shadow-lg shadow-rose-500/10">
              ⚠️
            </div>
            <div className="space-y-2">
              <h2 className="text-xl font-extrabold text-white">
                Application Error Detected
              </h2>
              <p className="text-xs text-slate-400 leading-relaxed">
                An unexpected runtime error occurred while rendering this
                interface. Our system has logged the trace.
              </p>
              {this.state.error && (
                <div className="mt-4 p-3 rounded-xl bg-slate-950/80 border border-slate-800 text-left font-mono text-[11px] text-rose-300 overflow-x-auto max-h-32">
                  {this.state.error.toString()}
                </div>
              )}
            </div>
            <div className="flex items-center justify-center gap-3 pt-2">
              <Button variant="secondary" onClick={this.handleGoHome} size="sm">
                ← Dashboard
              </Button>
              <Button variant="primary" onClick={this.handleReload} size="sm">
                ↻ Reload Application
              </Button>
            </div>
          </Card>
        </div>
      );
    }

    return this.props.children;
  }
}
