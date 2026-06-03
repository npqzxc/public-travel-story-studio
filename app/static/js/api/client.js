export function createApiClient() {
  async function getJson(path) {
    const response = await fetch(path, {
      headers: {
        Accept: "application/json",
      },
    });
    if (!response.ok) {
      throw new Error(`Request failed: ${response.status}`);
    }
    return response.json();
  }

  return {
    getDashboard() {
      return getJson("/api/dashboard");
    },
    getTickets(search = "") {
      return getJson(`/api/tickets${search}`);
    },
    getTicket(ticketId) {
      return getJson(`/api/tickets/${ticketId}`);
    },
    getProjects() {
      return getJson("/api/projects");
    },
    getTeam() {
      return getJson("/api/team");
    },
  };
}
