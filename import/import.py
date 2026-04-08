import csv
import psycopg

# --- Konfigurasi koneksi DB ---
conn = psycopg.connect(
    host="127.0.0.200",
    port=5432,
    dbname="sdmporta_nusasawit",
    user="sdmporta_nusasawit_user",
    password="@Pontianak123"
)
cur = conn.cursor()

# --- Load CSV ---
csv_file = 'area.csv'
with open(csv_file, newline='', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        prov_kode = row['Kode Provinsi'].strip()
        prov_nama = row['Provinsi'].strip()
        kab_kode = row['kode kabupaten'].strip()
        kab_nama = row['Kabupaten'].strip()
        kec_kode = row['kode kecamatan'].strip()[:6]  # Truncate ke 6 chars
        kec_nama = row['Kecamatan'].strip()
        desa_kode = row['kode desa'].strip()
        desa_nama = row['Desa'].strip()

        # --- Lookup provinsi_id ---
        cur.execute("SELECT id FROM area_provinsi WHERE kode=%s", 
(prov_kode,))
        prov_res = cur.fetchone()
        if not prov_res:
            print(f"⚠ Provinsi '{prov_nama}' tidak ditemukan, skip")
            continue
        prov_id = prov_res[0]

        # --- Lookup kabupaten_id ---
        cur.execute("""
            SELECT id
            FROM area_kabupatenkota
            WHERE kode=%s AND provinsi_id=%s
        """, (kab_kode, prov_id))
        kab_res = cur.fetchone()
        
        # If not found by kode, try by name
        if not kab_res:
            cur.execute("""
                SELECT id
                FROM area_kabupatenkota
                WHERE nama=%s AND provinsi_id=%s
            """, (kab_nama, prov_id))
            kab_res = cur.fetchone()
        
        # If still not found, auto-insert kabupaten baru
        if not kab_res:
            cur.execute("""
                INSERT INTO area_kabupatenkota (kode, nama, provinsi_id, jenis)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """, (kab_kode, kab_nama, prov_id, 'KABUPATEN'))
            kab_res = cur.fetchone()
            print(f"✨ Kabupaten baru '{kab_nama}' ({kab_kode}) berhasil dibuat")
        
        kab_id = kab_res[0]

        # --- Lookup kecamatan_id ---
        if kec_kode:
            cur.execute("""
                SELECT id
                FROM area_kecamatan
                WHERE kode=%s AND kabupaten_kota_id=%s
            """, (kec_kode, kab_id))
        else:
            cur.execute("""
                SELECT id
                FROM area_kecamatan
                WHERE nama=%s AND kabupaten_kota_id=%s
            """, (kec_nama, kab_id))
        kec_res = cur.fetchone()
        
        # If not found, auto-insert kecamatan baru
        if not kec_res:
            cur.execute("""
                INSERT INTO area_kecamatan (kode, nama, kabupaten_kota_id)
                VALUES (%s, %s, %s)
                RETURNING id
            """, (kec_kode, kec_nama, kab_id))
            kec_res = cur.fetchone()
            print(f"✨ Kecamatan baru '{kec_nama}' ({kec_kode}) berhasil dibuat")
        
        kec_id = kec_res[0]

        # --- Tentukan jenis desa ---
        desa_jenis = 'DESA'

        # --- Generate kode desa jika kosong ---
        if not desa_kode:
            cur.execute("""
                SELECT kode
                FROM area_desa
                WHERE kecamatan_id=%s
                ORDER BY kode DESC
                LIMIT 1
            """, (kec_id,))
            last = cur.fetchone()
            if last and last[0][-4:].isdigit():
                last_num = int(last[0][-4:])
                next_num = last_num + 1
            else:
                next_num = 1
            desa_kode = f"{kec_kode}{next_num:04d}"

        # --- Insert atau update desa ---
        cur.execute("""
            INSERT INTO area_desa (kecamatan_id, kode, jenis, nama)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (kode) DO UPDATE
            SET nama = EXCLUDED.nama, jenis = EXCLUDED.jenis
        """, (kec_id, desa_kode, desa_jenis, desa_nama))

        print(f"✅ {desa_nama} ({desa_kode}) berhasil diinsert/update")

# Commit sekali di akhir
conn.commit()
cur.close()
conn.close()
print("🎉 Import selesai") 
