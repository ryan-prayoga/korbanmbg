const API_BASE = 'http://127.0.0.1:8090/api/v1';

export async function load({ fetch, params }) {
	const res = await fetch(`${API_BASE}/incidents/${params.id}`);
	if (!res.ok) {
		return { incident: null };
	}
	return {
		incident: await res.json(),
	};
}
