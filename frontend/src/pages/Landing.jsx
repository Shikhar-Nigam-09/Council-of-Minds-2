import { Link } from "react-router-dom";
import Button from "../components/ui/Button";

export default function Landing() {
  return (
    <div className="space-y-8 sm:space-y-12 pb-12 min-w-0 px-2 sm:px-4 break-words">
      <div className="text-center max-w-3xl mx-auto pt-8 sm:pt-16 min-w-0">
        <h1 className="text-4xl sm:text-6xl md:text-7xl font-black tracking-tight mb-3 sm:mb-4 leading-tight text-slate-900 dark:text-white break-words">
          Council of Minds
        </h1>
        <p className="text-sm sm:text-base md:text-lg font-medium text-slate-600 dark:text-slate-400 max-w-xl mx-auto">
          Multi-agent answers you can actually trust.
        </p>
        <div className="mt-8 sm:mt-10 flex flex-col sm:flex-row items-center justify-center gap-3 sm:gap-4 w-full sm:w-auto">
          <Link to="/documents" className="w-full sm:w-auto">
            <Button variant="primary" size="lg" className="w-full sm:w-auto justify-center min-h-[44px] shadow-lg shadow-indigo-500/20">
              <span>📂 Open Document Repository</span>
            </Button>
          </Link>
          <Link to="/chat" className="w-full sm:w-auto">
            <Button variant="outline" size="lg" className="w-full sm:w-auto justify-center min-h-[44px]">
              <span>💬 Preview Chat Engine</span>
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
