const API_BASE = 'http://127.0.0.1:8090/api/v1';

const EMPTY_STATS = {
	total_articles: 0, total_victims: 0, total_deaths: 0, total_hospitalized: 0,
	provinces_affected: 0, unique_incidents: 0, last_updated: '', official_figures: [],
};

export async function load({ fetch }) {
	try {
		const [statsRes, timelineRes, provincesRes] = await Promise.all([
			fetch(`${API_BASE}/stats`),
			fetch(`${API_BASE}/timeline`),
			fetch(`${API_BASE}/provinces`),
		]);

		if (!statsRes.ok || !timelineRes.ok || !provincesRes.ok) {
			return { stats: EMPTY_STATS, timeline: [], provinces: [], apiError: true };
		}

		return {
			stats: await statsRes.json(),
			timeline: (await timelineRes.json()) || [],
			provinces: (await provincesRes.json()) || [],
			apiError: false,
		};
	} catch {
		return { stats: EMPTY_STATS, timeline: [], provinces: [], apiError: true };
	}
}
