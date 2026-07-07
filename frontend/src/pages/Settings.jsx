import { useState } from "react";
import Badge from "../components/ui/Badge";
import { useSettings } from "../hooks/useSettings";
import { useAuth } from "../hooks/useAuth";
import AgentWeightSlider from "../components/settings/AgentWeightSlider";
import ProfileForm from "../components/settings/ProfileForm";
import PasswordChangeForm from "../components/settings/PasswordChangeForm";
import ConfidenceMethodologyInfo from "../components/settings/ConfidenceMethodologyInfo";

export default function Settings() {
  const { settings, isLoading, updateAgentWeights, isUpdatingWeights, updateProfile, isUpdatingProfile } = useSettings();
  const { changePassword, isChangingPassword } = useAuth();
  const [activeTab, setActiveTab] = useState("weights");

  const tabs = [
    { id: "weights", label: "⚖️ Persona Weights", desc: "Aggregator Synthesis" },
    { id: "profile", label: "👤 Profile & Account", desc: "Display Name & ID" },
    { id: "security", label: "🔒 Security & Passwords", desc: "Token Invalidation" },
    { id: "methodology", label: "📊 Explainable AI", desc: "Scoring Methodology" },
  ];

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto py-16 text-center space-y-4">
        <div className="w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
        <p className="text-sm text-slate-500 dark:text-slate-400 font-medium">
          Loading platform configuration...
        </p>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6 sm:space-y-8 py-6 sm:py-8 px-2 sm:px-4 min-w-0 break-words">
      {/* Header */}
      <div className="border-b border-slate-200 dark:border-slate-800 pb-6 flex flex-col md:flex-row md:items-center md:justify-between gap-4 min-w-0">
        <div className="min-w-0">
          <div className="flex items-center gap-2 mb-2 flex-wrap">
            <Badge variant="indigo" className="px-2.5 py-0.5 text-xs">
              Platform Configuration
            </Badge>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-slate-900 dark:text-white break-words">
            System & Agent Settings
          </h1>
          <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-400 mt-1">
            Tune multi-agent reasoning parameters, manage account security, and explore confidence scoring methodology.
          </p>
        </div>
      </div>

      {/* Tab Switcher */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2 border-b border-slate-200 dark:border-slate-800 scrollbar-none min-w-0">
        {tabs.map((tab) => {
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-3 rounded-2xl font-bold text-xs sm:text-sm whitespace-nowrap transition-all duration-200 min-h-[40px] flex-shrink-0 ${
                isActive
                  ? "bg-gradient-to-r from-indigo-500/15 via-purple-500/10 to-transparent text-indigo-600 dark:text-indigo-400 border border-indigo-500/30 shadow-sm"
                  : "text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-900/60 hover:text-slate-900 dark:hover:text-white font-medium"
              }`}
            >
              <span>{tab.label}</span>
              <span className="text-[10px] font-mono text-slate-400 dark:text-slate-500 hidden sm:inline">
                ({tab.desc})
              </span>
            </button>
          );
        })}
      </div>

      {/* Tab Content */}
      <div className="transition-all duration-300">
        {activeTab === "weights" && (
          <AgentWeightSlider
            initialWeights={settings?.agent_weights}
            onSave={updateAgentWeights}
            isSaving={isUpdatingWeights}
          />
        )}

        {activeTab === "profile" && (
          <ProfileForm
            initialFullName={settings?.full_name}
            email={settings?.email}
            onSave={updateProfile}
            isSaving={isUpdatingProfile}
          />
        )}

        {activeTab === "security" && (
          <PasswordChangeForm
            onChangePassword={changePassword}
            isChanging={isChangingPassword}
          />
        )}

        {activeTab === "methodology" && <ConfidenceMethodologyInfo />}
      </div>
    </div>
  );
}
