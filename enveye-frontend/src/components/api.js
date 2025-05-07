export let API_BASE_URL = "";

export async function loadConfig() {
  const res = await fetch("/config.json");
  const config = await res.json();
  API_BASE_URL = config.backend_ip;
}
