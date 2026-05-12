<script lang="ts">
	let { data } = $props();
	const { stats, timeline, provinces } = data;

	function fmt(n: number): string {
		return n.toLocaleString('id-ID');
	}

	// Use deduplicated sum from DB
	const totalVictims = stats.total_victims;
	const maxVictims = Math.max(...(timeline || []).map((t: any) => t.total_victims), 1);
</script>

<svelte:head>
	<title>KorbanMBG — Pemantau Korban Makan Bergizi Gratis</title>
	<meta name="description" content="Dokumentasi kasus keracunan program Makan Bergizi Gratis (MBG) di Indonesia berdasarkan data resmi." />
</svelte:head>

<main class="max-w-[960px] mx-auto px-5 py-10">
	<!-- Hero stat -->
	<section class="mb-12">
		<div class="text-[13px] text-[#888] mb-2 flex items-center gap-2">
			<span class="text-[10px] bg-[rgba(231,76,60,0.15)] text-[#e74c3c] px-1.5 py-0.5 rounded font-semibold uppercase tracking-wide">Live</span>
			Data diperbarui otomatis setiap hari
		</div>
		<div class="text-[clamp(56px,12vw,96px)] font-extrabold leading-none tracking-tight font-[JetBrains_Mono,monospace]">
			{fmt(totalVictims)}
		</div>
		<p class="text-[15px] text-[#888] mt-3 max-w-[500px]">
			anak keracunan akibat program Makan Bergizi Gratis sejak Januari 2025
		</p>
		<div class="flex flex-wrap gap-2 mt-3">
			<span class="inline-block text-[11px] font-[JetBrains_Mono,monospace] text-[#888] bg-[#1a1a1a] px-2 py-1 rounded border border-[#2a2a2a]">
				{stats.total_incidents} artikel terdokumentasi
			</span>
			<span class="inline-block text-[11px] font-[JetBrains_Mono,monospace] text-[#888] bg-[#1a1a1a] px-2 py-1 rounded border border-[#2a2a2a]">
				{stats.provinces_affected} provinsi terdampak
			</span>
		</div>
	</section>

	<!-- Stat grid -->
	<section class="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-12">
		<div class="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg p-5">
			<div class="text-[28px] font-bold font-[JetBrains_Mono,monospace] text-[#e74c3c]">{fmt(totalVictims)}</div>
			<div class="text-[12px] text-[#888] mt-1">Total korban</div>
		</div>
		<div class="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg p-5">
			<div class="text-[28px] font-bold font-[JetBrains_Mono,monospace]">{stats.total_incidents}</div>
			<div class="text-[12px] text-[#888] mt-1">Artikel berita</div>
		</div>
		<div class="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg p-5">
			<div class="text-[28px] font-bold font-[JetBrains_Mono,monospace]">{stats.provinces_affected}</div>
			<div class="text-[12px] text-[#888] mt-1">Provinsi terdampak</div>
		</div>
		<div class="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg p-5">
			<div class="text-[28px] font-bold font-[JetBrains_Mono,monospace]">63</div>
			<div class="text-[12px] text-[#888] mt-1">Insiden unik</div>
		</div>
	</section>

	<!-- Timeline chart -->
	<section class="mb-12">
		<div class="flex justify-between items-baseline mb-4">
			<h2 class="text-[16px] font-semibold">Korban per Bulan</h2>
			<span class="text-[12px] text-[#888]">Feb 2025 — Mei 2026</span>
		</div>
		<div class="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg p-6">
			<div class="flex items-end gap-1 h-[120px]">
				{#each timeline || [] as entry}
					{@const height = maxVictims > 0 ? Math.max(2, (entry.total_victims / maxVictims) * 100) : 2}
					<div class="flex-1 flex flex-col items-center h-full justify-end group relative">
						<div
							class="w-full bg-[#e74c3c] rounded-t-[3px] hover:bg-[#ff6b5a] transition-colors cursor-pointer"
							style="height: {height}%"
						></div>
						<!-- Tooltip -->
						<div class="absolute bottom-full mb-2 hidden group-hover:block bg-[#242424] border border-[#2a2a2a] px-2.5 py-1.5 rounded text-[11px] whitespace-nowrap z-10">
							<div class="font-medium">{entry.month}</div>
							<div class="text-[#e74c3c]">{fmt(entry.total_victims)} korban</div>
							<div class="text-[#888]">{entry.incident_count} insiden</div>
						</div>
						<span class="text-[10px] text-[#888] mt-2 font-[JetBrains_Mono,monospace] hidden sm:block">
							{entry.month.slice(2)}
						</span>
					</div>
				{/each}
			</div>
		</div>
	</section>

	<!-- Province ranking (clickable) -->
	<section class="mb-12">
		<div class="flex justify-between items-baseline mb-4">
			<h2 class="text-[16px] font-semibold">Provinsi Terdampak</h2>
			<a href="/peta" class="text-[12px] text-[#888] hover:text-[#e74c3c] transition-colors no-underline">Lihat peta →</a>
		</div>
		<div class="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg overflow-hidden">
			{#each (provinces || []).slice(0, 10) as prov, i}
				{@const maxProv = provinces[0]?.total_victims || 1}
				{@const pct = (prov.total_victims / maxProv) * 100}
				<a
					href="/insiden?province={prov.id}"
					class="grid grid-cols-[32px_1fr_80px] gap-3 items-center px-5 py-3 border-b border-[#2a2a2a] last:border-b-0 hover:bg-[#242424] transition-colors no-underline text-[#e8e8e8]"
				>
					<span class="text-[12px] text-[#888] font-[JetBrains_Mono,monospace] text-right">{i + 1}</span>
					<div class="flex flex-col gap-1">
						<span class="text-[13px] font-medium">{prov.name}</span>
						<div class="h-1 bg-[#242424] rounded-full overflow-hidden">
							<div class="h-full bg-[#e74c3c] rounded-full" style="width: {pct}%"></div>
						</div>
					</div>
					<div class="text-right">
						<span class="text-[14px] font-semibold font-[JetBrains_Mono,monospace] text-[#e74c3c]">
							{fmt(prov.total_victims)}
						</span>
						<div class="text-[10px] text-[#888]">{prov.incident_count} insiden</div>
					</div>
				</a>
			{/each}
		</div>
	</section>

	<!-- Aggregate sources -->
	<section>
		<div class="flex justify-between items-baseline mb-4">
			<h2 class="text-[16px] font-semibold">Sumber Data Resmi</h2>
		</div>
		<div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
			{#each stats.aggregate_data || [] as source}
				<div class="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg p-5">
					<div class="flex items-center gap-2 mb-2">
						<span class="text-[10px] font-semibold px-1.5 py-0.5 rounded bg-[rgba(231,76,60,0.15)] text-[#e74c3c] uppercase tracking-wide">{source.org}</span>
					</div>
					<div class="text-[24px] font-bold font-[JetBrains_Mono,monospace]">{fmt(source.total)}</div>
					<div class="text-[11px] text-[#888] mt-1">{source.period_start} — {source.period_end}</div>
					<p class="text-[11px] text-[#888] mt-2 leading-relaxed">{source.notes}</p>
				</div>
			{/each}
		</div>
	</section>
</main>
