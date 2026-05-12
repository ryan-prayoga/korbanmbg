<script lang="ts">
	let { data } = $props();

	function fmt(n: number): string {
		return n.toLocaleString('id-ID');
	}

	const totalPages = Math.ceil((data.incidents.total || 0) / 20);
	const selectedProvName = data.selectedProvince
		? data.provinces.find((p: any) => String(p.id) === data.selectedProvince)?.name || ''
		: '';

	function buildUrl(page: number) {
		const params = new URLSearchParams();
		if (page > 1) params.set('page', String(page));
		if (data.selectedProvince) params.set('province', data.selectedProvince);
		if (data.query) params.set('q', data.query);
		if (data.sort && data.sort !== 'incident_date') params.set('sort', data.sort);
		const qs = params.toString();
		return '/insiden' + (qs ? '?' + qs : '');
	}
</script>

<svelte:head>
	<title>{data.query ? `Pencarian "${data.query}"` : selectedProvName ? `${selectedProvName}` : 'Daftar Insiden'} — KorbanMBG</title>
</svelte:head>

<main class="max-w-[960px] mx-auto px-5 py-10">
	<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
		<div>
			<h1 class="text-[16px] font-semibold">
				{#if data.query}
					Hasil pencarian: "{data.query}"
				{:else if selectedProvName}
					Insiden di {selectedProvName}
				{:else}
					Daftar Insiden
				{/if}
			</h1>
			<p class="text-[13px] text-[#888] mt-1">
				{fmt(data.incidents.total)} {data.query ? 'hasil ditemukan' : selectedProvName ? 'artikel di provinsi ini' : 'artikel terdokumentasi'}
			</p>
		</div>

		<div class="flex flex-wrap gap-2 items-center">
			<form method="get" class="flex flex-wrap gap-2">
				<input
					type="text"
					name="q"
					value={data.query}
					placeholder="Cari..."
					class="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg px-3 py-2 text-[13px] text-[#e8e8e8] placeholder-[#555] outline-none focus:border-[#e74c3c] transition-colors w-[110px]"
				/>
				<select name="province" class="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg px-3 py-2 text-[13px] text-[#e8e8e8] outline-none focus:border-[#e74c3c] transition-colors">
					<option value="">Semua Provinsi</option>
					{#each data.provinces as prov}
						<option value={prov.id} selected={String(prov.id) === data.selectedProvince}>{prov.name}</option>
					{/each}
				</select>
				<select name="sort" class="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg px-3 py-2 text-[13px] text-[#e8e8e8] outline-none focus:border-[#e74c3c] transition-colors">
					<option value="incident_date" selected={data.sort === 'incident_date'}>Terbaru</option>
					<option value="victim_count" selected={data.sort === 'victim_count'}>Korban terbanyak</option>
				</select>
				<button type="submit" class="bg-[#e74c3c] hover:bg-[#c0392b] px-4 py-2 rounded-lg text-[13px] font-medium transition-colors">
					Filter
				</button>
			</form>
			{#if data.selectedProvince || data.query}
				<a href="/insiden" class="text-[12px] text-[#888] hover:text-[#e8e8e8] transition-colors no-underline px-2 py-2 bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg">
					✕ Reset
				</a>
			{/if}
		</div>
	</div>

	<!-- Incident feed -->
	<div class="space-y-0">
		{#each data.incidents.data || [] as incident}
			<a href="/insiden/{incident.id}" class="flex justify-between items-start gap-3 py-4 border-b border-[#2a2a2a] no-underline text-[#e8e8e8] hover:bg-[#1a1a1a] -mx-3 px-3 rounded transition-colors">
				<div class="flex-1 min-w-0">
					<div class="text-[14px] font-medium leading-snug">{incident.title}</div>
					<div class="flex flex-wrap gap-1.5 mt-2">
						{#if incident.province}
							<span class="text-[11px] px-2 py-0.5 rounded bg-[#242424] text-[#888] border border-[#2a2a2a]">{incident.province}</span>
						{/if}
						{#if incident.district}
							<span class="text-[11px] px-2 py-0.5 rounded bg-[#242424] text-[#888] border border-[#2a2a2a]">{incident.district}</span>
						{/if}
						{#if incident.incident_date}
							<span class="text-[11px] px-2 py-0.5 rounded bg-[#242424] text-[#888] border border-[#2a2a2a]">{incident.incident_date}</span>
						{/if}
					</div>
					{#if incident.source_url}
						<span class="text-[11px] text-[#888] mt-2 inline-block">
							↗ {incident.source_name || 'Sumber'}
						</span>
					{/if}
				</div>
				<!-- Victim count — always visible including mobile -->
				<div class="shrink-0 text-right min-w-[56px]">
					{#if incident.victim_count > 0}
						<div class="text-[18px] font-bold font-[JetBrains_Mono,monospace] text-[#e74c3c] leading-tight">{fmt(incident.victim_count)}</div>
						<div class="text-[10px] text-[#888]">korban</div>
					{:else}
						<div class="text-[11px] text-[#555]">—</div>
					{/if}
				</div>
			</a>
		{/each}

		{#if (data.incidents.data || []).length === 0}
			<div class="text-center py-12">
				<p class="text-[#888]">Tidak ada insiden ditemukan</p>
			</div>
		{/if}
	</div>

	<!-- Pagination -->
	{#if totalPages > 1}
		<div class="flex justify-center items-center gap-3 mt-8">
			{#if data.currentPage > 1}
				<a href={buildUrl(data.currentPage - 1)}
					class="px-3 py-2 bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg text-[13px] hover:bg-[#242424] transition-colors no-underline text-[#e8e8e8]">
					← Prev
				</a>
			{/if}
			<span class="text-[13px] text-[#888] font-[JetBrains_Mono,monospace]">
				{data.currentPage}/{totalPages}
			</span>
			{#if data.currentPage < totalPages}
				<a href={buildUrl(data.currentPage + 1)}
					class="px-3 py-2 bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg text-[13px] hover:bg-[#242424] transition-colors no-underline text-[#e8e8e8]">
					Next →
				</a>
			{/if}
		</div>
	{/if}
</main>
