const API_BASE = 'http://127.0.0.1:8090/api/v1';

export async function load({ fetch, url }) {
	const page = url.searchParams.get('page') || '1';
	const province_id = url.searchParams.get('province') || '';
	const district_id = url.searchParams.get('district') || '';
	const q = url.searchParams.get('q') || '';
	const sort = url.searchParams.get('sort') || 'incident_date';

	const params = new URLSearchParams({
		page,
		limit: '20',
		sort,
		order: 'DESC',
	});
	if (province_id) params.set('province_id', province_id);
	if (district_id) params.set('district_id', district_id);
	if (q) params.set('q', q);

	const [incidentsRes, provincesRes] = await Promise.all([
		fetch(`${API_BASE}/incidents?${params}`),
		fetch(`${API_BASE}/provinces`),
	]).catch(() => [null, null] as const);

	const incidents = incidentsRes && incidentsRes.ok
		? await incidentsRes.json()
		: { data: [], total: 0, page: parseInt(page), limit: 20 };
	const provinces = provincesRes && provincesRes.ok
		? await provincesRes.json()
		: [];

	return {
		incidents,
		provinces,
		currentPage: parseInt(page),
		selectedProvince: province_id,
		selectedDistrict: district_id,
		query: q,
		sort,
		apiError: !incidentsRes || !incidentsRes.ok,
	};
}
