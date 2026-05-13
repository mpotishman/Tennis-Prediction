import React from "react";

function PartyRow({ party, won, hovered, onEnter, onLeave, onClick }) {
  return (
    <div
      onMouseEnter={onEnter}
      onMouseLeave={onLeave}
      onClick={onClick}
      className={`flex items-center gap-3 px-3 py-2.5 transition-all duration-150 ${
        onClick ? "cursor-pointer" : "cursor-default"
      } ${hovered ? "bg-[#f5f0de]/5" : ""}`}
    >
      <span
        className={`h-2 w-2 shrink-0 rounded-full transition-all duration-200 ${
          won
            ? "bg-[#dcb24d] shadow-[0_0_8px_rgba(220,178,77,0.7)]"
            : "bg-[#f5f0de]/15"
        }`}
      />
      <span
        className={`flex-1 truncate text-md font-semibold uppercase tracking-widest transition-all duration-150 ${
          won ? "text-[#fffbea]" : "text-[#f5f0de]/40"
        }`}
      >
        {party?.name ?? "TBD"}
      </span>
      <span
        className={`shrink-0 text-sm font-bold tabular-nums ${
          won ? "text-[#dcb24d]" : "text-[#f5f0de]/25"
        }`}
      >
        {party?.resultText ?? "–"}
      </span>
    </div>
  );
}

export default function MatchBracketCard({
  match,
  topParty,
  bottomParty,
  topWon,
  bottomWon,
  topHovered,
  bottomHovered,
  onMouseEnter,
  onMouseLeave,
  onPartyClick,
}) {
  return (
    <div className="h-full w-full p-1.5">
      <div className="relative h-full w-full overflow-hidden rounded-xl border border-[#f5f0de]/10 bg-[#071f1c]/85 shadow-[0_8px_24px_rgba(6,17,16,0.4)] backdrop-blur-md">

        {/* match number — top left, subtle */}
        <div className="absolute left-3 top-2 text-sm font-bold uppercase tracking-[0.2em] text-[#f5f0de]/20">
          Match #{match?.id + 1 ?? ""}
        </div>

        <div className="mt-6 flex flex-col">
          <PartyRow
            party={topParty}
            won={topWon}
            hovered={topHovered}
            onEnter={() => topParty?.id != null && onMouseEnter(topParty.id)}
            onLeave={onMouseLeave}
            onClick={onPartyClick ? () => onPartyClick(topParty, topWon) : undefined}
          />

          {/* divider */}
          <div className="mx-3 h-px bg-[#f5f0de]/8" />

          <PartyRow
            party={bottomParty}
            won={bottomWon}
            hovered={bottomHovered}
            onEnter={() => bottomParty?.id != null && onMouseEnter(bottomParty.id)}
            onLeave={onMouseLeave}
            onClick={onPartyClick ? () => onPartyClick(bottomParty, bottomWon) : undefined}
          />
        </div>
      </div>
    </div>
  );
}