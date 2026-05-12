const API_BASE = 'http://127.0.0.1:8090/api/v1';

export async function load({ fetch }) {
	const [statsRes, timelineRes, provincesRes] = await Promise.all([
		fetch(`${API_BASE}/stats`),
		fetch(`${API_BASE}/timeline`),
		fetch(`${API_BASE}/provinces`),
	]);

	return {
		stats: await statsRes.json(),
		timeline: await timelineRes.json(),
		provinces: await provincesRes.json(),
	};
}
