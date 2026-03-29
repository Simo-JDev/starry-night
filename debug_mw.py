import json

with open("data/mw.json") as f:
    geojson = json.load(f)

rows = []
for feature in geojson["features"]:
    fid = feature["id"]
    level = int(fid.lstrip("abcdefghijklmnopqrstuvwxyz"))
    for poly in feature["geometry"]["coordinates"]:
        coords = poly[0]
        ras  = [c[0] for c in coords]
        decs = [c[1] for c in coords]
        min_ra, max_ra   = min(ras),  max(ras)
        min_dec, max_dec = min(decs), max(decs)
        area = (max_ra - min_ra) * (max_dec - min_dec)
        rows.append({
            "id": fid,
            "level": level,
            "n_verts": len(coords),
            "min_ra": min_ra, "max_ra": max_ra,
            "min_dec": min_dec, "max_dec": max_dec,
            "area": area,
        })

rows.sort(key=lambda r: r["area"], reverse=True)

print(f"{'id':<12} {'lvl':>3} {'verts':>6}  {'min_ra':>8} {'max_ra':>8}  {'min_dec':>8} {'max_dec':>8}  {'bbox_area':>10}")
print("-" * 80)
for r in rows:
    print(
        f"{r['id']:<12} {r['level']:>3} {r['n_verts']:>6}  "
        f"{r['min_ra']:>8.2f} {r['max_ra']:>8.2f}  "
        f"{r['min_dec']:>8.2f} {r['max_dec']:>8.2f}  "
        f"{r['area']:>10.2f}"
    )
