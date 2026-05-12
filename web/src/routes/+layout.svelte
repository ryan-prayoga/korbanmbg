<script lang="ts">
	import '../app.css';
	let { children } = $props();
</script>

<svelte:head>
	<link rel="preconnect" href="https://fonts.googleapis.com">
	<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="anonymous">
	<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500&display=swap" rel="stylesheet">
</svelte:head>

<div class="min-h-screen bg-[#0f0f0f] text-[#e8e8e8] font-[Inter,-apple-system,sans-serif]">
	<header class="border-b border-[#2a2a2a] sticky top-0 z-50 bg-[#0f0f0f]/90 backdrop-blur-md">
		<div class="max-w-[960px] mx-auto px-5 py-3 flex items-center justify-between">
			<a href="/" class="flex items-center gap-2 no-underline text-[#e8e8e8]">
				<span class="w-2 h-2 bg-[#e74c3c] rounded-full animate-pulse"></span>
				<span class="font-bold text-[15px]">KorbanMBG</span>
			</a>
			<nav class="flex gap-6">
				<a href="/" class="text-[13px] text-[#888] hover:text-[#e8e8e8] transition-colors no-underline">Dashboard</a>
				<a href="/peta" class="text-[13px] text-[#888] hover:text-[#e8e8e8] transition-colors no-underline">Peta</a>
				<a href="/insiden" class="text-[13px] text-[#888] hover:text-[#e8e8e8] transition-colors no-underline">Insiden</a>
				<a href="/tentang" class="text-[13px] text-[#888] hover:text-[#e8e8e8] transition-colors no-underline">Tentang</a>
			</nav>
		</div>
	</header>

	{@render children()}

	<footer class="max-w-[960px] mx-auto px-5 py-8 mt-12 border-t border-[#2a2a2a]">
		<p class="text-[12px] text-[#888] leading-relaxed">Data: KPAI, BGN, JPPI, CISDI, detik.com · Independen, non-partisan</p>
		<p class="text-[12px] text-[#888] mt-1">Terakhir diperbarui: 12 Mei 2026</p>
	</footer>
</div>
