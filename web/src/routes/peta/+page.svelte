<script lang="ts">
	import { onMount } from 'svelte';
	let { data } = $props();

	let mapContainer: HTMLDivElement;
	let selectedProv = $state<{ code: string; name: string; victims: number; incidents: number } | null>(null);
	let mapLoading = $state(true);

	function fmt(n: number): string {
		return n.toLocaleString('id-ID');
	}

	// Color scale: dark → red based on intensity
	function getColor(intensity: number): string {
		if (intensity === 0) return '#1a1a1a';
		if (intensity < 0.05) return '#3d0c0c';
		if (intensity < 0.1) return '#4a1010';
		if (intensity < 0.2) return '#6a1313';
		if (intensity < 0.35) return '#8a1818';
		if (intensity < 0.5) return '#a82020';
		if (intensity < 0.7) return '#cc2a2a';
		return '#e74c3c';
	}

	onMount(async () => {
		const L = await import('leaflet');

		const map = L.map(mapContainer, {
			zoomControl: false,
			attributionControl: true,
		}).setView([-2.5, 118], 5);

		L.control.zoom({ position: 'bottomright' }).addTo(map);

		L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}{r}.png', {
			maxZoom: 18,
		}).addTo(map);

		let kabLayer: any = null;
		let provLayer: any = null;

		// --- Load provinces choropleth ---
		const provRes = await fetch('/api/geodata/provinces.geojson');
		const provGJ = await provRes.json();

		provLayer = L.geoJSON(provGJ, {
			style: (feature: any) => {
				const v = feature.properties.victims || 0;
				return {
					fillColor: v > 0 ? getColor(feature.properties.intensity) : '#1a1a1a',
					fillOpacity: v > 0 ? 0.75 : 0.15,
					color: '#2a2a2a',
					weight: 0.8,
					opacity: 0.8,
				};
			},
			onEachFeature: (feature: any, layer: any) => {
				const p = feature.properties;
				layer.on({
					mouseover: (e: any) => {
						if (p.victims > 0) {
							e.target.setStyle({ weight: 2, color: '#e74c3c', fillOpacity: 0.9 });
						} else {
							e.target.setStyle({ weight: 1.2, color: '#666', fillOpacity: 0.3 });
						}
					},
					mouseout: (e: any) => {
						provLayer.resetStyle(e.target);
					},
					click: async (e: any) => {
						selectedProv = {
							code: p.prov_code,
							name: p.prov_name,
							victims: p.victims,
							incidents: p.incidents,
						};

						if (kabLayer) map.removeLayer(kabLayer);
						map.fitBounds(e.target.getBounds(), { padding: [20, 20] });

						try {
							const kabRes = await fetch(`/api/geodata/kabupaten/${p.prov_code}.geojson`);
							if (!kabRes.ok) return;
							const kabGJ = await kabRes.json();

							kabLayer = L.geoJSON(kabGJ, {
								style: (feat: any) => {
									const v = feat.properties.victims || 0;
									if (v === 0) {
										return {
											fillColor: '#1a1a1a',
											fillOpacity: 0.4,
											color: '#2a2a2a',
											weight: 0.4,
											opacity: 0.5,
										};
									}
									return {
										fillColor: getColor(feat.properties.intensity),
										fillOpacity: 0.85,
										color: '#e74c3c',
										weight: 1,
										opacity: 0.9,
									};
								},
								onEachFeature: (feat: any, lyr: any) => {
									const kp = feat.properties;
									lyr.on({
										mouseover: (ev: any) => {
											if (kp.victims > 0) {
												ev.target.setStyle({ weight: 2, color: '#e74c3c', fillOpacity: 0.95 });
											} else {
												ev.target.setStyle({ weight: 1.2, color: '#666', fillOpacity: 0.25 });
											}
										},
										mouseout: (ev: any) => {
											kabLayer.resetStyle(ev.target);
										},
									});
									if (kp.victims > 0) {
										const provId = data.provinces.find((pv: any) => pv.name === kp.prov_name)?.id || '';
										const incidentUrl = kp.kab_id
											? `/insiden?province=${provId}&district=${kp.kab_id}`
											: `/insiden?province=${provId}`;
										const articleCount = kp.articles || kp.incidents;
										lyr.bindPopup(`
											<div style="font-family:Inter,sans-serif;font-size:12px;line-height:1.6;min-width:160px">
												<div style="color:#fff;font-weight:600;font-size:13px;margin-bottom:2px">${kp.kab_name}</div>
												<div style="color:#888;font-size:11px;margin-bottom:8px">${kp.prov_name}</div>
												<div style="margin-bottom:2px">
													<span style="color:#e74c3c;font-weight:700;font-size:18px;font-family:'JetBrains Mono',monospace">${fmt(kp.victims)}</span>
													<span style="color:#999;font-size:12px;margin-left:4px">korban</span>
												</div>
												<div style="color:#888;font-size:11px">${kp.incidents} insiden · ${articleCount} artikel</div>
												<div style="margin-top:10px;padding-top:8px;border-top:1px solid #2a2a2a">
													<a href="${incidentUrl}" style="color:#e74c3c;font-size:11px;font-weight:600;text-decoration:none">Lihat artikel →</a>
												</div>
											</div>
										`);
									} else {
										lyr.bindPopup(`
											<div style="font-family:Inter,sans-serif;font-size:12px;line-height:1.6;min-width:160px">
												<div style="color:#fff;font-weight:600;font-size:13px;margin-bottom:2px">${kp.kab_name}</div>
												<div style="color:#888;font-size:11px;margin-bottom:6px">${kp.prov_name}</div>
												<div style="color:#666;font-size:11px;font-style:italic">Tidak ada laporan</div>
											</div>
										`);
									}
								},
							}).addTo(map);
						} catch (err) {
							console.error('Failed to load kabupaten:', err);
						}
					},
				});

				// Tooltip on hover
				if (p.victims > 0) {
					layer.bindTooltip(`
						<strong>${p.prov_name}</strong><br>
						${fmt(p.victims)} korban · ${p.incidents} insiden
					`, { sticky: true });
				} else {
					layer.bindTooltip(p.prov_name, { sticky: true });
				}
			},
		}).addTo(map);
		mapLoading = false;

		// Back button: click on map background resets to province view
		map.on('click', (e: any) => {
			if (!e.originalEvent.target.closest('.leaflet-interactive')) {
				if (kabLayer) {
					map.removeLayer(kabLayer);
					kabLayer = null;
					selectedProv = null;
					map.setView([-2.5, 118], 5);
				}
			}
		});
	});
