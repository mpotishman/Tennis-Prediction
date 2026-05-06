// PLAYER DROPDOWN — searchable dropdown for selecting a tennis player.
// Receives the full players array from MatchupPanel (fetched from /api/players)
// and an onSelect callback which is called with the chosen player name.
//
// Filters the list in real time as the user types.
// Closes automatically when the user clicks outside (via a mousedown listener on document).
// Used twice in MatchupPanel — once for player1, once for player2.

import { useState, useRef, useEffect } from "react";

export default function PlayerDropdown({ players, onSelect }) {
  const [query, setQuery] = useState("");
  const [open, setOpen] = useState(false);
  const containerRef = useRef(null);

  // close when clicking outside the component
  useEffect(() => {
    function handleClickOutside(e) {
      if (containerRef.current && !containerRef.current.contains(e.target)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const filtered = players.filter((p) =>
    p.toLowerCase().includes(query.toLowerCase()),
  );

  return (
    <div ref={containerRef} className="relative w-64">
      <input
        className="w-full rounded-full px-4 py-2 text-sm font-semibold uppercase tracking-widest bg-transparent border border-stone-50/40 text-stone-50 placeholder:text-stone-400 focus:outline-none focus:border-stone-50"
        value={query}
        onChange={(e) => {
          setQuery(e.target.value);
          setOpen(true);
        }}
        onFocus={() => setOpen(true)}
        placeholder="Search player..."
      />

      {open && filtered.length > 0 && (
        <ul className="absolute z-10 w-full mt-2 rounded-xl border border-stone-50/20 bg-stone-900/90 backdrop-blur-sm max-h-48 overflow-y-auto">
          {filtered.map((player) => (
            <li
              key={player}
              onClick={() => {
                onSelect(player);
                setQuery(player);
                setOpen(false);
              }}
              className="px-4 py-2 text-sm text-stone-50 cursor-pointer hover:bg-stone-50/10 first:rounded-t-xl last:rounded-b-xl"
            >
              {player}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
