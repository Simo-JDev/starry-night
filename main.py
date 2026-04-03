import argparse
from render import render_map
from skymap import build_skymap_data


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
    parser.add_argument("--show-names", action="store_true",
                        help="Show constellation abbreviations (e.g. Ori, And).")
    args = parser.parse_args()

    if args.ring_only:
        print("Ring-only preview mode: skipping sky calculations.")
    else:
        print("Computing sky map data...")

    stars_df, mw_projected, segments_projected, constellation_labels = build_skymap_data(
        args.lat,
        args.lon,
        args.year,
        args.month,
        args.day,
        args.hour,
        args.minute,
        mag=args.mag,
        ring_only=args.ring_only,
        show_names=args.show_names,
    )

    print(f"Rendering to {args.output}...")
    render_map(
        stars_df,
        mw_projected,
        segments_projected,
        output_file=args.output,
        title=args.title,
        subtitle=args.subtitle,
        ring_only=args.ring_only,
        show_names=args.show_names,
        constellation_labels=constellation_labels,
    )

    print("Done.")


if __name__ == "__main__":
    main()
