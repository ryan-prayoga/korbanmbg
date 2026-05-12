<script lang="ts">
	import { onMount } from 'svelte';
	let { data } = $props();

	let mapContainer: HTMLDivElement;

	const districtCoords: Record<string, [number, number]> = {
		'Bandung Barat': [-6.8575, 107.4669],
		'Ketapang': [-1.8293, 109.9781],
		'Surabaya': [-7.2575, 112.7521],
		'Mojokerto': [-7.4704, 112.4401],
		'Demak': [-6.8936, 110.6381],
		'Bogor': [-6.5971, 106.8060],
		'Agam': [-0.3333, 100.3333],
		'Klaten': [-7.7056, 110.6042],
		'Dairi': [2.7500, 98.2167],
		'Tasikmalaya': [-7.3506, 108.2172],
		'Jakarta Timur': [-6.2250, 106.9004],
		'Bantul': [-7.8894, 110.3275],
		'Sumba': [-9.6500, 119.5000],
		'Manggarai Barat': [-8.5833, 120.0000],
		'Kepulauan Anambas': [3.2167, 106.2500],
		'Tulungagung': [-8.0654, 111.9024],
		'Majene': [-3.5333, 118.9667],
		'Lombok Timur': [-8.5500, 116.5500],
		'Rembang': [-6.7073, 111.3461],
		'Grobogan': [-7.0247, 110.8672],
		'Ciamis': [-7.3305, 108.3520],
		'Kediri': [-7.8160, 112.0178],
		'Bojonegoro': [-7.1503, 111.8815],
		'Kupang': [-10.1772, 123.6070],
		'Bandung': [-6.9175, 107.6191],
		'Cianjur': [-6.8204, 107.1400],
		'Kudus': [-6.8048, 110.8405],
		'Polewali Mandar': [-3.4167, 119.0000],
		'Sukabumi': [-6.9277, 106.9300],
		'Sumedang': [-6.8563, 107.9185],
		'Gunungkidul': [-7.9831, 110.6014],
		'Garut': [-7.2275, 107.9089],
		'Kolaka': [-4.0000, 121.5833],
		'Baubau': [-5.4667, 122.6333],
		'Landak': [0.3500, 109.6000],
		'Lamongan': [-7.1199, 112.4171],
		'Tomohon': [1.3167, 124.8333],
		'Gorontalo': [0.5333, 123.0667],
		'Nabire': [-3.3667, 135.5000],
	};

	function fmt(n: number): string {
		return n.toLocaleString('id-ID');
	}

	onMount(async () => {
		const L = await import('leaflet');

		const map = L.map(mapContainer, {
			zoomControl: false,
		}).setView([-2.5, 118], 5);

		L.control.zoom({ position: 'bottomright' }).addTo(map);

		L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
			attribution: '&copy; OSM &copy; CARTO',
			maxZoom: 18,
		}).addTo(map);

		// Group incidents by district
		const byDistrict: Record<string, { count: number; victims: number; province: string }> = {};
		for (const inc of data.incidents.data || []) {
			if (inc.district) {
				if (!byDistrict[inc.district]) {
					byDistrict[inc.district] = { count: 0, victims: 0, province: inc.province };
				}
				byDistrict[inc.district].count++;
				byDistrict[inc.district].victims += inc.victim_count;
			}
		}

		for (const [district, info] of Object.entries(byDistrict)) {
			const coords = districtCoords[district];
			if (!coords) continue;

			const radius = Math.max(6, Math.min(28, Math.sqrt(info.victims) * 1.2));

			L.circleMarker(coords, {
				radius,
				fillColor: '#e74c3c',
				color: '#991b1b',
				weight: 1,
				opacity: 0.9,
				fillOpacity: 0.4,
			})
				.bindPopup(`
					<div style="font-family:Inter,sans-serif;font-size:12px;line-height:1.5;color:#1a1a1a">
						<strong style="font-size:13px">${district}</strong><br>
						<span style="color:#666">${info.province}</span><br>
						<span style="color:#e74c3c;font-weight:700;font-size:14px">${fmt(info.victims)}</span> korban<br>
						${info.count} insiden
					</div>
				`)
				.addTo(map);
		}
	});
</script>

<svelte:head>
	<title>Peta Sebaran — KorbanMBG</title>
	<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
</svelte:head>

<main class="max-w-[960px] mx-auto px-5 py-10">
	<div class="mb-6">
		<h1 class="text-[16px] font-semibold">Peta Sebaran Korban</h1>
		<p class="text-[13px] text-[#888] mt-1">Ukuran lingkaran proporsional terhadap jumlah korban. Klik untuk detail.</p>
	</div>

	<div class="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg overflow-hidden mb-8">
		<div bind:this={mapContainer} class="h-[400px] sm:h-[500px] w-full"></div>
	</div>

	<!-- Province table -->
	<div class="flex justify-between items-baseline mb-4">
		<h2 class="text-[16px] font-semibold">Statistik per Provinsi</h2>
	</div>
	<div class="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg overflow-hidden">
		<div class="overflow-x-auto">
			<table class="w-full text-[13px]">
				<thead>
					<tr class="text-left text-[#888] border-b border-[#2a2a2a]">
						<th class="px-5 py-3 font-medium">#</th>
						<th class="px-5 py-3 font-medium">Provinsi</th>
						<th class="px-5 py-3 font-medium text-right">Korban</th>
						<th class="px-5 py-3 font-medium text-right">Insiden</th>
					</tr>
				</thead>
				<tbody>
					{#each data.provinces as prov, i}
						<tr class="border-b border-[#2a2a2a]/50 hover:bg-[#242424] transition-colors">
							<td class="px-5 py-2.5 text-[#888] font-[JetBrains_Mono,monospace] text-[12px]">{i + 1}</td>
							<td class="px-5 py-2.5">{prov.name}</td>
							<td class="px-5 py-2.5 text-right text-[#e74c3c] font-medium font-[JetBrains_Mono,monospace]">{fmt(prov.total_victims)}</td>
							<td class="px-5 py-2.5 text-right text-[#888] font-[JetBrains_Mono,monospace]">{prov.incident_count}</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	</div>
</main>
