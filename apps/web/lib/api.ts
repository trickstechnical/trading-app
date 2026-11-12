const API_BASE_URL =
  process.env.API_BASE_URL ?? "http://localhost:5000/api";

export async function getInstruments() {
  const response = await fetch(`${API_BASE_URL}/market/instruments`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error("Unable to load instruments");
  }

  return response.json();
}

export async function getSignals() {
  const response = await fetch(`${API_BASE_URL}/signals/`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error("Unable to load signals");
  }

  return response.json();
}

export async function getPaperAccount() {
  const response = await fetch(`${API_BASE_URL}/paper/account`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error("Unable to load paper account");
  }

  return response.json();
}