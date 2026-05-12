const API_BASE = 'http://127.0.0.1:8090/api/v1';

export async function load({ fetch, url }) {
	const page = url.searchParams.get('page') || '1';
	const province_id = url.searchParams.get('province') || '';
	const q = url.searchParams.get('q') || '';

	const params = new URLSearchParams({
		page,
		limit: '20',
		sort: 'incident_date',
		order: 'DESC',
	});
	if (province_id) params.set('province_id', province_id);
	if (q) params.set('q', q);

	const [incidentsRes, provincesRes] = await Promise.all([
		fetch(`${API_BASE}/incidents?${params}`),
		fetch(`${API_BASE}/provinces`),
	]);

	return {
		incidents: await incidentsRes.json(),
		provinces: await provincesRes.json(),
		currentPage: parseInt(page),
		selectedProvince: province_id,
		query: q,
	};
}
