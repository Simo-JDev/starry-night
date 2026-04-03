import argparse
from stars import load_stars, compute_star_positions
from milkyway import load_milky_way, project_milky_way
from constellations import load_constellation_lines, project_constellations
from render import render_map


def main():
    parser = argparse.ArgumentParser(description="Render a sky map for a given location and time.")
    parser.add_argument("--lat", type=float, required=True)
    parser.add_argument("--lon", type=float, required=True)
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--month", type=int, required=True)
    parser.add_argument("--day", type=int, required=True)
    parser.add_argument("--hour", type=int, required=True)
    parser.add_argument("--minute", type=int, required=True)
    parser.add_argument("--mag", type=float, default=6.5)
    parser.add_argument("--output", type=str, default="skymap.png")
    parser.add_argument("--title", type=str, default="")
    parser.add_argument("--subtitle", type=str, default="")
    parser.add_argument("--ring-only", action="store_true",
                        help="Render only the compass ring and labels (fast preview mode).")
    args = parser.parse_args()

    t = (args.lat, args.lon, args.year, args.month, args.day, args.hour, args.minute)

    stars_df = None
    mw_projected = None
    segments_projected = None

    if not args.ring_only:
        print("Loading stars...")
        df = load_stars(magnitude_limit=args.mag)

        print("Computing star positions...")
        stars_df = compute_star_positions(df, *t)

        print("Loading Milky Way...")
        mw_polygons = load_milky_way()

        print("Projecting Milky Way...")
        mw_projected = project_milky_way(mw_polygons, *t)

        print("Loading constellation lines...")
        segments = load_constellation_lines()

        print("Projecting constellations...")
        segments_projected = project_constellations(segments, *t)
    else:
        print("Ring-only preview mode: skipping sky calculations.")

    print(f"Rendering to {args.output}...")
    render_map(stars_df, mw_projected, segments_projected, output_file=args.output,
               title=args.title, subtitle=args.subtitle, ring_only=args.ring_only)

    print("Done.")


if __name__ == "__main__":
    main()
