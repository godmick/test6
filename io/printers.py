"""I/O for prints."""

from graphzer.entities.io import Results


def display_results(results: Results, bulk_mode: bool = False) -> None:
    """Prints the results."""

    if bulk_mode:
        # For bulk mode: only show found domains, no details
        print("\n    ╔══════════════════════════════════════════════════════╗")
        print("    ║                  DISCOVERED DOMAINS                  ║")
        print("    ╚══════════════════════════════════════════════════════╝")
        print()
        found_count = 0
        for domain in results:
            if results[domain]:  # Only show domains with found URLs
                print(f"    ┌─ {domain}")
                print(f"    └─ {len(results[domain])} GraphQL endpoints detected")
                found_count += 1
                print()
        print("    ╔══════════════════════════════════════════════════════╗")
        print(f"    ║     SCAN COMPLETE: {found_count} domains with endpoints     ║")
        print("    ╚══════════════════════════════════════════════════════╝")
    else:
        # For single domain: show detailed results as before
        print("\n    ╔══════════════════════════════════════════════════════╗")
        print("    ║                   ANALYSIS RESULTS                   ║")
        print("    ╚══════════════════════════════════════════════════════╝")
        print()
        for domain in results:
            print(f"    ╭─ Domain: {domain}")
            print(f"    ├─ Endpoints Found: {len(results[domain])}")
            if results[domain]:
                print("    ├─ GraphQL Endpoints:")
                for result in sorted(results[domain]):
                    print(f"    │  └─ {result}")
            else:
                print("    ├─ No GraphQL endpoints detected")
            print("    ╰─────────────────────────────────────────")
            print()
