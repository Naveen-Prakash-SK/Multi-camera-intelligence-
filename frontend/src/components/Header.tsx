"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Video, Activity, Settings, Database, Clock, Camera as CameraIcon } from "lucide-react";
import { useEffect, useState } from "react";
import { api } from "@/lib/api/client";

export function Header() {
  const pathname = usePathname();
  const [healthStatus, setHealthStatus] = useState<"OPERATIONAL" | "DEGRADED" | "OFFLINE" | "LOADING">("LOADING");

  useEffect(() => {
    let mounted = true;
    const checkHealth = async () => {
      try {
        const res = await api.getServicesHealth();
        if (!mounted) return;
        
        if (res.api === "ONLINE") {
          // Check if any sub-service is degraded
          const hasDegraded = Object.values(res.models).some((status: any) => 
            typeof status === "string" && status.includes("DEGRADED")
          );
          setHealthStatus(hasDegraded ? "DEGRADED" : "OPERATIONAL");
        } else {
          setHealthStatus("OFFLINE");
        }
      } catch (err) {
        if (mounted) setHealthStatus("OFFLINE");
      }
    };
    
    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => { mounted = false; clearInterval(interval); };
  }, []);

  const navItems = [
    { name: "Dashboard", href: "/", icon: null },
    { name: "Cameras", href: "/cameras", icon: CameraIcon },
    { name: "Footage", href: "/footage", icon: Database },
    { name: "Timeline", href: "/timeline", icon: Clock },
    { name: "Alerts", href: "/alerts", icon: Activity },
    { name: "Health", href: "/health", icon: Activity },
    { name: "Settings", href: "/settings", icon: Settings },
  ];

  return (
    <header className="sticky top-0 z-50 glass-panel border-b border-white/40 px-6 py-4 flex items-center justify-between">
      <div className="flex items-center space-x-6">
        <Link href="/" className="flex items-center space-x-3">
          <div className="h-8 w-8 bg-blue-600 rounded-lg flex items-center justify-center shadow-lg shadow-blue-500/20">
            <Video className="w-5 h-5 text-white" />
          </div>
          <h1 className="text-xl font-bold tracking-tight text-slate-800 hidden sm:block">
            Video Intelligence
          </h1>
        </Link>
        
        <div className="hidden lg:flex items-center px-4 py-1.5 rounded-full bg-white/60 border border-white subtle-shadow">
          <span className="text-xs font-semibold text-slate-500 mr-2">System Status:</span>
          {healthStatus === "LOADING" && <span className="text-xs font-bold text-slate-400">● CHECKING...</span>}
          {healthStatus === "OPERATIONAL" && <span className="text-xs font-bold text-emerald-500">● OPERATIONAL</span>}
          {healthStatus === "DEGRADED" && <span className="text-xs font-bold text-amber-500">● DEGRADED</span>}
          {healthStatus === "OFFLINE" && <span className="text-xs font-bold text-red-500">● OFFLINE</span>}
        </div>
      </div>
      
      <nav className="flex space-x-2 md:space-x-4 text-sm font-medium items-center">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;
          return (
            <Link 
              key={item.name}
              href={item.href} 
              className={`flex items-center px-3 py-2 rounded-lg transition-colors font-semibold ${
                isActive ? "text-blue-700 bg-blue-50 border border-blue-200 subtle-shadow" : "text-slate-500 hover:text-slate-800 hover:bg-white/60"
              }`}
            >
              {Icon && <Icon className="w-4 h-4 mr-1.5 hidden md:block" />}
              {item.name}
            </Link>
          );
        })}
      </nav>
    </header>
  );
}
