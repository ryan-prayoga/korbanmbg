const API_BASE = 'http://127.0.0.1:8090/api/v1';

export async function load({ fetch }) {
	try {
		const [provincesRes, incidentsRes] = await Promise.all([
			fetch(`${API_BASE}/provinces`),
			fetch(`${API_BASE}/incidents?limit=100&sort=victim_count&order=DESC`),
		]);

		return {
			provinces: provincesRes.ok ? (await provincesRes.json()) || [] : [],
			incidents: incidentsRes.ok ? await incidentsRes.json() : { data: [], total: 0 },
			apiError: !provincesRes.ok,
		};
	} catch {
		return { provinces: [], incidents: { data: [], total: 0 }, apiError: true };
	}
}
