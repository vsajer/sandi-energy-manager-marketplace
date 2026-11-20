"""Convert the previous ranking without making formerly shedable loads protected."""

def migrate_priorities(options):
    updated = dict(options)
    legacy_groups = {key: options.get(key, default) for key, default in (
        ("ev_priority", 10), ("boiler_priority", 20), ("outlet_priority", 30),
    )}
    group_ranks = _negative_ranks(legacy_groups.values())
    updated.update({key: group_ranks[value] for key, value in legacy_groups.items()})
    if "outlets" in options:
        outlet_ranks = _negative_ranks(item["priority"] for item in options["outlets"])
        updated["outlets"] = [{**item, "priority": outlet_ranks[item["priority"]]} for item in options["outlets"]]
    return updated


def _negative_ranks(values):
    return {priority: -min(rank, 5) for rank, priority in enumerate(sorted(set(values)), start=1)}
