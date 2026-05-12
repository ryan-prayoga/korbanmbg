const API_BASE = 'http://127.0.0.1:8090/api/v1';

export async function load({ fetch }) {
	const [provincesRes, incidentsRes] = await Promise.all([
		fetch(`${API_BASE}/provinces`),
		fetch(`${API_BASE}/incidents?limit=100&sort=victim_count&order=DESC`),
	]);

	return {
		provinces: await provincesRes.json(),
		incidents: await incidentsRes.json(),
	};
}
