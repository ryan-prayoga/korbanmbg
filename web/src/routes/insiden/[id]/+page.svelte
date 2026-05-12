<script lang="ts">
	let { data } = $props();
	const { incident } = data;

	function fmt(n: number): string {
		return n.toLocaleString('id-ID');
	}
</script>

<svelte:head>
	<title>{incident ? incident.title : 'Insiden Tidak Ditemukan'} — KorbanMBG</title>
</svelte:head>

<main class="max-w-[640px] mx-auto px-5 py-10">
	{#if incident}
		<!-- Back link -->
		<a href="/insiden" class="text-[13px] text-[#888] hover:text-[#e8e8e8] transition-colors no-underline mb-6 inline-block">
			← Kembali ke daftar insiden
		</a>

		<!-- Title -->
		<h1 class="text-[18px] font-semibold leading-snug mt-4">{incident.title}</h1>

		<!-- Meta tags -->
		<div class="flex flex-wrap gap-2 mt-4">
			{#if incident.incident_date}
				<span class="text-[11px] px-2 py-1 rounded bg-[#242424] text-[#888] border border-[#2a2a2a]">
					{incident.incident_date}
				</span>
			{/if}
			{#if incident.province}
				<span class="text-[11px] px-2 py-1 rounded bg-[#242424] text-[#888] border border-[#2a2a2a]">
					{incident.province}
				</span>
			{/if}
			{#if incident.district}
				<span class="text-[11px] px-2 py-1 rounded bg-[#242424] text-[#888] border border-[#2a2a2a]">
					{incident.district}
				</span>
			{/if}
			{#if incident.verified}
				<span class="text-[11px] px-2 py-1 rounded bg-[rgba(46,204,113,0.15)] text-[#2ecc71] border border-[rgba(46,204,113,0.3)]">
					Terverifikasi
				</span>
			{/if}
		</div>

		<!-- Victim count -->
		{#if incident.victim_count > 0}
			<div class="mt-6 bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg p-5">
				<div class="text-[12px] text-[#888] mb-1">Jumlah korban</div>
				<div class="text-[36px] font-bold font-[JetBrains_Mono,monospace] text-[#e74c3c]">
					{fmt(incident.victim_count)}
				</div>
				<div class="flex gap-4 mt-3">
					{#if incident.hospitalized > 0}
						<div>
							<span class="text-[20px] font-bold font-[JetBrains_Mono,monospace]">{fmt(incident.hospitalized)}</span>
							<span class="text-[12px] text-[#888] ml-1">dirawat</span>
						</div>
					{/if}
					{#if incident.deaths > 0}
						<div>
							<span class="text-[20px] font-bold font-[JetBrains_Mono,monospace]">{fmt(incident.deaths)}</span>
							<span class="text-[12px] text-[#888] ml-1">meninggal</span>
						</div>
					{/if}
				</div>
			</div>
		{/if}

		<!-- Description -->
		{#if incident.description}
			<div class="mt-6">
				<h2 class="text-[13px] font-semibold text-[#888] uppercase tracking-wide mb-2">Deskripsi</h2>
				<p class="text-[14px] text-[#ccc] leading-relaxed">{incident.description}</p>
			</div>
		{/if}

		<!-- Location detail -->
		{#if incident.location_detail}
			<div class="mt-6">
				<h2 class="text-[13px] font-semibold text-[#888] uppercase tracking-wide mb-2">Lokasi</h2>
				<p class="text-[14px] text-[#ccc]">
					{incident.location_detail}{incident.district ? `, ${incident.district}` : ''}{incident.province ? `, ${incident.province}` : ''}
				</p>
			</div>
		{/if}

		<!-- Menu items -->
		{#if incident.menu_items && incident.menu_items.length > 0}
			<div class="mt-6">
				<h2 class="text-[13px] font-semibold text-[#888] uppercase tracking-wide mb-2">Menu penyebab</h2>
				<div class="flex flex-wrap gap-2">
					{#each incident.menu_items as item}
						<span class="text-[12px] px-2 py-1 rounded bg-[rgba(231,76,60,0.1)] text-[#e74c3c] border border-[rgba(231,76,60,0.2)]">
							{item}
						</span>
					{/each}
				</div>
			</div>
		{/if}

		<!-- Symptoms -->
		{#if incident.symptoms && incident.symptoms.length > 0}
			<div class="mt-6">
				<h2 class="text-[13px] font-semibold text-[#888] uppercase tracking-wide mb-2">Gejala</h2>
				<div class="flex flex-wrap gap-2">
					{#each incident.symptoms as symptom}
						<span class="text-[12px] px-2 py-1 rounded bg-[#242424] text-[#888] border border-[#2a2a2a]">
							{symptom}
						</span>
					{/each}
				</div>
			</div>
		{/if}

		<!-- Source link -->
		{#if incident.source_url}
			<div class="mt-8 pt-6 border-t border-[#2a2a2a]">
				<h2 class="text-[13px] font-semibold text-[#888] uppercase tracking-wide mb-3">Sumber berita</h2>
				<a
					href={incident.source_url}
					target="_blank"
					rel="noopener noreferrer"
					class="inline-flex items-center gap-2 bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg px-4 py-3 text-[13px] text-[#e8e8e8] hover:border-[#e74c3c] transition-colors no-underline group"
				>
					<span class="text-[#888] group-hover:text-[#e74c3c] transition-colors">↗</span>
					<span>Baca berita lengkap di {incident.source_name || 'sumber'}</span>
				</a>
				<p class="text-[11px] text-[#888] mt-2 font-[JetBrains_Mono,monospace] break-all">{incident.source_url}</p>
			</div>
		{/if}

	{:else}
		<div class="text-center py-20">
			<div class="text-[48px] mb-4">404</div>
			<p class="text-[#888]">Insiden tidak ditemukan</p>
			<a href="/insiden" class="text-[13px] text-[#e74c3c] mt-4 inline-block no-underline">← Kembali</a>
		</div>
	{/if}
</main>
