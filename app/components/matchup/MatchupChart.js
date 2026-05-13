import DonutChart from '../shared/DonutChart'

export default function MatchupChart({player1, player2, player1winPct, player2winPct}) {
  return (
    <DonutChart player1={player1} player2={player2} player1Pct={player1winPct} player2Pct={player2winPct} />
  )
}
