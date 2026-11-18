"""Convert the previous ranking without making formerly shedable loads protected."""

from .const import GROUP_PRIORITIES


def migrate_priorities(options):
    updated = dict(options)
    legacy_groups = {key: options.get(key, default) for key, default in zip(GROUP_PRIORITIES, (10, 20, 30))}
    group_ranks = _negative_ranks(legacy_groups.values())
    updated.update({key: group_ranks[value] for key, value in legacy_groups.items()})
    if "outlets" in options:
        outlet_ranks = _negative_ranks(item["priority"] for item in options["outlets"])
        updated["outlets"] = [{**item, "priority": outlet_ranks[item["priority"]]} for item in options["outlets"]]
    return updated


def _negative_ranks(values):
    return {priority: -min(rank, 5) for rank, priority in enumerate(sorted(set(values)), start=1)}