</script>

<svelte:head>
	<title>Peta Sebaran — KorbanMBG</title>
	<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
	<style>
		.kab-tooltip { background: #1a1a1a; border: 1px solid #333; color: #e8e8e8; font-size: 11px; }
		.leaflet-tooltip { background: #1a1a1a; border: 1px solid #333; color: #e8e8e8; font-size: 11px; box-shadow: none; }
		.leaflet-tooltip::before { border-top-color: #333; }
		.leaflet-control-attribution { background: rgba(15,15,15,0.85) !important; color: #555 !important; font-size: 9px !important; }
		.leaflet-control-attribution a { color: #888 !important; }
		/* Remove focus outline on SVG paths (the "border kotak" after click) */
		.leaflet-interactive:focus { outline: none !important; }
		path.leaflet-interactive { outline: none !important; }
		/* Popup dark theme matching site palette */
		.leaflet-popup {
			margin-bottom: 20px !important;
		}
		.leaflet-popup-content-wrapper {
			position: relative !important;
			background: #0f0f0f !important;
			color: #e8e8e8 !important;
			border: 1px solid #2a2a2a !important;
			border-radius: 8px !important;
			box-shadow: 0 6px 24px rgba(0,0,0,0.7) !important;
			padding: 14px 36px 14px 16px !important;
			min-width: 180px !important;
		}
		.leaflet-popup-content {
			margin: 0 !important;
			line-height: 1.5 !important;
			color: #e8e8e8 !important;
			font-size: 12px !important;
		}
		.leaflet-popup-content strong { color: #ffffff !important; font-weight: 600 !important; }
		.leaflet-popup-tip-container {
			margin-top: -1px !important;
		}
		.leaflet-popup-tip {
			background: #0f0f0f !important;
			border: 1px solid #2a2a2a !important;
			box-shadow: none !important;
		}
		.leaflet-popup-close-button {
			position: absolute !important;
			top: 8px !important;
			right: 8px !important;
			width: 22px !important;
			height: 22px !important;
			padding: 0 !important;
			margin: 0 !important;
			color: #888 !important;
			font-size: 16px !important;
			font-weight: 400 !important;
			line-height: 22px !important;
			text-align: center !important;
			text-decoration: none !important;
			border: none !important;
			border-radius: 4px !important;
			background: transparent !important;
		}
		.leaflet-popup-close-button:hover {
			color: #e74c3c !important;
			background: #1a1a1a !important;
			text-decoration: none !important;
		}
	</style>
</svelte:head>

<main class="max-w-[960px] mx-auto px-5 py-10">
	<div class="flex items-start justify-between mb-4 gap-4">
		<div>
			<h1 class="text-[16px] font-semibold">Peta Sebaran Korban</h1>
			<p class="text-[13px] text-[#888] mt-1">
				{#if selectedProv}
					Klik kabupaten untuk detail · <button onclick={() => { selectedProv = null; }} class="text-[#e74c3c] hover:underline cursor-pointer bg-transparent border-none p-0">← Kembali ke semua provinsi</button>
				{:else}
					Klik provinsi untuk melihat sebaran per kabupaten/kota
				{/if}
			</p>
		</div>

		<!-- Legend -->
		<div class="shrink-0 bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg px-3 py-2">
			<div class="text-[10px] text-[#888] mb-1.5 uppercase tracking-wide">Intensitas</div>
			<div class="flex items-center gap-1">
				<div class="w-3 h-3 rounded-sm" style="background:#1a1a1a;border:1px solid #333"></div>
				<div class="w-3 h-3 rounded-sm" style="background:#4a1010"></div>
				<div class="w-3 h-3 rounded-sm" style="background:#7a1515"></div>
				<div class="w-3 h-3 rounded-sm" style="background:#a82020"></div>
				<div class="w-3 h-3 rounded-sm" style="background:#cc2a2a"></div>
				<div class="w-3 h-3 rounded-sm" style="background:#e74c3c"></div>
			</div>
			<div class="flex justify-between text-[9px] text-[#888] mt-0.5">
				<span>0</span>
				<span>Maks</span>
			</div>
		</div>
	</div>

	<!-- Selected province info bar -->
	{#if selectedProv}
		<div class="bg-[#1a1a1a] border border-[#e74c3c]/30 rounded-lg px-5 py-3 mb-4 flex items-center justify-between">
			<div>
				<span class="text-[14px] font-semibold">{selectedProv.name}</span>
				<span class="text-[#888] text-[13px] ml-3">
					<span class="text-[#e74c3c] font-bold font-[JetBrains_Mono,monospace]">{fmt(selectedProv.victims)}</span> korban ·
					{selectedProv.incidents} insiden
				</span>
			</div>
			<a href="/insiden?province={data.provinces.find((p: any) => p.name === selectedProv?.name)?.id || ''}"
				class="text-[12px] text-[#e74c3c] hover:underline no-underline">
				Lihat insiden →
			</a>
		</div>
	{/if}

	<div class="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg overflow-hidden mb-8 relative">
		{#if mapLoading}
			<div class="h-[450px] sm:h-[550px] w-full flex items-center justify-center">
				<div class="text-center">
					<div class="w-8 h-8 border-2 border-[#e74c3c] border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
					<p class="text-[12px] text-[#888]">Memuat peta Indonesia...</p>
				</div>
			</div>
		{/if}
		<div bind:this={mapContainer} class="h-[450px] sm:h-[550px] w-full {mapLoading ? 'h-0' : ''}"></div>
	</div>

	<!-- Province table -->
	<div class="flex justify-between items-baseline mb-4">
		<h2 class="text-[16px] font-semibold">Statistik per Provinsi</h2>
		<span class="text-[12px] text-[#888]">{data.provinces.length} provinsi terdampak</span>
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
							<td class="px-5 py-2.5">
								<a href="/insiden?province={prov.id}" class="text-[#e8e8e8] hover:text-[#e74c3c] no-underline transition-colors">{prov.name}</a>
							</td>
							<td class="px-5 py-2.5 text-right text-[#e74c3c] font-medium font-[JetBrains_Mono,monospace]">{fmt(prov.total_victims)}</td>
							<td class="px-5 py-2.5 text-right text-[#888] font-[JetBrains_Mono,monospace]">{prov.incident_count}</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	</div>
</main>
