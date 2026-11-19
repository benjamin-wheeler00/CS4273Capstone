"use client";
import Link from "next/link";
import React, { useState } from "react";
import { PanelLeftClose, PanelLeftOpen } from "lucide-react";
import Image from "next/image";
import { usePathname } from "next/navigation";
import normanPDLogo from "@/../public/norman-pd-logo.svg";
import evaluateIconBlack from "@/../public/evaluate-icon-black.svg";
import evaluateIconWhite from "@/../public/evaluate-icon-white.svg";
import recordsIconWhite from "@/../public/records-icon-white.svg";
import recordsIconBlack from "@/../public/records-icon-black.svg";
import helpIconWhite from "@/../public/help-icon-white.svg";
import helpIconBlack from "@/../public/help-icon-black.svg";

const Navbar = () => {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);

  const activePage =
    pathname === "/evaluate"
      ? "Evaluate"
      : pathname.startsWith("/records")
        ? "Records"
        : pathname.startsWith("/help")
          ? "Help"
          : "";

  const links = [
    { href: "/evaluate", label: "Evaluate", activeIcon: evaluateIconBlack, icon: evaluateIconWhite },
    { href: "/records", label: "Records", activeIcon: recordsIconBlack, icon: recordsIconWhite },
    { href: "/help", label: "Help", activeIcon: helpIconBlack, icon: helpIconWhite },
  ];

  return (
    <aside
      aria-label="Main navigation"
      className={`sticky top-0 flex h-dvh shrink-0 flex-col bg-[#002d62] py-3 transition-[width] duration-200 motion-reduce:transition-none ${collapsed ? "w-[64px]" : "w-[200px]"}`}
    >
      <div className={`flex px-3 ${collapsed ? "justify-center" : "justify-end"}`}>
        <button
          type="button"
          onClick={() => setCollapsed((value) => !value)}
          aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          aria-expanded={!collapsed}
          aria-controls="sidebar-navigation"
          title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          className="rounded-md p-2 text-white hover:bg-white/15 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white"
        >
          {collapsed ? <PanelLeftOpen size={20} aria-hidden="true" /> : <PanelLeftClose size={20} aria-hidden="true" />}
        </button>
      </div>

      {!collapsed && (
        <Link href="/records" aria-label="Norman Police Department records" className="mx-auto my-5 rounded focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white">
          <Image src={normanPDLogo} alt="Norman Police Department" width={130} height={130} />
        </Link>
      )}

      <nav id="sidebar-navigation" className={`flex flex-col gap-2 ${collapsed ? "mt-4 px-2" : "px-3"}`}>
        {links.map(({ href, label, activeIcon, icon }) => {
          const active = activePage === label;
          return (
            <Link
              key={href}
              href={href}
              aria-label={label}
              aria-current={active ? "page" : undefined}
              title={collapsed ? label : undefined}
              className={`flex min-h-10 items-center rounded-lg py-2 font-roboto text-base font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white ${collapsed ? "justify-center px-2" : "gap-3 px-3"} ${active ? "bg-white text-[#002d62]" : "text-white hover:bg-white/15"}`}
            >
              <span className="flex h-6 w-6 shrink-0 items-center justify-center">
                <Image src={active ? activeIcon : icon} alt="" width={label === "Help" ? 17 : 24} height={24} />
              </span>
              {!collapsed && <span>{label}</span>}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
};

export default Navbar;
