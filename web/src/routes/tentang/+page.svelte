<svelte:head>
	<title>Tentang — KorbanMBG</title>
</svelte:head>

<main class="max-w-[640px] mx-auto px-5 py-10">
	<h1 class="text-[16px] font-semibold mb-8">Tentang</h1>

	<div class="space-y-6 text-[14px] leading-relaxed text-[#ccc]">
		<section>
			<h2 class="text-[13px] font-semibold text-[#e8e8e8] uppercase tracking-wide mb-3">Apa ini</h2>
			<p>
				KorbanMBG mendokumentasikan kasus keracunan makanan pada program
				Makan Bergizi Gratis (MBG) yang diluncurkan pemerintah Indonesia sejak Januari 2025.
				Website ini bertujuan untuk transparansi dan akuntabilitas publik.
			</p>
		</section>

		<section>
			<h2 class="text-[13px] font-semibold text-[#e8e8e8] uppercase tracking-wide mb-3">Sumber data</h2>
			<ul class="space-y-2">
				<li><span class="text-[#e74c3c] font-medium">KPAI</span> — Komisi Perlindungan Anak Indonesia (lembaga negara)</li>
				<li><span class="text-[#e74c3c] font-medium">BGN</span> — Badan Gizi Nasional (penyelenggara MBG)</li>
				<li><span class="text-[#e74c3c] font-medium">JPPI</span> — Jaringan Pemantau Pendidikan Indonesia</li>
				<li><span class="text-[#e74c3c] font-medium">CISDI</span> — Center for Indonesia's Strategic Development Initiatives</li>
				<li><span class="text-[#e74c3c] font-medium">Media</span> — detik.com dan sumber berita nasional lainnya</li>
			</ul>
		</section>

		<section>
			<h2 class="text-[13px] font-semibold text-[#e8e8e8] uppercase tracking-wide mb-3">Metodologi</h2>
			<p>
				Data dikumpulkan melalui monitoring media dan laporan resmi lembaga negara.
				Setiap insiden diverifikasi dengan minimal satu sumber berita terpercaya.
				Angka korban menggunakan data terakhir yang dilaporkan per insiden.
			</p>
			<p class="mt-3 text-[#888] text-[13px]">
				Catatan: Angka total dari berbagai sumber berbeda karena perbedaan metodologi
				dan periode pengumpulan. KPAI menggunakan monitoring media, BGN menggunakan
				laporan internal, JPPI menggunakan pemantauan lapangan.
			</p>
		</section>

		<section>
			<h2 class="text-[13px] font-semibold text-[#e8e8e8] uppercase tracking-wide mb-3">Disclaimer</h2>
			<p class="text-[#888]">
				Website ini bukan milik pemerintah dan tidak berafiliasi dengan partai politik manapun.
				Semua data bersumber dari laporan resmi dan pemberitaan media yang dapat diverifikasi.
			</p>
		</section>

		<section class="pt-4 border-t border-[#2a2a2a]">
			<p class="text-[12px] text-[#888]">
				Dibangun dengan Go, SvelteKit, TailwindCSS, PostgreSQL, Leaflet.js
			</p>
		</section>
	</div>
</main>
