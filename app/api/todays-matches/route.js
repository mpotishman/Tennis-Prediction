export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(request) {
  try {
    const { day, month, year } = await request.json();

    if (
      !Number.isInteger(day) ||
      !Number.isInteger(month) ||
      !Number.isInteger(year)
    ) {
      return Response.json(
        { error: "Day, month, and year must all be integers." },
        { status: 400 },
      );
    }

    if (month < 1 || month > 12) {
      return Response.json(
        { error: "Month must be between 1 and 12." },
        { status: 400 },
      );
    }

    const daysInMonth = new Date(year, month, 0).getDate();

    if (day < 1 || day > daysInMonth) {
      return Response.json(
        { error: `The selected month has only ${daysInMonth} days.` },
        { status: 400 },
      );
    }

    const formattedMonth = String(month).padStart(2, "0");
    const formattedDay = String(day).padStart(2, "0");
    const espnDate = `${year}${formattedMonth}${formattedDay}`;

    const espnUrl =
      "https://site.api.espn.com/apis/site/v2/sports/tennis/atp/scoreboard" +
      `?dates=${espnDate}&limit=1000`;

    const espnResponse = await fetch(espnUrl, {
      cache: "no-store",
    });

    if (!espnResponse.ok) {
      return Response.json(
        {
          error: `ESPN returned status ${espnResponse.status}.`,
        },
        { status: 502 },
      );
    }

    const data = await espnResponse.json();

    return Response.json(data);
  } catch (error) {
    return Response.json(
      {
        error: error.message || "Could not retrieve tennis matches.",
      },
      { status: 500 },
    );
  }
}