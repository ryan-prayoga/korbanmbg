<svelte:head>
	<title>Tentang & Metodologi — KorbanMBG</title>
	<meta name="description" content="Metodologi pengumpulan data, sumber, dan batasan website KorbanMBG." />
</svelte:head>

<main class="max-w-[720px] mx-auto px-5 py-10">
	<h1 class="text-[28px] font-bold mb-2">Tentang KorbanMBG</h1>
	<p class="text-[14px] text-[#888] mb-10">
		Website independen untuk mendokumentasikan kasus keracunan makanan pada program Makan Bergizi Gratis (MBG) di Indonesia.
	</p>

	<!-- Apa ini -->
	<section class="mb-10">
		<h2 class="text-[18px] font-semibold mb-3">Apa Ini?</h2>
		<div class="text-[14px] text-[#ccc] leading-relaxed space-y-3">
			<p>
				KorbanMBG adalah platform pemantauan publik yang mengumpulkan dan menstrukturkan data kasus keracunan 
				makanan terkait program Makan Bergizi Gratis (MBG) pemerintah Indonesia. Website ini bersifat 
				<strong>independen, non-partisan, dan tidak berafiliasi</strong> dengan pihak manapun.
			</p>
			<p>
				Tujuannya sederhana: menyediakan data yang akurat, transparan, dan mudah diakses agar publik, 
				jurnalis, dan pembuat kebijakan bisa memantau keamanan pangan program ini.
			</p>
		</div>
	</section>

	<!-- Sumber Data -->
	<section class="mb-10">
		<h2 class="text-[18px] font-semibold mb-3">Sumber Data</h2>
		<div class="text-[14px] text-[#ccc] leading-relaxed space-y-3">
			<p>Data berasal dari dua kategori:</p>
			
			<div class="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg p-5 mt-3">
				<h3 class="text-[14px] font-semibold text-[#e74c3c] mb-2">1. Angka Resmi (Headline)</h3>
				<p class="text-[13px] text-[#888]">
					Angka utama yang ditampilkan di halaman depan berasal dari sumber otoritatif:
				</p>
				<ul class="text-[13px] text-[#888] mt-2 space-y-1 list-disc list-inside">
					<li><strong>JPPI</strong> — 33.626 pelajar keracunan (per April 2026, dilaporkan Kompas.id)</li>
					<li><strong>Presiden Prabowo</strong> — mengakui 28.000 siswa keracunan (Februari 2026)</li>
					<li><strong>KPAI</strong> — 12.658 anak di 38 provinsi (per akhir 2025)</li>
					<li><strong>BGN</strong> — 4.711 → 11.640 korban (September–November 2025)</li>
				</ul>
			</div>

			<div class="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg p-5 mt-3">
				<h3 class="text-[14px] font-semibold text-[#e74c3c] mb-2">2. Data Insiden (Agregasi Berita)</h3>
				<p class="text-[13px] text-[#888]">
					Data insiden dikumpulkan dari pemberitaan media nasional dan lokal melalui Google News RSS. 
					Setiap insiden diidentifikasi berdasarkan lokasi (provinsi + kabupaten/kota) dan tanggal kejadian.
				</p>
			</div>
		</div>
	</section>

	<!-- Metodologi -->
	<section class="mb-10">
		<h2 class="text-[18px] font-semibold mb-3">Metodologi</h2>
		<div class="text-[14px] text-[#ccc] leading-relaxed space-y-3">
			<div class="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg p-5">
				<h3 class="text-[14px] font-semibold mb-3">Proses Pengumpulan Data</h3>
				<ol class="text-[13px] text-[#888] space-y-2 list-decimal list-inside">
					<li><strong>Scraping</strong> — Artikel dikumpulkan dari Google News RSS dengan query terkait "keracunan MBG", "keracunan makan bergizi gratis", dll.</li>
					<li><strong>Ekstraksi</strong> — Jumlah korban diekstrak dari judul artikel menggunakan pattern matching (regex).</li>
					<li><strong>Geolokasi</strong> — Provinsi dan kabupaten diidentifikasi dari judul/deskripsi artikel via keyword matching.</li>
					<li><strong>Deduplikasi</strong> — Artikel yang meliput insiden yang sama (lokasi + tanggal ±7 hari) dikelompokkan menjadi satu insiden unik. Jumlah korban diambil dari angka tertinggi yang dilaporkan.</li>
					<li><strong>Verifikasi</strong> — Data dibandingkan dengan angka resmi dari BGN, KPAI, JPPI, dan sumber otoritatif lainnya.</li>
				</ol>
			</div>
		</div>
	</section>

	<!-- Batasan -->
	<section class="mb-10">
		<h2 class="text-[18px] font-semibold mb-3">Batasan & Disclaimer</h2>
		<div class="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg p-5">
			<ul class="text-[13px] text-[#888] space-y-2 list-disc list-inside">
				<li>Data insiden berasal dari pemberitaan media — bukan investigasi lapangan langsung.</li>
				<li>Sebagian besar kasus berstatus <strong>"diduga keracunan"</strong> — belum tentu terkonfirmasi secara medis.</li>
				<li>Jumlah korban diekstrak dari judul berita yang bisa berubah seiring waktu (update bertahap).</li>
				<li>Tidak semua insiden terliput media — angka aktual kemungkinan lebih tinggi.</li>
				<li>Deduplikasi otomatis bisa salah: dua insiden berbeda di lokasi sama dalam seminggu bisa tergabung.</li>
				<li>Website ini <strong>bukan</strong> sumber data primer — selalu rujuk ke sumber asli untuk keperluan akademis/jurnalistik.</li>
			</ul>
		</div>
	</section>

	<!-- Tech stack -->
	<section class="mb-10">
		<h2 class="text-[18px] font-semibold mb-3">Teknologi</h2>
		<div class="text-[14px] text-[#ccc] leading-relaxed">
			<p>Website ini dibangun dengan:</p>
			<ul class="text-[13px] text-[#888] mt-2 space-y-1 list-disc list-inside">
				<li>Frontend: SvelteKit + TailwindCSS</li>
				<li>Backend API: Go (Fiber v2)</li>
				<li>Database: PostgreSQL</li>
				<li>Peta: Leaflet + GeoJSON batas administrasi Indonesia</li>
				<li>Data: Google News RSS + scraping media nasional</li>
			</ul>
		</div>
	</section>

	<!-- Kontak -->
	<section class="mb-10">
		<h2 class="text-[18px] font-semibold mb-3">Kontak & Kontribusi</h2>
		<div class="text-[14px] text-[#ccc] leading-relaxed space-y-3">
			<p>
				Punya data tambahan, koreksi, atau ingin berkontribusi? Hubungi melalui:
			</p>
			<ul class="text-[13px] text-[#888] mt-2 space-y-1 list-disc list-inside">
				<li>Email: <span class="text-[#e74c3c]">kontak@ryanprayoga.dev</span></li>
				<li>GitHub: <a href="https://github.com/ryan-prayoga/korbanmbg" target="_blank" rel="noopener" class="text-[#e74c3c] hover:underline no-underline">ryan-prayoga/korbanmbg</a></li>
			</ul>
		</div>
	</section>

	<!-- Last updated -->
	<div class="text-[12px] text-[#888] border-t border-[#2a2a2a] pt-4">
		Diperbarui otomatis setiap hari · Data bersifat terbuka dan dapat diverifikasi
	</div>
</main>
