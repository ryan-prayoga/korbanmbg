<script lang="ts">
	import '../app.css';
	import { page } from '$app/stores';

	let { children } = $props();
	let menuOpen = $state(false);

	const navLinks = [
		{ href: '/', label: 'Dashboard' },
		{ href: '/peta', label: 'Peta' },
		{ href: '/insiden', label: 'Insiden' },
		{ href: '/tentang', label: 'Tentang' },
	];

	function isActive(href: string) {
		if (href === '/') return $page.url.pathname === '/';
		return $page.url.pathname.startsWith(href);
	}

	function closeMenu() {
		menuOpen = false;
	}
</script>

<svelte:head>
	<link rel="preconnect" href="https://fonts.googleapis.com">
	<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="anonymous">
	<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500&display=swap" rel="stylesheet">
</svelte:head>

<div class="min-h-screen bg-[#0f0f0f] text-[#e8e8e8] font-[Inter,-apple-system,sans-serif]">
	<header class="border-b border-[#2a2a2a] sticky top-0 z-50 bg-[#0f0f0f]/95 backdrop-blur-md">
		<div class="max-w-[960px] mx-auto px-5 py-3 flex items-center justify-between gap-4">
			<!-- Logo -->
			<a href="/" class="flex items-center gap-2 no-underline text-[#e8e8e8] shrink-0" onclick={closeMenu}>
				<span class="w-2 h-2 bg-[#e74c3c] rounded-full animate-pulse"></span>
				<span class="font-bold text-[15px]">KorbanMBG</span>
			</a>

			<!-- Desktop nav -->
			<nav class="hidden sm:flex gap-6 items-center">
				{#each navLinks as link}
					<a
						href={link.href}
						class="text-[13px] transition-colors no-underline {isActive(link.href) ? 'text-[#e8e8e8] font-medium' : 'text-[#888] hover:text-[#e8e8e8]'}"
					>
						{link.label}
					</a>
				{/each}
			</nav>

			<!-- Desktop search -->
			<form method="get" action="/insiden" class="hidden sm:flex items-center gap-2">
				<div class="relative">
					<input
						type="text"
						name="q"
						placeholder="Cari insiden..."
						class="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg pl-3 pr-8 py-1.5 text-[12px] text-[#e8e8e8] placeholder-[#555] outline-none focus:border-[#e74c3c] transition-colors w-[160px]"
					/>
					<button type="submit" class="absolute right-2 top-1/2 -translate-y-1/2 text-[#555] hover:text-[#888] transition-colors text-[13px]">
						⌕
					</button>
				</div>
			</form>

			<!-- Mobile hamburger -->
			<button
				class="sm:hidden flex flex-col gap-1.5 p-1"
				onclick={() => menuOpen = !menuOpen}
				aria-label="Toggle menu"
			>
				<span class="w-5 h-0.5 bg-[#888] block transition-all {menuOpen ? 'rotate-45 translate-y-2' : ''}"></span>
				<span class="w-5 h-0.5 bg-[#888] block transition-all {menuOpen ? 'opacity-0' : ''}"></span>
				<span class="w-5 h-0.5 bg-[#888] block transition-all {menuOpen ? '-rotate-45 -translate-y-2' : ''}"></span>
			</button>
		</div>

		<!-- Mobile menu -->
		{#if menuOpen}
			<div class="sm:hidden border-t border-[#2a2a2a] bg-[#0f0f0f]">
				<!-- Mobile search -->
				<div class="px-5 pt-3 pb-2">
					<form method="get" action="/insiden" class="flex gap-2">
						<input
							type="text"
							name="q"
							placeholder="Cari insiden..."
							class="flex-1 bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg px-3 py-2 text-[13px] text-[#e8e8e8] placeholder-[#555] outline-none focus:border-[#e74c3c] transition-colors"
						/>
						<button type="submit" class="bg-[#e74c3c] px-3 py-2 rounded-lg text-[13px] font-medium">
							Cari
						</button>
					</form>
				</div>
				<!-- Mobile nav links -->
				<nav class="px-5 pb-3 flex flex-col">
					{#each navLinks as link}
						<a
							href={link.href}
							onclick={closeMenu}
							class="py-3 text-[14px] border-b border-[#1a1a1a] no-underline transition-colors {isActive(link.href) ? 'text-[#e8e8e8] font-medium' : 'text-[#888]'}"
						>
							{link.label}
						</a>
					{/each}
				</nav>
			</div>
		{/if}
	</header>

	{@render children()}

	<footer class="max-w-[960px] mx-auto px-5 py-8 mt-12 border-t border-[#2a2a2a]">
		<p class="text-[12px] text-[#888] leading-relaxed">Data: KPAI, BGN, JPPI, CISDI, detik.com · Independen, non-partisan</p>
		<p class="text-[12px] text-[#888] mt-1">Diperbarui otomatis setiap hari</p>
	</footer>
</div>
