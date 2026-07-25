import React, { useRef, useEffect, useState } from "react";
import {
  SingleEliminationBracket,
  Match,
} from "@g-loot/react-tournament-brackets";
import MatchBracketCard from "./MatchBracketCard";

export default function BracketDisplay({ bracketInformation, featuresSelected }) {
  // bracketInformation is {roundNum: {matchNum: {player1 win percentage, player2 win percentage}}}
  const containerRef = useRef(null);
  const [containerWidth, setContainerWidth] = useState(0);
  const [containerHeight, setContainerHeight] = useState(0);
  const [scoreline, setScoreline] = useState(null);

  useEffect(() => {
    const observer = new ResizeObserver(([entry]) => {
      setContainerWidth(entry.contentRect.width);
      setContainerHeight(entry.contentRect.height);
    });
    if (containerRef.current) observer.observe(containerRef.current);
    return () => observer.disconnect();
  }, []);

  async function handleMatchClick(p1, p2) {
    if (!p1 || !p2) return; // guard TBD slots
    const res = await fetch("/api/score", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ player1: p1, player2: p2,   featuresSelected,
}),
    });
    const data = await res.json();
    setScoreline(
      data.error
        ? data.error
        : `${data.most_likely_winner} wins ${data.most_likely_score}`,
    );
  }

  const predictedWinners = {};
  for (const [round, matches] of Object.entries(bracketInformation)) {
    predictedWinners[round] = {};
    for (const [matchPos, players] of Object.entries(matches)) {
      predictedWinners[round][matchPos] = players;
    }
  }

  //   need to changed predictedwinners into the correct format for the library
  //   create a lookup, so round 1 match 1 will be "1-0" with an id of 1
  const idLookup = {};
  let id = 0;
  for (const [round, matches] of Object.entries(predictedWinners)) {
    for (const matchPos of Object.keys(matches)) {
      idLookup[`${round}-${matchPos}`] = id;
      id++;
    }
  }

  // constID now looks like this { "1-0": 0, "1-1": 1, "1-2": 2, ... "2-0": 64, "2-1": 65, ... }
  // so now for each match find the id of the next match, which is just "round+1 - math.floor(matchpos//2)" and get the id associated with that one
  const bracketMatchups = [];
  for (const [roundMatch, id] of Object.entries(idLookup)) {
    const currentMatchId = id;
    const [round, matchPos] = roundMatch.split("-");
    const nextMatchId =
      idLookup[`${Number(round) + 1}-${Math.floor(matchPos / 2)}`];
    const players = Object.keys(predictedWinners[round][matchPos]);

    let player1, player2;
    if (Number(round) === 1) {
      player1 = players[0];
      player2 = players[1];
    } else {
      const feeder1 = Number(matchPos) * 2;
      const feeder2 = Number(matchPos) * 2 + 1;
      player1 = Object.keys(predictedWinners[Number(round) - 1][feeder1])[0];
      player2 = Object.keys(predictedWinners[Number(round) - 1][feeder2])[0];
    }

    bracketMatchups.push({
      id: currentMatchId,
      nextMatchId: nextMatchId,
      tournamentRoundText: String(round),
      participants: [
        {
          id: player1.toLowerCase().replaceAll(" ", "_"),
          name: player1,
          isWinner:
            predictedWinners[round][matchPos][player1] >
            predictedWinners[round][matchPos][player2],
          resultText: `${predictedWinners[round][matchPos][player1]}%`,
        },
        {
          id: player2.toLowerCase().replaceAll(" ", "_"),
          name: player2,
          isWinner:
            predictedWinners[round][matchPos][player2] >
            predictedWinners[round][matchPos][player1],
          resultText: `${predictedWinners[round][matchPos][player2]}%`,
        },
      ],
    });
  }

  function getRoundHeaderLabel(currentRound, totalRounds) {
    const playersInRound = 2 ** (totalRounds - currentRound + 1);

    if (playersInRound === 2) return "FINAL";
    if (playersInRound === 4) return "SF";
    if (playersInRound === 8) return "QF";
    return `R${currentRound}`;
  }

  const headerFontSize =
    containerWidth > 0
      ? Math.max(12, Math.min(18, Math.round(containerWidth / 70)))
      : 12;
  const headerHeight = Math.round(headerFontSize * 2.3);
  const headerMarginBottom = Math.round(headerFontSize * 0.9);

  return (
    <div className="mt-6 w-full rounded-4xl border border-stone-50/10 bg-stone-950/20 p-4 shadow-[0_20px_50px_rgba(6,17,16,0.18)] backdrop-blur-sm">
      <div
        ref={containerRef}
        className="w-full max-h-[72vh] overflow-y-auto overflow-x-hidden"
      >
        <SingleEliminationBracket
          matches={bracketMatchups}
          matchComponent={MatchBracketCard}
          onPartyClick={(topParty, bottomParty) =>
            handleMatchClick(topParty?.name, bottomParty?.name)
          }
          options={{
            style: {
              boxHeight: Math.max(130, window.innerHeight / 8),
              connectorColor: "rgba(245, 240, 222, 0.3)",
              connectorColorHighlight: "#f5f0de",
              svgBackground: "transparent",
              roundHeader: {
                isShown: true,
                height: headerHeight,
                marginBottom: headerMarginBottom,
                backgroundColor: "rgba(245, 240, 222, 0.06)",
                fontColor: "#f5f0de",
                fontFamily:
                  '"Iowan Old Style", "Palatino Linotype", "Book Antiqua", Georgia, serif',
                fontSize: headerFontSize,
                roundTextGenerator: (currentRound, totalRounds) =>
                  getRoundHeaderLabel(currentRound, totalRounds),
              },
              matchBackground: {
                wonColor: "rgba(245, 240, 222, 0.15)",
                lostColor: "rgba(245, 240, 222, 0.04)",
              },
            },
          }}
          svgWrapper={({ children, bracketWidth, bracketHeight }) => {
            if (!React.isValidElement(children)) {
              return children;
            }

            const renderedWidth = containerWidth || bracketWidth;
            const renderedHeight = bracketWidth
              ? (renderedWidth / bracketWidth) * bracketHeight
              : bracketHeight;

            return React.cloneElement(children, {
              width: "100%",
              height: renderedHeight,
              preserveAspectRatio: "xMinYMin meet",
              style: {
                display: "block",
                width: "100%",
                height: "auto",
              },
            });
          }}
        />
      </div>
      {scoreline}
    </div>
    
  );
}
