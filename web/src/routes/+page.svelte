<script lang="ts">
	let { data } = $props();
	const { stats, timeline, provinces, apiError } = data;

	// Apakah data inti benar-benar kosong (API down / belum ada data).
	// Dipakai untuk mencegah headline tampil sebagai fakta "0".
	const hasData = !apiError && (stats?.total_victims > 0 || (stats?.official_figures || []).length > 0);

	function fmt(n: number): string {
		return n.toLocaleString('id-ID');
	}

	// Use official figure as headline (highest authoritative source)
	const officialFigures = stats.official_figures || [];
	const headlineFigure = officialFigures[0]; // Highest (JPPI: 33,626 — dilaporkan Kompas.id 9 Apr 2026)
	const totalVictims = headlineFigure ? headlineFigure.total : stats.total_victims;
	const headlineSource = headlineFigure?.org || 'Data agregasi';

	// Trim leading/trailing months that are noise (0 korban + ≤1 insiden)
	const rawTimeline = (timeline || []) as any[];
	function isNoise(t: any): boolean { return (t.total_victims || 0) === 0 && (t.incident_count || 0) <= 1; }
	let _start = 0, _end = rawTimeline.length;
	while (_start < _end && isNoise(rawTimeline[_start])) _start++;
	while (_end > _start && isNoise(rawTimeline[_end - 1])) _end--;
	const trimmed = rawTimeline.slice(_start, _end);

	// API hanya mengembalikan bulan yang punya insiden, sehingga bulan kosong
	// (mis. Jun 2025) hilang dan bar terlihat kontinu padahal ada celah. Isi
	// bulan yang hilang dengan nilai nol agar sumbu waktu tidak menyesatkan.
	function fillGaps(entries: any[]): any[] {
		if (entries.length === 0) return entries;
		const out: any[] = [];
		const [sy, sm] = entries[0].month.split('-').map(Number);
		const [ey, em] = entries[entries.length - 1].month.split('-').map(Number);
		const byMonth = new Map(entries.map((e) => [e.month, e]));
		for (let y = sy, m = sm; y < ey || (y === ey && m <= em); ) {
			const key = `${y}-${String(m).padStart(2, '0')}`;
			out.push(byMonth.get(key) || { month: key, total_victims: 0, incident_count: 0 });
			if (++m > 12) { m = 1; y++; }
		}
		return out;
	}
	const displayTimeline = fillGaps(trimmed);
	const maxVictims = Math.max(...displayTimeline.map((t: any) => t.total_victims), 1);

	const monthNames = ['Jan','Feb','Mar','Apr','Mei','Jun','Jul','Agu','Sep','Okt','Nov','Des'];
	function fmtMonth(m: string): string {
		// "2025-09" → "Sep 25"
		const [y, mo] = m.split('-');
		return `${monthNames[parseInt(mo) - 1]} ${y.slice(2)}`;
	}

	function fmtDate(d: string): string {
		if (!d) return '';
		const [y, m, day] = d.split('-');
		return `${parseInt(day)} ${monthNames[parseInt(m) - 1]} ${y}`;
	}

	// "last_updated" = waktu artikel terbaru masuk (MAX created_at), bukan waktu rebuild.
	function fmtLastUpdated(s: string): string {
		if (!s) return '';
		const [date] = s.split(' ');
		return fmtDate(date);
	}
</script>

<svelte:head>
	<title>KorbanMBG — Pemantau Korban Makan Bergizi Gratis</title>
	<meta name="description" content="Dokumentasi kasus keracunan program Makan Bergizi Gratis (MBG) di Indonesia berdasarkan data resmi." />
	<meta property="og:title" content="KorbanMBG — Pemantau Korban Makan Bergizi Gratis">
	<meta property="og:description" content="33.626 pelajar keracunan akibat MBG. Data dari JPPI, KPAI, BGN. Independen, non-partisan.">
	<meta property="og:url" content="https://korbanmbg.ryanprayoga.dev">
</svelte:head>

