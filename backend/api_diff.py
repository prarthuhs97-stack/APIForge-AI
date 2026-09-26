def compare_apis(previous_endpoints, current_endpoints):
    """
    Compare two parsed API endpoint lists and detect changes.
    """

    previous_map = {
        (endpoint["method"], endpoint["path"]): endpoint
        for endpoint in previous_endpoints
    }

    current_map = {
        (endpoint["method"], endpoint["path"]): endpoint
        for endpoint in current_endpoints
    }

    changes = []

    # ---------------------------------------------------------
    # Added endpoints
    # ---------------------------------------------------------
    for key, endpoint in current_map.items():
        if key not in previous_map:
            changes.append({
                "type": "added",
                "method": endpoint["method"],
                "path": endpoint["path"],
                "message": "New endpoint added."
            })

    # ---------------------------------------------------------
    # Removed endpoints
    # ---------------------------------------------------------
    for key, endpoint in previous_map.items():
        if key not in current_map:
            changes.append({
                "type": "removed",
                "method": endpoint["method"],
                "path": endpoint["path"],
                "message": "Endpoint removed."
            })

    # ---------------------------------------------------------
    # Modified endpoints
    # ---------------------------------------------------------
    for key in previous_map.keys() & current_map.keys():

        previous = previous_map[key]
        current = current_map[key]

        previous_params = {
            (
                param["name"],
                param["type"],
                param["location"]
            )
            for param in previous.get("parameters", [])
        }

        current_params = {
            (
                param["name"],
                param["type"],
                param["location"]
            )
            for param in current.get("parameters", [])
        }

        added_params = current_params - previous_params
        removed_params = previous_params - current_params

        if added_params:
            changes.append({
                "type": "modified",
                "method": current["method"],
                "path": current["path"],
                "message": "Endpoint parameters changed.",
                "details": {
                    "added_parameters": list(added_params),
                    "removed_parameters": list(removed_params)
                }
            })

        elif removed_params:
            changes.append({
                "type": "modified",
                "method": current["method"],
                "path": current["path"],
                "message": "Endpoint parameters changed.",
                "details": {
                    "added_parameters": [],
                    "removed_parameters": list(removed_params)
                }
            })

    # ---------------------------------------------------------
    # Breaking changes
    # ---------------------------------------------------------
    breaking_changes = []

    for change in changes:

        if change["type"] == "removed":
            breaking_changes.append({
                **change,
                "breaking": True,
                "message": "Removing an existing endpoint may break API clients."
            })

        elif change["type"] == "modified":

            removed = change.get("details", {}).get(
                "removed_parameters",
                []
            )

            if removed:
                breaking_changes.append({
                    **change,
                    "breaking": True,
                    "message": "Removing an existing parameter may break API clients."
                })

    return {
        "changes": changes,
        "breaking_changes": breaking_changes,
        "has_changes": bool(changes)
    }