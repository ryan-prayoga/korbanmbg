<script lang="ts">
	let { data } = $props();

	function fmt(n: number): string {
		return n.toLocaleString('id-ID');
	}

	const totalPages = Math.ceil((data.incidents.total || 0) / 20);
</script>

<svelte:head>
	<title>Daftar Insiden — KorbanMBG</title>
</svelte:head>

<main class="max-w-[960px] mx-auto px-5 py-10">
	<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
		<div>
			<h1 class="text-[16px] font-semibold">Daftar Insiden</h1>
			<p class="text-[13px] text-[#888] mt-1">{fmt(data.incidents.total)} insiden terdokumentasi</p>
		</div>

		<form method="get" class="flex gap-2">
			<select name="province" class="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg px-3 py-2 text-[13px] text-[#e8e8e8] outline-none focus:border-[#e74c3c] transition-colors">
				<option value="">Semua Provinsi</option>
				{#each data.provinces as prov}
					<option value={prov.id} selected={String(prov.id) === data.selectedProvince}>{prov.name}</option>
				{/each}
			</select>
			<button type="submit" class="bg-[#e74c3c] hover:bg-[#c0392b] px-4 py-2 rounded-lg text-[13px] font-medium transition-colors">
				Filter
			</button>
		</form>
	</div>

	<!-- Incident feed -->
	<div class="space-y-0">
		{#each data.incidents.data || [] as incident}
			<a href="/insiden/{incident.id}" class="flex justify-between items-start gap-4 py-4 border-b border-[#2a2a2a] no-underline text-[#e8e8e8] hover:bg-[#1a1a1a] -mx-3 px-3 rounded transition-colors">
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
						<a href={incident.source_url} target="_blank" rel="noopener" class="text-[11px] text-[#888] hover:text-[#e8e8e8] mt-2 inline-block transition-colors no-underline">
							↗ {incident.source_name || 'Sumber'}
						</a>
					{/if}
				</div>
				{#if incident.victim_count > 0}
					<div class="shrink-0 text-right">
						<span class="text-[18px] font-semibold font-[JetBrains_Mono,monospace] text-[#e74c3c]">{fmt(incident.victim_count)}</span>
					</div>
				{/if}
			</a>
		{/each}
	</div>

	<!-- Pagination -->
	{#if totalPages > 1}
		<div class="flex justify-center items-center gap-3 mt-8">
			{#if data.currentPage > 1}
				<a href="?page={data.currentPage - 1}{data.selectedProvince ? `&province=${data.selectedProvince}` : ''}"
					class="px-3 py-2 bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg text-[13px] hover:bg-[#242424] transition-colors no-underline text-[#e8e8e8]">
					← Prev
				</a>
			{/if}
			<span class="text-[13px] text-[#888] font-[JetBrains_Mono,monospace]">
				{data.currentPage}/{totalPages}
			</span>
			{#if data.currentPage < totalPages}
				<a href="?page={data.currentPage + 1}{data.selectedProvince ? `&province=${data.selectedProvince}` : ''}"
					class="px-3 py-2 bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg text-[13px] hover:bg-[#242424] transition-colors no-underline text-[#e8e8e8]">
					Next →
				</a>
			{/if}
		</div>
	{/if}
</main>