<main class="max-w-[960px] mx-auto px-5 py-10">
	{#if !hasData}
		<div class="bg-[rgba(231,76,60,0.08)] border border-[#e74c3c]/40 rounded-lg px-5 py-4 mb-8">
			<div class="flex items-start gap-3">
				<span class="w-2 h-2 bg-[#e74c3c] rounded-full mt-1.5 shrink-0 animate-pulse"></span>
				<div>
					<p class="text-[14px] font-semibold text-[#e8e8e8]">Data sementara tidak tersedia</p>
					<p class="text-[13px] text-[#9a9a9a] mt-1 leading-relaxed">
						Server data sedang tidak dapat dijangkau. Angka di bawah mungkin belum termuat —
						silakan muat ulang halaman dalam beberapa saat.
					</p>
				</div>
			</div>
		</div>
	{/if}

	<!-- Hero stat -->
	<section class="mb-12">
		<div class="text-[13px] text-[#888] mb-2 flex items-center gap-2 flex-wrap">
			<span class="text-[10px] bg-[rgba(231,76,60,0.15)] text-[#e74c3c] px-1.5 py-0.5 rounded font-semibold uppercase tracking-wide">Data Resmi</span>
			Sumber: {headlineSource} ({headlineFigure?.period_end || ''})
		</div>
		<div class="text-[clamp(56px,12vw,96px)] font-extrabold leading-none tracking-tight font-[JetBrains_Mono,monospace]">
			{hasData ? fmt(totalVictims) : '—'}
		</div>
		<p class="text-[15px] text-[#888] mt-3 max-w-[520px]">
			pelajar diduga keracunan akibat program Makan Bergizi Gratis sejak Januari 2025
		</p>
		<p class="text-[12px] text-[#9a9a9a] mt-3 max-w-[560px] leading-relaxed">
			Angka headline adalah <span class="text-[#cccccc]">angka resmi tertinggi</span> dari sumber
			otoritatif (JPPI). Sebagai pembanding, <span class="text-[#cccccc]">estimasi independen kami</span>
			dari {fmt(stats.total_articles)} artikel berita mencapai
			<span class="text-[#cccccc] font-medium">{fmt(stats.total_victims)}</span> korban — lebih tinggi
			karena turut mencakup insiden lokal yang belum terangkum dalam laporan resmi.
			Sebagian besar kasus berstatus <span class="text-[#cccccc]">diduga</span> dan belum tentu
			terkonfirmasi medis. <a href="/tentang" class="text-[#e74c3c] no-underline hover:underline">Metodologi →</a>
		</p>
	</section>

	<!-- Stat grid -->
	<section class="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-12">
		<div class="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg p-5">
			<div class="text-[28px] font-bold font-[JetBrains_Mono,monospace] text-[#e74c3c]">{fmt(stats.total_victims)}</div>
			<div class="text-[12px] text-[#888] mt-1">Korban (agregasi berita)</div>
		</div>
		<div class="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg p-5">
			<div class="text-[28px] font-bold font-[JetBrains_Mono,monospace]">{stats.unique_incidents}</div>
			<div class="text-[12px] text-[#888] mt-1">Insiden unik</div>
		</div>
		<div class="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg p-5">
			<div class="text-[28px] font-bold font-[JetBrains_Mono,monospace]">{stats.provinces_affected}</div>
			<div class="text-[12px] text-[#888] mt-1">Provinsi terdampak</div>
		</div>
		<div class="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg p-5">
			<div class="text-[28px] font-bold font-[JetBrains_Mono,monospace]">{fmt(stats.total_articles)}</div>
			<div class="text-[12px] text-[#888] mt-1">Artikel berita</div>
		</div>
	</section>

	<!-- Timeline chart -->
	<section class="mb-12">
		<div class="flex justify-between items-baseline mb-4">
			<h2 class="text-[16px] font-semibold">Korban per Bulan</h2>
			<span class="text-[12px] text-[#888]">{displayTimeline[0] ? fmtMonth(displayTimeline[0].month) : ''} — {displayTimeline[displayTimeline.length - 1] ? fmtMonth(displayTimeline[displayTimeline.length - 1].month) : ''}</span>
		</div>
		<div class="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg p-6">
			<div class="flex items-end gap-1 h-[160px]">
				{#each displayTimeline as entry, i}
					{@const height = maxVictims > 0 ? Math.max(2, (entry.total_victims / maxVictims) * 100) : 2}
					{@const isNewYear = i > 0 && entry.month.slice(0,4) !== (displayTimeline[i-1]?.month || '').slice(0,4)}
					<div class="flex-1 flex flex-col items-center h-full justify-end group relative {isNewYear ? 'border-l border-[#444] ml-1 pl-1' : ''}">
						<!-- Value label on top -->
						<span class="text-[9px] text-[#888] font-[JetBrains_Mono,monospace] mb-1 hidden sm:block {entry.total_victims > 0 ? '' : 'sm:invisible'}">
							{entry.total_victims >= 1000 ? (entry.total_victims / 1000).toFixed(1) + 'K' : entry.total_victims}
						</span>
						<div
							class="w-full bg-[#e74c3c] rounded-t-[3px] hover:bg-[#ff6b5a] transition-colors cursor-pointer"
							style="height: {height}%"
						></div>
						<!-- Tooltip -->
						<div class="absolute bottom-full mb-2 hidden group-hover:block bg-[#242424] border border-[#2a2a2a] px-2.5 py-1.5 rounded text-[11px] whitespace-nowrap z-10">
							<div class="font-medium">{fmtMonth(entry.month)}</div>
							<div class="text-[#e74c3c]">{fmt(entry.total_victims)} korban</div>
							<div class="text-[#888]">{entry.incident_count} insiden</div>
						</div>
					</div>
				{/each}
			</div>
			<!-- Month labels row -->
			<div class="flex gap-1 mt-2 border-t border-[#2a2a2a] pt-2">
				{#each displayTimeline as entry, i}
					{@const isNewYear = i > 0 && entry.month.slice(0,4) !== (displayTimeline[i-1]?.month || '').slice(0,4)}
					<div class="flex-1 text-center {isNewYear ? 'border-l border-[#444] ml-1 pl-1' : ''}">
						<span class="text-[9px] text-[#ccc] font-[JetBrains_Mono,monospace] block">
							{monthNames[parseInt(entry.month.slice(5)) - 1]}
						</span>
					</div>
				{/each}
			</div>
			<!-- Year labels row -->
			<div class="flex gap-1 mt-1">
				{#each displayTimeline as entry, i}
					{@const year = entry.month.slice(0,4)}
					{@const isFirstOfYear = i === 0 || year !== (displayTimeline[i-1]?.month || '').slice(0,4)}
					<div class="flex-1 text-center">
						{#if isFirstOfYear}
							<span class="text-[10px] text-[#e74c3c] font-semibold font-[JetBrains_Mono,monospace]">
								{year}
							</span>
						{/if}
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

	<!-- Official figures from authoritative sources -->
	<section class="mb-12">
		<div class="flex justify-between items-baseline mb-4">
			<h2 class="text-[16px] font-semibold">Sumber Data Resmi</h2>
			<a href="/tentang" class="text-[12px] text-[#888] hover:text-[#e74c3c] transition-colors no-underline">Metodologi →</a>
		</div>
		<div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
			{#each officialFigures as source}
				<a
					href={source.source_url || '#'}
					target="_blank"
					rel="noopener"
					class="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg p-5 no-underline text-inherit hover:border-[#e74c3c] transition-colors block"
				>
					<div class="flex items-center gap-2 mb-2">
						<span class="text-[10px] font-semibold px-1.5 py-0.5 rounded bg-[rgba(231,76,60,0.15)] text-[#e74c3c] uppercase tracking-wide">{source.org}</span>
						<span class="text-[10px] text-[#888]">↗ Lihat sumber</span>
					</div>
					<div class="text-[24px] font-bold font-[JetBrains_Mono,monospace]">{fmt(source.total)}</div>
					<div class="text-[11px] text-[#888] mt-1">Per {fmtDate(source.period_end)}</div>
					<p class="text-[11px] text-[#888] mt-2 leading-relaxed">{source.notes}</p>
				</a>
			{/each}
		</div>
	</section>

	<!-- Methodology note -->
	<section class="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg p-6">
		<h3 class="text-[14px] font-semibold mb-2">Catatan Metodologi</h3>
		<p class="text-[12px] text-[#888] leading-relaxed">
			Angka headline menggunakan data resmi dari sumber otoritatif (JPPI, KPAI, BGN, pernyataan Presiden). 
			Data insiden dikumpulkan dari {fmt(stats.total_articles)} artikel berita yang dikelompokkan menjadi 
			{stats.unique_incidents} insiden unik berdasarkan lokasi dan tanggal kejadian. 
			Satu insiden bisa diliput oleh banyak media — kami deduplikasi untuk menghindari penghitungan ganda.
			<a href="/tentang" class="text-[#e74c3c] hover:underline no-underline ml-1">Baca selengkapnya →</a>
		</p>
		{#if stats.last_updated}
			<p class="text-[11px] text-[#888] mt-3 font-[JetBrains_Mono,monospace]">
				Artikel terbaru: {fmtLastUpdated(stats.last_updated)}
			</p>
		{/if}
	</section>
</main>
