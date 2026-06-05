<script lang="ts">
	import { page } from '$app/stores';
</script>

<svelte:head>
	<title>{$page.status} — KorbanMBG</title>
</svelte:head>

<main class="max-w-[640px] mx-auto px-5 py-20 text-center">
	<div class="text-[48px] font-bold font-[JetBrains_Mono,monospace] text-[#e74c3c]">
		{$page.status}
	</div>
	<p class="text-[15px] text-[#888] mt-3">
		{#if $page.status === 404}
			Halaman tidak ditemukan.
		{:else}
			Terjadi kesalahan. Coba muat ulang sebentar lagi.
		{/if}
	</p>
	{#if $page.error?.message}
		<p class="text-[12px] text-[#555] mt-2 font-[JetBrains_Mono,monospace]">{$page.error.message}</p>
	{/if}
	<a href="/" class="text-[13px] text-[#e74c3c] mt-6 inline-block no-underline hover:underline">
		← Kembali ke dashboard
	</a>
</main>
